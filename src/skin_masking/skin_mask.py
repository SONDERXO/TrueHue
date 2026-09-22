"""
Facial skin-region masking for an OpenCV BGR face crop.

Pipeline sequence implemented here
----------------------------------

1. Input is a BGR *face crop* that was already produced by the face-detection
   stage (this module does **not** do face detection).
2. A candidate skin mask is built from HSV + YCrCb thresholds combined with a
   logical AND, followed by morphological cleaning (see
   :func:`create_candidate_mask_bgr`).
3. ``keep_largest_connected_component`` keeps only the biggest connected skin
   blob, which discards remaining isolated noise far from the face.
4. Anatomical feature exclusion (eyes, eyebrows, lips) is applied via
   MediaPipe landmarks (see ``src.skin_masking.landmark_exclusion``); the
   final mask is ``candidate AND largest-component AND NOT exclusion``.

The output is a one-channel ``uint8`` mask using exactly the values
``0`` (= not skin) and ``255`` (= skin). ITA estimation is intentionally *not*
computed here; it is a separate pipeline stage operating on this mask, and the
1,000-pixel minimum-skin rule lives in that stage, not here.

Fallback behaviour
------------------
Feature exclusion depends on MediaPipe and its ``face_landmarker.task`` model.
When they are unavailable or no face is detected in the crop, the pipeline
does **not** silently change behaviour: ``compute_skin_mask_result()`` returns
a ``SkinMaskResult`` whose ``landmarks_available=False`` and whose ``status``
explains exactly why, while ``mask`` falls back to the V1
(candidate AND largest-component) mask. Use the structured API whenever the
status matters; ``create_skin_mask_bgr`` is kept as a simple V1-compatible
mask-only wrapper.

Threshold values are baseline ranges from standard skin-detection literature.
They may be tuned after pilot validation (see the TODO note in
``create_candidate_mask_bgr``); they are kept as-is until then.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from src.skin_masking.landmark_exclusion import (
    FeatureExclusionResult,
    compute_feature_exclusion_mask,
    download_landmarker_model,
)


@dataclass
class SkinMaskResult:
    """Full result of the skin-mask pipeline.

    Attributes
    ----------
    mask : np.ndarray
        Final ``uint8`` mask (H, W) with values 0/255.
    candidate_mask : np.ndarray
        Raw HSV/YCrCb candidate mask *before* largest-component selection and
        exclusion — useful for visual review and diagnostics.
    exclusion_mask : np.ndarray
        Anatomical feature exclusion mask (all zeros when unavailable).
    landmarks_available : bool
        ``True`` when feature exclusion was computed from detected landmarks.
    status : str
        Human-readable description of what the pipeline did (including any
        fallback).
    """

    mask: np.ndarray
    candidate_mask: np.ndarray
    exclusion_mask: np.ndarray
    landmarks_available: bool
    status: str


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


def create_candidate_mask_bgr(face_bgr: np.ndarray) -> np.ndarray:
    """Build the HSV/YCrCb candidate skin mask for a BGR face crop.

    Applies HSV + YCrCb thresholding (logical AND) and morphological cleanup
    (one open, two closes) but **not** the largest-component filter. This mask
    is the raw colour-based candidate used by the full pipeline and can be
    inspected to see exactly which colour regions were found.

    Parameters
    ----------
    face_bgr : np.ndarray
        Face crop in OpenCV BGR format, shape ``(H, W, 3)``, dtype ``uint8``.

    Returns
    -------
    np.ndarray
        One-channel ``uint8`` mask of shape ``(H, W)`` with values ``0`` or
        ``255``.

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

    return mask


