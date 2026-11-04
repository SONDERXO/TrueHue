"""Experimental correction-only GrabCut refinement, not semantic skin parsing."""
import cv2
import numpy as np
from src.skin_masking.material_checked_support import material_checked_support


def graphcut_correction_support(image_bgr,input_mask,exclusion_mask):
    """Refine existing and added support using fixed input-only initialization.

    A central ellipse intersects original skin to seed foreground. Excluded
    features and the one-pixel crop border seed background. Color-checked
    support initializes probable foreground; other pixels probable background.
    Five GrabCut iterations, RNG seed 42, no label/reference-based fitting.
    Incorrect central seeds or skin at borders may be lost; development only.
    """
    candidate=material_checked_support(image_bgr,input_mask,exclusion_mask)
    height,width=input_mask.shape
    yy,xx=np.mgrid[:height,:width]
    central=((xx/(width-1)-.5)/.22)**2+((yy/(height-1)-.55)/.25)**2<=1
    foreground=central & input_mask & ~exclusion_mask
    background=exclusion_mask.copy()
    background[[0,-1],:]=True; background[:,[0,-1]]=True
    foreground &= ~background
    if foreground.sum()<100: raise ValueError('Insufficient central input skin seeds')
    labels=np.full(input_mask.shape,cv2.GC_PR_BGD,np.uint8)
    labels[candidate]=cv2.GC_PR_FGD
    labels[background]=cv2.GC_BGD;labels[foreground]=cv2.GC_FGD
    bg_model=np.zeros((1,65),np.float64);fg_model=np.zeros((1,65),np.float64)
    # OpenCV global RNG is reset for reproducible, serial development runs.
    cv2.setRNGSeed(42)
    cv2.grabCut(image_bgr.copy(),labels,None,bg_model,fg_model,5,cv2.GC_INIT_WITH_MASK)
    return candidate & np.isin(labels,[cv2.GC_FGD,cv2.GC_PR_FGD]) & ~exclusion_mask
