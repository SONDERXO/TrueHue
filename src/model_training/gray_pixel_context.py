"""Experimental GP(std)-inspired contextual descriptor, no correction predictor.

Independent equation implementation: Yang/Gao/Li, CVPR2015, equations6-8.
Numerical support/tie conventions: gray-pixel-selector-protocol-2026-11-12.md.
No author source code used; no runtime integration or physical-neutrality claim.
"""
import math

import cv2
import numpy as np


GRAY_CONTEXT_FEATURES = ('gp_context_log_r_over_g', 'gp_context_log_b_over_g')


def _box(a, size):
    return cv2.boxFilter(a, cv2.CV_64F, (size, size), normalize=True,
                         borderType=cv2.BORDER_REFLECT_101)


def local_log_statistics(rgb):
    """Stable centered population variance with complete positive support."""
    a = rgb.astype(np.float64)/255
    positive = np.all(a > 0, axis=2)
    # Placeholders never enter accepted full-support windows.
    logs = np.zeros_like(a)
    np.log(a, out=logs, where=a > 0)
    padded = np.pad(logs, ((1, 1), (1, 1), (0, 0)), mode='reflect')
    height, width = a.shape[:2]
    windows = [padded[i:i+height, j:j+width] for i in range(3) for j in range(3)]
    # Subtract the first value before averaging: truly constant patches stay exact.
    origin = windows[0]
    offsets = [w-origin for w in windows]
    mean_offset = sum(offsets)/9
    sd = np.sqrt(sum((v-mean_offset)**2 for v in offsets)/9)
    channel_offsets = sd-sd[:, :, :1]
    mean_channel_offset = channel_offsets.mean(axis=2)
    m = sd[:, :, 0]+mean_channel_offset
    pos_pad = np.pad(positive, 1, mode='reflect')
    valid = np.logical_and.reduce([pos_pad[i:i+height, j:j+width]
                                   for i in range(3) for j in range(3)]) & (m > 0)
    spread = ((channel_offsets-mean_channel_offset[:, :, None])**2).mean(axis=2)
    p = np.zeros_like(m)
    np.divide(spread, m, out=p, where=valid)
    np.sqrt(p, out=p)
    return p, valid, a.mean(axis=2)


def gray_pixel_context(rgb):
    if (not isinstance(rgb, np.ndarray) or rgb.dtype != np.uint8 or
            rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 16):
        raise ValueError('RGB8 image at least16x16 required')
    p, valid, lightness = local_log_statistics(rgb)
    raw = np.zeros(p.shape, dtype=np.float64)
    np.divide(p, lightness, out=raw, where=valid)
    # Full support, exact boolean logic rather than a tolerance on box-filter counts.
    pad = np.pad(valid, 3, mode='reflect')
    h, w = valid.shape
    final_valid = np.logical_and.reduce([pad[i:i+h, j:j+w] for i in range(7) for j in range(7)])
    score = _box(raw, 7)
    candidates = np.flatnonzero(final_valid.ravel())
    metadata = dict(valid_candidates=int(candidates.size),
        requested_count=max(1, math.ceil(h*w/10000)),
        zero_channel_pixels=int(np.any(rgb == 0, axis=2).sum()),
        saturated_channel_pixels=int(np.any(rgb == 255, axis=2).sum()))
    if not candidates.size:
        return dict(available=False, reason='no_complete_positive_nonflat_support',
                    features=None, selected_flat_indices=[], selected_count=0, **metadata)
    order = np.lexsort((candidates, score.ravel()[candidates]))
    count = min(metadata['requested_count'], int(candidates.size))
    selected = candidates[order[:count]]
    cutoff = score.ravel()[selected[-1]]
    mean = rgb.reshape(-1, 3)[selected].astype(float).mean(axis=0)
    values = [math.log(mean[0]/mean[1]), math.log(mean[2]/mean[1])]
    return dict(available=True, reason=None, features=dict(zip(GRAY_CONTEXT_FEATURES, values)),
        selected_flat_indices=selected.tolist(), selected_count=count,
        cutoff_score=float(cutoff), cutoff_equal_candidates=int(np.count_nonzero(
            score.ravel()[candidates] == cutoff)), selected_mean_rgb_codes=mean.tolist(), **metadata)
