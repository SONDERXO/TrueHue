"""
Individual Typology Angle (ITA) estimation from CIELAB skin pixels.

The Individual Typology Angle is computed from the mean CIE L* and CIE b*
of the selected facial skin pixels:

    ITA = arctan((L* - 50) / b*) * 180 / pi

ITA is expressed in degrees and is a widely used image-derived metric for
subgrouping/visualising skin tone ranges. In this thesis it is used only as:

- an input feature for the later decision-tree correction model, and
- a subgroup/evaluation aid when analysing results across image sets.

ITA reflects what a camera recorded under its lighting conditions — it is an
*image-derived measurement*, not a statement about a person's identity or
"true" skin colour, and it carries no medical, racial, or ethnic meaning.
No MST (Monk Skin Tone) mapping is performed in this module.

Because OpenCV stores Lab in a non-standard encoding (L 0-255 instead of
0-100, and a/b offset by +128), the raw values must be converted to
approximate conventional CIELAB values before computing any mean or ITA.
"""

from __future__ import annotations

import math

import cv2
import numpy as np

# b* near zero makes the ITA ratio undefined; a small epsilon guards against
# accidental division by zero while still accepting very small b* values.
_ITA_EPSILON = 1e-6

# Keys and default values shared by every result dict returned by
# compute_masked_lab_statistics(), so callers can rely on a stable contract.
_EMPTY_STATISTICS = {
    "mean_l_star": None,
    "mean_a_star": None,
    "mean_b_star": None,
    "ita_degrees": None,
}


def opencv_lab_to_cielab(lab_image: np.ndarray) -> np.ndarray:
    """Convert an OpenCV ``uint8`` Lab image to conventional CIELAB values.

    OpenCV's Lab encoding differs from the standard CIELAB representation:

    - the L channel is stored in ``0..255`` so it maps onto ``uint8``, whereas
      CIE L* runs from ``0`` (black) to ``100`` (white);
    - the a and b channels are offset by ``+128`` because they can be negative.

    Using those raw OpenCV values directly in the ITA formula would produce
    incorrect numbers (L* would be about 2.55x too large and b* shifted by
    128). This function converts each pixel to approximate conventional CIELAB:

        L* = L_opencv * (100 / 255)
        a* = a_opencv - 128
        b* = b_opencv - 128

    The conversion is an approximation to OpenCV's Lab space (which itself is
    only an approximation of true CIE Lab), but it is the consistent,
    documented approach the rest of this pipeline relies on.

    Parameters
    ----------
    lab_image : np.ndarray
        Lab image as produced by
        ``cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)``, shape ``(H, W, 3)``,
        dtype ``uint8``.

    Returns
    -------
    np.ndarray
        ``float32`` array of the same shape with channels stacked as
        ``(L*, a*, b*)`` in that order.

    Raises
    ------
    ValueError
        If ``lab_image`` is not a ``(H, W, 3)`` array.
    """
    if lab_image is None or lab_image.ndim != 3 or lab_image.shape[2] != 3:
        raise ValueError(
            f"lab_image must have shape (H, W, 3), got "
            f"{None if lab_image is None else lab_image.shape}."
        )

    lab_float = lab_image.astype(np.float32)

    l_star = lab_float[:, :, 0] * (100.0 / 255.0)
    a_star = lab_float[:, :, 1] - 128.0
    b_star = lab_float[:, :, 2] - 128.0

    return np.stack((l_star, a_star, b_star), axis=2)


def compute_ita(mean_l_star: float, mean_b_star: float) -> float | None:
    """Compute the Individual Typology Angle from mean L* and b*.

    Formula
    -------
    ``ITA = arctan((L* - 50) / b*) * 180 / pi``

    The term ``50`` shifts L* relative to the middle of the 0-100 lightness
    scale, so light skin gives positive ITA and darker skin negative ITA under
    the usual image conditions.

    If ``b*`` is essentially zero, the ratio ``(L* - 50) / b*`` explodes and
    the angle is undefined, so ``None`` is returned instead of raising or
    silently producing an arbitrary angle. A tiny epsilon (``1e-6``) is used as
    the "too close to zero" threshold.

    Parameters
    ----------
    mean_l_star : float
        Mean CIE L* of the selected skin pixels (0-100 range).
    mean_b_star : float
        Mean CIE b* of the selected skin pixels (centred near 0).

    Returns
    -------
    float | None
        ITA in degrees, or ``None`` if ``abs(mean_b_star) < 1e-6``.
    """
    if abs(mean_b_star) < _ITA_EPSILON:
        return None

    ratio = (mean_l_star - 50.0) / mean_b_star
    angle_radians = math.atan(ratio)
    return math.degrees(angle_radians)


