"""Separate full-frame semantic measurement; never loads the old MST lookup."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.square_measurement import SquareMeasurement
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage, VERSION
from src.model_training.facial_endpoint_features import facial_endpoint_features

PARSER_SHA256 = '0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f'


def contract(root):
    root = Path(root)
    config = get_config()
    if config.IMAGE_SIZE != 256:
        raise ValueError('Configured square256 required')
    parser = root / config.MODELS_ROOT / 'face_parser_experimental_v1/resnet18.onnx'
    files = [Path(__file__), parser, root / config.FACE_MODEL_PATH,
             root / config.FACE_LANDMARKER_MODEL_PATH]
    files += [root / p for p in (
        'scripts/11_prepare_training_manifests.py', 'src/face_detection/detect_faces.py',
        'src/skin_masking/semantic_face_coverage.py', 'src/skin_masking/anatomical_face_coverage.py',
        'src/skin_masking/face_parsing_experiment.py', 'src/skin_masking/face_outline_experiment.py',
        'src/skin_masking/landmark_exclusion.py', 'src/skin_masking/mouth_exclusion.py',
        'src/ita_estimation/compute_ita.py', 'src/model_training/facial_endpoint_features.py')]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if digest(parser) != PARSER_SHA256:
        raise ValueError('Existing pinned parser required')
    spec = dict(version='semantic_fullframe_square256_measurement_v1', size=256,
                decode='opencv_IMREAD_COLOR_default_orientation', resize='whole_frame_INTER_LINEAR',
                detector_confidence=.85, required_faces=1, landmarks_required=True,
                mask_version=VERSION, measurement_support='full_frame_binary_not_alpha',
                minimum_pixels=1000, statistics='existing_OpenCV_encoded_Lab_four_decimal_ITA',
                color='assumed_sRGB_no_ICC_or_camera_calibration',
                opencv_version=cv2.__version__, numpy_version=np.__version__,
                dependency_sha256={p.relative_to(root).as_posix(): digest(p) for p in files})
    return spec, hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def measure(image, detector, landmarks, parser):
    """Injected detector/landmarks/parser; all mask pixels share the square frame."""
    report = dict(status='failed', stage='input', features=None, mask_version=VERSION,
                  mask_review='not_human_reviewed', training_admitted=False, mst=None)
    square = mask = None
    try:
        if not isinstance(image, np.ndarray) or image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or not image.size:
            raise ValueError('Nonempty uint8 BGR image required')
        report['source_decoded_shape'] = list(image.shape)
        square = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)
        report['stage'] = 'face_detection'
        boxes = detector(square)
        report['face_count'] = len(boxes)
        if len(boxes) != 1:
            raise ValueError('Exactly one face required')
        box = boxes[0]
        if len(box) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, np.integer)) for v in box):
            raise ValueError('Integer face box required')
        x, y, w, h = map(int, box)
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > 256 or y+h > 256:
            raise ValueError('Face box outside square frame')
        report.update(stage='landmarks', face_box=[x, y, w, h])
        points = landmarks(square, box)
        if points is None:
            raise ValueError('Required landmarks unavailable')
        report['stage'] = 'semantic_mask'
        result = build_semantic_face_coverage(square, points, parser.categories_bgr(square))
        mask = result.mask
        report.update(stage='measurement', mask_report=result.report)
        stats = compute_masked_lab_statistics(square, mask, 1000)
        report['statistics'] = stats
        report['skin_pixels'] = stats['skin_pixels']
        if not stats['valid']:
            raise ValueError(stats['reason'])
        features = {f'input_{k}': stats[k] for k in ('mean_l_star', 'mean_a_star', 'mean_b_star', 'ita_degrees')}
        endpoints = facial_endpoint_features(square, mask > 0)
        if not endpoints['valid']:
            raise ValueError(endpoints['reason'])
        features.update(endpoints['features'])
        report.update(status='success', features=features)
    except (ValueError, TypeError, RuntimeError, cv2.error) as error:
        report['reason'] = str(error)
    return SquareMeasurement(report, square, mask)
