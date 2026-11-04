"""Fixed correction-only boundary trial on38 square pairs,48 point probes and83184."""
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
from src.skin_masking.lower_face_boundary_experiment import lower_face_boundary
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support
from src.evaluation.mask_support_quality import support_retention
from src.distortion_generation.generate_distortions import transform_rgb


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,image):
    if not cv2.imwrite(str(p),image):raise OSError(p)


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    ycb=importlib.import_module('56_compare_ycrcb_estimation')
    old=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    generation=ROOT/'outputs/hair_clean_generation_v1'
    output=ROOT/'outputs/lower_face_boundary_v1'
    if output.exists():raise FileExistsError(output)
    summary=json.loads((old/'summary.json').read_text())
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json'
    label_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(label_path.read_text())
    assert not labels['draft'] and labels['manifest_sha256']==digest(manifest)
    label_map={r['point_id']:r['label'] for r in labels['labels']}
    sentinel=ROOT/config.DATA_RAW/'FairFace/train/83184.jpg'
    tracked=[Path(__file__),old/'summary.json',manifest,label_path,sentinel,
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
        ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
        ROOT/'src/skin_masking/lower_face_boundary_experiment.py',
        ROOT/'src/skin_masking/face_outline_experiment.py',ROOT/'scripts/11_prepare_training_manifests.py']
    tracked+=list(old.glob('*_ycrcb_support.png'))+list(old.glob('*_ycrcb_estimate.png'))
    tracked+=list(generation.glob('*_input.png'))
    tracked+=[ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1] for image_id in {p['image_id'] for p in points}]
    hashes={str(p):digest(p) for p in tracked}
    output.mkdir(parents=True)
    policy=dict(version='lower_face_boundary_v1',applies_to='Correction support only; no estimator/features/targets changed',
        boundary='Face oval below landmark168 nose bridge; upper rows unchanged',
        minimum_retained_fraction=.75,unavailable='Explicit failure, no fallback or empty-mask success',
        controls='Unrestricted paired YCrCb support and full-oval diagnostic',
        status='Fixed developmental hypothesis based on observed lower-boundary spill; no tuning or adoption')
    (output/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')

    def apply(image,support,stem):
        record={};candidate=None
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:return dict(status='expected_single_face'),None
        x,y,w,h=boxes[0]
        landmarks,margin,message=prepare.detect_landmarks_with_margin(image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        if landmarks is None:return dict(status='landmarks_unavailable',detail=message),None
        if np.any(support[:y]) or np.any(support[y+h:]) or np.any(support[:, :x]) or np.any(support[:,x+w:]):
            raise ValueError('Cached support escaped recomputed face box')
        crop=support[y:y+h,x:x+w]
        control,oval=restrict_to_face_outline(crop.astype(np.uint8)*255,landmarks)
        record.update(input_support_pixels=int(support.sum()),full_oval_pixels=int(np.count_nonzero(control)),
                      full_oval_retained_fraction=float(np.count_nonzero(control)/support.sum()) if support.any() else None,
                      face_box=list(map(int,boxes[0])),landmark_margin=margin)
        try:
            bounded,metadata=lower_face_boundary(crop,landmarks)
            candidate=np.zeros_like(support);candidate[y:y+h,x:x+w]=bounded
            assert not np.any(candidate&~support)
            split=metadata['split_row'];np.testing.assert_array_equal(bounded[:split],crop[:split])
            record.update(status='available',**metadata)
            save(output/(stem+'_bounded_support.png'),candidate.astype(np.uint8)*255)
        except ValueError as error:record.update(status='boundary_unavailable',reason=str(error))
        return record,candidate

    pairs=[];observations=[];boards={}
    for row in summary['square_pairs']:
        pair=row['pair_id'];source=pair.split('__',1)[1].rsplit('__',1)[0]
        image=cv2.imread(str(generation/(pair+'_input.png')))
        support=cv2.imread(str(old/(pair+'_ycrcb_support.png')),0)>0
        estimate=cv2.imread(str(old/(pair+'_ycrcb_estimate.png')),0)>0
        reference=cv2.imread(str(generation/(source+'_generation_mask.png')),0)>0
        record,candidate=apply(image,support,pair)
        record.update(pair_id=pair,historical_table_use=row['historical_table_use'],
                      original_retention=support_retention(reference,estimate,support))
        if candidate is not None:
            removed=support&~candidate
            record.update(bounded_retention=support_retention(reference,estimate,candidate),
                removed_inside_generation=int((removed&reference).sum()),removed_outside_generation=int((removed&~reference).sum()))
        pairs.append(record);panels=[]
        for title,mask,color in [('YCrCb support',support,[0,200,0]),('Lower fence',candidate,[0,200,0]),
                                  ('Removed',support&~candidate if candidate is not None else None,[0,0,255])]:
            panel=image.copy()
            if mask is not None:panel[mask]=np.rint(.4*panel[mask]+.6*np.array(color)).astype(np.uint8)
            panel=cv2.copyMakeBorder(panel,30,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(panel,pair.rsplit('__',1)[1]+' '+title if mask is not None else 'UNAVAILABLE '+title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
            panels.append(panel)
        boards.setdefault(source,[]).append(np.hstack(panels))
        print(pair+': '+record['status'],flush=True)
    for image_id in sorted({p['image_id'] for p in points}):
        clean=cv2.imread(str(ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1]))
        for variant in ['clean','global_color_shift']:
            image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            stem=image_id.replace('/','_')+'_'+variant
            support=cv2.imread(str(old/(stem+'_ycrcb_support.png')),0)>0
            record,candidate=apply(image,support,stem)
            for point in [p for p in points if p['image_id']==image_id]:
                assert image.shape[:2]==(point['height'],point['width'])
                observations.append(dict(point_id=point['point_id'],variant=variant,label=label_map[point['point_id']],
                    unbounded_selected=bool(support[point['y'],point['x']]),available=candidate is not None,
                    bounded_selected=bool(candidate[point['y'],point['x']]) if candidate is not None else None,
                    boundary_status=record['status']))
    # Historical failure sentinel: diagnostic-only source, never admitted to fitting.
    segmenter=SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    sentinels=[]
    try:
        for variant in ['clean','global_color_shift']:
            image=cv2.imread(str(sentinel))
            if variant!='clean':image=cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
            record=dict(variant=variant,status='expected_single_face')
            if len(boxes)==1:
                x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w]
                baseline=prepare.compute_versioned_skin_mask(crop,image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
                if baseline.landmarks_available:
                    estimation=ycb.ycrcb_mask(crop,baseline.exclusion_mask>0)
                    try:
                        material=np.zeros(image.shape[:2],bool)
                        material[y:y+h,x:x+w]=material_checked_support(crop,estimation,baseline.exclusion_mask>0)
                        support=hair_veto_support(segmenter.categories_bgr(image),material)
                        record,candidate=apply(image,support,'sentinel83184_'+variant)
                        record['variant']=variant
                    except ValueError as error:record.update(status='upstream_unavailable',reason=str(error))
                else:record['status']='landmarks_unavailable'
            sentinels.append(record)
    finally:segmenter.close()
    counts={}
    for variant in ['clean','global_color_shift']:
        cohort=[p for p in observations if p['variant']==variant]
        counts[variant]={label:dict(total=sum(p['label']==label for p in cohort),available=sum(p['label']==label and p['available'] for p in cohort),
            unbounded_selected=sum(p['label']==label and p['unbounded_selected'] for p in cohort),
            bounded_selected=sum(p['label']==label and p['bounded_selected'] is True for p in cohort)) for label in sorted(set(label_map.values()))}
    assert len(pairs)==38 and len(observations)==48
    assert hashes=={p:digest(p) for p in hashes},'Inputs changed'
    report=dict(status='complete',pairs=pairs,point_observations=observations,point_counts=counts,sentinels=sentinels,input_sha256=hashes,
                boundary_status_counts=dict(Counter(p['status'] for p in pairs)),
                warning='No inference features/targets/training/policies changed. Generation support is not skin truth; guard is not validated landmark confidence.')
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    links=[]
    for source,panels in boards.items():
        filename=source+'_comparison.png';save(output/filename,np.vstack(panels));links.append(f'- [{source}]({filename})')
    (output/'review-index.md').write_text('# Lower-face boundary trial\n\nSupport and removed pixels, not corrected images.\n\n'+'\n'.join(links),encoding='utf-8')
    print(json.dumps(dict(status=report['boundary_status_counts'],points=counts,sentinels=sentinels),indent=2))


if __name__=='__main__':main()
