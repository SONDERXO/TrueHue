"""Bound actual-record adapter. No scientific IO or work on import."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import json,math,time
from .portable_linear_leaf_tree import LinearLeafTree,SCHEMA,TARGETS,f32
from .linear_leaf_generated import solve_leaf,LAMBDA

ROLES=['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def topology(scaffold):
    return [dict(n) if n['kind']=='split' else dict(kind='linear_leaf') for n in scaffold['nodes']]

def join_actual(plan,records,snapshot,bindings):
    wanted=plan['fitting_cases']
    if len(wanted)!=60 or len(set(wanted))!=60 or len(snapshot)!=60 or [r['case_id'] for r in snapshot]!=wanted:raise ValueError('Exact60 ordered snapshot required')
    bound={r['case_id']:r for r in bindings}
    if len(bindings)!=60 or set(bound)!=set(wanted):raise ValueError('Exact60 source/role/target bindings required')
    selected={}
    for r in records:
        c=r['case_id']
        if c not in wanted:continue
        if c in selected:raise ValueError('Duplicate fitting case')
        selected[c]=r
    if set(selected)!=set(wanted):raise ValueError('Missing fitting case')
    result=[]
    for s in snapshot:
        r=selected[s['case_id']];b=bound[s['case_id']]
        if r.get('generated_fixture') is not False or r.get('status')!='available':raise ValueError('Actual available record required; no generated flag conversion')
        if r['source']!=s['source'] or r['source']!=b['source'] or r['source']==plan['excluded_source'] or r['role']!=s['role'] or r['role']!=b['role']:raise ValueError('Source/role/exclusion mismatch')
        if r['x']!=s['x'] or len(r['x'])!=281 or any(f32(v)!=v for v in r['x']):raise ValueError('Exact canonical281 float32 values required')
        if r['y']!=s['y'] or r['y']!=b['nominal'] or len(r['y'])!=3 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in r['y']):raise ValueError('Exact positive raw targets required')
        result.append(dict(case_id=r['case_id'],source=r['source'],role=r['role'],x=list(r['x']),y=list(r['y']),generated_fixture=False,status='available'))
    if len({r['source'] for r in result})!=10 or Counter(r['role'] for r in result)!={r:10 for r in ROLES}:raise ValueError('Ten sources and ten examples per role required')
    return result

def fit_once(out,plan,rows,scaffold,saved_replay,receipt,*,solver=solve_leaf):
    out=Path(out);out.mkdir();write(out/'execution_PRIVATE.json',receipt);calls=0
    try:
        if LAMBDA!=plan['lambda_fixed'] or plan['leaf_coordinates']!=[5,6] or topology(scaffold)!=plan['topology'] or scaffold['feature_names']!=plan['feature_names']:raise ValueError('Exact fixed scaffold/coordinate/penalty contract required')
        if len(rows)!=60 or [r['case_id'] for r in rows]!=plan['fitting_cases'] or any(r.get('generated_fixture') is not False or r.get('status')!='available' for r in rows):raise ValueError('Actual60row join required')
        payload=dict(schema_version=SCHEMA,feature_names=plan['feature_names'],target_names=TARGETS.copy(),leaf_feature_indices=[5,6],input_dtype='float32',coefficient_dtype='float64',comparison='<=',root=0,nodes=deepcopy(plan['topology']))
        for n in payload['nodes']:
            if n['kind']=='linear_leaf':n['coefficients']=[[1.,0.,0.] for _ in range(3)]
        router=LinearLeafTree(payload);members={i:[] for i,n in enumerate(payload['nodes']) if n['kind']=='linear_leaf'}
        if len(members)!=6 or len(saved_replay['candidate_predictions'])!=60 or len(saved_replay['candidate_leaves'])!=60:raise ValueError('Six leaves and60 saved native predictions required')
        for i,r in enumerate(rows):
            leaf=router.leaf_id(r['x']);members[leaf].append(r)
            if saved_replay['candidate_leaves'][i]!=leaf or saved_replay['candidate_predictions'][i]!=scaffold['nodes'][leaf]['values']:raise ValueError('Saved native baseline binding mismatch')
        write(out/'fitting_inputs_PRIVATE.json',rows);write(out/'baseline_SAVED_PRIVATE.json',saved_replay);statistics={};start=time.monotonic()
        for leaf,rs in members.items():
            if not rs:raise ValueError('Empty scaffold leaf')
            calls+=1;coefficients,stats=solver([r['x'] for r in rs],[r['y'] for r in rs]);payload['nodes'][leaf]['coefficients']=coefficients;statistics[str(leaf)]=stats
            write(out/'leaf_progress_PRIVATE.json',dict(solver_calls=calls,completed_statistics=statistics,nodes=payload['nodes']))
        model=LinearLeafTree(payload);pred=[model.predict_one(r['x']) for r in rows];leaves=[model.leaf_id(r['x']) for r in rows]
        write(out/'candidate_PRIVATE.json',payload);write(out/'replay_PRIVATE.json',dict(solver_calls=calls,branch_fits=0,held_predictions=0,lambda_fixed=LAMBDA,leaf_coordinates=[5,6],leaf_statistics=statistics,predictions=pred,leaves=leaves,elapsed_seconds=time.monotonic()-start))
        write(out/'status_PRIVATE.json',dict(status='FITTED_PENDING_INDEPENDENT_VERIFICATION',solver_calls=calls,branch_fits=0,held_predictions=0))
    except BaseException as error:write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',solver_calls=calls,branch_fits=0,held_predictions=0,error=repr(error)));raise
