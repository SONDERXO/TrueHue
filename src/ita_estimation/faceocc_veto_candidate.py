"""Isolated removal-only measurement candidate; no active pipeline imports."""
import numpy as np
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features

VERSION='faceocc_visible_face_measurement_veto_v1'


def combine_saved(image,baseline,logits,matrix):
    if not isinstance(baseline,np.ndarray) or baseline.dtype!=np.uint8 or baseline.ndim!=2 or not set(np.unique(baseline))<={0,255}:
        raise ValueError('Binary parent measurement mask required')
    if np.asarray(logits).shape!=(256,256) or not np.isfinite(logits).all():
        raise ValueError('Finite256x256 FaceOcc logits required')
    aligned=(logits>0).astype(np.uint8)*255
    visible=map_visible_mask(aligned,baseline.shape,matrix)
    candidate=np.where((baseline>0)&(visible>0),255,0).astype(np.uint8)
    count=int(np.count_nonzero(candidate));old=int(np.count_nonzero(baseline))
    stats=compute_masked_lab_statistics(image,candidate,1000)
    report=dict(version=VERSION,status='failed',features=None,mst=None,admitted=False,
        parent_pixels=old,candidate_pixels=count,removed_pixels=old-count,
        retained_fraction=count/old if old else None,statistics=stats)
    if stats['valid']:
        features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(image,candidate>0)['features'])
        report.update(status='success',features=features)
    else:report['reason']=stats['reason']
    return candidate,visible,report
