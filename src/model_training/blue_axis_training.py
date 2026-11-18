"""One60row bluecoverage fit; no learned baseline or held inference."""
from pathlib import Path
import math,time
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from .gap_training_feasibility import SETTINGS,TARGETS,f32
from .portable_tree import PortableTree,export_tree
from .blue_axis_preparation import write

def join60(plan,records):
    wanted=plan['first_fitting_cases'];selected={}
    if len(wanted)!=len(set(wanted)) or len(wanted)!=60:raise ValueError('Exact60case roster required')
    binding={r['case_id']:r for r in plan['cases']}
    for r in records:
        c=r['case_id']
        if c not in wanted:continue
        if c in selected:raise ValueError('Duplicatefitcase')
        selected[c]=r
    if set(selected)!=set(wanted):raise ValueError('Missingfitcase')
    rows=[]
    for c in wanted:
        r=selected[c];b=binding[c]
        if r.get('generated_fixture') is not False or r['status']!='available' or r['source']!=b['source'] or r['role']!=b['role'] or r['source']==plan['first_excluded_source']:raise ValueError('Source/role/provenance mismatch')
        if len(r['x'])!=281 or any(f32(v)!=v for v in r['x']):raise ValueError('281finitefloat32 required')
        if r['y']!=b['nominal_controls'] or len(r['y'])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in r['y']):raise ValueError('Exactnominalpositive3targets required')
        rows.append(dict(case_id=c,source=r['source'],role=r['role'],x=list(r['x']),y=list(r['y'])))
    if len({r['source'] for r in rows})!=10:raise ValueError('Tenfittingsources required')
    return rows

def fit_once(out,rows,names,receipt,*,factory=DecisionTreeRegressor):
    out=Path(out);out.mkdir();write(out/'execution_plan_PRIVATE.json',receipt)
    try:
        if len(rows)!=60 or len(names)!=281 or len(set(names))!=281:raise ValueError('Fixed60x281 required')
        if any(len(r['x'])!=281 or any(f32(v)!=v for v in r['x']) or len(r['y'])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in r['y']) for r in rows):raise ValueError('Finite281/positive3 schema required')
        write(out/'fitting_inputs_PRIVATE.json',rows)
        x=np.asarray([r['x'] for r in rows],dtype=np.float32);y=np.asarray([r['y'] for r in rows],dtype=float)
        model=factory(**SETTINGS);start=time.monotonic();model.fit(x,y)
        payload=export_tree(model,names,TARGETS,dict(candidate='blue_axis_60fit_281input_v1',runtime_adopted=False))
        portable=PortableTree(payload);predictions=model.predict(x).tolist();leaves=model.apply(x).tolist()
        if portable.predict(x)!=predictions or [portable.leaf_id(r) for r in x.tolist()]!=leaves:raise ValueError('Exportparity failed')
        write(out/'candidate_PRIVATE.json',payload)
        write(out/'training_replay_PRIVATE.json',dict(fit_calls=1,held_predictions=0,settings=model.get_params(deep=False),candidate_predictions=predictions,candidate_leaves=leaves,elapsed_seconds=time.monotonic()-start))
        write(out/'status_PRIVATE.json',dict(status='FITTED_PENDING_INDEPENDENT_VERIFICATION',fit_calls=1,held_predictions=0))
    except BaseException as error:write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
