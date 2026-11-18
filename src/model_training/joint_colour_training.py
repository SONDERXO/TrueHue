"""Frozen281input fitting-only runner; no dataset IO or fits at import."""
from pathlib import Path
from copy import deepcopy
import json,math,time
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from .gap_training_feasibility import SETTINGS,TARGETS,f32
from .joint_log_colour import NAMES
from .portable_tree import PortableTree,export_tree

def join(plan,base_rows,audited):
    names=plan['feature_names'];roster=plan['fitting_records']
    if len(names)!=281 or len(set(names))!=281 or names[22:]!=list(NAMES):raise ValueError('Fixed22+259schema required')
    cases=[r['case_id'] for r in roster]
    if not cases or len(set(cases))!=len(cases):raise ValueError('Unique fitting roster required')
    base={r['case_id']:r for r in base_rows}
    if len(base)!=len(base_rows) or set(base)!=set(cases):raise ValueError('Exact baseline fitting cases required')
    selected={}
    for a in audited:
        case=a['case_id']
        if case not in base:continue  # Ignore held/other metadata BEFORE feature access.
        if case in selected:raise ValueError('Duplicate fitting feature record')
        selected[case]=a
    if set(selected)!=set(cases):raise ValueError('Missing fitting feature record')
    result=[]
    for binding in roster:
        case=binding['case_id'];b=base[case];a=selected[case]
        if (a.get('generated_fixture') is not False or a['source']!=b['source'] or a['role']!=b['role']
            or b['source']!=binding['source'] or b['role']!=binding['role'] or b['source']==plan['excluded_group'] or '29863' in case):
            raise ValueError('Fitting source/role/provenance mismatch')
        if len(b['x'])!=22 or any(f32(v)!=v for v in b['x']) or [f32(v) for v in a['old22']]!=b['x']:
            raise ValueError('Exact float32old22prefix required')
        if len(a['features'])!=259 or type(a['available']) is not bool:raise ValueError('259features and explicit availability required')
        extra=[f32(v) for v in a['features']]
        if any(v<0 or v>1 for v in extra) or extra[0]!=float(a['available']):raise ValueError('Invalid availability/count/histogram bounds')
        if not a['available'] and any(extra):raise ValueError('Unavailable descriptor must have explicit zero payload')
        if len(b['y'])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in b['y']):
            raise ValueError('Three positive raw targets required')
        result.append(dict(case_id=case,source=b['source'],role=b['role'],x=list(b['x'])+extra,y=list(b['y'])))
    return result

def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def run_once(out,rows,names,baseline,receipt,*,factory=DecisionTreeRegressor):
    out=Path(out);out.mkdir()
    write(out/'execution_plan_PRIVATE.json',receipt)
    try:
        original=deepcopy(rows)
        if len(names)!=281 or len(set(names))!=281 or names[22:]!=list(NAMES) or not rows:raise ValueError('Fixed281input fitting rows required')
        parent=PortableTree(baseline)
        if list(parent.feature_names)!=names[:22] or list(parent.target_names)!=TARGETS:raise ValueError('Saved22baseline schema mismatch')
        if len({r['case_id'] for r in rows})!=len(rows):raise ValueError('Duplicate fitting case')
        for row in rows:
            if len(row['x'])!=281 or any(f32(v)!=v for v in row['x']):raise ValueError('281finite float32inputs required')
            if len(row['y'])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in row['y']):raise ValueError('Positive3targets required')
        write(out/'fitting_inputs_PRIVATE.json',rows);write(out/'baseline_SAVED_PRIVATE.json',baseline)
        x=np.asarray([r['x'] for r in rows],dtype=np.float32);y=np.asarray([r['y'] for r in rows],dtype=float)
        model=factory(**SETTINGS);start=time.monotonic();model.fit(x,y)  # One call; no retry or alternative.
        payload=export_tree(model,names,TARGETS,dict(candidate='joint_log_colour_281input_fitting_only_v1',runtime_adopted=False))
        portable=PortableTree(json.loads(json.dumps(payload)))
        predictions=model.predict(x).tolist();leaves=model.apply(x).tolist()
        if portable.predict(x)!=predictions or [portable.leaf_id(r) for r in x.tolist()]!=leaves:raise ValueError('Native/export route mismatch')
        if rows!=original:raise ValueError('Input mutation')
        write(out/'candidate_PRIVATE.json',payload)
        write(out/'training_replay_PRIVATE.json',dict(fit_calls=1,held_predictions=0,settings=model.get_params(deep=False),
            candidate_predictions=predictions,candidate_leaves=leaves,baseline_predictions=parent.predict([r[:22] for r in x.tolist()]),
            elapsed_fit_seconds=time.monotonic()-start))
        write(out/'status_PRIVATE.json',dict(status='FITTED_PENDING_INDEPENDENT_VERIFICATION',fit_calls=1,held_predictions=0))
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
