"""Experimental control/distortion partitioning with three-parameter leaf outputs."""
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from src.model_training.development_build import SETTINGS
from src.model_training.portable_tree import PortableTree,SCHEMA
from src.data_preparation.controlled_training_table import TARGETS


def fit_control_partition_tree(features,targets,identity_controls,feature_names,provenance=None):
    """Fit label-separating splits; identity in a leaf forces identity output.

    Only fitting arrays enter this function. Distortion-only leaves get their
    fitting target mean. This is not standard squared-error regression fitting.
    """
    x=np.asarray(features,dtype=float);y=np.asarray(targets,dtype=float);controls=np.asarray(identity_controls)
    names=list(feature_names)
    if x.ndim!=2 or not len(x) or x.shape[1]!=len(names) or len(set(names))!=len(names):
        raise ValueError('Nonempty feature matrix and unique ordered names required')
    if y.shape!=(len(x),3) or controls.shape!=(len(x),) or controls.dtype!=bool:
        raise ValueError('Three targets and boolean control flags required for every fitting row')
    if not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(y<=0):raise ValueError('Finite features and positive targets required')
    if not controls.any() or controls.all():raise ValueError('Both fitting controls and distortions required')
    if not np.all(y[controls]==1.):raise ValueError('Fitting identity controls must have exact identity targets')
    classifier=DecisionTreeClassifier(**SETTINGS).fit(x,controls.astype(int))
    tree=classifier.tree_;leaves=classifier.apply(x);nodes=[];audit=[]
    for i in range(tree.node_count):
        if tree.children_left[i]!=-1:
            nodes.append(dict(kind='split',feature=int(tree.feature[i]),threshold=float(tree.threshold[i]),left=int(tree.children_left[i]),right=int(tree.children_right[i])))
        else:
            selected=leaves==i;control_count=int(controls[selected].sum())
            values=[1.,1.,1.] if control_count else np.mean(y[selected],axis=0).tolist()
            nodes.append(dict(kind='leaf',values=values))
            audit.append(dict(leaf=i,fitting_indices=np.flatnonzero(selected).tolist(),identity_members=control_count,parameters=values))
    payload=dict(schema_version=SCHEMA,input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=names,target_names=list(TARGETS),nodes=nodes,
        provenance=dict(experimental=True,training_objective='gini_control_partition_then_conservative_parameter_leaves',
            settings=SETTINGS,source=provenance or {}))
    PortableTree(payload)
    return payload,classifier,audit
