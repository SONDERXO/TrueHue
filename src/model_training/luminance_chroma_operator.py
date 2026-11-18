"""Isolated linear-light luminance/chroma research operator. No runtime adoption."""
import math
import numpy as np
LOWER=np.array([.25,.25,.25,.25,.25])
UPPER=np.array([4.,4.,4.,4.,1.5])
IDENTITY=np.ones(5)
W=np.array([.2126,.7152,.0722])

def parameters(p):
    a=np.asarray(p,dtype=float)
    if a.shape!=(5,) or not np.isfinite(a).all() or np.any(a<LOWER) or np.any(a>UPPER):raise ValueError('Finite bounded five controls required')
    return a

def decode(x):
    x=np.asarray(x,dtype=float)
    if not np.isfinite(x).all() or np.any(x<0) or np.any(x>1):raise ValueError('EncodedRGBin[0,1] required')
    return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)

def encode(x):
    x=np.asarray(x,dtype=float)
    if not np.isfinite(x).all() or np.any(x < -1e-12) or np.any(x>1+1e-12):raise ValueError('Gamut computation failed')
    x=np.clip(x,0,1) # Numerical boundary cleanup only; gamut is handled before encoding.
    return np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)

def transform(image,p,*,details=False):
    q,g,r,b,s=parameters(p)
    image=np.asarray(image,dtype=float)
    if image.ndim<2 or image.shape[-1]!=3:raise ValueError('RGBarray required')
    v=decode(image)*np.array([r,1,b])
    y=v@W;positive=y>0
    ratio=np.zeros_like(v);np.divide(v,y[...,None],out=ratio,where=positive[...,None])
    luminance=np.minimum(1.,g*np.power(y,q))
    delta=luminance[...,None]*s*(ratio-1)
    limit=np.ones_like(v)
    np.divide(1-luminance[...,None],delta,out=limit,where=delta>0)
    np.divide(luminance[...,None],-delta,out=limit,where=delta<0)
    t=np.minimum(1.,np.min(limit,axis=-1))
    if not np.isfinite(t).all() or np.any(t < -1e-12):raise ValueError('Invalid neutral-ray limit')
    linear=luminance[...,None]+t[...,None]*delta
    linear[~positive]=0
    result=encode(linear)
    if details:return result,dict(linear=linear,luminance=luminance,gamut_factor=t)
    return result

def render_float(image,alpha,protected,p):
    image=np.asarray(image,dtype=float);alpha=np.asarray(alpha,dtype=float);protected=np.asarray(protected)
    if image.shape[:-1]!=alpha.shape or alpha.shape!=protected.shape or protected.dtype!=bool:raise ValueError('Support shapes/type mismatch')
    if not np.isfinite(alpha).all() or np.any(alpha<0) or np.any(alpha>1) or np.any(alpha[protected]!=0):raise ValueError('Invalid alpha/protection')
    output=(1-alpha[...,None])*image+alpha[...,None]*transform(image,p)
    output[(alpha==0)|protected]=image[(alpha==0)|protected]
    return output

def render_rgb8(image,alpha,protected,p):
    image=np.asarray(image)
    if image.dtype!=np.uint8:raise ValueError('RGB8 required')
    result=np.rint(render_float(image/255.,alpha,protected,p)*255).astype(np.uint8)
    result[(np.asarray(alpha)==0)|protected]=image[(np.asarray(alpha)==0)|protected]
    return result

def fit_target(image,reference,alpha,protected):
    from scipy.optimize import least_squares
    image=np.asarray(image);reference=np.asarray(reference);alpha=np.asarray(alpha)
    if image.shape!=reference.shape or image.dtype!=np.uint8 or reference.dtype!=np.uint8:raise ValueError('MatchedRGB8 required')
    # Validate supports even when target is unavailable.
    render_float(image/255.,alpha,protected,IDENTITY)
    mask=alpha>0
    if not mask.any() or not np.any(image[mask]):return dict(status='unavailable_no_signal',parameters=None,solver_calls=0)
    if np.array_equal(image,reference):return dict(status='identity_exact',parameters=IDENTITY.tolist(),solver_calls=0,float_mse=0.)
    # Pointwise formula allows fitting just selected pixels; same blended objective.
    x=image[mask]/255.;ref=reference[mask]/255.;a=alpha[mask,None]
    def residual(p):return ((1-a)*x+a*transform(x,p)-ref).reshape(-1)
    result=least_squares(residual,IDENTITY.copy(),method='trf',bounds=(LOWER,UPPER),
        x_scale='jac',ftol=1e-10,xtol=1e-10,gtol=1e-10,max_nfev=500)
    singular=np.linalg.svd(result.jac,compute_uv=False)
    rank=int(np.linalg.matrix_rank(result.jac))
    return dict(status='available_local_diagnostic' if result.success and rank==5 else 'unqualified_local_result',
        parameters=result.x.tolist(),solver_calls=1,converged=bool(result.success),rank=rank,
        condition=float(singular[0]/singular[-1]) if singular[-1]>0 else None,
        singular_values=singular.tolist(),nfev=int(result.nfev),active_bounds=result.active_mask.tolist(),
        float_mse=float(np.mean(residual(result.x)**2)),message=str(result.message),model_ready=False)