def compute_skin_mask_result(
    face_bgr: np.ndarray,
    exclude_features: bool = True,
    exclusion_dilation: int = 0,
    model_path: str | None = None,
    download_landmarker_if_missing: bool = False,
) -> SkinMaskResult:
    """Run the full skin-mask pipeline with structured status.

    Final mask is ``HSV/YCrCb candidate AND largest-component AND NOT
    (feature exclusion)``. When feature exclusion cannot be computed, the mask
    falls back to the V1 result and the cause is reported in ``status`` +
    ``landmarks_available=False`` — it is never hidden.

    Parameters
    ----------
    face_bgr : np.ndarray
        Face crop in OpenCV BGR format, shape ``(H, W, 3)``, dtype ``uint8``.
    exclude_features : bool
        Apply anatomical feature exclusion (default ``True``).
    exclusion_dilation : int
        Optional dilation pixels for the exclusion mask (see
        ``landmark_exclusion.build_feature_exclusion_mask``).
    model_path : str | None
        Path to ``face_landmarker.task``. Defaults to the configured path.
    download_landmarker_if_missing : bool
        If True, attempt to download the landmarker model when the model file
        is missing (default False so the pipeline never surprises you with a
        network call).

    Returns
    -------
    SkinMaskResult
        Final mask plus diagnostics (see the dataclass).

    Raises
    ------
    ValueError
        If ``face_bgr`` is ``None``, empty, or not a 3-channel BGR image.
    """
    if face_bgr is None or face_bgr.size == 0:
        raise ValueError("face_bgr must be a non-empty BGR face crop.")

    candidate = create_candidate_mask_bgr(face_bgr)
    largest = keep_largest_connected_component(candidate)
    empty_exclusion = np.zeros_like(largest)

    if not exclude_features:
        return SkinMaskResult(
            mask=largest,
            candidate_mask=candidate,
            exclusion_mask=empty_exclusion,
            landmarks_available=False,
            status="skin mask computed without feature exclusion "
            "(exclude_features=False)",
        )

    if download_landmarker_if_missing:
        try:
            download_landmarker_model(model_path)
        except Exception as exc:  # network or filesystem failure
            return SkinMaskResult(
                mask=largest,
                candidate_mask=candidate,
                exclusion_mask=empty_exclusion,
                landmarks_available=False,
                status=f"feature-exclusion FALLBACK used (V1 skin mask): "
                f"could not obtain landmarker model: {exc}",
            )

    exclusion_result: FeatureExclusionResult = compute_feature_exclusion_mask(
        face_bgr, model_path=model_path, dilation=exclusion_dilation
    )

    if not exclusion_result.landmarks_available:
        return SkinMaskResult(
            mask=largest,
            candidate_mask=candidate,
            exclusion_mask=empty_exclusion,
            landmarks_available=False,
            status="feature-exclusion FALLBACK used (V1 skin mask): "
            + exclusion_result.status,
        )

    final_mask = cv2.bitwise_and(largest, cv2.bitwise_not(exclusion_result.mask))
    return SkinMaskResult(
        mask=final_mask,
        candidate_mask=candidate,
        exclusion_mask=exclusion_result.mask,
        landmarks_available=True,
        status="skin mask computed with feature exclusion: "
        + exclusion_result.status,
    )


def create_skin_mask_bgr(face_bgr: np.ndarray) -> np.ndarray:
    """Build the final binary skin mask from a BGR face crop.

    Convenience wrapper around :func:`compute_skin_mask_result` that returns
    only the final ``uint8`` mask. It applies feature exclusion when
    landmarks are available and otherwise falls back to the V1 mask. Use
    ``compute_skin_mask_result`` when you also need the exclusion mask,
    candidate mask, and the ``landmarks_available``/``status`` diagnostics.

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
    return compute_skin_mask_result(face_bgr).mask


def save_mask_visualization(
    face_bgr: np.ndarray,
    candidate_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    final_mask: np.ndarray,
    save_path: str,
    landmarks_available: bool = False,
) -> None:
    """Save a diagnostic grid showing candidate, exclusion, and final masks.

    Writes a 2x2 PNG: the original crop, the HSV/YCrCb candidate, the
    anatomical feature exclusion mask, and the final mask — for manual review
    of skin-mask quality. This function only writes the file you ask for; it
    never modifies the input arrays.

    Parameters
    ----------
    face_bgr : np.ndarray
        Original BGR face crop, used for the first panel.
    candidate_mask : np.ndarray
        Raw HSV/YCrCb candidate mask.
    exclusion_mask : np.ndarray
        Feature exclusion mask (all zeros when unavailable).
    final_mask : np.ndarray
        Final output mask.
    save_path : str
        Destination PNG/JPG path (extension decides the encoding).
    landmarks_available : bool
        Flag echoed into the status text so saved review images record whether
        feature exclusion actually ran.

    Raises
    ------
    ValueError
        If any input array is empty or the masks do not match the crop size.
    """
    h, w = face_bgr.shape[:2]
    masks = {
        "Candidate": candidate_mask,
        "Exclusion": exclusion_mask,
        "Final": final_mask,
    }
    for label, mask in masks.items():
        if mask is None or mask.shape != (h, w):
            raise ValueError(
                f"{label} mask must have shape {(h, w)}, got "
                f"{None if mask is None else mask.shape}."
            )

    original = face_bgr.copy()
    panels = []
    for label, mask in masks.items():
        panel = cv2.cvtColor(np.ascontiguousarray(mask), cv2.COLOR_GRAY2BGR)
        cv2.putText(
            panel,
            label,
            (6, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )
        panels.append(panel)
    cv2.putText(
        original,
        "Original" if landmarks_available else "Original (fallback)",
        (6, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    panels.insert(0, original)

    top = np.hstack((panels[0], panels[1]))
    bottom = np.hstack((panels[2], panels[3]))
    grid = np.vstack((top, bottom))

    written = cv2.imwrite(str(save_path), grid)
    if not written:
        raise OSError(f"Could not write visualization to {save_path}.")