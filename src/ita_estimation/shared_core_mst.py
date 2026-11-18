"""Portable input-only scores for an explicitly unvalidated development map."""
from bisect import bisect_right
import math


def predict_score(artifact,ita,*,measurement_core_sha256,feature_control_contract_sha256):
    if artifact.get('schema_version')!='truehue_shared_core_development_mst_v1':
        raise ValueError('Known development mapping schema required')
    if artifact.get('measurement_core_sha256')!=measurement_core_sha256 or artifact.get('feature_control_contract_sha256')!=feature_control_contract_sha256:
        raise ValueError('Measurement core/application contract mismatch')
    if artifact.get('status')!='development_unvalidated_transfer' or artifact.get('calibration_admitted') is not False or artifact.get('runtime_adopted') is not False:
        raise ValueError('This interface is for explicitly unadmitted development only')
    if isinstance(ita,bool) or not isinstance(ita,(float,int)) or not math.isfinite(ita):
        raise ValueError('Finite input-derived ITA required')
    xs,ys=artifact.get('ita_knots'),artifact.get('mst_score_knots')
    if not isinstance(xs,list) or not isinstance(ys,list) or not xs or len(xs)!=len(ys):
        raise ValueError('Matching nonempty knots required')
    if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in xs+ys):
        raise ValueError('Finite knots required')
    if any(a>=b for a,b in zip(xs,xs[1:])) or any(a<b for a,b in zip(ys,ys[1:])) or any(not 1<=y<=10 for y in ys):
        raise ValueError('Increasing ITA/nonincreasing decimal score1–10 required')
    outside=ita<xs[0] or ita>xs[-1]
    if ita<=xs[0]:value=ys[0]
    elif ita>=xs[-1]:value=ys[-1]
    else:
        i=bisect_right(xs,ita)-1;value=ys[i]+(ys[i+1]-ys[i])*(ita-xs[i])/(xs[i+1]-xs[i])
    return dict(score=float(value),outside_fitting_support=outside,endpoint_clipped=outside,
                fitting_support=[xs[0],xs[-1]])
