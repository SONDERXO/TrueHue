"""Isolated gamma restriction: freeze gains; omit only two scene chroma ratios."""
from copy import deepcopy
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,export_tree
EXCLUDED=('scene_log_r_over_g','scene_log_b_over_g')
def fit_restricted_gamma(base,features,targets):
    names=base['feature_names'];x=np.asarray(features,float);y=np.asarray(targets,float)
    if x.ndim!=2 or x.shape[1]!=len(names) or y.shape!=(len(x),3) or not len(x) or not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(y<=0):raise ValueError('Aligned finite features and positive three-control targets required')
    if not all(n in names for n in EXCLUDED):raise ValueError('Both excluded scene features required')
    x=x.copy();excluded=[names.index(n) for n in EXCLUDED];x[:,excluded]=0
    values=y[:,[0]];mean=values.mean(axis=0);std=values.std(axis=0);scale=np.where(std==0,1.,std)
    fitted=DecisionTreeRegressor(**SETTINGS).fit(x,(values-mean)/scale);raw=deepcopy(fitted);leaves=fitted.apply(x)
    for leaf in set(leaves.tolist()):raw.tree_.value[leaf,:,0]=values[leaves==leaf].mean(axis=0)
    prior=base['heads']['gamma'];tree=export_tree(raw,names,prior['tree']['target_names'],dict(experimental=True,excluded_gamma_features=list(EXCLUDED),constant_zero_fitting_columns=True))
    assert all(n['feature'] not in excluded for n in tree['nodes'] if n['kind']=='split')
    np.testing.assert_allclose(np.array(PortableTree(tree).predict(features)),np.asarray(fitted.predict(x)).reshape(-1,1)*scale+mean,atol=1e-12,rtol=0)
    payload=deepcopy(base);payload['heads']['gamma']=dict(tree=tree,normalization=dict(mean=mean.tolist(),population_std=std.tolist(),scale=scale.tolist(),constant_axes=(std==0).tolist(),fitting_rows=len(x)),excluded_features=list(EXCLUDED))
    assert payload['heads']['gains']==base['heads']['gains'];return payload
