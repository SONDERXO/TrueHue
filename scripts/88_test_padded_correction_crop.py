"""Fixed padded-crop correction proposal on32 saved inputs; no regeneration/fit."""
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
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def propose(image,measurement,old,categories,prepare,ycb,model):
    boxes=prepare._detect_face_boxes(image,ROOT/get_config().FACE_MODEL_PATH,.85)
    if len(boxes)!=1:raise ValueError('Expected single face')
    x,y,w,h=map(int,boxes[0]);pad=max(2,int(np.ceil(.10*max(w,h))))
    x0,y0=max(0,x-pad),max(0,y-pad);x1,y1=min(image.shape[1],x+w+pad),min(image.shape[0],y+h+pad)
    crop=image[y0:y1,x0:x1]
    points,_,_=prepare.detect_landmarks_with_margin(image,boxes[0],model)
    if points is None:raise ValueError('Unavailable landmarks; no fallback')
    points=points+np.asarray([x-x0,y-y0])
    excluded=build_feature_exclusion_mask(crop,points,dilation=0)>0
    _,mouth=exclude_complete_mouth(np.full(crop.shape[:2],255,np.uint8),points)
    excluded|=mouth>0
    _,oval=restrict_to_face_outline(np.full(crop.shape[:2],255,np.uint8),points)
    raw=ycb.ycrcb_mask(crop,excluded)
    semantic=np.isin(categories[y0:y1,x0:x1],[2,3])
    proposal=raw&semantic
    ratio=float((proposal&(oval>0)).sum()/proposal.sum()) if proposal.any() else 0.
    if ratio<.75:raise ValueError(f'Face-oval geometry retention{ratio:.4f}<.75')
    seeds=measurement[y0:y1,x0:x1]&~excluded
    if seeds.sum()<1000:raise ValueError('Insufficient existing measurement seeds')
    lab=cv2.cvtColor(crop.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
    samples=lab[seeds].astype(float);center=np.median(samples,axis=0)
    scale=np.maximum(1.4826*np.median(np.abs(samples-center),axis=0),[12.,6.,6.])
    material=np.sqrt(np.sum(((lab-center)/scale)**2,axis=2))<=3
    distance=cv2.distanceTransform((~excluded).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE) if excluded.any() else np.full(excluded.shape,np.inf)
    allowed=proposal&(oval>0)&material&(distance>2)&~excluded
    additions=np.zeros_like(old);additions[y0:y1,x0:x1]=allowed
    additions&=~old
    new=old|additions
    full_excluded=np.zeros_like(old);full_excluded[y0:y1,x0:x1]=excluded
    assert not (old&~new).any() and not (additions&full_excluded).any()
    return new,additions,dict(detector_box=[x,y,w,h],processing_box=[x0,y0,x1-x0,y1-y0],pad=pad,oval_retention=ratio),full_excluded


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests');ycb=importlib.import_module('56_compare_ycrcb_estimation')
    output=ROOT/'outputs/padded_correction_crop_v1'
    if output.exists():raise FileExistsError(output)
    approval=ROOT/'data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json'
    approved=set(json.loads(approval.read_text())['approved_pairs']);selected=[]
    tracked=[Path(__file__),approval,ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',ROOT/'data/manifests/development_exposure_additions.jsonl']
    for folder in ['non_skin_regenerated_remaining28_v1','non_skin_regenerated_two_v1']:
        parent=ROOT/'outputs'/folder;tracked.append(parent/'summary.json')
        for row in json.loads((parent/'summary.json').read_text())['attempts']:
            pair=Path(row['image_id']).stem+'_'+row['variant']
            if folder=='non_skin_regenerated_two_v1' and pair not in approved:continue
            selected.append((parent,row,pair))
            tracked += [parent/'images'/(pair+s) for s in ['_input.png','_baseline_estimate.png','_support.png']]
            tracked.append(parent/'images'/(Path(row['image_id']).stem+'_generation.png'))
    manifest=ROOT/'data/manifests/material_review_v1/review_manifest.json';labels_path=manifest.with_name('material_review_labels.json')
    points=json.loads(manifest.read_text())['points'];labels=json.loads(labels_path.read_text());assert not labels['draft'] and labels['manifest_sha256']==digest(manifest)
    label_map={r['point_id']:r['label'] for r in labels['labels']};tracked += [manifest,labels_path]
    raw_paths={ident:ROOT/config.DATA_RAW/'FairFace'/ident.split('__',1)[1] for ident in {p['image_id'] for p in points}}
    sentinel_path=ROOT/config.DATA_RAW/'FairFace/train/83184.jpg';tracked.append(sentinel_path)
    for ident,path in raw_paths.items():
        tracked.append(path)
        for variant in ['clean','global_color_shift']:
            stem=ident.replace('/','_')+'_'+variant
            tracked += [ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png'),ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')]
    hashes={str(p):digest(p) for p in tracked};output.mkdir();(output/'masks').mkdir();(output/'boards').mkdir()
    policy=dict(status='Fixed before run; diagnostic masks only',pad='ceil10% of larger detector dimension,min2pixels,clip to image',
        landmarks='Reuse selected-face landmarks remapped into padded processing crop; explicit geometry failure/no fallback',
        additions='Padded YCrCb proposal AND predicted face/body skin AND faceoval AND existing robust Lab material<=3 AND >2pixels from eye/brow/complete-mouth exclusions. Geometry oval retention must be>=.75.',
        invariants='Union additions with original correction support; existing support preserved. No measurement/generation changes, no new inputs or model fitting.',
        limitations='Semantic/material gates do not guarantee paint/non-skin rejection. Full oval may restrict legitimate face edges; no neck localization. Current synthetic generation did not distort all new correction pixels.')
    (output/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    records=[];boards={};observations=[];sentinels=[]

    def render(image,old,new,added,title):
        panels=[]
        for name,mask in [('Original',old),('Padded candidate',new),('Additions red',added)]:
            shown=image.copy()
            if mask is not None:shown[mask]=np.rint(.5*shown[mask]+.5*np.asarray([0,0,255] if name=='Additions red' else [0,220,0])).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,32,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,title,(3,13),cv2.FONT_HERSHEY_SIMPLEX,.31,(255,255,255),1);cv2.putText(shown,name,(3,27),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1);panels.append(shown)
        return np.hstack(panels)

    try:
        for parent,row,pair in selected:
            image=cv2.imread(str(parent/'images'/(pair+'_input.png')))
            measurement=cv2.imread(str(parent/'images'/(pair+'_baseline_estimate.png')),0)>0
            old=cv2.imread(str(parent/'images'/(pair+'_support.png')),0)>0
            try:
                new,added,geometry,excluded=propose(image,measurement,old,segmenter.categories_bgr(image),prepare,ycb,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                generation=cv2.imread(str(parent/'images'/(Path(row['image_id']).stem+'_generation.png')),0)>0
                record=dict(pair_id=pair,status='candidate_available',added_pixels=int(added.sum()),additions_outside_old_generation=int((added&~generation).sum()),geometry=geometry)
                for name,mask in [('candidate',new),('added',added),('excluded',excluded)]:cv2.imwrite(str(output/'masks'/(pair+'_'+name+'.png')),mask.astype(np.uint8)*255)
            except ValueError as error:
                record=dict(pair_id=pair,status='candidate_unavailable',reason=str(error));new=old.copy();added=np.zeros_like(old)
            records.append(record);boards.setdefault(Path(row['image_id']).stem,[]).append(render(image,old,new,added,pair+' '+record['status']))
        for ident,images in boards.items():cv2.imwrite(str(output/'boards'/(ident+'_comparison.png')),np.vstack(images))
        for ident,path in raw_paths.items():
            clean=cv2.imread(str(path))
            for variant in ['clean','global_color_shift']:
                image=clean if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                stem=ident.replace('/','_')+'_'+variant;cats=segmenter.categories_bgr(image);skin=np.isin(cats,[2,3])
                measure=(cv2.imread(str(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')),0)>0)&skin
                old=(cv2.imread(str(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')),0)>0)&skin
                try:new,added,_,_=propose(image,measure,old,cats,prepare,ycb,ROOT/config.FACE_LANDMARKER_MODEL_PATH);status='available'
                except ValueError: new=None;status='unavailable'
                for point in [p for p in points if p['image_id']==ident]:
                    x,y=point['x'],point['y'];assert image.shape[:2]==(point['height'],point['width'])
                    observations.append(dict(point_id=point['point_id'],variant=variant,label=label_map[point['point_id']],status=status,before=bool(old[y,x]),after=bool(new[y,x]) if new is not None else None))
        sentinel=cv2.imread(str(sentinel_path))
        for variant in ['clean','global_color_shift']:
            image=sentinel if variant=='clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(sentinel,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
            if len(boxes)!=1:sentinels.append(dict(variant=variant,status='rejected_single_face'));continue
            x,y,w,h=boxes[0];base=prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
            measure=np.zeros(image.shape[:2],bool);measure[y:y+h,x:x+w]=base.mask>0
            try:
                _,added,geo,_=propose(image,measure,measure,segmenter.categories_bgr(image),prepare,ycb,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                sentinels.append(dict(variant=variant,status='candidate_available_not_geometry_validated',added_pixels=int(added.sum()),geometry=geo))
            except ValueError as error:sentinels.append(dict(variant=variant,status='explicitly_rejected',reason=str(error)))
        assert len(records)==32 and len(observations)==48
        assert hashes=={p:digest(p) for p in hashes}
        counts={v:{label:dict(total=sum(r['variant']==v and r['label']==label for r in observations),available=sum(r['variant']==v and r['label']==label and r['status']=='available' for r in observations),before=sum(r['variant']==v and r['label']==label and r['before'] for r in observations),after=sum(r['variant']==v and r['label']==label and r['after'] is True for r in observations)) for label in sorted(set(label_map.values()))} for v in ['clean','global_color_shift']}
        summary=dict(status='complete_no_adoption_no_regeneration_no_fitting',pairs=records,point_observations=observations,point_counts=counts,sentinels=sentinels,input_sha256=hashes)
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'review-index.md').write_text('# Padded correction crop experiment\n\nOriginal/candidate/additions. Unavailable cases display original only and are not fallbacks eligible for adoption.\n\n'+'\n'.join(f'- [{ident}](boards/{ident}_comparison.png)' for ident in boards),encoding='utf-8')
        print(json.dumps(dict(statuses=dict(Counter(r['status'] for r in records)),cheek=[r for r in records if r['pair_id'].startswith('40048')],points=counts,sentinels=sentinels),indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
