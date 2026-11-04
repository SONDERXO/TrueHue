"""Portable interpolation for explicitly experimental monotone MST artifacts."""
from bisect import bisect_right
import math
from numbers import Real


class DevelopmentMonotoneLookup:
    """No claim of validation; schema intentionally differs from calibrated lookup."""
    def __init__(self,payload,measurement_contract_sha256):
        if payload.get('schema_version')!='truehue_development_monotone_mst_v1' or payload.get('status')!='experimental_not_final_validated':
            raise ValueError('Explicit development lookup required')
        if payload.get('measurement_contract_sha256')!=measurement_contract_sha256:
            raise ValueError('Measurement contract mismatch')
        if payload.get('rounding')!='floor_plus_half' or payload.get('outside_range')!='clip':
            raise ValueError('Unsupported interpolation contract')
        x,y=payload.get('ita_knots'),payload.get('mst_knots')
        if not isinstance(x,list) or not isinstance(y,list) or len(x)!=len(y) or not x:
            raise ValueError('Matching nonempty knot arrays required')
        if any(isinstance(v,bool) or not isinstance(v,Real) or not math.isfinite(v) for v in x+y):
            raise ValueError('Finite numeric knots required')
        if any(a>=b for a,b in zip(x,x[1:])) or any(a<b for a,b in zip(y,y[1:])) or any(not 1<=v<=10 for v in y):
            raise ValueError('Increasing ITA, nonincreasing MST1–10required')
        self._x=tuple(x);self._y=tuple(y)
        self.measurement_contract_sha256=measurement_contract_sha256

    def continuous(self,value):
        if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value):
            raise ValueError('Finite input ITA required')
        if value<=self._x[0]:return float(self._y[0])
        if value>=self._x[-1]:return float(self._y[-1])
        i=bisect_right(self._x,value)-1
        return self._y[i]+(self._y[i+1]-self._y[i])*(value-self._x[i])/(self._x[i+1]-self._x[i])

    def label(self,value):return math.floor(self.continuous(value)+.5)
