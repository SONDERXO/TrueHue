"""Independent scalar arithmetic; no vector renderer, trainer or optimizer import."""
import math

def decode(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def encode(x):
    assert -1e-12<=x<=1+1e-12
    x=min(1.,max(0.,x))
    return 12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055

def pixel(rgb,p):
    q,g,r,b,s=p
    v=[decode(c)*balance for c,balance in zip(rgb,[r,1.,b])]
    y=math.fsum(c*w for c,w in zip(v,[.2126,.7152,.0722]))
    if y==0:return [0.,0.,0.]
    luminance=min(1.,g*y**q)
    delta=[luminance*s*(c/y-1.) for c in v]
    candidates=[1.]
    for d in delta:
        if d>0:candidates.append((1-luminance)/d)
        elif d<0:candidates.append(luminance/-d)
    factor=min(candidates)
    return [encode(luminance+factor*d) for d in delta]

def replay(image,reference,alpha,protected,p):
    import numpy as np
    out=np.empty_like(image);squared=[];maxdiff=0.
    for y,x in np.ndindex(alpha.shape):
        source=[int(v)/255 for v in image[y,x]]
        if alpha[y,x]==0 or protected[y,x]:out[y,x]=image[y,x];continue
        corrected=pixel(source,p)
        continuous=[(1-float(alpha[y,x]))*v+float(alpha[y,x])*c for v,c in zip(source,corrected)]
        out[y,x]=[round(v*255) for v in continuous]
        squared.extend((v-int(target)/255)**2 for v,target in zip(continuous,reference[y,x]))
    return out,math.fsum(squared)/len(squared) if squared else None
