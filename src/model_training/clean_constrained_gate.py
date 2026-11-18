"""One convex clean constraint on a frozen signed-benefit ridge specification."""
from copy import deepcopy
import numpy as np
from scipy.optimize import minimize,LinearConstraint
MARGIN=1e-6

def fit_clean_constrained_gate(base,features,benefits,clean_indices):
    x=np.asarray(features,float);y=np.asarray(benefits,float);idx=np.asarray(clean_indices,int)
    if x.ndim!=2 or x.shape!=(base['fitting_rows'],len(base['mean'])) or y.shape!=(len(x),) or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Exact aligned frozen training data required')
    if idx.ndim!=1 or not len(idx) or len(set(idx.tolist()))!=len(idx) or np.any(idx<0) or np.any(idx>=len(x)):raise ValueError('Unique fitting clean indices required')
    z=(x-np.asarray(base['mean']))/np.asarray(base['scale']);d=np.column_stack([z,np.ones(len(z))]);w=np.asarray(base['weights']);total=w.sum();regularizer=np.diag([1.]*x.shape[1]+[0.]);h=(d.T@(w[:,None]*d)+regularizer)/total;g=d.T@(w*y)/total
    objective=lambda t:.5*float(t@h@t)-float(g@t)
    gradient=lambda t:h@t-g
    initial=np.zeros(x.shape[1]+1);initial[-1]=-MARGIN;c=d[idx]
    solved=minimize(objective,initial,jac=gradient,constraints=[LinearConstraint(c,-np.inf,-MARGIN)],method='SLSQP',options=dict(ftol=1e-10,maxiter=2000))
    scores=c@solved.x
    if not solved.success or not np.isfinite(solved.x).all() or scores.max()>-MARGIN/2 or objective(solved.x)>objective(initial)+1e-8:raise ValueError('Constrained solve failed: '+str(solved.message))
    payload=deepcopy(base);payload.update(schema_version='truehue_experimental_clean_constrained_signed_rgb_gate_v1',coefficient=solved.x[:-1].tolist(),intercept=float(solved.x[-1]),constraint_margin=MARGIN,clean_indices=idx.tolist(),training_clean_scores=scores.tolist(),solver=dict(method='SLSQP',success=bool(solved.success),iterations=int(solved.nit),status=int(solved.status),message=str(solved.message),ftol=1e-10,maxiter=2000,quadratic_objective=objective(solved.x)))
    return payload