def _invalid_result(reason: str, skin_pixels: int = 0) -> dict:
    """Build an invalid-result dict with every key filled consistently."""
    return {
        "valid": False,
        "reason": reason,
        "skin_pixels": skin_pixels,
        **_EMPTY_STATISTICS,
    }


def compute_masked_lab_statistics(
    face_bgr: np.ndarray,
    skin_mask: np.ndarray,
    minimum_skin_pixels: int = 1000,
) -> dict:
    """Compute mean CIELAB statistics and ITA from masked skin pixels only.

    This is the main function downstream batch processing calls. It expects
    a BGR face crop and a binary skin mask of the same spatial size (typically
    produced by ``src.skin_masking.skin_mask.create_skin_mask_bgr``), converts
    the crop to CIELAB, averages the channels over the selected skin pixels,
    and computes ITA from the means.

    If fewer than ``minimum_skin_pixels`` pixels are selected, statistics are
    not computed: with too few pixels the averages are not representative of
    the facial skin. The function never raises for *data* problems (empty or
    mismatched inputs, insufficient pixels, undefined ITA); it always returns a
    structured result with ``"valid"`` and ``"reason"`` describing the outcome.

    Result dict keys (identical in every case)::

        {
            "valid": bool,
            "reason": str,
            "skin_pixels": int,
            "mean_l_star": float | None,
            "mean_a_star": float | None,
            "mean_b_star": float | None,
            "ita_degrees": float | None,
        }

    Parameters
    ----------
    face_bgr : np.ndarray
        BGR face crop, shape ``(H, W, 3)``, dtype ``uint8``.
    skin_mask : np.ndarray
        Single-channel skin mask, shape ``(H, W)``; nonzero = skin.
    minimum_skin_pixels : int
        Minimum number of selected skin pixels required to compute ITA
        (default 1000).

    Returns
    -------
    dict
        Structured result as described above.

    Raises
    ------
    ValueError
        If ``minimum_skin_pixels`` is not a positive integer (a programming
        error, unlike the data problems handled above).
    """
    if face_bgr is None or face_bgr.size == 0:
        return _invalid_result("face_bgr is None or empty")

    if skin_mask is None or skin_mask.size == 0:
        return _invalid_result("skin_mask is None or empty")

    if skin_mask.ndim != 2:
        return _invalid_result(
            f"skin_mask must be a 2D single-channel mask, got {skin_mask.ndim} dimension(s)"
        )

    if skin_mask.shape[:2] != face_bgr.shape[:2]:
        return _invalid_result(
            "skin_mask shape does not match face_bgr shape: "
            f"{skin_mask.shape[:2]} vs {face_bgr.shape[:2]}"
        )

    if (
        not isinstance(minimum_skin_pixels, (int, np.integer))
        or minimum_skin_pixels <= 0
    ):
        raise ValueError(
            f"minimum_skin_pixels must be a positive integer, got {minimum_skin_pixels!r}"
        )

    skin_pixel_count = int(np.count_nonzero(skin_mask > 0))

    if skin_pixel_count == 0:
        return _invalid_result("no skin pixels selected", skin_pixels=0)

    if skin_pixel_count < minimum_skin_pixels:
        return _invalid_result(
            "insufficient skin pixels: "
            f"{skin_pixel_count} < minimum_skin_pixels ({minimum_skin_pixels})",
            skin_pixels=skin_pixel_count,
        )

    opencv_lab = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2LAB)
    cielab = opencv_lab_to_cielab(opencv_lab)

    # Select only the skin-mask pixels, then average each CIELAB channel.
    skin_cielab_pixels = cielab[skin_mask > 0]
    mean_l_star = round(float(np.mean(skin_cielab_pixels[:, 0])), 4)
    mean_a_star = round(float(np.mean(skin_cielab_pixels[:, 1])), 4)
    mean_b_star = round(float(np.mean(skin_cielab_pixels[:, 2])), 4)

    ita_degrees = compute_ita(mean_l_star, mean_b_star)

    if ita_degrees is None:
        return {
            "valid": False,
            "reason": (
                "mean b* is too close to zero; ITA is undefined for this sample"
            ),
            "skin_pixels": skin_pixel_count,
            "mean_l_star": mean_l_star,
            "mean_a_star": mean_a_star,
            "mean_b_star": mean_b_star,
            "ita_degrees": None,
        }

    return {
        "valid": True,
        "reason": "ITA computed successfully",
        "skin_pixels": skin_pixel_count,
        "mean_l_star": mean_l_star,
        "mean_a_star": mean_a_star,
        "mean_b_star": mean_b_star,
        "ita_degrees": round(float(ita_degrees), 4),
    }