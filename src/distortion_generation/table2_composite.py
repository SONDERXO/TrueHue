"""Explicit development interpretation of the proposal's Table2 settings."""
import numpy as np

VERSION='table2_encoded_rgb_composite_v1'
SETTINGS={
 'light':dict(gamma=.85,brightness=-20,contrast=5,cyan_red=-6,yellow_blue=6),
 'medium':dict(gamma=.70,brightness=-35,contrast=8,cyan_red=-10,yellow_blue=10),
 'dark':dict(gamma=.60,brightness=-45,contrast=10,cyan_red=-14,yellow_blue=14),
}


def composite_rgb(image,group):
    """Return encoded uint8 composite and pre-encoding clipping accounting."""
    image=np.asarray(image)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8RGB required')
    if group not in SETTINGS:raise ValueError('Explicit light/medium/dark group required')
    s=SETTINGS[group]
    raw=np.power(image.astype(float)/255,1/s['gamma'])
    raw=(raw-.5)*(1+s['contrast']/100)+.5+s['brightness']/255
    raw+=np.array([s['cyan_red'],0,s['yellow_blue']])/255
    below=raw<0;above=raw>1
    return np.rint(np.clip(raw,0,1)*255).astype(np.uint8),dict(
        transform_version=VERSION,settings=dict(s),clipped_pixels=int(np.any(below|above,axis=2).sum()),
        clipped_channel_samples=int((below|above).sum()),total_channel_samples=int(raw.size))
