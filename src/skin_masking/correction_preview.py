"""Reusable development correction preview; no photograph IDs or tone labels."""
from dataclasses import dataclass
import cv2
import numpy as np
from src.skin_masking.full_face_support import build_full_face_support
from src.skin_masking.continuous_correction import continuous_support
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.clear_lens_correction import protect_with_clear_lenses
from src.correction.seamless_blend import apply_blended

GLASSES_MODES = ('clear', 'opaque', 'uncertain')


@dataclass
class CorrectionPreview:
    support: object
    protected: np.ndarray
    lens_interiors: np.ndarray
    approximate_rims: np.ndarray
    alpha: np.ndarray
    output: np.ndarray
    report: dict


def render_preview(image, facial_mask, categories, landmarks, visible_face, *,
                   glasses='uncertain', parameters=(.85, 1.05, .95), protected=None):
    """Compose unchanged candidate masks with explicit per-photo glasses handling.

    ``visible_face`` must come from the matching pinned FaceOcc mapping. There is
    no permissive fallback if it is unavailable. Uncertain glasses remain fully
    protected and mark the preview as needing a choice; no type is inferred.
    """
    if not isinstance(glasses, str) or glasses not in GLASSES_MODES:
        raise ValueError('Glasses choice must be clear, opaque or uncertain')
    support = continuous_support(build_full_face_support(image, facial_mask, categories,
        landmarks, face_count=1, protected=protected), protected=protected)
    outline = build_face_coverage(image, landmarks).face_outline
    revised, veto, lenses, rims = protect_with_clear_lenses(support, categories,
        visible_face, outline, transparent_glasses=glasses == 'clear', protected=protected)
    _, xx = np.nonzero(facial_mask)
    if not len(xx):
        raise ValueError('Nonempty facial measurement support required')
    width = int(xx.max()-xx.min()+1)
    output, alpha, blend = apply_blended(image, revised.correction_mask, parameters,
        face_width=width, protected=veto)
    detected = bool((categories == 6).any())
    needs_choice = detected and glasses == 'uncertain'
    report = dict(version='reusable_object_protected_correction_preview_v1',
        status='needs_glasses_choice' if needs_choice else 'preview_available',
        glasses_choice=glasses, glasses_choice_source='explicit_caller_choice_not_classifier',
        parser_glasses_present=detected, requires_glasses_choice=needs_choice,
        correction_report=revised.report, blend_report=blend,
        parameters=list(parameters), parameters_are_illustrative=True,
        correction_model_used=False, MST=None, training_admitted=False,
        actual_skin_validity='unverified', scientific_admission=False,
        glasses_detection_validated=False)
    return CorrectionPreview(revised, veto, lenses, rims, alpha, output, report)
