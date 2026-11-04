"""Versioned decision-tree JSON and standard-library-only prediction.

The runtime evaluator imports neither sklearn nor numpy. Inputs are rounded to
IEEE754 float32 before comparisons against exported float64 thresholds.
"""
from copy import deepcopy
import math
from numbers import Real
import struct

SCHEMA='truehue_regression_tree_v1'

def _integer(value):return isinstance(value,int) and not isinstance(value,bool)

def _finite(value):
    if isinstance(value,bool) or not isinstance(value,Real):raise ValueError('Finite numeric values required')
    try:result=float(value)
    except (OverflowError,ValueError) as error:raise ValueError('Finite numeric values required') from error
    if not math.isfinite(result):raise ValueError('Finite numeric values required')
    return result

def float32(value):
    value=_finite(value)
    try:rounded=struct.unpack('!f',struct.pack('!f',value))[0]
    except (OverflowError,struct.error) as error:raise ValueError('Input overflows float32') from error
    if not math.isfinite(rounded):raise ValueError('Input overflows float32')
    return rounded

class PortableTree:
    """Validated immutable-copy evaluator for exported multi-output regression."""
    def __init__(self,payload):
        if not isinstance(payload,dict) or payload.get('schema_version')!=SCHEMA:raise ValueError('Unsupported tree schema')
        if payload.get('input_dtype')!='float32' or payload.get('threshold_dtype')!='float64' or payload.get('comparison')!='<=':
            raise ValueError('Unsupported numeric routing contract')
        self.feature_names=self._names(payload.get('feature_names'))
        self.target_names=self._names(payload.get('target_names'))
        self.n_features_in_=len(self.feature_names)
        nodes=deepcopy(payload.get('nodes'));root=payload.get('root')
        if not isinstance(nodes,list) or not nodes or not _integer(root) or root!=0:raise ValueError('Nonempty tree rooted at0 required')
        pending=[0];seen=set()
        while pending:
            index=pending.pop()
            if not _integer(index) or not 0<=index<len(nodes) or index in seen:raise ValueError('Invalid/cyclic/shared-child tree graph')
            seen.add(index);node=nodes[index]
            if not isinstance(node,dict):raise ValueError('Invalid tree node')
            if node.get('kind')=='leaf':
                values=node.get('values')
                if not isinstance(values,list) or len(values)!=len(self.target_names):raise ValueError('Leaf target width mismatch')
                node['values']=[_finite(v) for v in values]
                if any(v<=0 for v in node['values']):raise ValueError('Correction targets must be positive')
            elif node.get('kind')=='split':
                feature=node.get('feature')
                if not _integer(feature) or not 0<=feature<self.n_features_in_:raise ValueError('Invalid split feature')
                node['threshold']=_finite(node.get('threshold'))
                pending.extend([node.get('left'),node.get('right')])
            else:raise ValueError('Unknown node kind')
        if len(seen)!=len(nodes):raise ValueError('Unreachable tree nodes')
        self._nodes=nodes

    @staticmethod
    def _names(names):
        if not isinstance(names,list) or not names or any(not isinstance(n,str) or not n.strip() for n in names) or len(set(names))!=len(names):
            raise ValueError('Nonempty unique feature/target names required')
        return tuple(names)

    def leaf_id(self,features):
        if isinstance(features,dict):
            if set(features)!=set(self.feature_names):raise ValueError('Named features must exactly match schema')
            features=[features[n] for n in self.feature_names]
        try:
            if len(features)!=self.n_features_in_:raise ValueError('Feature width mismatch')
            values=[float32(v) for v in features]
        except TypeError as error:raise ValueError('One finite feature vector required') from error
        index=0
        while self._nodes[index]['kind']=='split':
            node=self._nodes[index];index=node['left'] if values[node['feature']]<=node['threshold'] else node['right']
        return index

    def predict_one(self,features):return list(self._nodes[self.leaf_id(features)]['values'])
    def predict(self,rows):return [self.predict_one(row) for row in rows]

def export_tree(model,feature_names,target_names,provenance):
    """Export an already fitted sklearn-style tree without fitting or loading it."""
    estimator_type=getattr(model,'_estimator_type',None)
    if estimator_type is None and callable(getattr(model,'__sklearn_tags__',None)):
        estimator_type=model.__sklearn_tags__().estimator_type
    if estimator_type!='regressor':raise ValueError('A regression tree is required')
    names=list(feature_names);targets=list(target_names);tree=model.tree_
    if int(model.n_features_in_)!=len(names) or int(model.n_outputs_)!=len(targets):raise ValueError('Model/schema width mismatch')
    nodes=[]
    for i in range(int(tree.node_count)):
        left,right=int(tree.children_left[i]),int(tree.children_right[i])
        if left==right:
            if left!=-1:raise ValueError('Unexpected leaf child sentinel')
            values=tree.value[i]
            if values.shape!=(len(targets),1):raise ValueError('Only multi-output regression values supported')
            nodes.append(dict(kind='leaf',values=[float(v[0]) for v in values]))
        else:nodes.append(dict(kind='split',feature=int(tree.feature[i]),threshold=float(tree.threshold[i]),left=left,right=right))
    payload=dict(schema_version=SCHEMA,input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=names,target_names=targets,nodes=nodes,provenance=deepcopy(provenance))
    PortableTree(payload)
    return payload
