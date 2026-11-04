"""Attribute original-mask losses to the actual recomputed rule-mask stages."""
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
h=importlib.import_module('256_compare_clean_control_tree_depth')


def main():
    parent=ROOT/'outputs/endpoint_full_path_jpeg_v1';inputs=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
    out=ROOT/'outputs/jpeg_mask_stage_trace_v1'
    if out.exists():raise FileExistsError(out)
    verification=h.read(parent/'verification.json');assert verification['status']=='pass'
    for path,sha in verification['evidence_sha256'].items():assert h.digest(parent/path)==sha
    rows={r['pair_id']:r for r in h.read(parent/'plan.json')['rows']}
    encoded={(r['pair_id'],r['encoding']):r for r in h.read(inputs/'predictions.json')}
    records=[];kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    for r in h.read(parent/'attempts.json'):
        assert r['status']=='success'
        pair=r['pair_id'];encoding=r['encoding'];row=rows[pair]
        image=cv2.imread(str(inputs/encoded[(pair,encoding)]['encoded_input_path']))
        original=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        actual=cv2.imread(str(parent/'images'/(pair+'_'+encoding+'_mask.png')),0)>0
        x,y,w,height=r['measurement']['face_box'];crop=image[y:y+height,x:x+w]
        hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV);ycrcb=cv2.cvtColor(crop,cv2.COLOR_BGR2YCrCb)
        hs=cv2.inRange(hsv,np.array([0,48,0],np.uint8),np.array([20,255,255],np.uint8))>0
        yc=cv2.inRange(ycrcb,np.array([0,133,77],np.uint8),np.array([255,173,127],np.uint8))>0
        raw=hs&yc;cleaned=cv2.morphologyEx(raw.astype(np.uint8)*255,cv2.MORPH_OPEN,kernel)
        for _ in range(2):cleaned=cv2.morphologyEx(cleaned,cv2.MORPH_CLOSE,kernel)
        np.testing.assert_array_equal(cleaned,create_candidate_mask_bgr(crop))
        largest=keep_largest_connected_component(cleaned)>0
        points=np.load(parent/'geometry'/(pair+'_'+encoding+'_landmarks.npy'))
        excluded=build_feature_exclusion_mask(crop,points,dilation=0)>0
        _,mouth=exclude_complete_mouth(np.full(crop.shape[:2],255,np.uint8),points);excluded|=mouth>0
        expected=np.zeros_like(original);expected[y:y+height,x:x+w]=largest&~excluded
        np.testing.assert_array_equal(expected,actual)
        lost=original&~actual;inside=np.zeros_like(original);inside[y:y+height,x:x+w]=True
        local=lost[y:y+height,x:x+w]
        attributions={'outside_new_face_box':int((lost&~inside).sum()),
            'anatomical_exclusion':int((local&largest&excluded).sum()),
            'largest_component_discard':int((local&(cleaned>0)&~largest).sum()),
            'morphology_discard':int((local&raw&(cleaned==0)).sum()),
            'hsv_only_rejection':int((local&~raw&(cleaned==0)&~hs&yc).sum()),
            'ycrcb_only_rejection':int((local&~raw&(cleaned==0)&hs&~yc).sum()),
            'both_color_rules_reject':int((local&~raw&(cleaned==0)&~hs&~yc).sum())}
        assert sum(attributions.values())==int(lost.sum())
        records.append(dict(pair_id=pair,encoding=encoding,lost_original_pixels=int(lost.sum()),added_pixels=int((actual&~original).sum()),attribution=attributions))
    assert len(records)==141
    aggregate=[]
    for encoding in ('lossless','jpeg95','jpeg85'):
        selected=[r for r in records if r['encoding']==encoding]
        aggregate.append(dict(encoding=encoding,frames=len(selected),lost_pixels=sum(r['lost_original_pixels'] for r in selected),
            attribution={k:sum(r['attribution'][k] for r in selected) for k in records[0]['attribution']}))
    out.mkdir();h.write(out/'summary.json',dict(status='stage_attribution_not_skin_accuracy',aggregate=aggregate,records=records,
        caveat='Sequential attribution of original-mask disagreements, not independent causal intervention or human truth.',active_demo_changed=False))
    h.write(out/'verification.json',dict(status='pass',reconstructed_masks=141,disjoint_loss_attributions=141,
        parent_verification_sha256=h.digest(parent/'verification.json'),producer_sha256=h.digest(Path(__file__)),summary_sha256=h.digest(out/'summary.json')))
    print(aggregate)


if __name__=='__main__':main()
