"""Preserve baseline support and fence only new YCrCb additions; no fitting."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.additions_boundary_experiment import restrict_new_support
from src.evaluation.mask_support_quality import support_retention
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,image):
    if not cv2.imwrite(str(path),image):raise OSError(path)


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    old=ROOT/'outputs/ycrcb_estimation_ablation_v1'
    lower=ROOT/'outputs/lower_face_boundary_v1'
    generation=ROOT/'outputs/hair_clean_generation_v1'
    output=ROOT/'outputs/additions_only_boundary_v1'
    if output.exists():raise FileExistsError(output)
    summary=json.loads((old/'summary.json').read_text())
    controls=json.loads((lower/'summary.json').read_text())
    point_path=ROOT/'data/manifests/material_review_v1/review_manifest.json'
    label_path=point_path.with_name('material_review_labels.json')
    points=json.loads(point_path.read_text())['points'];labels=json.loads(label_path.read_text())
    assert not labels['draft'] and labels['manifest_sha256']==digest(point_path)
    label_map={p['point_id']:p['label'] for p in labels['labels']}
    image_paths={image_id:ROOT/config.DATA_RAW/'FairFace'/image_id.split('__',1)[1] for image_id in {p['image_id'] for p in points}}
    paths=[Path(__file__),old/'summary.json',lower/'summary.json',point_path,label_path,
           ROOT/'src/skin_masking/additions_boundary_experiment.py',
           ROOT/'src/skin_masking/lower_face_boundary_experiment.py',ROOT/'src/skin_masking/face_outline_experiment.py',
           ROOT/'scripts/11_prepare_training_manifests.py',ROOT/config.FACE_MODEL_PATH,
           ROOT/config.FACE_LANDMARKER_MODEL_PATH,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    paths+=list(old.glob('*_support.png'))+list(old.glob('*_estimate.png'))
    paths+=list(lower.glob('*_bounded_support.png'))+list(generation.glob('*_input.png'))
    paths+=list(generation.glob('*_generation_mask.png'))+list(image_paths.values())
    hashes={str(p):digest(p) for p in paths}
    output.mkdir(parents=True)
    (output/'policy.json').write_text(json.dumps(dict(
        version='additions_only_boundary_v1',rule='baseline HSV/YCrCb support UNION lower-boundary-checked YCrCb proposal',
        guard='Unchanged75%proposal retention gate evaluated BEFORE union; no geometry-failure fallback',
        scope='Correction support only; candidate YCrCb estimation/features unchanged; no training tables or production estimators altered',
        warning='Baseline errors are retained deliberately; reference generation support is not annotated skin.'),indent=2),encoding='utf-8')

    def apply(image,stem):
        baseline=cv2.imread(str(old/(stem+'_baseline_support.png')),0)>0
        proposal=cv2.imread(str(old/(stem+'_ycrcb_support.png')),0)>0
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:return dict(status='expected_single_face'),None,baseline,proposal
        x,y,w,h=boxes[0]
        landmarks,margin,message=prepare.detect_landmarks_with_margin(image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        if landmarks is None:return dict(status='landmarks_unavailable'),None,baseline,proposal
        for mask in [baseline,proposal]:
            crop=np.zeros_like(mask);crop[y:y+h,x:x+w]=mask[y:y+h,x:x+w]
            np.testing.assert_array_equal(mask,crop)
        try:
            crop,metadata=restrict_new_support(baseline[y:y+h,x:x+w],proposal[y:y+h,x:x+w],landmarks)
        except ValueError as error:return dict(status='boundary_unavailable',reason=str(error)),None,baseline,proposal
        candidate=np.zeros_like(baseline);candidate[y:y+h,x:x+w]=crop
        expected=cv2.imread(str(lower/(stem+'_bounded_support.png')),0)>0
        np.testing.assert_array_equal(candidate,baseline|expected)
        assert not np.any(baseline&~candidate)
        assert not np.any(candidate&~(baseline|proposal))
        save(output/(stem+'_support.png'),candidate.astype(np.uint8)*255)
        return dict(status='available',**metadata),candidate,baseline,proposal

    pairs=[];observations=[];boards={}
    for row in summary['square_pairs']:
        pair=row['pair_id'];source=pair.split('__',1)[1].rsplit('__',1)[0]
        image=cv2.imread(str(generation/(pair+'_input.png')))
        record,candidate,baseline,proposal=apply(image,pair)
        record.update(pair_id=pair,historical_table_use=row['historical_table_use'],
                      input_estimation_status=row['methods']['baseline']['status'])
        if candidate is not None:
            reference=cv2.imread(str(generation/(source+'_generation_mask.png')),0)>0
            estimation=cv2.imread(str(old/(pair+'_ycrcb_estimate.png')),0)>0
            record.update(retention=support_retention(reference,estimation,candidate),
                removed_from_unrestricted_proposal=int((proposal&~candidate).sum()),
                baseline_pixels_lost=int((baseline&~candidate).sum()))
        pairs.append(record);panels=[]
        for title,mask in [('Original baseline',baseline),('YCb unrestricted',proposal),('Additions fence',candidate)]:
            panel=image.copy()
            if mask is not None:panel[mask]=np.rint(.45*panel[mask]+.55*np.array([0,200,0])).astype(np.uint8)
            panel=cv2.copyMakeBorder(panel,30,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(panel,pair.rsplit('__',1)[1]+' '+title if mask is not None else 'UNAVAILABLE',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
            panels.append(panel)
        boards.setdefault(source,[]).append(np.hstack(panels))
    for image_id,path in sorted(image_paths.items()):
        clean=cv2.imread(str(path))
        for variant in ['clean','global_color_shift']:
            image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            stem=image_id.replace('/','_')+'_'+variant
            record,candidate,baseline,proposal=apply(image,stem)
            for point in [p for p in points if p['image_id']==image_id]:
                assert image.shape[:2]==(point['height'],point['width'])
                px,py=point['x'],point['y']
                observations.append(dict(point_id=point['point_id'],variant=variant,label=label_map[point['point_id']],
                    baseline_selected=bool(baseline[py,px]),ycrcb_selected=bool(proposal[py,px]),
                    available=candidate is not None,selected=bool(candidate[py,px]) if candidate is not None else None))
    counts={}
    for variant in ['clean','global_color_shift']:
        cohort=[p for p in observations if p['variant']==variant]
        counts[variant]={label:dict(total=sum(p['label']==label for p in cohort),available=sum(p['label']==label and p['available'] for p in cohort),
            baseline_selected=sum(p['label']==label and p['baseline_selected'] for p in cohort),
            candidate_selected=sum(p['label']==label and p['selected'] is True for p in cohort)) for label in sorted(set(label_map.values()))}
    assert len(pairs)==38 and len(observations)==48
    assert hashes=={p:digest(p) for p in hashes},'Existing evidence changed'
    report=dict(status='complete',pairs=pairs,point_observations=observations,point_counts=counts,input_sha256=hashes,
        prior_geometry_sentinels=dict(source=str(lower/'summary.json'),results=controls['sentinels'],status='Prior controls reused; not new sentinel inference. Same proposal gate precedes union; invalid-geometry behavior unit-tested.'),
        training_screen_pass=sum(r['historical_table_use']=='train' and r['status']=='available' and r['retention']['screen_pass'] for r in pairs),
        warning='No model,cohort or runtime change. Baseline preservation retains baseline errors. Mask agreement is not accuracy.')
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    links=[]
    for source,panels in boards.items():
        name=source+'_comparison.png';save(output/name,np.vstack(panels));links.append(f'- [{source}]({name})')
    (output/'review-index.md').write_text('# Additions-only boundary\n\nAll original support retained; only new proposals restricted.\n\n'+'\n'.join(links),encoding='utf-8')
    print(json.dumps(dict(available=sum(r['status']=='available' for r in pairs),training_screen_pass=report['training_screen_pass'],points=counts),indent=2))


if __name__=='__main__':main()
