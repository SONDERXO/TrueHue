"""One fixed key/layer-balanced fitting objective, isolated from default trees."""
from collections import Counter
from copy import deepcopy
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import export_tree
from src.data_preparation.controlled_training_table import TARGETS


def fit_balanced(x,y,names,keys,layers):
    x=np.asarray(x,float);y=np.asarray(y,float)
    if x.ndim!=2 or not len(x) or x.shape[1]!=len(names) or len(set(names))!=len(names) or y.shape!=(len(x),3):raise ValueError('Valid fitting schema required')
    if len(keys)!=len(x) or len(layers)!=len(x) or not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(y<=0):raise ValueError('Valid targets/groups required')
    allowed={'clean','core','composite_stress_design'};unique=set(keys)
    if not unique or any({l for k,l in zip(keys,layers) if k==key}!=allowed for key in unique):raise ValueError('Every key requires all three layers')
    counts=Counter(zip(keys,layers));weights=np.array([1/(len(unique)*3*counts[k,l]) for k,l in zip(keys,layers)])
    center=np.average(y,axis=0,weights=weights);constant=np.ptp(y,axis=0)==0;center=np.where(constant,y[0],center)
    std=np.sqrt(np.average((y-center)**2,axis=0,weights=weights));scale=np.where(std==0,1.,std)
    model=DecisionTreeRegressor(**SETTINGS).fit(x,(y-center)/scale,sample_weight=weights)
    restored=deepcopy(model);leaves=model.apply(x)
    for leaf in set(leaves):restored.tree_.value[leaf,:,0]=np.average(y[leaves==leaf],axis=0,weights=weights[leaves==leaf])
    meta=dict(mean=center.tolist(),population_std=std.tolist(),scale=scale.tolist(),weights=weights.tolist(),
        keys=list(keys),layers=list(layers),fitting_rows=len(x),objective='equal key total; equal clean/core/stress total within key')
    return export_tree(restored,names,TARGETS,dict(experimental=True,normalization=meta)),model,meta
