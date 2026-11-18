"""Own six input-only quantization-gap summaries; no correction decisions."""
import numpy as np

NAMES=tuple(f'scene_{channel}_{band}_internal_gap_fraction'
    for channel in ('red','green','blue') for band in ('low','high'))
VERSION='full_frame_rgb8_internal_gap_halves_v1'

def histogram_gap_features(image_rgb):
    if not isinstance(image_rgb,np.ndarray) or image_rgb.dtype!=np.uint8 or image_rgb.ndim!=3 or image_rgb.shape[2]!=3:
        raise ValueError('RGB8 HxWx3 input required')
    if image_rgb.size==0:return dict(valid=False,reason='empty_input',features=None,version=VERSION)
    features=[];channels=[]
    for j in range(3):
        counts=np.bincount(image_rgb[:,:,j].ravel(),minlength=256)
        present=np.flatnonzero(counts);lo=int(present[0]);hi=int(present[-1]);details=[]
        for left,right in [(0,127),(128,255)]:
            a=max(left,lo);b=min(right,hi);n=max(0,b-a+1)
            holes=int(np.count_nonzero(counts[a:b+1]==0)) if n else 0
            features.append(holes/n if n else 0.)
            details.append(dict(eligible_codes=n,empty_codes=holes,band_outside_observed_range=n==0))
        channels.append(dict(min_code=lo,max_code=hi,occupied_bins=len(present),bands=details))
    return dict(valid=True,version=VERSION,features=dict(zip(NAMES,features)),sample_pixels=int(image_rgb.shape[0]*image_rgb.shape[1]),channels=channels)
