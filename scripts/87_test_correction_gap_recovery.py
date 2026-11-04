"""Fixed correction-only enclosed-gap recovery; never alter feature/generation masks."""
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
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recover(image,measurement,support,excluded,categories):
    """All-or-nothing additions to small enclosed components under fixed gates."""
    if any(m.dtype!=bool or m.shape!=image.shape[:2] for m in [measurement,support,excluded]):
        raise ValueError('Matching boolean masks required')
    if image.dtype!=np.uint8 or categories.dtype!=np.uint8 or categories.shape!=support.shape or (categories>5).any():
        raise ValueError('uint8 image and six-class map required')
    if measurement.sum()<1000:raise ValueError('Insufficient measurement seeds')
    lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
    samples=lab[measurement&~excluded].astype(float)
    if len(samples)<1000:raise ValueError('Insufficient unprotected seeds')
    center=np.median(samples,axis=0)
    scale=np.maximum(1.4826*np.median(np.abs(samples-center),axis=0),[12.,6.,6.])
    material=np.sqrt(np.sum(((lab-center)/scale)**2,axis=2))<=3
    distance=cv2.distanceTransform((~excluded).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE) if excluded.any() else np.full(support.shape,np.inf)
    count,labels,stats,_=cv2.connectedComponentsWithStats((~support).astype(np.uint8),connectivity=8)
    border=set(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]].tolist())
    added=np.zeros_like(support);components=[]
    for label in range(1,count):
        region=labels==label;area=int(stats[label,cv2.CC_STAT_AREA]);reasons=[]
        if label in border:reasons.append('connected_to_image_boundary')
        if area>64:reasons.append('larger_than_64_pixels')
        if (region&excluded).any() or not (distance[region]>2).all():reasons.append('protected_feature_or_within2pixels')
        if not np.isin(categories[region],[2,3]).all():reasons.append('non_skin_category')
        if not material[region].all():reasons.append('material_inconsistency')
        if not reasons:added|=region
        if label not in border:
            x,y,w,h=map(int,stats[label,:4]);components.append(dict(bounds=[x,y,x+w,y+h],pixels=area,added=not reasons,reasons=reasons))
    candidate=support|added
    assert not (support&~candidate).any() and not (added&excluded).any()
    return candidate,added,components


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    output=ROOT/'outputs/correction_gap_recovery_v1'
    if output.exists():raise FileExistsError(output)
    batches=[ROOT/'outputs/non_skin_regenerated_remaining28_v1',ROOT/'outputs/non_skin_regenerated_two_v1']
    approval=ROOT/'data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json'
    approved=set(json.loads(approval.read_text())['approved_pairs']);selected=[]
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json';label_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(label_path.read_text());assert labels['manifest_sha256']==digest(manifest) and not labels['draft']
    label_map={r['point_id']:r['label'] for r in labels['labels']}
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    tracked=[Path(__file__),approval,manifest,label_path,model,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/development_exposure_additions.jsonl']
    for parent in batches:
        tracked.append(parent/'summary.json')
        for row in json.loads((parent/'summary.json').read_text())['attempts']:
            pair=Path(row['image_id']).stem+'_'+row['variant']
            if parent==batches[1] and pair not in approved:continue
            selected.append((parent,row,pair))
            tracked += [parent/'images'/(pair+s) for s in ['_input.png','_baseline_estimate.png','_support.png']]
            tracked += [parent/'images'/(Path(row['image_id']).stem+'_generation.png')]
    raw_paths={ident:ROOT/config.DATA_RAW/'FairFace'/ident.split('__',1)[1] for ident in {p['image_id'] for p in points}}
    for ident,path in raw_paths.items():
        tracked.append(path)
        for variant in ['clean','global_color_shift']:
            stem=ident.replace('/','_')+'_'+variant
            tracked += [ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png'),ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')]
    assert len(selected)==32
    hashes={str(p):digest(p) for p in tracked};output.mkdir();(output/'masks').mkdir();(output/'boards').mkdir()
    policy=dict(status='Fixed before running; experimental correction-only candidate',maximum_component_pixels=64,
        rule='Fill entire component only if fully enclosed,at most64pixels,no protected feature overlap,allpixels>2pixels from exclusions,allpredictedbody/face-skin,and allrobustLabdistance<=3.',
        material='Same fixed median/MAD channel scales with floors12/6/6; seed from current measurement mask,not reference.',
        invariants='Preserve all original correction pixels; do not alter measurement/generation/features or synthesize new inputs; do not fill image-border-connected gaps.',
        limits='Development heuristic,not validated cutoff or paint detector. No threshold search or model fitting. Boundary coverage and neck support not solved.')
    (output/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model);records=[];boards={};observations=[]

    def exclusions(image):
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:raise ValueError('Unavailable single-face geometry')
        x,y,w,h=boxes[0]
        result=prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not result.landmarks_available:raise ValueError('Unavailable landmarks; no fallback')
        full=np.zeros(image.shape[:2],bool);full[y:y+h,x:x+w]=result.exclusion_mask>0
        return full

    def board(image,old,new,added,pair):
        panels=[]
        for title,mask in [('Original correction',old),('Candidate correction',new),('Added pixels: red',added)]:
            shown=image.copy()
            shown[mask]=np.rint(.5*shown[mask]+.5*np.asarray([0,220,0] if title!='Added pixels: red' else [0,0,255])).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,34,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,pair,(3,13),cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1);cv2.putText(shown,title,(3,28),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
            panels.append(shown)
        return np.hstack(panels)

    try:
        for parent,row,pair in selected:
            image=cv2.imread(str(parent/'images'/(pair+'_input.png')))
            measurement=cv2.imread(str(parent/'images'/(pair+'_baseline_estimate.png')),0)>0
            old=cv2.imread(str(parent/'images'/(pair+'_support.png')),0)>0
            excluded=exclusions(image);categories=segmenter.categories_bgr(image)
            new,added,components=recover(image,measurement,old,excluded,categories)
            for name,mask in [('candidate',new),('added',added),('excluded',excluded),('categories',categories)]:
                pixels=mask if name=='categories' else mask.astype(np.uint8)*255
                assert cv2.imwrite(str(output/'masks'/(pair+'_'+name+'.png')),pixels)
            records.append(dict(pair_id=pair,source=row['image_id'],variant=row['variant'],added_pixels=int(added.sum()),components=components,training_eligible=False))
            boards.setdefault(Path(row['image_id']).stem,[]).append(board(image,old,new,added,pair))
        for source,images in boards.items():cv2.imwrite(str(output/'boards'/(source+'_comparison.png')),np.vstack(images))
        # Match the fixed non-skin-veto correction baseline on original224 probes.
        for ident,path in raw_paths.items():
            clean=cv2.imread(str(path))
            for variant in ['clean','global_color_shift']:
                image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                stem=ident.replace('/','_')+'_'+variant;categories=segmenter.categories_bgr(image);skin=np.isin(categories,[2,3])
                measurement=(cv2.imread(str(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')),0)>0)&skin
                old=(cv2.imread(str(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')),0)>0)&skin
                new,added,_=recover(image,measurement,old,exclusions(image),categories)
                for point in [p for p in points if p['image_id']==ident]:
                    assert image.shape[:2]==(point['height'],point['width'])
                    x,y=point['x'],point['y']
                    observations.append(dict(point_id=point['point_id'],variant=variant,label=label_map[point['point_id']],before=bool(old[y,x]),after=bool(new[y,x]),added=bool(added[y,x])))
        assert len(observations)==48
        counts={v:{label:dict(total=sum(p['variant']==v and p['label']==label for p in observations),
            before=sum(p['variant']==v and p['label']==label and p['before'] for p in observations),after=sum(p['variant']==v and p['label']==label and p['after'] for p in observations)) for label in sorted(set(label_map.values()))} for v in ['clean','global_color_shift']}
        assert hashes=={p:digest(p) for p in hashes}
        summary=dict(status='complete_no_adoption_no_fitting',policy=policy,pairs=records,point_observations=observations,point_counts=counts,
            changed_masks=sum(r['added_pixels']>0 for r in records),added_pixels_total=sum(r['added_pixels'] for r in records),
            rejection_reasons=dict(Counter(reason for r in records for c in r['components'] for reason in c['reasons'])),input_sha256=hashes)
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'review-index.md').write_text('# Correction-only gap recovery\n\nOriginal / candidate / additions in red. Green selection is not skin ground truth.\n\n'+'\n'.join(f'- [{source}](boards/{source}_comparison.png)' for source in boards),encoding='utf-8')
        print(json.dumps(dict(changed=summary['changed_masks'],pixels=summary['added_pixels_total'],reasons=summary['rejection_reasons'],points=counts),indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
