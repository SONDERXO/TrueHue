"""Fixed, key/class-balanced linear gate, isolated from correction runtime."""
from collections import Counter
import math
import numpy as np
from sklearn.linear_model import LogisticRegression


def fit_gate(features,labels,keys):
    x=np.asarray(features,float);y=np.asarray(labels)
    if x.ndim!=2 or not len(x) or not np.isfinite(x).all() or y.shape!=(len(x),) or len(keys)!=len(x):raise ValueError('Finite matrix and aligned labels/keys required')
    if any(type(v) is not int or v not in (0,1) for v in labels):raise ValueError('Explicit integer binary labels required')
    if any(not isinstance(k,str) or not k for k in keys):raise ValueError('Nonempty group keys required')
    unique=set(keys);counts=Counter(zip(keys,labels))
    if any((k,c) not in counts for k in unique for c in (0,1)):raise ValueError('Both classes required for every fitting key')
    w=np.array([len(x)/(len(unique)*2*counts[k,c]) for k,c in zip(keys,labels)])
    mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean)
    scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(scale==0,1.,scale)
    model=LogisticRegression(C=1.,solver='lbfgs',max_iter=1000,tol=1e-4,random_state=42).fit((x-mean)/scale,y,sample_weight=w)
    if int(model.n_iter_[0])>=1000:raise ValueError('Gate failed convergence guard')
    payload=dict(schema_version='truehue_experimental_linear_correction_gate_v1',mean=mean.tolist(),scale=scale.tolist(),
        coefficient=model.coef_[0].tolist(),intercept=float(model.intercept_[0]),classes=[0,1],
        positive_logit_action='apply_saved_depth3_correction',zero_or_negative_action='unchanged',
        C=1.,iterations=int(model.n_iter_[0]),training_keys=sorted(unique),weights=w.tolist(),fitting_rows=len(x))
    return payload,model


def gate_decision(payload,features):
    x=np.asarray(features,float)
    if x.shape!=(len(payload['mean']),) or not np.isfinite(x).all():raise ValueError('Exact finite gate feature vector required')
    value=float(np.dot((x-payload['mean'])/payload['scale'],payload['coefficient'])+payload['intercept'])
    if not math.isfinite(value):raise ValueError('Nonfinite gate output')
    return dict(logit=value,apply_correction=value>0)
