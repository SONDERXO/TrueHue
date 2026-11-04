"""Versioned YCrCb-only candidate; old measurement and lookup remain separate."""
from pathlib import Path
import hashlib
import json
import cv2
import numpy as np
from src.ita_estimation.square_measurement import measure as original_measure,contract as original_contract
from src.skin_masking.skin_mask import SkinMaskResult,keep_largest_connected_component
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth

VERSION='face_ycrcb_complete_mouth_square256_v1'


def build_mask(crop,points):
    colors=ycrcb_color_candidate(crop)
    if points is None:
        return SkinMaskResult(mask=np.zeros_like(colors),candidate_mask=colors,exclusion_mask=np.zeros_like(colors),
            landmarks_available=False,status='Required frame-local landmarks unavailable; no fallback')
    excluded=build_feature_exclusion_mask(crop,points,dilation=0)
    _,mouth=exclude_complete_mouth(np.full(colors.shape,255,np.uint8),points)
    excluded=cv2.bitwise_or(excluded,mouth)
    mask=cv2.bitwise_and(keep_largest_connected_component(colors),cv2.bitwise_not(excluded))
    return SkinMaskResult(mask=mask,candidate_mask=colors,exclusion_mask=excluded,landmarks_available=True,status=VERSION)


def measure(image,detector,landmark_provider):
    def masker(square,box):
        x,y,w,h=box
        return build_mask(square[y:y+h,x:x+w],landmark_provider(square,box))
    result=original_measure(image,detector,masker)
    result.report['mask_version']=VERSION
    return result


def contract(root):
    root=Path(root);base,base_hash=original_contract(root)
    dependencies=dict(base['dependency_sha256'])
    for relative in ['src/ita_estimation/ycrcb_measurement.py','src/skin_masking/ycrcb_candidate.py']:
        dependencies[relative]=hashlib.sha256((root/relative).read_bytes()).hexdigest()
    payload=dict(base,version=VERSION,mask_version=VERSION,
        parent_measurement_contract_sha256=base_hash,
        color_rule='YCrCb Cr133..173,Cb77..127; ellipse5open/close/close; largest component; existing anatomy/complete mouth',
        landmark_framing='same existing first-success margin provider; no missing-landmark fallback',
        dependency_sha256=dependencies,existing_mst_lookup_applicable=False)
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert identity!=base_hash
    return payload,identity
