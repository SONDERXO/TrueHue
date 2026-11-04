"""Fixed input-only brightness statistics, matching historical script72."""
import cv2
import numpy as np
from src.ita_estimation.compute_ita import opencv_lab_to_cielab

ADDITIONS=('input_l_p10','input_l_median','input_l_p90','input_l_iqr','input_l_left_minus_right','input_l_top_minus_bottom')


def facial_brightness_features(image_bgr,mask):
    image=np.asarray(image_bgr);selected=np.asarray(mask)
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or selected.dtype!=bool or selected.shape!=image.shape[:2]:
        raise ValueError('Matching uint8BGR and boolean measurement mask required')
    yy,xx=np.nonzero(selected)
    if len(xx)<1000:return dict(valid=False,reason='fewer_than_1000_mask_pixels',skin_pixels=len(xx))
    bounds=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]
    x0,y0,x1,y1=bounds;xm,ym=(x0+x1-1)/2,(y0+y1-1)/2
    lightness=opencv_lab_to_cielab(cv2.cvtColor(image,cv2.COLOR_BGR2LAB))[:,:,0]
    pixels=lightness[selected]
    regions={'left':pixels[xx<=xm],'right':pixels[xx>xm],'top':pixels[yy<=ym],'bottom':pixels[yy>ym]}
    counts={k:len(v) for k,v in regions.items()}
    if min(counts.values())<100:return dict(valid=False,reason='fewer_than_100_pixels_in_half',skin_pixels=len(xx),region_pixels=counts,bounds=bounds)
    p10,p25,p50,p75,p90=np.percentile(pixels,[10,25,50,75,90],method='linear')
    values=[p10,p50,p90,p75-p25,float(regions['left'].mean())-float(regions['right'].mean()),float(regions['top'].mean())-float(regions['bottom'].mean())]
    return dict(valid=True,reason='available',skin_pixels=len(xx),region_pixels=counts,bounds=bounds,
        features=dict(zip(ADDITIONS,map(float,values))))
