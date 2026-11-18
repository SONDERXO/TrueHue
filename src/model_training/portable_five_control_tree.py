"""Isolated stdlib-only five-control research tree; no active runtime modification."""
from copy import deepcopy
import math
import struct

SCHEMA='truehue_five_control_tree_research_v1'
TARGETS=['gamma','red_gain','blue_gain','input_scale','input_offset']
LOWER=[.25,.25,.25,.5,-.3]
UPPER=[4.,4.,4.,2.,.3]


def finite(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):
        raise ValueError('Finite numeric value required')
    return float(v)


def f32(v):
    try:result=struct.unpack('!f',struct.pack('!f',finite(v)))[0]
    except (OverflowError,struct.error) as error:raise ValueError('Float32 overflow') from error
    if not math.isfinite(result):raise ValueError('Float32 overflow')
    return result


def controls(p):
    if not isinstance(p,list) or len(p)!=5:raise ValueError('Five controls required')
    values=[finite(v) for v in p]
    if any(v<=0 for v in values[:4]) or any(v<lo-1e-12 or v>hi+1e-12 for v,lo,hi in zip(values,LOWER,UPPER)):
        raise ValueError('Positive gamma/gains/scale and finite bounded signed offset required')
    return values


class FiveControlTree:
    def __init__(self,payload):
        if payload.get('schema_version')!=SCHEMA or payload.get('target_names')!=TARGETS:
            raise ValueError('Explicit five-control research schema required')
        if payload.get('input_dtype')!='float32' or payload.get('comparison')!='<=' or payload.get('threshold_dtype')!='float64':
            raise ValueError('Fixed routing precision required')
        self.names=payload.get('feature_names')
        if not isinstance(self.names,list) or not self.names or len(set(self.names))!=len(self.names) or any(not isinstance(n,str) or not n for n in self.names):
            raise ValueError('Unique feature schema required')
        self.names=tuple(self.names);self.nodes=deepcopy(payload.get('nodes'))
        if payload.get('root')!=0 or not isinstance(self.nodes,list) or not self.nodes:
            raise ValueError('Tree rooted at0 required')
        seen=set();stack=[(0,0)]
        while stack:
            i,depth=stack.pop()
            if type(i) is not int or i<0 or i>=len(self.nodes) or i in seen or depth>4:
                raise ValueError('Invalid/cyclic/shared/deep tree')
            seen.add(i);node=self.nodes[i]
            if node.get('kind')=='leaf':node['values']=controls(node.get('values'))
            elif node.get('kind')=='split':
                j=node.get('feature')
                if type(j) is not int or not 0<=j<len(self.names):raise ValueError('Invalid feature')
                node['threshold']=finite(node.get('threshold'))
                stack.extend([(node.get('left'),depth+1),(node.get('right'),depth+1)])
            else:raise ValueError('Unknown node')
        if len(seen)!=len(self.nodes):raise ValueError('Unreachable nodes')

    def leaf_id(self,features):
        if len(features)!=len(self.names):raise ValueError('Feature width mismatch')
        x=[f32(v) for v in features];i=0
        while self.nodes[i]['kind']=='split':
            n=self.nodes[i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        return i

    def predict_one(self,x):return list(self.nodes[self.leaf_id(x)]['values'])
    def predict(self,rows):return [self.predict_one(x) for x in rows]


def export(model,names,provenance):
    if model.n_outputs_!=5 or model.n_features_in_!=len(names):raise ValueError('Model/schema mismatch')
    nodes=[];t=model.tree_
    for i in range(t.node_count):
        left,right=int(t.children_left[i]),int(t.children_right[i])
        if left==right:
            if left!=-1 or t.value[i].shape!=(5,1):raise ValueError('Invalid regression leaf')
            nodes.append(dict(kind='leaf',values=[float(v[0]) for v in t.value[i]]))
        else:nodes.append(dict(kind='split',feature=int(t.feature[i]),threshold=float(t.threshold[i]),left=left,right=right))
    result=dict(schema_version=SCHEMA,feature_names=list(names),target_names=TARGETS,
        input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,nodes=nodes,
        provenance=deepcopy(provenance))
    FiveControlTree(result)
    return result
