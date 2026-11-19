"""Use existing measured facial skin, rather than all application pixels, for headroom.

The rendering mask remains unchanged. No clipped-channel guarantee is made for
accessories, neck or feathered pixels outside the facial measurement region.
"""
import numpy as np

from .exposure_headroom import cap_exposure_headroom


def cap_facial_exposure_headroom(image, measurement, alpha, protected, controls):
    image=np.asarray(image);measurement=np.asarray(measurement)
    alpha=np.asarray(alpha);protected=np.asarray(protected)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[-1]!=3:
        raise ValueError('RGB8 image required')
    if (measurement.dtype!=np.uint8 or measurement.shape!=image.shape[:2]
            or not np.isin(measurement,[0,255]).all()):
        raise ValueError('Matching binary RGB8 facial measurement mask required')
    if (alpha.shape!=image.shape[:2] or alpha.dtype.kind!='f'
            or not np.isfinite(alpha).all() or np.any(alpha<0) or np.any(alpha>1)):
        raise ValueError('Matching finite floating alpha in[0,1] required')
    if (protected.shape!=alpha.shape or protected.dtype!=bool
            or np.any(alpha[protected]!=0)):
        raise ValueError('Matching boolean protection with zero alpha required')
    scoped_alpha=np.where(measurement>0,alpha,0.)
    result=cap_exposure_headroom(image,scoped_alpha,protected,controls)
    result['policy']='facial_measurement_luminance_headroom_v1'
    result['decision_region']='measurement_intersect_application_unprotected'
    result['decision_pixels']=int(np.count_nonzero((measurement>0)&(alpha>0)&~protected))
    result['application_pixels']=int(np.count_nonzero((alpha>0)&~protected))
    return result
