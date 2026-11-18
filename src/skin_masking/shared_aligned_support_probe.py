"""Diagnostic common face-coordinate support; not correspondence or skin truth."""
import cv2
import numpy as np
from src.skin_masking.faceocc_coordinates import map_visible_mask

def common_support(masks,matrices):
    if len(masks)!=3 or len(matrices)!=3:
        raise ValueError('Exactly three complete condition masks and transforms required')
    aligned=[]
    for mask,matrix in zip(masks,matrices):
        if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.shape!=(256,256) or not set(np.unique(mask))<={0,255}:
            raise ValueError('Binary square256 uint8 masks required')
        m=np.asarray(matrix,dtype=float)
        if m.shape!=(2,3) or not np.isfinite(m).all() or abs(np.linalg.det(m[:,:2]))<1e-12:
            raise ValueError('Finite invertible affine matrices required')
        aligned.append(cv2.warpAffine(mask,m,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0))
    common=np.where(np.logical_and.reduce([a>0 for a in aligned]),255,0).astype(np.uint8)
    projected=[cv2.bitwise_and(map_visible_mask(common,mask.shape,matrix),mask) for mask,matrix in zip(masks,matrices)]
    return common,projected
