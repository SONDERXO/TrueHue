"""Locate enclosed gaps separately from intentional feature exclusions; no fill."""
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


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'outputs/correction_gap_audit_v1'
    if output.exists():raise FileExistsError(output)
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    batches=[ROOT/'outputs/non_skin_regenerated_remaining28_v1',ROOT/'outputs/non_skin_regenerated_two_v1']
    approval_path=ROOT/'data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json'
    approved=set(json.loads(approval_path.read_text())['approved_pairs'])
    selected=[];tracked=[Path(__file__),approval_path,ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    for parent in batches:
        tracked.append(parent/'summary.json')
        for record in json.loads((parent/'summary.json').read_text())['attempts']:
            pair=Path(record['image_id']).stem+'_'+record['variant']
            if parent==batches[1] and pair not in approved:continue
            selected.append((parent,record,pair))
            tracked += [parent/'images'/(pair+s) for s in ['_input.png','_baseline_estimate.png','_support.png']]
    assert len(selected)==32
    hashes={str(p):digest(p) for p in tracked};output.mkdir();(output/'boards').mkdir()
    records=[];boards={}
    for parent,row,pair in selected:
        image=cv2.imread(str(parent/'images'/(pair+'_input.png')))
        mask=cv2.imread(str(parent/'images'/(pair+'_support.png')),0)>0
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:raise ValueError('Unavailable geometry: '+pair)
        x,y,w,h=boxes[0]
        geometry=prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not geometry.landmarks_available:raise ValueError('Unavailable landmarks: '+pair)
        excluded=np.zeros(mask.shape,bool);excluded[y:y+h,x:x+w]=geometry.exclusion_mask>0
        count,labels,stats,_=cv2.connectedComponentsWithStats((~mask).astype(np.uint8),connectivity=8)
        border_labels=set(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]].tolist())
        gap=np.zeros_like(mask);components=[]
        for label in range(1,count):
            if label in border_labels:continue
            region=labels==label;protected=bool((region&excluded).any())
            sx,sy,sw,sh,area=map(int,stats[label])
            components.append(dict(bounds=[sx,sy,sx+sw,sy+sh],pixels=area,
                overlaps_intentional_exclusion=protected,pixels_outside_exclusion=int((region&~excluded).sum())))
            if not protected:gap|=region
        record=dict(pair_id=pair,source=row['image_id'],variant=row['variant'],enclosed_components=components,
            unprotected_enclosed_components=sum(not r['overlaps_intentional_exclusion'] for r in components),
            unprotected_gap_pixels=int(gap.sum()),protected_component_count=sum(r['overlaps_intentional_exclusion'] for r in components),
            limitation='Unprotected gap is not verified skin; touching protected features remains protected. Boundary-connected missing skin is not counted.')
        records.append(record)
        cv2.imwrite(str(output/'boards'/(pair+'_unprotected_gaps.png')),gap.astype(np.uint8)*255)
        overlay=image.copy();overlay[mask]=np.rint(.6*overlay[mask]+.4*np.array([0,200,0])).astype(np.uint8)
        overlay[gap]=[0,0,255];overlay[excluded]=np.rint(.5*overlay[excluded]+.5*np.array([0,210,255])).astype(np.uint8)
        panels=[]
        for title,im in [('Input',image),('Green support / red gaps / yellow exclusions',overlay)]:
            im=cv2.copyMakeBorder(im,32,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(im,pair,(3,13),cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1);cv2.putText(im,title,(3,27),cv2.FONT_HERSHEY_SIMPLEX,.29,(255,255,255),1);panels.append(im)
        boards.setdefault(Path(row['image_id']).stem,[]).append(np.hstack(panels))
    for source,images in boards.items():cv2.imwrite(str(output/'boards'/(source+'_gaps.png')),np.vstack(images))
    assert hashes=={p:digest(Path(p)) for p in hashes}
    report=dict(status='audit_only_no_mask_change',pairs=records,images=32,
        images_with_unprotected_enclosed_gaps=sum(r['unprotected_gap_pixels']>0 for r in records),
        unprotected_gap_pixels_total=sum(r['unprotected_gap_pixels'] for r in records),input_sha256=hashes,
        limitation='Topology and anatomical exclusions are diagnostic only, not automatic filling criteria. Paint/non-skin islands may be intentional; semantic predictions are not sufficient ground truth. Measurement need not cover every correction pixel.')
    (output/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (output/'review-index.md').write_text('# Correction-mask gap inspection\n\nGreen selected support;red enclosed unprotected gaps;yellow intentional anatomical exclusions. Red is not automatically skin.\n\n'+'\n'.join(f'- [{source}](boards/{source}_gaps.png)' for source in boards),encoding='utf-8')
    print(json.dumps(dict(images=32,images_with_gaps=report['images_with_unprotected_enclosed_gaps'],gap_pixels=report['unprotected_gap_pixels_total'],largest=sorted([(r['pair_id'],r['unprotected_gap_pixels']) for r in records],key=lambda r:-r[1])[:8]),indent=2))


if __name__=='__main__':main()
