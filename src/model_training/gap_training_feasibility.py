"""Fixed fitting-only 22-input runner core; no dataset or image IO at import."""
from pathlib import Path
import json
import math
import struct
import time
import platform
import numpy as np
import sklearn
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree,export_tree

SETTINGS=dict(criterion='squared_error',splitter='best',max_depth=4,random_state=42,
    min_samples_leaf=1,min_samples_split=2,min_weight_fraction_leaf=0.,max_features=None,
    max_leaf_nodes=None,min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
TARGETS=['gamma','red_gain','blue_gain']

def f32(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('Finite numeric feature required')
    try:value=struct.unpack('!f',struct.pack('!f',value))[0]
    except (OverflowError,struct.error) as error:raise ValueError('Feature overflows float32') from error
    if not math.isfinite(value):raise ValueError('Feature overflows float32')
    return value

def join_inputs(plan,records,audited):
    roster=plan['fitting_records'];cases=[r['case_id'] for r in roster]
    if len(cases)!=len(set(cases)) or set(records)!=set(cases):raise ValueError('Exact fitting roster required')
    newnames=plan['new_feature_names'];names=plan['feature_names']
    if len(names)!=22 or len(newnames)!=6 or names[16:]!=newnames or len(set(names))!=22:
        raise ValueError('Frozen 16+6 feature order required')
    wanted=set(cases);joined={}
    for item in audited:
        # Ignore all other exposed cases BEFORE inspecting their features.
        case=item['case_id']
        if case not in wanted:continue
        if case in joined:raise ValueError('Duplicate fitting gap record')
        if item.get('generated_fixture') is not False:raise ValueError('Generated or unqualified feature record')
        if list(item['features'])!=newnames:raise ValueError('Gap feature order changed')
        joined[case]=item
    if set(joined)!=wanted:raise ValueError('Missing fitting gap record')
    snapshot=[]
    for binding in roster:
        case=binding['case_id'];old=records[case];gap=joined[case]
        if (old['case_id']!=case or old['status']!='available' or old.get('generated_fixture') is not False or
            old['publisher_group']!=binding['source'] or old['publisher_group']==plan['excluded_group'] or
            gap['source']!=binding['source'] or gap['role']!=binding['role'] or
            old['experimental_role']!=binding['role'] or '29863' in case):
            raise ValueError('Source/role/availability mismatch')
        values=old['input_vector_float32']
        if len(values)!=16 or any(f32(v)!=v for v in values):raise ValueError('Old 16 float32 values must remain exact')
        extra=[f32(gap['features'][n]) for n in newnames]
        if any(v<0 or v>1 for v in extra):raise ValueError('Gap fractions must lie in [0,1]')
        y=old['nominal_controls']
        if len(y)!=3 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in y):
            raise ValueError('Three finite positive targets required')
        snapshot.append(dict(case_id=case,source=binding['source'],role=binding['role'],x=list(values)+extra,y=list(y)))
    return snapshot

def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def run_once(out,snapshot,names,baseline,receipt,*,factory=DecisionTreeRegressor):
    out=Path(out);out.mkdir()  # Preserve complete AND partial attempts.
    write(out/'execution_plan_PRIVATE.json',receipt)
    try:
        if len(names)!=22 or len(set(names))!=22 or not snapshot:raise ValueError('Nonempty 22-input fit required')
        parent=PortableTree(baseline)
        if list(parent.feature_names)!=names[:16] or list(parent.target_names)!=TARGETS:raise ValueError('Saved comparator schema mismatch')
        for r in snapshot:
            if len(r['x'])!=22 or len(r['y'])!=3:raise ValueError('Invalid fitting dimensions')
            if any(f32(v)!=v for v in r['x']):raise ValueError('Fitting inputs must already be float32')
            if any(isinstance(v,bool) or not math.isfinite(v) or v<=0 for v in r['y']):raise ValueError('Invalid targets')
        x=np.asarray([r['x'] for r in snapshot],dtype=np.float32);y=np.asarray([r['y'] for r in snapshot],dtype=float)
        write(out/'fitting_inputs_PRIVATE.json',snapshot);write(out/'baseline_SAVED_PRIVATE.json',baseline)
        model=factory(**SETTINGS)
        start=time.monotonic();model.fit(x,y)  # Exactly one fit call; no retry.
        elapsed=time.monotonic()-start
        payload=export_tree(model,names,TARGETS,dict(candidate='histogram_gap_22input_fitting_only_v1',runtime_adopted=False))
        portable=PortableTree(json.loads(json.dumps(payload)))
        predictions=model.predict(x).tolist();leaf_ids=model.apply(x).tolist()
        if portable.predict(x)!=predictions or [portable.leaf_id(r) for r in x.tolist()]!=leaf_ids:
            raise ValueError('Sklearn/portable export parity failed')
        write(out/'candidate_PRIVATE.json',payload)
        write(out/'training_replay_PRIVATE.json',dict(sklearn_predictions=predictions,sklearn_leaf_ids=leaf_ids,
            saved_parent_predictions=parent.predict([r[:16] for r in x.tolist()]),fit_calls=1,
            elapsed_fit_seconds=elapsed,python_version=platform.python_version(),numpy_version=np.__version__,
            sklearn_version=sklearn.__version__,settings=model.get_params(deep=False),held_predictions=0))
        write(out/'status_PRIVATE.json',dict(status='FITTED_PENDING_INDEPENDENT_VERIFICATION',fit_calls=1))
    except BaseException as error:
        write(out/'status_PRIVATE.json',dict(status='FAILED_PRESERVED_NO_RETRY',error_type=type(error).__name__,error=str(error)))
        raise
