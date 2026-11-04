"""Isolated three-output photographic target construction; never inference/admission."""
import numpy as np
from scipy.optimize import least_squares
from src.distortion_generation.paper_gamma import transform_rgb

VERSION = 'direct_gamma_rgb_three_control_blended_target_v1'
LOWER = np.array([.25, .25, .25])
UPPER = np.array([4., 4., 4.])


def _image(image):
    image = np.asarray(image)
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[-1] != 3 or not image.size:
        raise ValueError('Nonempty uint8 RGB image required')
    return image


def _alpha(alpha, shape):
    alpha = np.asarray(alpha)
    if alpha.shape != shape or not np.issubdtype(alpha.dtype, np.floating):
        raise ValueError('Matching floating-point alpha required')
    if not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any():
        raise ValueError('Alpha must be finite within [0,1]')
    return alpha


def render_rgb8(image, alpha, parameters):
    """Same direct-power, clipping, blend and rounding as current baseline renderer."""
    image = _image(image); alpha = _alpha(alpha, image.shape[:2])
    x = image.astype(float)/255
    corrected = transform_rgb(x, *parameters)
    mixed = x*(1-alpha[..., None]) + corrected*alpha[..., None]
    result = np.rint(mixed*255).astype(np.uint8)
    result[alpha == 0] = image[alpha == 0]
    return result


def fit_target(image, reference, alpha, scoring_mask):
    """One bounded local fit to supplied target; not prediction or true-colour truth.

    Fit float blended error, then verify the actual RGB8 output separately.
    No automatic quality threshold/admission; exact-neutral pairs return neutral.
    """
    image = _image(image); reference = _image(reference)
    if reference.shape != image.shape: raise ValueError('Matching reference required')
    alpha = _alpha(alpha, image.shape[:2]); mask = np.asarray(scoring_mask)
    if mask.dtype != bool or mask.shape != image.shape[:2] or not mask.any():
        raise ValueError('Explicit nonempty boolean scoring mask required')
    if (mask & (alpha == 0)).any():
        raise ValueError('Scoring mask must be within application alpha')
    base = dict(version=VERSION, training_admitted=False, calibration_admitted=False,
                reference_used_for_supervision_only=True, runtime_output_schema_changed=False,
                outside_alpha_mismatch_channels=int(np.count_nonzero(
                    image[alpha == 0] != reference[alpha == 0])))
    if np.array_equal(image[mask], reference[mask]):
        return dict(base, status='exact_neutral_target', parameters=[1., 1., 1.],
                    rgb8_mae_codes=0., input_rgb8_mae_codes=0., evaluations=0)
    x = image[mask].astype(float)/255; y = reference[mask].astype(float)/255
    if not np.all(np.ptp(x, axis=0) > 1/255):
        return dict(base, status='unavailable_degenerate_input', parameters=None)
    a = alpha[mask, None]
    def render(p):
        return x*(1-a) + np.clip(x**p[0]*[p[1], 1., p[2]], 0, 1)*a
    result = least_squares(lambda p: (render(p)-y).ravel(), np.ones(3),
        bounds=(LOWER, UPPER), method='trf', loss='linear',
        ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=500)
    rank = int(np.linalg.matrix_rank(result.jac))
    valid = bool(result.success and rank == 3 and np.isfinite(result.x).all())
    params = result.x.tolist() if valid else None
    output = render_rgb8(image, alpha, result.x)
    return dict(base, status='available_approximate_target' if valid else 'unavailable_fit_or_identifiability',
        parameters=params, evaluations=int(result.nfev), jacobian_rank=rank,
        active_bounds=result.active_mask.tolist(), converged=bool(result.success),
        float_rmse=float(np.sqrt(np.mean((render(result.x)-y)**2))),
        rgb8_mae_codes=float(np.abs(output[mask].astype(float)-reference[mask]).mean()),
        input_rgb8_mae_codes=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),
        raw_out_of_range_channel_samples=int(np.count_nonzero((x**result.x[0]*[result.x[1],1.,result.x[2]]>1))),
        objective='float_encoded_RGB_squared_error_with_supplied_alpha; actual_RGB8_residual_separately_reported',
        guarantee='bounded_local_approximation_not_exact_inverse_or_global_optimum_or_automatic_model')
