"""Separate exposure and paired colour trees; experimental three-control output."""
from copy import deepcopy
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import export_tree,PortableTree
from src.data_preparation.controlled_training_table import TARGETS

HEADS={'gamma':(0,),'gains':(1,2)}


def fit_split_predictors(features,targets,names):
    x=np.asarray(features,float);y=np.asarray(targets,float);names=list(names)
    if x.ndim!=2 or not len(x) or x.shape[1]!=len(names) or len(set(names))!=len(names) or y.shape!=(len(x),3):raise ValueError('Valid full feature/three-target matrix required')
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(y<=0):raise ValueError('Finite features/positive targets required')
    artifacts={};models={}
    for head,columns in HEADS.items():
        values=y[:,columns];center=values.mean(axis=0);std=values.std(axis=0);scale=np.where(std==0,1.,std)
        model=DecisionTreeRegressor(**SETTINGS).fit(x,(values-center)/scale);raw=deepcopy(model);leafids=model.apply(x)
        for leaf in set(leafids):raw.tree_.value[leaf,:,0]=values[leafids==leaf].mean(axis=0)
        meta=dict(mean=center.tolist(),population_std=std.tolist(),scale=scale.tolist(),constant_axes=(std==0).tolist(),fitting_rows=len(x))
        payload=export_tree(raw,names,[TARGETS[i] for i in columns],dict(experimental=True,split_head=head,normalization=meta))
        expected=np.asarray(model.predict(x)).reshape(len(x),len(columns))*scale+center
        np.testing.assert_allclose(PortableTree(payload).predict(x),expected,atol=1e-12,rtol=0)
        artifacts[head]=dict(tree=payload,normalization=meta);models[head]=model
    return dict(schema_version='truehue_split_control_candidate_v1',feature_names=names,target_names=list(TARGETS),heads=artifacts),models


def predict_split(payload,features):
    if payload.get('schema_version')!='truehue_split_control_candidate_v1' or payload.get('target_names')!=list(TARGETS) or set(payload.get('heads',{}))!=set(HEADS):raise ValueError('Exact split-control schema required')
    outputs=[]
    for head,columns in HEADS.items():
        tree=PortableTree(payload['heads'][head]['tree'])
        if tree.feature_names!=tuple(payload['feature_names']) or tree.target_names!=tuple(TARGETS[i] for i in columns):raise ValueError('Head feature/target order mismatch')
        outputs.extend(tree.predict_one(features))
    return outputs
