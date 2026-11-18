"""Fixed weighted ridge estimate of signed correction benefit; experimental only."""
from collections import Counter
import numpy as np

def fit_signed_benefit(features,benefits,keys):
    x=np.asarray(features,float);y=np.asarray(benefits,float)
    if x.ndim!=2 or not len(x) or y.shape!=(len(x),) or len(keys)!=len(x) or not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Aligned finite features, signed benefits and keys required')
    if any(not isinstance(k,str) or not k for k in keys):raise ValueError('Nonempty keys required')
    labels=(y>0).astype(int).tolist();counts=Counter(zip(keys,labels));unique=set(keys)
    if any((k,c) not in counts for k in unique for c in [0,1]):raise ValueError('Both sign classes required per training key')
    w=np.array([len(x)/(len(unique)*2*counts[k,c]) for k,c in zip(keys,labels)])
    mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean);std=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(std==0,1.,std);z=(x-mean)/scale
    intercept=float(np.average(y,weights=w));a=z.T@(w[:,None]*z)+np.eye(x.shape[1]);rhs=z.T@(w*(y-intercept));coefficient=np.linalg.solve(a,rhs)
    return dict(schema_version='truehue_experimental_signed_rgb_benefit_ridge_v1',mean=mean.tolist(),scale=scale.tolist(),coefficient=coefficient.tolist(),intercept=intercept,weights=w.tolist(),alpha=1.,training_keys=sorted(unique),fitting_rows=len(x),positive_action='apply_frozen_split_controls',nonpositive_action='unchanged')
def signed_benefit_decision(payload,features):
    x=np.asarray(features,float)
    if x.shape!=(len(payload['mean']),) or not np.isfinite(x).all():raise ValueError('Exact finite feature vector required')
    gain=float(np.dot((x-payload['mean'])/payload['scale'],payload['coefficient'])+payload['intercept'])
    if not np.isfinite(gain):raise ValueError('Nonfinite expected benefit')
    return dict(predicted_rgb_mae_gain=gain,apply_correction=gain>0)
