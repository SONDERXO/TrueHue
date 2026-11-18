"""Standalone hard-tree inference with two-coordinate vector affine leaves."""
from copy import deepcopy
import math,struct
SCHEMA='truehue_linear_leaf_tree_v1'
LEAF_INDICES=[5,6]
TARGETS=['gamma','red_gain','blue_gain']

def number(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v):raise ValueError('Finite numeric value required')
    return float(v)

def f32(v):
    try:v=struct.unpack('!f',struct.pack('!f',number(v)))[0]
    except (OverflowError,struct.error) as e:raise ValueError('Float32 overflow') from e
    if not math.isfinite(v):raise ValueError('Float32 overflow')
    return v

class LinearLeafTree:
    def __init__(self,payload):
        p=deepcopy(payload)
        if not isinstance(p,dict) or p.get('schema_version')!=SCHEMA:raise ValueError('Linear-leaf schema required')
        names=p.get('feature_names');nodes=p.get('nodes')
        if not isinstance(names,list) or len(names)!=281 or any(not isinstance(n,str) or not n for n in names) or len(set(names))!=281:raise ValueError('Unique281 feature schema required')
        if names[5:7]!=['scene_log_r_over_g','scene_log_b_over_g'] or p.get('leaf_feature_indices')!=LEAF_INDICES or p.get('target_names')!=TARGETS:raise ValueError('Fixed leaf/target schema required')
        if p.get('input_dtype')!='float32' or p.get('coefficient_dtype')!='float64' or p.get('comparison')!='<=' or type(p.get('root')) is not int or p['root']!=0:raise ValueError('Numeric contract required')
        if not isinstance(nodes,list) or not 1<=len(nodes)<=31:raise ValueError('One bounded tree required')
        pending=[(0,0)];seen=set()
        while pending:
            i,depth=pending.pop()
            if type(i) is not int or not 0<=i<len(nodes) or i in seen or depth>4:raise ValueError('Invalid tree graph')
            seen.add(i);n=nodes[i]
            if not isinstance(n,dict):raise ValueError('Node object required')
            if n.get('kind')=='split':
                j=n.get('feature')
                if type(j) is not int or not 0<=j<281:raise ValueError('Invalid branch feature')
                number(n.get('threshold'));pending.extend([(n.get('left'),depth+1),(n.get('right'),depth+1)])
            elif n.get('kind')=='linear_leaf':
                c=n.get('coefficients')
                if not isinstance(c,list) or len(c)!=3 or any(not isinstance(row,list) or len(row)!=3 for row in c):raise ValueError('Three affine rows required')
                for row in c:
                    for v in row:number(v)
            else:raise ValueError('Unsupported node')
        if len(seen)!=len(nodes):raise ValueError('Unreachable nodes')
        self._payload=p

    def artifact(self):return deepcopy(self._payload)

    def _route(self,row):
        if len(row)!=281:raise ValueError('Exactly281 inputs required')
        x=[f32(v) for v in row];i=0
        while self._payload['nodes'][i]['kind']=='split':
            n=self._payload['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
        return i,x

    def leaf_id(self,row):return self._route(row)[0]

    def predict_one(self,row):
        i,x=self._route(row)
        try:result=[math.fsum([c[0],c[1]*x[5],c[2]*x[6]]) for c in self._payload['nodes'][i]['coefficients']]
        except (OverflowError,ValueError) as e:raise ValueError('Invalid predicted controls') from e
        if any(not math.isfinite(v) or v<=0 for v in result):raise ValueError('Nonpositive or nonfinite predicted control; no rendering')
        return result
