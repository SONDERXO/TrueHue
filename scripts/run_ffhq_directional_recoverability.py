"""One frozen real reference-aware diagnostic. No tree training or locked source access."""
from pathlib import Path
import sys
import json
import hashlib
import platform
import importlib.metadata
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.evaluation import directional_recoverability as flow
from src.evaluation.directional_recoverability_loading import load_sources
from src.model_training import blended_recovery_targets as targets

OUT = ROOT / 'outputs/ffhq_directional_recoverability_v1'
DESIGN = ROOT / 'outputs/ffhq_directional_recoverability_design_v1/plan_PRIVATE.json'
QA = ROOT / 'outputs/directional_recoverability_engineering_v1/verification_PRIVATE.json'
EXPECTED = {'54632','39568','29617','16061','52445','32685','53146','48879','49131','59807','46795'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check():
    plan = json.loads(DESIGN.read_text(encoding='utf-8'))
    qa = json.loads(QA.read_text(encoding='utf-8'))
    assert qa['passed'] and qa['scope'] == 'generated_engineering_only'
    assert qa['records'] == 66 and qa['actual_generated_local_solver_calls'] == 55
    for name, digest in qa['input_sha256'].items():
        assert sha(ROOT/name) == digest
    for name, digest in qa['artifact_sha256'].items():
        assert sha(QA.parent/name) == digest
    for name, digest in plan['input_sha256'].items():
        assert sha(ROOT/name) == digest
    versions = {'Python': platform.python_version(), **{p: importlib.metadata.version(p)
                for p in ['numpy','scipy','scikit-image','opencv-python']}}
    assert versions == qa['versions'], 'Use the generated-QA dependency versions'
    assert {r['source_id'] for r in plan['source_references']} == EXPECTED
    assert {s['source_id'] for s in plan['support_sources']} == EXPECTED
    assert plan['conditions'] == 66 and plan['maximum_local_target_optimizations'] == 55
    assert len(plan['roster']) == 66
    assert {(r['source_id'],r['role']) for r in plan['roster']} == {(s,r) for s in EXPECTED for r in flow.ROLES}
    assert plan['correction_tree_fits'] == plan['new_user_ratings'] == 0
    assert plan['single_counterfactual_setting'] == dict(gamma=.70,brightness=-35,contrast=8,cyan_red=-10,yellow_blue=10)
    assert not plan['source_tone_assignment']
    assert next(s for s in plan['support_sources'] if s['source_id']=='59807')['selected']['manual_assisted']
    return plan, versions


def main():
    if sys.argv[1:] == ['--check-bindings-only']:
        check()
        print('PASS: frozen roster, QA artifacts, code and dependency bindings; no source image access.')
        return
    if sys.argv[1:] != ['--execute-fixed-real-diagnostic']:
        raise SystemExit('Use --check-bindings-only or --execute-fixed-real-diagnostic')
    if OUT.exists():
        raise FileExistsError('Preserve real attempt; never retry or overwrite')
    plan, versions = check()
    OUT.mkdir()
    bindings = {str(p.relative_to(ROOT)):sha(p) for p in [DESIGN,QA,Path(__file__),
                ROOT/'scripts/verify_ffhq_directional_recoverability.py']}
    flow.write(OUT/'execution_plan_PRIVATE.json', dict(scope='real_exposed_reference_aware_diagnostic',
        plan=plan, input_sha256=bindings, generated_qa_sha256=sha(QA), versions=versions,
        NPZ_access='whole containers hashed, input_rgb8 only decoded; other NPZ keys unread',
        maximum_local_solver_calls=55, correction_tree_fits=0, model_ready=False))
    calls = []
    original = targets.least_squares
    def counted(fun, start, **kwargs):
        if len(calls) >= 55:
            raise RuntimeError('Frozen55-call optimizer budget exhausted')
        np.testing.assert_array_equal(start, [1,1,1])
        np.testing.assert_array_equal(kwargs['bounds'], [[.25]*3,[4.]*3])
        assert kwargs['method']=='trf' and kwargs['loss']=='linear' and kwargs['max_nfev']==500
        assert kwargs['ftol']==kwargs['xtol']==kwargs['gtol']==1e-10
        calls.append(True)
        flow.write(OUT/'solver_accounting_PRIVATE.json', {'actual_local_solver_calls_started':len(calls),
                   'maximum':55,'correction_tree_fits':0})
        print(f'Local target optimization {len(calls)}/55', flush=True)
        return original(fun,start,**kwargs)
    try:
        sources = load_sources(ROOT,plan,generated_fixture=False)
        assert all(s['reference'].shape == (256,256,3) and not s['generated_fixture'] for s in sources)
        flow.write(OUT/'source_array_bindings_PRIVATE.json', [dict(source_id=s['source_id'],
            **{k:flow.array_hash(s[k]) for k in ['reference','alpha','protected']}) for s in sources])
        targets.least_squares = counted
        records = flow.execute_sources(sources,OUT/'cases')
        assert len(records)==66 and len(calls)<=55
        # Recheck original container/support hashes, without decoding them again.
        for r in plan['source_references']:
            assert sha(r['identity_container']) == r['identity_sha256']
        for s in plan['support_sources']:
            selected=s['selected'];folder=ROOT/selected['directory']
            assert sha(folder/selected['receipt'])==selected['receipt_sha256']
            for name,digest in selected['files'].items(): assert sha(folder/name)==digest
        assert all(sha(ROOT/name)==digest for name,digest in bindings.items())
        flow.write(OUT/'execution_complete_PRIVATE.json',dict(status='complete_pending_independent_verification',
            cases=66,sources=11,actual_local_solver_calls=len(calls),tree_fits=0,
            generated_fixture=False,model_ready=False,locked_access=False))
        print('Complete:66real diagnostic records; independent verification pending.',flush=True)
    except Exception as error:
        flow.write(OUT/'execution_failure_PRIVATE.json',dict(status='failed_preserved',
            error_type=type(error).__name__,error=str(error),local_solver_calls=len(calls)))
        raise
    finally:
        targets.least_squares = original


if __name__=='__main__':
    main()
