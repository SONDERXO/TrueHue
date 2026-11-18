"""Seven fixed input-only scene summaries for one paired development experiment."""
import cv2
import numpy as np

SCENE_FEATURES=('scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90',
                'scene_any_zero_fraction','scene_any_full_fraction')


def scene_features(rgb):
    if not isinstance(rgb,np.ndarray) or rgb.dtype!=np.uint8 or rgb.ndim!=3 or rgb.shape[2]!=3 or not rgb.size:
        raise ValueError('Nonempty original RGB8 scene required')
    means=rgb.reshape(-1,3).mean(axis=0)
    lab=cv2.cvtColor(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),cv2.COLOR_BGR2LAB)
    light=lab[:,:,0].astype(np.float32)*(100/255)
    quantiles=np.percentile(light,[10,50,90],method='linear')
    values=[np.log((means[0]+1)/(means[1]+1)),np.log((means[2]+1)/(means[1]+1)),*quantiles,
            np.any(rgb==0,axis=2).mean(),np.any(rgb==255,axis=2).mean()]
    return dict(zip(SCENE_FEATURES,map(float,values)))
