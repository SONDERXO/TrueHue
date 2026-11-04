"""New, separately bound measurement revision; no old MST lookup reuse."""
import hashlib
import json
from pathlib import Path
import numpy as np
from src.ita_estimation import semantic_measurement
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.skin_masking.full_face_support import nostril_guard,VERSION


def contract(root):
    root=Path(root);parent,identity=semantic_measurement.contract(root)
    files=[Path(__file__),root/'src/skin_masking/full_face_support.py']
    spec=dict(version=VERSION,parent_measurement_contract_sha256=identity,
        parent_contract=parent,nostril_policy='two_supersampled_nasal_base_hulls_plus_one_pixel_guard',
        unchanged_exclusions='eyes_brows_hair_lips_mouth_neck_non_skin_classes',
        dependency_sha256={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    return spec,hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def measure(image,detector,landmarks,parser):
    saved={}
    def capture(im,box):
        points=landmarks(im,box);saved['points']=points;return points
    result=semantic_measurement.measure(image,detector,capture,parser)
    report=result.report;report.update(mask_version=VERSION,mst=None,old_lookup_compatible=False)
    if report['status']!='success':return result
    report.update(status='failed',features=None,stage='nostril_measurement')
    try:
        guard=nostril_guard(result.mask.shape,saved['points'])
        report['nostril_guard_removed_pixels']=int(((result.mask>0)&guard).sum())
        result.mask=result.mask.copy();result.mask[guard]=0
        stats=compute_masked_lab_statistics(result.image,result.mask,1000)
        report.update(statistics=stats,skin_pixels=stats['skin_pixels'])
        report['parent_mask_report']=report.get('mask_report')
        report['mask_report']=dict(version=VERSION,selected_pixels=stats['skin_pixels'],
            nostril_guard_removed_pixels=report['nostril_guard_removed_pixels'])
        if not stats['valid']:raise ValueError(stats['reason'])
        features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(result.image,result.mask>0)['features'])
        report.update(status='success',features=features)
    except ValueError as error:report['reason']=str(error)
    return result
