"""Source-derived FaceOcc alignment math; no automatic landmark substitution.

Callers must supply matching five-point landmarks and the pinned source template.
This is not an adoption of a TrueHue landmark-to-FaceOcc correspondence.
"""
# Derived from FaceOcc face_align/align.py (MIT), pinned at 8d86c9a2c1a0094dbc1a1e5467413b49f8936b32.
# Copyright (c) 2024 Xiangnan Yin (ECL Liris), Di Huang (Beihang University), Liming Chen (ECL Liris).
# Copyright (c) 2026 Mert Akın. See docs/third-party/faceocc-LICENSE.txt.
import cv2
import numpy as np

VERSION = 'faceocc_source_coordinate_contract_v1'


def alignment_matrix(points_xy, template_xyz, image_height):
    points = np.asarray(points_xy, dtype=np.float64)
    template = np.asarray(template_xyz, dtype=np.float64)
    if points.shape != (5, 2) or template.shape != (5, 3) or not np.isfinite(points).all() or not np.isfinite(template).all():
        raise ValueError('Finite matching source-ordered five-point landmarks/template required')
    if isinstance(image_height, bool) or not isinstance(image_height, (int, np.integer)) or image_height < 1:
        raise ValueError('Positive integer image height required')
    # Match source Preprocess/POS exactly, including its h versus h-1 distinction.
    flipped = np.stack((points[:, 0], image_height - 1 - points[:, 1]), axis=1)
    homogeneous = np.column_stack((template, np.ones(5)))
    design = np.zeros((10, 8), dtype=np.float64)
    design[0::2, :4] = homogeneous
    design[1::2, 4:] = homogeneous
    coefficients, _, rank, _ = np.linalg.lstsq(design, flipped.reshape(-1, 1), rcond=None)
    if rank < 8:
        raise ValueError('Degenerate source template geometry')
    scale_estimate = (np.linalg.norm(coefficients[:3]) + np.linalg.norm(coefficients[4:7])) / 2
    if not np.isfinite(scale_estimate) or scale_estimate <= 1e-8:
        raise ValueError('Degenerate face scale')
    scale = 116.0 / scale_estimate
    tx, ty = float(coefficients[3, 0]), float(coefficients[7, 0])
    return np.array([[scale, 0, 128-tx*scale], [0, scale, 128-(image_height-ty)*scale]], dtype=np.float64)


def map_visible_mask(aligned_mask, source_shape, forward_matrix):
    """Inverse-warp binary model mask, vetoing predictions without source pixels."""
    if not isinstance(aligned_mask, np.ndarray) or aligned_mask.dtype != np.uint8 or aligned_mask.shape != (256, 256) or not set(np.unique(aligned_mask)) <= {0, 255}:
        raise ValueError('Binary uint8 aligned256 mask required')
    if len(source_shape) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, np.integer)) or v < 1 for v in source_shape):
        raise ValueError('Positive source height/width required')
    matrix = np.asarray(forward_matrix, dtype=np.float64)
    if matrix.shape != (2, 3) or not np.isfinite(matrix).all() or abs(np.linalg.det(matrix[:, :2])) < 1e-12:
        raise ValueError('Finite invertible affine mapping required')
    height, width = source_shape
    valid = cv2.warpAffine(np.full((height, width),255,np.uint8),matrix,(256,256),
        flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    selected = cv2.bitwise_and(aligned_mask,valid)
    return cv2.warpAffine(selected,cv2.invertAffineTransform(matrix),(width,height),
        flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
