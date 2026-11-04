"""Synthetic development roles, separate from dataset or training admission."""
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS

VERSION = 'synthetic_core_stress_clean_roles_v1'


def _inputs(reference, alpha):
    reference = np.asarray(reference)
    alpha = np.asarray(alpha)
    if reference.dtype != np.uint8 or reference.ndim != 3 or reference.shape[-1] != 3 or not reference.size:
        raise ValueError('Nonempty RGB8 reference required')
    if (alpha.shape != reference.shape[:2] or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()
            or not (alpha > 0).any()):
        raise ValueError('Nonempty finite floating application alpha required')
    return reference, alpha


def core_exposure(reference, alpha, group, direction):
    """One fixed power-only exposure probe; Table2 offsets/contrast stay in stress.

    No additive colour in this core probe. This is an explicit decomposition,
    not an implementation of the complete Table2 distortion or physical exposure.
    """
    reference, alpha = _inputs(reference, alpha)
    if group not in SETTINGS or direction not in ('under', 'over'):
        raise ValueError('Explicit severity group and exposure direction required')
    gamma = SETTINGS[group]['gamma']
    exponent = 1/gamma if direction == 'under' else gamma
    x = reference.astype(float)/255
    raw = x**exponent
    image = np.rint(255*(x*(1-alpha[..., None])+raw*alpha[..., None])).astype(np.uint8)
    image[alpha == 0] = reference[alpha == 0]
    selected = alpha > 0
    return image, dict(version=VERSION, group=group, direction=direction,
        effective_direct_exponent=exponent, brightness_offset=0, contrast_extra=0,
        colour_shift=[0, 0, 0],
        clipped_channel_samples=int(np.count_nonzero(
            ((raw < 0) | (raw > 1)) & selected[..., None])),
        new_endpoint_channel_samples=int(np.count_nonzero(
            ((image == 0) | (image == 255)) & (reference > 0) & (reference < 255)
            & selected[..., None])),
        limitation='RGB8_quantisation_and_blended_recovery_not_exact_inversion')


def assign_role(reference, image, alpha, *, scenario, clipped_channel_samples):
    """Assign an explanatory development role; never create eligibility/labels.

    Clipping evidence must come from the forward operator before blending.
    RGB8 endpoints alone cannot distinguish clipping from legitimate endpoints.
    No target-fit residual is used to select a clean-only cohort.
    """
    reference, alpha = _inputs(reference, alpha)
    image = np.asarray(image)
    if image.dtype != np.uint8 or image.shape != reference.shape:
        raise ValueError('Matching RGB8 distorted image required')
    if scenario not in ('clean', 'exposure', 'color', 'combined'):
        raise ValueError('Explicit scenario required')
    if (isinstance(clipped_channel_samples, (bool, np.bool_))
            or not isinstance(clipped_channel_samples, (int, np.integer))
            or clipped_channel_samples < 0
            or clipped_channel_samples > int(np.count_nonzero(alpha > 0))*3):
        raise ValueError('Valid operator-reported clipping count required')
    outside_mismatches = int(np.count_nonzero(image[alpha == 0] != reference[alpha == 0]))
    unchanged = bool(np.array_equal(image, reference))
    if outside_mismatches:
        role, reason = 'invalid_support', 'outside_application_pixels_changed'
    elif scenario == 'clean':
        if unchanged and clipped_channel_samples == 0:
            role, reason = 'clean_control', 'exact_identity'
        else:
            role, reason = 'invalid_clean', 'clean_claim_inconsistent_with_image_or_forward_clipping'
    elif clipped_channel_samples:
        role, reason = 'clipping_stress', 'forward_operator_exceeded_range'
    elif unchanged:
        role, reason = 'unchanged_distortion', 'nonclean_recipe_quantised_to_identity'
    else:
        role, reason = 'core_candidate', 'no_forward_clipping_not_proof_of_recoverability'
    return dict(version=VERSION, role=role, reason=reason,
        scenario=scenario, clipped_channel_samples=int(clipped_channel_samples),
        outside_mismatch_channels=outside_mismatches,
        training_admitted=False, dataset_admitted=False,
        automatic_target_acceptance=False,
        policy='stress_retained_and_reported_separately_not_automatically_used_for_training')
