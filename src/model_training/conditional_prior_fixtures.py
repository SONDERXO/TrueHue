"""Fixed synthetic encoded RGB lists only. No physical or skin-tone labels."""
from math import exp
from itertools import product
ROLES=dict(identity=(1.,1.),red_decrease=(245/255,1.),blue_decrease=(1.,245/255),blue_increase=(1.,255/245))
def trend(k):
    g=(k+.5)/8;return [g*exp(.12+.08*g),g,g*exp(-.15+.04*g)]
def reference(source,values):return dict(source=source,role='reference',generated_fixture=True,pixels=values)
def references():
    counts=dict(A=[1]*6,B=[1,2,3,4,5,6],C=[6,5,4,3,2,1],H=[2,1,4,1,3,5]);result=[]
    for source,cs in counts.items():
        order=list(range(6))[::-1] if source=='H' else range(6)
        result.append(reference(source,[trend(k) for k in order for _ in range(cs[k])]))
    return result
def transform(values,red=1.,blue=1.,gamma=1.):
    return [[min(1.,max(0.,r**gamma*red)),g**gamma,min(1.,max(0.,b**gamma*blue))] for r,g,b in values]
def quantize(values):return [[round(v*255)/255 for v in row] for row in values]
def offset_probes():
    h=references()[-1]['pixels']
    return [dict(offset=[r,b],role=role,pixels=transform(h,red=exp(r)*gains[0],blue=exp(b)*gains[1]),expected_edit=[__import__('math').log(v) for v in gains]) for r,b in product([-.1,0.,.1],repeat=2) for role,gains in ROLES.items()]
