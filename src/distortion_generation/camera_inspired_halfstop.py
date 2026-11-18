"""Own camera-inspired processed-sRGB perturbation, not raw-camera simulation."""
import numpy as np
from src.model_training.luminance_chroma_operator import decode,encode
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
def settings(role):
    if role not in ROLES:raise ValueError('Fixed six-role condition required')
    ev=-.5 if role.endswith('under') else .5 if role.endswith('over') else 0.
    colour=role=='colour_only' or role.startswith('combined_')
    return ev,.85 if colour else 1.,1.15 if colour else 1.
def inverse(role):
    ev,r,b=settings(role)
    return [1.,2.**(-ev),1./r,1./b,1.]
def generate(reference,role):
    reference=np.asarray(reference)
    if reference.dtype!=np.uint8 or reference.ndim!=3 or reference.shape[-1]!=3:raise ValueError('RGB8 image required')
    ev,r,b=settings(role)
    raw=decode(reference/255.)*(2.**ev)*np.array([r,1.,b])
    clipped=raw>1.
    result=np.rint(encode(np.minimum(raw,1.))*255).astype(np.uint8)
    return result,dict(EV=ev,linear_red_balance=r,linear_blue_balance=b,
        preclip_overflow_channel_samples=int(clipped.sum()),preclip_overflow_pixels=int(clipped.any(axis=2).sum()),
        quantized_black_pixels=int(np.all(result==0,axis=2).sum()),
        newly_all_black_pixels=int((np.all(result==0,axis=2)&~np.all(reference==0,axis=2)).sum()))
