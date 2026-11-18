"""Isolated five-control reference targets; no model, dataset IO or runtime adoption."""
import numpy as np
from scipy.optimize import least_squares

VERSION = 'affine_prepower_five_control_target_v1'
NAMES = ['gamma', 'red_gain', 'blue_gain', 'input_scale', 'input_offset']
IDENTITY = np.array([1., 1., 1., 1., 0.])
LOWER = np.array([.25, .25, .25, .5, -.3])
UPPER = np.array([4., 4., 4., 2., .3])


def parameters(values):
    raw = np.asarray(values)
    if raw.shape != (5,) or raw.dtype.kind not in 'fiu' or any(isinstance(v, (bool, np.bool_)) for v in values):
        raise ValueError('Five explicit numeric controls required')
    p = raw.astype(float)
    if not np.isfinite(p).all() or (p[:4] <= 0).any():
        raise ValueError('Finite positive gamma/gains/scale and finite signed offset required')
    return p


def image_float(image):
    image = np.asarray(image)
    if (image.ndim != 3 or image.shape[-1] != 3 or not image.size
            or not np.issubdtype(image.dtype, np.floating) or not np.isfinite(image).all()
            or (image < 0).any() or (image > 1).any()):
        raise ValueError('Nonempty normalized floating RGB required')
    return image.astype(float, copy=False)


def support(alpha, protected, shape):
    alpha, protected = np.asarray(alpha), np.asarray(protected)
    if (alpha.shape != shape or not np.issubdtype(alpha.dtype, np.floating)
            or not np.isfinite(alpha).all() or (alpha < 0).any() or (alpha > 1).any()
            or not (alpha > 0).any()):
        raise ValueError('Finite nonempty floating application alpha required')
    if protected.shape != shape or protected.dtype != bool or (alpha[protected] != 0).any():
        raise ValueError('Boolean protection must already veto alpha')
    return alpha, protected


def transform(values, p):
    p = parameters(p)
    with np.errstate(over='raise', invalid='raise'):
        pre = p[3] * values + p[4]
        raw = np.maximum(0., pre) ** p[0] * [p[1], 1., p[2]]
    return np.clip(raw, 0., 1.)


def render_float(image, alpha, protected, controls):
    image = image_float(image)
    alpha, _ = support(alpha, protected, image.shape[:2])
    changed = transform(image, controls)
    result = image * (1 - alpha[..., None]) + changed * alpha[..., None]
    result[alpha == 0] = image[alpha == 0]
    return result


def render_rgb8(image, alpha, protected, controls):
    image = np.asarray(image)
    if image.dtype != np.uint8:
        raise ValueError('RGB8 input required')
    result = np.rint(render_float(image.astype(float)/255, alpha, protected, controls)*255).astype(np.uint8)
    result[alpha == 0] = image[alpha == 0]
    return result


def fit_float_target(image, reference, alpha, protected, *, generated_fixture):
    if type(generated_fixture) is not bool:
        raise ValueError('Explicit source provenance required')
    image, reference = image_float(image), image_float(reference)
    if reference.shape != image.shape:
        raise ValueError('Matching reference required')
    alpha, protected = support(alpha, protected, image.shape[:2])
    mask = alpha > 0
    x, y, a = image[mask], reference[mask], alpha[mask, None]
    base = dict(version=VERSION, control_names=NAMES, generated_fixture=generated_fixture,
        training_admitted=False, calibration_admitted=False, model_ready=False,
        runtime_adopted=False, reference_used_for_supervision_only=True,
        selected_pixels=int(mask.sum()), objective='selected_float_blended_encoded_RGB_squared_error',
        guarantee='one_bounded_local_fit_not_global_optimum_or_input_only_prediction')
    identity_mse = float(np.mean((x-y)**2))
    if np.array_equal(x, y):
        return dict(base, status='exact_neutral_target', parameters=IDENTITY.tolist(),
                    evaluations=0, identity_mse=0., float_rmse=0., float_mse=0.)
    if not np.all(np.ptp(x, axis=0) > 1/255):
        return dict(base, status='unavailable_degenerate_input', parameters=None, evaluations=0,
                    identity_mse=identity_mse)
    def residual(p):
        return (x*(1-a)+transform(x,p)*a-y).ravel()
    result = least_squares(residual, IDENTITY.copy(), bounds=(LOWER,UPPER), method='trf',
                           loss='linear', ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=500)
    valid_controls = (np.asarray(result.x).shape == (5,) and np.isfinite(result.x).all()
                      and (result.x >= LOWER).all() and (result.x <= UPPER).all())
    valid_jacobian = np.isfinite(result.jac).all()
    singular = np.linalg.svd(result.jac, compute_uv=False) if valid_jacobian else np.array([])
    rank = int(np.linalg.matrix_rank(result.jac)) if valid_jacobian else 0
    condition = float(singular[0]/singular[-1]) if len(singular) and singular[-1]>0 else None
    mse = float(np.mean(residual(result.x)**2)) if valid_controls else None
    valid = bool(valid_controls and result.success and rank==5 and mse is not None
                 and mse <= identity_mse+1e-12)
    status = 'available_approximate_target' if valid else 'unavailable_fit_or_identifiability'
    info = dict(base, status=status, parameters=result.x.tolist() if valid else None,
        evaluations=int(result.nfev), converged=bool(result.success), jacobian_rank=rank,
        jacobian_singular_values=singular.tolist(), jacobian_condition_number=condition,
        active_bounds=np.asarray(result.active_mask).tolist(), identity_mse=identity_mse,
        float_mse=mse, float_rmse=float(np.sqrt(mse)) if mse is not None else None)
    if valid:
        pre=result.x[3]*x+result.x[4]
        raw=np.maximum(0.,pre)**result.x[0]*[result.x[1],1.,result.x[2]]
        info.update(prepower_floor_channel_samples=int((pre<0).sum()),
                    output_overflow_channel_samples=int((raw>1).sum()))
    return info


def fit_rgb8_target(image, reference, alpha, protected, *, generated_fixture):
    image, reference = np.asarray(image), np.asarray(reference)
    if image.dtype != np.uint8 or reference.dtype != np.uint8:
        raise ValueError('RGB8 input/reference required')
    result = fit_float_target(image.astype(float)/255, reference.astype(float)/255,
                              alpha, protected, generated_fixture=generated_fixture)
    result['target_encoding'] = 'RGB8_supervision_float_objective_actual_RGB8_residual'
    mask=alpha>0
    result['input_rgb8_mae_codes']=float(np.abs(image[mask].astype(float)-reference[mask]).mean())
    result['rgb8_mae_codes']=None
    if result['parameters'] is not None:
        output=render_rgb8(image,alpha,protected,result['parameters'])
        result['rgb8_mae_codes']=float(np.abs(output[mask].astype(float)-reference[mask]).mean())
    return result
