"""One exact zero-MST coefficient on the frozen clean-constrained benefit gate."""
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize,LinearConstraint

MST_INDEX=4
MARGIN=1e-6


def fit_mst_excluded_clean_gate(base,features,benefits,clean_indices):
    x=np.asarray(features,float);y=np.asarray(benefits,float);idx=np.asarray(clean_indices,int)
    if x.ndim!=2 or x.shape!=(base['fitting_rows'],12) or len(base['mean'])!=12 or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Exact aligned frozen12-feature training data required')
    if idx.ndim!=1 or not len(idx) or len(set(idx.tolist()))!=len(idx) or np.any(idx<0) or np.any(idx>=len(x)):
        raise ValueError('Unique fitting clean indices required')
    z=(x-np.asarray(base['mean']))/np.asarray(base['scale'])
    d=np.column_stack([z,np.ones(len(z))]);w=np.asarray(base['weights']);total=w.sum()
    regularizer=np.diag([1.]*12+[0.]);h=(d.T@(w[:,None]*d)+regularizer)/total;g=d.T@(w*y)/total
    objective=lambda t:.5*float(t@h@t)-float(g@t)
    gradient=lambda t:h@t-g
    initial=np.zeros(13);initial[-1]=-MARGIN;c=d[idx]
    bounds=[(None,None)]*13;bounds[MST_INDEX]=(0.,0.)
    solved=minimize(objective,initial,jac=gradient,bounds=bounds,
        constraints=[LinearConstraint(c,-np.inf,-MARGIN)],method='SLSQP',
        options=dict(ftol=1e-10,maxiter=2000))
    scores=c@solved.x
    if not solved.success or not np.isfinite(solved.x).all() or solved.x[MST_INDEX]!=0 or scores.max()>-MARGIN/2 or objective(solved.x)>objective(initial)+1e-8:
        raise ValueError('MST-excluded constrained solve failed: '+str(solved.message))
    payload=deepcopy(base)
    payload.update(schema_version='truehue_experimental_mst_excluded_clean_signed_gate_v1',
        coefficient=solved.x[:-1].tolist(),intercept=float(solved.x[-1]),
        constraint_margin=MARGIN,clean_indices=idx.tolist(),training_clean_scores=scores.tolist(),
        fixed_zero_coefficient_indices=[MST_INDEX],
        solver=dict(method='SLSQP',success=bool(solved.success),iterations=int(solved.nit),
            status=int(solved.status),message=str(solved.message),ftol=1e-10,maxiter=2000,
            quadratic_objective=objective(solved.x)))
    return payload
