"""Fitting-only rendered loss normalization; not used at inference."""
import numpy as np


def normalize_fitting_costs(costs, identity_flags):
    raw=np.asarray(costs,dtype=float);flags=np.asarray(identity_flags)
    if raw.ndim!=2 or not raw.size or raw.shape[1]<1 or flags.shape!=(len(raw),) or flags.dtype!=bool:
        raise ValueError('Nonempty cost matrix and matching boolean identity flags required')
    if not np.isfinite(raw).all() or (raw<0).any() or (raw[flags,0]!=0).any():
        raise ValueError('Finite nonnegative costs and exact identity baseline required')
    if (raw[~flags,0]<=0).any():
        raise ValueError('Nonidentity rows require positive own identity cost; no epsilon substitute')
    scales=np.where(flags,1.,raw[:,0])
    return raw/scales[:,None],scales
