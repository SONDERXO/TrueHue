"""Contour-before-component development candidate; no runtime replacement."""
import hashlib
import json
from pathlib import Path
import numpy as np
from src.ita_estimation.ycrcb_measurement import build_mask as base_build_mask,contract as base_contract
from src.ita_estimation.square_measurement import measure as original_measure
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.face_constrained_component import face_constrained_component

VERSION='face_contour_ycrcb_square256_v1'


def build_mask(crop,points):
    result=base_build_mask(crop,points)
    if not result.landmarks_available:return result
    _,oval=restrict_to_face_outline(np.full(crop.shape[:2],255,np.uint8),points)
    result.mask=face_constrained_component(result.candidate_mask,oval,result.exclusion_mask)
    result.status=VERSION
    return result


def measure(image,detector,landmark_provider):
    def masker(square,box):
        x,y,w,h=box
        return build_mask(square[y:y+h,x:x+w],landmark_provider(square,box))
    result=original_measure(image,detector,masker)
    result.report['mask_version']=VERSION
    return result


def contract(root):
    root=Path(root);base,parent_hash=base_contract(root);deps=dict(base['dependency_sha256'])
    for p in ['src/ita_estimation/contour_ycrcb_measurement.py','src/skin_masking/face_outline_experiment.py','src/skin_masking/face_constrained_component.py']:
        deps[p]=hashlib.sha256((root/p).read_bytes()).hexdigest()
    payload=dict(base,version=VERSION,mask_version=VERSION,parent_measurement_contract_sha256=parent_hash,
        containment='fixed landmark oval before largest color component; existing exclusions afterwards',dependency_sha256=deps)
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert identity!=parent_hash
    return payload,identity
