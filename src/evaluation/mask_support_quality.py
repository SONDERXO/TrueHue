"""Development-only support retention against synthetic generation regions.

The reference region is not annotated skin truth and must never become an
inference feature, runtime fallback mask or a general segmentation score.
"""
import numpy as np


def support_retention(reference, estimation, correction, *, minimum_region_pixels=100,
                      minimum_estimation_retention=.5, minimum_correction_retention=.8):
    """Flag major loss globally or in source-bounding-box quadrants.

    Fixed exploratory thresholds are a development screen, not validated skin
    quality cutoffs. Absolute input pixel eligibility is checked separately.
    """
    masks=[np.asarray(m) for m in (reference,estimation,correction)]
    if any(m.dtype!=bool or m.ndim!=2 or m.shape!=masks[0].shape for m in masks):
        raise ValueError('Expected matching 2D boolean masks')
    if minimum_region_pixels<1 or not all(0<=v<=1 for v in
            [minimum_estimation_retention,minimum_correction_retention]):
        raise ValueError('Invalid screening settings')
    reference,estimation,correction=masks
    yy,xx=np.nonzero(reference)
    if not len(xx):raise ValueError('Empty generation support')
    middle_x=(int(xx.min())+int(xx.max())+1)//2
    middle_y=(int(yy.min())+int(yy.max())+1)//2
    y,x=np.indices(reference.shape)
    regions={'whole':reference,
             'upper_left':reference&(x<middle_x)&(y<middle_y),
             'upper_right':reference&(x>=middle_x)&(y<middle_y),
             'lower_left':reference&(x<middle_x)&(y>=middle_y),
             'lower_right':reference&(x>=middle_x)&(y>=middle_y)}
    metrics={};flags=[]
    for name,region in regions.items():
        pixels=int(region.sum())
        eligible=name=='whole' or pixels>=minimum_region_pixels
        estimation_fraction=float((region&estimation).sum()/pixels) if pixels else None
        correction_fraction=float((region&correction).sum()/pixels) if pixels else None
        metrics[name]=dict(reference_pixels=pixels,evaluated=eligible,
                           estimation_retention=estimation_fraction,correction_retention=correction_fraction)
        if eligible:
            if estimation_fraction<minimum_estimation_retention:flags.append(name+':estimation_loss')
            if correction_fraction<minimum_correction_retention:flags.append(name+':correction_loss')
    return dict(screen_pass=not flags,flags=flags,regions=metrics,
                reference_pixels=int(reference.sum()),estimation_pixels=int(estimation.sum()),
                correction_pixels=int(correction.sum()),
                correction_outside_reference_pixels=int((correction&~reference).sum()))
