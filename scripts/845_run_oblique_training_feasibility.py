"""Explicit one-shot runner; importing this module never starts an experiment."""
from pathlib import Path
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_tree import PortableTree
from src.model_training.portable_oblique_tree import PortableObliqueTree, from_axis_tree
from src.model_training.oblique_regression_tao import train_oblique

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def check_bindings(root, bindings):
    for name, digest in bindings.items():
        path = (root/name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != digest:
            raise ValueError('Changed or invalid bound input: '+name)

def run_arrays(out, axis, x, y, roles, receipt, *, trainer=train_oblique):
    """Single-run core, also exercised using generated inputs in temporary dirs."""
    out.mkdir()  # Atomic refusal of any prior complete/partial attempt.
    write(out/'execution_plan_PRIVATE.json', receipt)
    try:
        initial = from_axis_tree(axis)
        write(out/'initial_axis_PRIVATE.json', axis)
        write(out/'initial_oblique_PRIVATE.json', initial)
        write(out/'fitting_inputs_PRIVATE.json', dict(x=x,y=y,roles=roles))
        if PortableTree(axis).predict(x) != PortableObliqueTree(initial).predict(x):
            raise ValueError('Initial prediction parity failed')
        write(out/'initial_parity_PRIVATE.json', dict(passed=True,rows=len(x)))
        start = time.monotonic()
        candidate, report = trainer(initial,x,y,max_passes=20,max_proposals=300,max_seconds=60.)
        write(out/'candidate_PRIVATE.json', candidate)
        write(out/'optimization_PRIVATE.json', report)
        write(out/'run_status_PRIVATE.json', dict(status='COMPLETED_PENDING_INDEPENDENT_VERIFICATION',
            trainer_wall_seconds=time.monotonic()-start,fit_calls=1,held_predictions=0,photo_reads=0))
    except BaseException as error:
        write(out/'run_status_PRIVATE.json', dict(status='FAILED_PRESERVED_NO_RETRY',
            error_type=type(error).__name__,error=str(error)))
        raise

def main():
    if sys.argv[1:] != ['--execute-fixed-fitting-only']:
        raise SystemExit('No execution by default. Explicit entry: --execute-fixed-fitting-only')
    design = ROOT/'outputs/oblique_training_feasibility_design_v1'
    plan = read(design/'plan_PRIVATE.json')
    verification = read(design/'verification_PRIVATE.json')
    assert verification['passed'] and sha(design/'plan_PRIVATE.json') == verification['plan_sha256']
    assert sha(design/'initial_schema_conversion_PRIVATE.json') == verification['converted_initial_sha256']
    check_bindings(ROOT,plan['input_sha256'])
    assert plan['caps'] == dict(max_depth=4,max_passes=20,max_proposals=300,max_seconds=60,processes=1,restarts=0)
    out = ROOT/plan['future_run_directory']
    if out.exists():
        raise FileExistsError('Preserve prior attempt; no restart')
    text = (ROOT/plan['initial_tree_source']['path']).read_text(encoding='utf-8').lstrip()
    first,_ = json.JSONDecoder().raw_decode(text[1:].lstrip())
    cases = [r['case_id'] for r in plan['fitting_rows']]
    assert first['definition']['fitting_cases'] == cases
    assert first['definition']['held_publisher_group'] == plan['held_group_excluded']
    axis = first['tree']
    assert from_axis_tree(axis) == read(design/'initial_schema_conversion_PRIVATE.json')
    assert axis['feature_names'] == plan['feature_names'] and axis['target_names'] == plan['target_names']
    x=[];y=[];roles=[]
    for binding in plan['fitting_rows']:
        row=read(ROOT/binding['path'])
        assert row['case_id']==binding['case_id'] and row['status']=='available'
        assert row['publisher_group']==binding['publisher_group'] != plan['held_group_excluded']
        assert row['experimental_role']==binding['role']
        assert len(row['input_vector_float32'])==16 and len(row['nominal_controls'])==3
        x.append(row['input_vector_float32']);y.append(row['nominal_controls']);roles.append(binding['role'])
    assert len(x)==40 and len(set(cases))==40
    receipt=dict(design_sha256=sha(design/'plan_PRIVATE.json'),input_sha256=plan['input_sha256'],
        runner_sha256=sha(Path(__file__)),verifier_sha256=sha(ROOT/'scripts/846_verify_oblique_training_feasibility.py'),
        fitting_cases=cases,held_group_excluded=plan['held_group_excluded'],caps=plan['caps'])
    run_arrays(out,axis,x,y,roles,receipt)
    check_bindings(ROOT,plan['input_sha256'])

if __name__=='__main__':
    main()
