"""Fixed YCrCb-only ablation: all square pairs plus labeled clean/shift probes.

Only the HSV intersection is removed. Face boxes, feature exclusions, YCrCb
ranges, morphology, component rule and correction policy remain paired.
"""
import csv
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.skin_mask import keep_largest_connected_component
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,image):
    if not cv2.imwrite(str(path),image):raise OSError(path)


def ycrcb_mask(crop,exclude):
    raw=cv2.inRange(cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb),
                   np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    raw=cv2.morphologyEx(raw,cv2.MORPH_OPEN,kernel)
    raw=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,kernel)
    raw=cv2.morphologyEx(raw,cv2.MORPH_CLOSE,kernel)
    return (keep_largest_connected_component(raw)>0)&~exclude


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    baseline=ROOT/'outputs/hair_clean_generation_v1'
    output=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    if output.exists():raise FileExistsError(output)
    table=ROOT/'data/manifests/controlled_square256_v1/all_pairs_audit.csv'
    with table.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json'
    label_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(label_path.read_text())
    assert not labels['draft'] and labels['manifest_sha256']==digest(manifest)
    label_map={r['point_id']:r['label'] for r in labels['labels']}
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    paths=[Path(__file__),table,manifest,label_path,model,
           ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,ROOT/config.FACE_MODEL_PATH,
           ROOT/config.FACE_LANDMARKER_MODEL_PATH,ROOT/'scripts/11_prepare_training_manifests.py',
           ROOT/'src/skin_masking/skin_mask.py',ROOT/'src/skin_masking/material_checked_support.py',
           ROOT/'src/evaluation/mask_support_quality.py']
    paths += list(baseline.glob('*.png'))
    image_paths={image_id:ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1] for image_id in {p['image_id'] for p in points}}
    paths+=list(image_paths.values());hashes={str(p):digest(p) for p in paths}
    output.mkdir(parents=True)
    (output/'policy.json').write_text(json.dumps(dict(
        status='Fixed exploratory ablation; not adopted or tuned',
        candidate='YCrCb-only Cr133..173,Cb77..127; same open,close,close5x5 ellipse; largest component; same complete-mouth anatomical exclusions',
        correction='same material color check and hair veto',
        square_inputs='All38 saved hair-clean generation probes; same input for baseline/candidate',
        labeled_inputs='24 original224 coordinates on clean and global color shift gamma1,red.85,blue1.15; labels reused,48 observations per method',
        warning='Matches the detailed proposal color rule more closely but retains implementation-specific detector, exclusions and correction helpers.'),indent=2),encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model)

    def paired(image,stem):
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        records={};masks={}
        if len(boxes)!=1:
            return {name:dict(status='expected_single_face',face_count=len(boxes)) for name in ['baseline','ycrcb']},masks
        x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w]
        result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available:
            return {name:dict(status='landmarks_unavailable') for name in ['baseline','ycrcb']},masks
        exclude=result.exclusion_mask>0;categories=segmenter.categories_bgr(image)
        for name,estimate in [('baseline',result.mask>0),('ycrcb',ycrcb_mask(crop,exclude))]:
            assert not np.any(estimate&exclude)
            full=np.zeros(image.shape[:2],bool);full[y:y+h,x:x+w]=estimate
            support=np.zeros_like(full)
            stats=compute_masked_lab_statistics(crop,estimate.astype(np.uint8)*255,1000)
            if stats['valid']:
                material=np.zeros_like(full);material[y:y+h,x:x+w]=material_checked_support(crop,estimate,exclude)
                support=hair_veto_support(categories,material)
                assert not np.any(support&(categories==1))
                assert not np.any(support[y:y+h,x:x+w]&exclude)
            records[name]=dict(status='success' if stats['valid'] else stats['reason'],
                               **stats,correction_pixels=int(support.sum()))
            masks[name]=(full,support)
            for suffix,mask in [('estimate',full),('support',support)]:save(output/(stem+'_'+name+'_'+suffix+'.png'),mask.astype(np.uint8)*255)
        return records,masks

    square=[];observations=[];boards={}
    try:
        for row in rows:
            pair=row['pair_id'];image=cv2.imread(str(baseline/(pair+'_input.png')))
            records,masks=paired(image,pair)
            reference=cv2.imread(str(baseline/(row['source_image_id'].replace('/','_')+'_generation_mask.png')),0)>0
            for name in records:
                if name in masks:
                    records[name]['retention']=support_retention(reference,*masks[name])
            if 'baseline' in masks:
                np.testing.assert_array_equal(masks['baseline'][0],cv2.imread(str(baseline/(pair+'_estimation.png')),0)>0)
                np.testing.assert_array_equal(masks['baseline'][1],cv2.imread(str(baseline/(pair+'_correction.png')),0)>0)
            square.append(dict(pair_id=pair,historical_table_use=row['table_use'],methods=records))
            panels=[]
            for name in ['baseline','ycrcb']:
                panel=image.copy()
                if name in masks:
                    support=masks[name][1];panel[support]=np.rint(.55*panel[support]+.45*np.array([0,220,0])).astype(np.uint8)
                panel=cv2.copyMakeBorder(panel,30,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,row['variant']+' '+name,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1);panels.append(panel)
            boards.setdefault(row['source_image_id'],[]).append(np.hstack(panels))
            print(pair,flush=True)
        for image_id,path in sorted(image_paths.items()):
            clean=cv2.imread(str(path))
            for variant in ['clean','global_color_shift']:
                image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                records,masks=paired(image,image_id.replace('/','_')+'_'+variant)
                for point in [p for p in points if p['image_id']==image_id]:
                    assert image.shape[:2]==(point['height'],point['width'])
                    for name in records:
                        available=records[name]['status']=='success'
                        observations.append(dict(point_id=point['point_id'],image_id=image_id,label=label_map[point['point_id']],variant=variant,
                            method=name,available=available,selected=bool(masks[name][1][point['y'],point['x']]) if available else None))
        counts={}
        for variant in ['clean','global_color_shift']:
            counts[variant]={}
            for name in ['baseline','ycrcb']:
                cohort=[p for p in observations if p['method']==name and p['variant']==variant]
                counts[variant][name]={label:dict(total=sum(p['label']==label for p in cohort),
                    available=sum(p['label']==label and p['available'] for p in cohort),
                    selected=sum(p['label']==label and p['selected'] is True for p in cohort)) for label in sorted(set(label_map.values()))}
        assert len(square)==38 and len(observations)==96
        assert hashes=={p:digest(p) for p in hashes}
        report=dict(status='complete',square_pairs=square,labeled_observations=observations,point_counts=counts,input_sha256=hashes,
                    screen_pass_training={name:sum(r['historical_table_use']=='train' and r['methods'][name]['status']=='success' and r['methods'][name]['retention']['screen_pass'] for r in square) for name in ['baseline','ycrcb']},
                    warning='No fitting/adoption; source support not true skin; labeled probes reused development evidence.')
        (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        links=[]
        for source,panels in boards.items():
            filename=source.replace('/','_')+'_comparison.png';save(output/filename,np.vstack(panels));links.append(f'- [{source}]({filename})')
        (output/'review-index.md').write_text('# Baseline versus YCrCb-only correction support\n\nNot corrected images.\n\n'+'\n'.join(links),encoding='utf-8')
        print(json.dumps(dict(training=report['screen_pass_training'],points=counts),indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
