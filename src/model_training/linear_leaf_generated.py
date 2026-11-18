"""Fixed ridge leaf solve and supplied-topology fitting; no real-data IO."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
from .portable_linear_leaf_tree import LinearLeafTree,SCHEMA,TARGETS,f32,number
LAMBDA=.01

def solve_leaf(x,y):
    if not x or len(x)!=len(y):raise ValueError('Populated matching leaf records required')
    if any(len(r)!=281 for r in x) or any(len(r)!=3 for r in y):raise ValueError('Fixed281input/3target widths required')
    xx=np.asarray([[f32(v) for v in r] for r in x],dtype=float)[:,[5,6]]
    yy=np.asarray([[number(v) for v in r] for r in y],dtype=float)
    if np.any(yy<=0):raise ValueError('Positive targets required')
    mu=xx.mean(axis=0);scale=xx.std(axis=0,ddof=0);scale[scale==0]=1.
    z=(xx-mu)/scale;intercept=yy.mean(axis=0);centered=yy-intercept
    matrix=z.T@z/len(x)+LAMBDA*np.eye(2);rhs=z.T@centered/len(x)
    slopes=np.linalg.solve(matrix,rhs);raw=slopes/scale[:,None];bias=intercept-mu@raw
    coefficients=np.column_stack([bias,raw.T]).tolist()
    if not np.isfinite(coefficients).all():raise ValueError('Nonfinite fitted coefficients')
    return coefficients,dict(n=len(x),means=mu.tolist(),scales=scale.tolist(),target_means=intercept.tolist(),matrix=matrix.tolist(),rhs=rhs.tolist(),standardized_slopes=slopes.tolist(),lambda_fixed=LAMBDA)

def fit_supplied_tree(topology,rows,names):
    payload=dict(schema_version=SCHEMA,feature_names=list(names),target_names=TARGETS.copy(),leaf_feature_indices=[5,6],input_dtype='float32',coefficient_dtype='float64',comparison='<=',root=0,nodes=deepcopy(topology))
    for n in payload['nodes']:
        if n.get('kind')=='linear_leaf':n['coefficients']=[[1.,0.,0.] for _ in range(3)]
    router=LinearLeafTree(payload);members={i:[] for i,n in enumerate(payload['nodes']) if n['kind']=='linear_leaf'}
    if not rows:raise ValueError('Training rows required')
    for r in rows:
        if r.get('generated_fixture') is not True:raise ValueError('Generated-only fitter refuses scientific records')
        members[router.leaf_id(r['x'])].append(r)
    statistics={}
    for i,rs in members.items():
        coefficients,stats=solve_leaf([r['x'] for r in rs],[r['y'] for r in rs]);payload['nodes'][i]['coefficients']=coefficients;statistics[str(i)]=stats
    model=LinearLeafTree(payload);predictions=[model.predict_one(r['x']) for r in rows]
    return payload,dict(leaf_statistics=statistics,predictions=predictions,leaves=[model.leaf_id(r['x']) for r in rows],generated_fixture_only=True)

def run_generated_once(out,topology,rows,names):
    out=Path(out);out.mkdir()
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    try:
        write('generated_inputs.json',dict(topology=topology,rows=rows,feature_names=names))
        tree,replay=fit_supplied_tree(topology,rows,names)
        write('candidate.json',tree);write('replay.json',replay);write('status.json',dict(status='GENERATED_FIT_COMPLETE',real_data_used=False))
        return tree,replay
    except BaseException as error:
        write('status.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error),real_data_used=False));raise
