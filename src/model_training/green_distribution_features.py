"""Four fixed input-only summaries on the existing normalized facial support."""
import numpy as np

ADDITIONS=('input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast')

def green_distribution_features(image_bgr,mask):
    if not isinstance(image_bgr,np.ndarray) or image_bgr.dtype!=np.uint8 or image_bgr.shape!=(256,256,3):
        raise ValueError('Normalized256 BGR8 input required')
    if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.shape!=(256,256) or not set(np.unique(mask))<={0,255}:
        raise ValueError('Matching binary uint8 measurement mask required')
    count=int(np.count_nonzero(mask))
    if count<1000:return dict(valid=False,skin_pixels=count,reason='fewer_than_1000_measurement_pixels',features=None)
    q=np.percentile(image_bgr[:,:,1][mask>0],[10,50,90],method='linear')
    values=[*map(float,q),float(np.log((q[2]+1)/(q[0]+1)))]
    assert np.isfinite(values).all()
    return dict(valid=True,skin_pixels=count,features=dict(zip(ADDITIONS,values)))
