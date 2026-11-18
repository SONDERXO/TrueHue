"""Necessary RGB8 rounding interval for identity with fixed channel gains.

This is a diagnostic certificate for a binary correction mask, not a fitted
gamma, search procedure or inference gate. Closed rounding bounds deliberately
relax tie-to-even endpoints, so empty intersections are safe infeasibility
certificates; nonempty intersections need not prove exact render feasibility.
"""
import numpy as np


def fixed_gain_identity_bounds(image_rgb,mask,red_gain,blue_gain):
    image=np.asarray(image_rgb);mask=np.asarray(mask)
    gains=np.asarray([red_gain,1.,blue_gain],float)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or mask.dtype!=bool or mask.shape!=image.shape[:2] or not mask.any():
        raise ValueError('Nonempty matching RGB8 image and binary boolean mask required')
    if not np.isfinite(gains).all() or np.any(gains<=0):raise ValueError('Positive finite fixed gains required')
    coordinates=np.argwhere(mask);pixels=image[mask].astype(float)
    lower=0.;upper=np.inf;lower_witness=upper_witness=None;endpoint_witness=None
    for channel,gain in enumerate(gains):
        values=pixels[:,channel]
        bad=np.flatnonzero(values==255)
        if len(bad) and gain*255<254.5:
            endpoint_witness=dict(pixel_yx=coordinates[bad[0]].tolist(),channel=int(channel),value=255,gain=float(gain))
        indices=np.flatnonzero((values>0)&(values<255))
        if not len(indices):continue
        v=values[indices];den=np.log(v/255.)
        lo=np.log((v+.5)/(255.*gain))/den
        hi=np.log((v-.5)/(255.*gain))/den
        il=int(lo.argmax());ih=int(hi.argmin())
        if lo[il]>lower:
            lower=float(lo[il]);lower_witness=dict(pixel_yx=coordinates[indices[il]].tolist(),channel=int(channel),value=int(v[il]),gain=float(gain))
        if hi[ih]<upper:
            upper=float(hi[ih]);upper_witness=dict(pixel_yx=coordinates[indices[ih]].tolist(),channel=int(channel),value=int(v[ih]),gain=float(gain))
    empty=bool(lower>upper or upper<=0 or endpoint_witness is not None)
    return dict(necessary_gamma_lower=lower,necessary_gamma_upper=None if not np.isfinite(upper) else upper,
        fixed_gain_identity_impossible=empty,lower_witness=lower_witness,upper_witness=upper_witness,
        endpoint_witness=endpoint_witness,rounding_bounds='closed_relaxation_of_numpy_ties_to_even',
        scope='fixed_gains_and_binary_mask_only_not_global_task_impossibility')
