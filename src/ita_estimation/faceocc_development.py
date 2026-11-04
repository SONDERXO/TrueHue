"""Isolated preferred experimental measurement service; never admits training.

Prediction is injected so the main project need not import the PyTorch runtime.
Technical success never certifies actual-skin validity or supplies mapped MST.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import numpy as np
import cv2
from src.ita_estimation import nostril_measurement
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.utilities.config import get_config

VERSION='faceocc_preferred_experimental_measurement_service_v1'
WEIGHT_SHA256='5d6d27a9cb221692425840a80eb4efc07e6245670b233e2eb618e83fd9b7caf6'


@dataclass
class DevelopmentMeasurement:
    report: dict
    image: object=None
    baseline_mask: object=None
    mask: object=None
    aligned: object=None
    matrix: object=None
    logits: object=None


def contract(root):
    root=Path(root);parent,parent_identity=nostril_measurement.contract(root)
    folder=root/get_config().MODELS_ROOT/'faceocc_candidate_v1'
    paths=[folder/'model.safetensors',folder/'config.json',folder/'similarity_Lm3D_all.mat',Path(__file__)]
    paths += [root/p for p in ['src/skin_masking/faceocc_coordinates.py','src/skin_masking/faceocc_mediapipe_bridge.py',
        'src/ita_estimation/faceocc_veto_candidate.py','src/model_training/facial_endpoint_features.py']]
    hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if hashes[(folder/'model.safetensors').relative_to(root).as_posix()]!=WEIGHT_SHA256:
        raise ValueError('Pinned FaceOcc weights changed')
    spec=dict(version=VERSION,parent_contract=parent,parent_sha256=parent_identity,
        dependency_sha256=hashes,input='aligned_BGR_to_RGB_ImageNet_mean_std_CPU_float32',
        output='finite256x256logits_strict_gt0_inverse_validity_veto',minimum_pixels=1000,
        actual_skin_validity='unverified',mst_available=False,training_admission=False)
    identity=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return spec,identity


def evaluate_parent(parent,points,template,predictor):
    """Run one bridge/veto from a parent result, without mutating its evidence."""
    result=DevelopmentMeasurement(dict(version=VERSION,status='failed',stage='parent_measurement',
        features=None,mst=None,actual_skin_validity='unverified',calibration_admitted=False,
        training_admitted=False,parent_status=parent.report.get('status')),image=parent.image)
    if parent.report.get('status')!='success':
        result.report['reason']=parent.report.get('reason','Parent measurement unavailable')
        return result
    result.baseline_mask=parent.mask.copy()
    try:
        result.report['stage']='alignment'
        result.aligned,result.matrix,bridge=align_input(parent.image,points,template)
        result.report['bridge']=bridge
        result.report['stage']='faceocc_prediction'
        logits=np.asarray(predictor(result.aligned.copy()))
        if logits.shape!=(256,256) or not np.isfinite(logits).all():
            raise ValueError('Finite256x256 FaceOcc logits required')
        result.logits=logits.copy()
        result.report['stage']='candidate_measurement'
        result.mask,_,candidate=combine_saved(parent.image,result.baseline_mask,result.logits,result.matrix)
        result.report.update(candidate)
        result.report.update(version=VERSION,veto_version=candidate['version'],actual_skin_validity='unverified',calibration_admitted=False,
            training_admitted=False,mst=None)
    except (ValueError,TypeError,RuntimeError,cv2.error) as error:
        result.report.update(status='failed',features=None,reason=str(error))
    return result


def measure(image,detector,landmarks,parser,predictor,template):
    cached={}
    def capture(im,box):
        points=landmarks(im,box);cached['points']=points;return points
    parent=nostril_measurement.measure(image,detector,capture,parser)
    return evaluate_parent(parent,cached.get('points'),template,predictor)
