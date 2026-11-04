"""Isolated diagnostic candidate; does not alter runtime measurement."""
import hashlib
import json
from pathlib import Path
import numpy as np
from src.ita_estimation import nostril_measurement
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.skin_masking.anatomical_face_coverage import build_face_coverage

VERSION = 'face_contained_nostril_measurement_candidate_v1'


def contract(root):
    root = Path(root)
    parent, identity = nostril_measurement.contract(root)
    spec = dict(version=VERSION, parent_contract=parent, parent_sha256=identity,
        rule='current_nostril_mask_AND_original_face_outline', minimum_pixels=1000,
        dependency_sha256={Path(__file__).relative_to(root).as_posix(): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    return spec, hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def measure_saved(image, baseline_mask, landmarks):
    if not isinstance(baseline_mask, np.ndarray) or baseline_mask.dtype != np.uint8 or baseline_mask.ndim != 2 or not set(np.unique(baseline_mask)) <= {0, 255}:
        raise ValueError('Binary uint8 parent measurement mask required')
    report = dict(status='failed', features=None, mst=None, admitted=False, version=VERSION)
    mask = None
    try:
        geometry = build_face_coverage(image, landmarks)
        if baseline_mask.shape != geometry.face_outline.shape:
            raise ValueError('Matching full-image parent mask required')
        mask = np.where((baseline_mask > 0) & (geometry.face_outline > 0), 255, 0).astype(np.uint8)
        old = int(np.count_nonzero(baseline_mask)); count = int(np.count_nonzero(mask))
        report.update(parent_pixels=old, candidate_pixels=count, removed_pixels=old-count,
                      retained_fraction=count/old if old else None)
        stats = compute_masked_lab_statistics(image, mask, 1000)
        report['statistics'] = stats
        if not stats['valid']:
            raise ValueError(stats['reason'])
        features = {f'input_{k}': stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(image, mask > 0)['features'])
        report.update(status='success', features=features)
    except (ValueError, TypeError) as error:
        report['reason'] = str(error)
    return mask, report
