"""Input-only color-distribution features for a separately versioned experiment."""
import cv2
import numpy as np
from src.ita_estimation.compute_ita import opencv_lab_to_cielab

ADDITIONS=('input_a_iqr','input_b_iqr','input_cov_l_a','input_cov_l_b')


def chroma_distribution_features(image_bgr,mask):
    """Same measured input support; population covariance, linear percentiles."""
    image=np.asarray(image_bgr);selected=np.asarray(mask)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3:
        raise ValueError('Expected uint8 BGR image')
    if selected.dtype!=bool or selected.shape!=image.shape[:2]:
        raise ValueError('Expected matching boolean measurement mask')
    count=int(selected.sum())
    if count<1000:
        return dict(valid=False,reason='fewer_than_1000_measurement_pixels',skin_pixels=count)
    pixels=opencv_lab_to_cielab(cv2.cvtColor(image,cv2.COLOR_BGR2LAB))[selected].astype(float)
    centered=pixels-pixels.mean(axis=0)
    quartiles=np.percentile(pixels[:,1:],[25,75],axis=0,method='linear')
    values=[*(quartiles[1]-quartiles[0]),float(np.mean(centered[:,0]*centered[:,1])),float(np.mean(centered[:,0]*centered[:,2]))]
    return dict(valid=True,skin_pixels=count,features=dict(zip(ADDITIONS,map(float,values))))
