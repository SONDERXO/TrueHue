"""Fitting-only target normalization; portable leaves remain ordinary raw parameters."""
from copy import deepcopy
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import export_tree
from src.data_preparation.controlled_training_table import TARGETS


def fit_target_scaled_tree(features,targets,feature_names,provenance=None):
    x=np.asarray(features,float);y=np.asarray(targets,float);names=list(feature_names)
    if x.ndim!=2 or not len(x) or x.shape[1]!=len(names) or len(set(names))!=len(names):raise ValueError('Nonempty features and ordered unique names required')
    if y.shape!=(len(x),3) or not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(y<=0):raise ValueError('Finite features and positive three-output targets required')
    center=y.mean(axis=0);std=y.std(axis=0,ddof=0)
    if not np.isfinite(center).all() or not np.isfinite(std).all():raise ValueError('Finite fitting target statistics required')
    scale=np.where(std==0,1.,std);normalized=(y-center)/scale
    model=DecisionTreeRegressor(**SETTINGS).fit(x,normalized)
    restored=deepcopy(model);restored.tree_.value[:]=restored.tree_.value*scale[:,None]+center[:,None]
    leaves=model.apply(x)
    for leaf in set(leaves):restored.tree_.value[leaf,:,0]=y[leaves==leaf].mean(axis=0)
    metadata=dict(fitting_target_mean=center.tolist(),fitting_population_std=std.tolist(),applied_scale=scale.tolist(),
        constant_axes=(std==0).tolist(),fitting_rows=len(x),objective='MSE after fitting-only per-target standardization',source=provenance or {})
    payload=export_tree(restored,names,TARGETS,dict(experimental=True,normalization=metadata))
    return payload,model,metadata
