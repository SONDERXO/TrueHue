"""Fixed dense/anatomical and relative-material ablation, development only."""
import cv2
import numpy as np


def combined_supports(image,dense,categories,excluded,face_box,measurement):
    if image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty uint8 BGR image required')
    shape=image.shape[:2]
    for value in (dense,excluded,measurement):
        if value.dtype!=bool or value.shape!=shape:raise ValueError('Matching boolean masks required')
    if categories.dtype!=np.uint8 or categories.shape!=shape or (categories>5).any():
        raise ValueError('Native coarse categories0..5 required')
    x,y,w,h=map(int,face_box)
    if min(x,y)<0 or min(w,h)<=0 or x+w>shape[1] or y+h>shape[0]:raise ValueError('Invalid detector bounds')
    pad=max(2,int(np.ceil(.10*max(w,h))))
    bounds=np.zeros(shape,bool)
    bounds[max(0,y-pad):min(shape[0],y+h+pad),max(0,x-pad):min(shape[1],x+w+pad)]=True
    base=dense & (categories==3) & ~excluded & bounds
    seeds=measurement & base
    if seeds.sum()<1000:raise ValueError('Fewer than1000 material seeds; no fallback')
    lab=cv2.cvtColor(image.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
    sample=lab[seeds].astype(float);center=np.median(sample,axis=0)
    scale=np.maximum(1.4826*np.median(np.abs(sample-center),axis=0),[12.,6.,6.])
    standardized=(lab-center)/scale
    full_distance=np.sqrt(np.square(standardized).sum(axis=2))
    chroma_distance=np.sqrt(np.square(standardized[:,:,1:]).sum(axis=2))
    arms=dict(A=base,F=base & (full_distance<=3),C=base & (chroma_distance<=3))
    assert not (arms['F'] & ~arms['C']).any()
    assert not (arms['C'] & ~arms['A']).any()
    return arms,dict(seed_pixels=int(seeds.sum()),median=center.tolist(),scale=scale.tolist(),
                     pad=pad,face_box=[x,y,w,h]),seeds,full_distance,chroma_distance
