"""Own deterministic soft joint log-colour features; no learned estimator."""
import numpy as np

VERSION='joint_log_rg_bg_soft16_range2_v1'
NAMES=('joint_colour_available','joint_colour_positive_fraction','joint_colour_clipped_fraction')+tuple(
    f'joint_colour_u{i:02}_v{j:02}' for i in range(16) for j in range(16))

def extract(image):
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty RGB8HxWx3 required')
    values=image.reshape(-1,3);positive=np.all(values>0,axis=1)
    hist=np.zeros((16,16),float)
    if not positive.any():
        return dict(version=VERSION,available=False,features=dict(zip(NAMES,[0.]*259)),positive_pixels=0,total_pixels=len(values))
    pixels=values[positive].astype(float)
    uv=np.log(pixels[:,[0,2]]/pixels[:,1,None])
    clipped=np.any((uv< -2)|(uv>2),axis=1)
    position=(np.clip(uv,-2,2)+2)*(15/4)
    lower=np.floor(position).astype(int);upper=np.minimum(lower+1,15);weight=position-lower
    for a in [0,1]:
        for b in [0,1]:
            ix=lower[:,0] if a==0 else upper[:,0];iy=lower[:,1] if b==0 else upper[:,1]
            w=(1-weight[:,0] if a==0 else weight[:,0])*(1-weight[:,1] if b==0 else weight[:,1])
            np.add.at(hist,(ix,iy),w)
    hist/=len(pixels)
    features=[1.,len(pixels)/len(values),float(clipped.mean())]+hist.ravel().tolist()
    return dict(version=VERSION,available=True,features=dict(zip(NAMES,features)),positive_pixels=len(pixels),total_pixels=len(values))
