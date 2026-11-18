"""Frozen artificial vectors, not photographic feature/target observations."""
from itertools import product
from copy import deepcopy
NAMES=[f'generated_feature_{i}' for i in range(281)]
NAMES[5]='scene_log_r_over_g';NAMES[6]='scene_log_b_over_g';NAMES[13]='input_green_p50_codes'
ONE=[dict(kind='linear_leaf')]
THREE=[dict(kind='split',feature=13,threshold=80.,left=1,right=2),dict(kind='linear_leaf'),dict(kind='split',feature=13,threshold=180.,left=3,right=4),dict(kind='linear_leaf'),dict(kind='linear_leaf')]
def row(u,v,y,branch=128.,**metadata):
    x=[0.]*281;x[5]=float(u);x[6]=float(v);x[13]=float(branch)
    return dict(generated_fixture=True,x=x,y=list(y),**metadata)
def fixtures():
    colour=[row(u,v,[1.,1-.2*u,1-.2*v]) for u,v in product([-.2,0.,.2],repeat=2)]
    neutral=[dict(r,y=[1.,1.,1.]) for r in deepcopy(colour)]
    nuisance=[row(s+t,z+w,[1.,1-.2*t,1-.2*w],source_offset=[s,z],edit=[t,w]) for s,z in product([-.1,0.,.1],repeat=2) for t,w in [(0.,0.),(-.2,0.),(0.,-.2),(0.,.2)]]
    return dict(separable=(ONE,colour),neutral=(ONE,neutral),three_leaf=(THREE,[row(0,0,[.7,1.,1.],64),row(.1,.1,[.7,1.,1.],64)]+colour+[row(0,0,[1/.7,1.,1.],224),row(.1,.1,[1/.7,1.,1.],224)]),
      single=(ONE,[row(.1,.2,[1.,1.04,1.])]),conflicting=(ONE,[row(.1,.1,[1.,1.,1.]),row(.1,.1,[1.,1.04,1.])]),
      zero_variance=(ONE,[row(0,v,[1.,1.,1-.2*v]) for v in [-.2,0.,.2]]),correlated=(ONE,[row(t,t,[1.,1-.2*t,1-.2*t]) for t in [-.2,0.,.2]]),
      nuisance_fit=(ONE,[r for r in nuisance if r['source_offset']==[0.,0.]])),nuisance
