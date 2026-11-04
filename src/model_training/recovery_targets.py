"""Reference-informed target construction, never image-time inference."""
import numpy as np
from scipy.optimize import least_squares

TARGET_METHOD='bounded_rgb_recovery_target_v1'
LOWER=np.array([.25,.25,.25]);UPPER=np.array([4.,4.,4.])


def fit_recovery_target(input_rgb,reference_rgb,application_mask,reference_mask):
    image=np.asarray(input_rgb);reference=np.asarray(reference_rgb)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3 or not image.size or reference.dtype!=np.uint8 or reference.shape!=image.shape:
        raise ValueError('Matching nonempty uint8RGB images required')
    masks=[np.asarray(application_mask),np.asarray(reference_mask)]
    if any(m.dtype!=bool or m.shape!=image.shape[:2] for m in masks):raise ValueError('Explicit matching boolean application/reference masks required')
    selected=masks[0]&masks[1];n=int(selected.sum())
    if n<100:return dict(status='unavailable_insufficient_pixels',parameters=None,selected_pixels=n,target_method=TARGET_METHOD)
    x=image[selected].astype(float)/255;y=reference[selected].astype(float)/255
    if not np.all(np.ptp(x,axis=0)>1/255):return dict(status='unavailable_degenerate_input',parameters=None,selected_pixels=n,target_method=TARGET_METHOD)
    def correct(p):return np.clip(np.power(x,1/p[0])*[p[1],1,p[2]],0,1)
    def residual(p):return (correct(p)-y).ravel()
    fitted=least_squares(residual,np.ones(3),bounds=(LOWER,UPPER),method='trf',loss='linear',
        ftol=1e-10,xtol=1e-10,gtol=1e-10,max_nfev=500)
    rank=int(np.linalg.matrix_rank(fitted.jac))
    valid=bool(fitted.success and rank==3 and np.isfinite(fitted.x).all())
    output=correct(fitted.x)
    return dict(status='available_approximate_target' if valid else 'unavailable_fit_or_identifiability',
        parameters=fitted.x.tolist() if valid else None,target_method=TARGET_METHOD,selected_pixels=n,
        converged=bool(fitted.success),optimizer_status=int(fitted.status),function_evaluations=int(fitted.nfev),
        jacobian_rank=rank,active_bounds=fitted.active_mask.tolist(),
        float_rgb_rmse=float(np.sqrt(np.mean((output-y)**2))),
        identity_float_rgb_rmse=float(np.sqrt(np.mean((x-y)**2))),
        quantized_rgb_mae=float(np.mean(np.abs(np.rint(output*255)-reference[selected].astype(float)))/255),
        input_black_channel_fraction=float(np.mean(x==0)),input_white_channel_fraction=float(np.mean(x==1)),
        objective='normalized_encodedRGB_squared_error_on_explicit_mask_intersection',
        guarantee='bounded_local_solution_not_exact_inverse_or_learned_performance')
