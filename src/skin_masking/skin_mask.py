"""
Facial skin-region masking for an OpenCV BGR face crop.

Pipeline sequence implemented here
----------------------------------

1. Input is a BGR *face crop* that was already produced by the face-detection
   stage (this module does **not** do face detection).
2. The crop is converted to two colour spaces: HSV and YCrCb.
3. Each colour space is thresholded to a raw skin mask with ``cv2.inRange``.
4. The two raw masks are combined with a logical AND (``cv2.bitwise_and``), so
   a pixel counts as skin only when both colour spaces agree.
5. Morphological cleaning is applied: one elliptical open (removes small
   isolated specks) followed by two elliptical closes (fills small gaps and
   holes inside the face region).
6. ``keep_largest_connected_component`` keeps only the biggest connected skin
   blob, which discards remaining isolated noise far from the face.

The output is a one-channel ``uint8`` mask using exactly the values
``0`` (= not skin) and ``255`` (= skin). ITA estimation is intentionally *not*
computed here; it is a separate pipeline stage operating on this mask.

Threshold values are baseline ranges from standard skin-detection literature.
They may be tuned after pilot validation (see the TODO note in
``create_skin_mask_bgr``); they are kept as-is until then.
"""

from __future__ import annotations

import cv2
import numpy as np


def keep_largest_connected_component(mask: np.ndarray) -> np.ndarray:
    """Keep only the largest foreground connected component of a binary mask.

    A *connected component* is a group of foreground pixels that are adjacent
    to each other (here with 8-connectivity, i.e. sharing a side or a corner).
    In a skin mask the foreground is usually dominated by one large blob — the
    face — plus small isolated specks produced by noise. Keeping the largest
    component removes those specks while preserving the face region.

    Parameters
    ----------
    mask : np.ndarray
        Single-channel 2D image/mask. Foreground may be any nonzero value
        (for example ``255``); background must be ``0``.

    Returns
    -------
    np.ndarray
        ``uint8`` mask of the same shape as ``mask``, with ``255`` for the
        selected largest component and ``0`` everywhere else. If ``mask`` has
        no foreground, an all-zero ``uint8`` mask is returned.

    Raises
    ------
    ValueError
        If ``mask`` is not a 2D array.
    """
    if mask.ndim != 2:
        raise ValueError(
            f"mask must be a 2D single-channel image, got {mask.ndim} dimension(s)."
        )

    # Anything nonzero counts as foreground.  False -> 0, True -> 255.
    binary = np.where(mask > 0, 255, 0).astype(np.uint8)

    # Label 0 is always the background and must never be selected, so scan
    # labels starting at 1 and remember the label with the largest area.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary, connectivity=8
    )

    largest_label = 0  # 0 means "none found"; it maps to an all-zero result
    largest_area = 0
    for label in range(1, num_labels):  # skip label 0 (background)
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area > largest_area:
            largest_area = area
            largest_label = label

    result = np.zeros_like(mask, dtype=np.uint8)
    if largest_label > 0:
        result[labels == largest_label] = 255
    return result


def create_skin_mask_bgr(face_bgr: np.ndarray) -> np.ndarray:
    """Build a binary skin mask from a BGR face crop.

    Combines HSV and YCrCb skin thresholds with a logical AND, applies
    morphological cleaning, and finally keeps only the largest connected
    component. See the module docstring for the full pipeline sequence.

    Parameters
    ----------
    face_bgr : np.ndarray
        Face crop in OpenCV BGR format, shape ``(H, W, 3)``, dtype ``uint8``.

    Returns
    -------
    np.ndarray
        One-channel ``uint8`` mask of shape ``(H, W)`` with values ``0``
        (non-skin) or ``255`` (selected skin pixels).

    Raises
    ------
    ValueError
        If ``face_bgr`` is ``None``, empty, or not a 3-channel BGR image.
    """
    if face_bgr is None or face_bgr.size == 0:
        raise ValueError("face_bgr must be a non-empty BGR face crop.")

    if face_bgr.ndim != 3 or face_bgr.shape[2] != 3:
        raise ValueError(
            f"face_bgr must be a 3-channel BGR image, got shape {face_bgr.shape}."
        )

    hsv = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2YCrCb)

    # HSV baseline skin range (H ~ 0-20, S >= 48, V unrestricted).
    lower_hsv = np.array([0, 48, 0], dtype=np.uint8)
    upper_hsv = np.array([20, 255, 255], dtype=np.uint8)

    # YCrCb baseline skin range (Cr ~ 133-173, Cb ~ 77-127, Y unrestricted).
    lower_ycrcb = np.array([0, 133, 77], dtype=np.uint8)
    upper_ycrcb = np.array([255, 173, 127], dtype=np.uint8)

    # TODO(validation): these threshold ranges are baseline literature values.
    # They may be tuned after pilot validation on the pilot image set, but they
    # are intentionally left unchanged here until such validation is done.

    mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)
    mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)

    # A pixel is skin only if both colour spaces agree it is skin.
    mask = cv2.bitwise_and(mask_hsv, mask_ycrcb)

    # Morphological cleanup: open once (remove specks), then close twice
    # (fill small gaps and holes in the face region).
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return keep_largest_connected_component(mask)