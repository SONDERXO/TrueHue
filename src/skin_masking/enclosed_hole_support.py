"""Development-only enclosed-hole support; geometry does not establish skin."""
import cv2
import numpy as np

VERSION = 'enclosed_hole_support_v1'


def complete_enclosed_holes(mask, exclusions, face_outline):
    """Add whole enclosed background components, retaining anatomical holes.

    All arguments are matching 2D boolean arrays. No reference image, color
    statistics or thresholds enter the rule. Existing selected pixels are
    preserved. Empty support fails rather than fabricating a face mask.
    """
    arrays = [np.asarray(a) for a in (mask, exclusions, face_outline)]
    if any(a.ndim != 2 or a.dtype != bool for a in arrays) or any(a.shape != arrays[0].shape for a in arrays):
        raise ValueError('Matching 2D boolean masks required')
    mask, exclusions, face_outline = arrays
    if not mask.size or not mask.any():
        raise ValueError('Nonempty existing skin support required')
    if np.any(mask & exclusions):
        raise ValueError('Existing mask overlaps anatomical exclusions')
    count, labels = cv2.connectedComponents((~mask).astype(np.uint8), connectivity=8)
    border = set(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1])).tolist())
    forbidden = set(labels[exclusions | ~face_outline].tolist())
    eligible = [i for i in range(1, count) if i not in border and i not in forbidden]
    additions = np.isin(labels, eligible)
    return mask | additions
