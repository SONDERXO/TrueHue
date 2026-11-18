"""Frozen generated rehearsal or single real matched capacity comparison."""
from pathlib import Path
import sys
import json
import hashlib
import platform
import importlib.metadata
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.evaluation import affine_capacity_comparison as comparison
from src.evaluation import affine_capacity_verification as independent
from src.model_training import affine_prepower_targets as target

IDS=['54632','39568','29617','16061','52445','32685','53146','48879','49131','59807','46795']
CODE=['src/evaluation/affine_capacity_comparison.py','src/evaluation/affine_capacity_verification.py',
 'src/model_training/affine_prepower_targets.py','src/evaluation/affine_prepower_scalar.py',
 'src/evaluation/directional_recoverability.py','src/evaluation/directional_recoverability_scalar.py',
 'scripts/run_affine_capacity_comparison.py','scripts/verify_affine_capacity_comparison.py',
 'tests/test_affine_capacity_comparison.py','tests/test_affine_prepower_targets.py',
 'docs/affine-prepower-ffhq-capacity-comparison-protocol-2026-11-14.md']


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def versions():return dict(Python=platform.python_version(),**{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-image','opencv-python']})


def main():
    if sys.argv[1:]==['--generated-workflow-qa']:generated=True
    elif sys.argv[1:]==['--execute-fixed-real-comparison']:generated=False
    else:raise SystemExit('Use --generated-workflow-qa or --execute-fixed-real-comparison')
    name='affine_capacity_comparison_engineering_v1' if generated else 'affine_capacity_comparison_v1'
    out=ROOT/'outputs'/name
    if out.exists():raise FileExistsError('Preserve prior/partial comparison')
    bindings={p:sha(ROOT/p) for p in CODE}
    fitter_qa=ROOT/'outputs/affine_prepower_target_engineering_v1/verification_PRIVATE.json'
    q=read(fitter_qa);assert q['passed']
    for p,h in q['input_sha256'].items():assert sha(ROOT/p)==h
    bindings[str(fitter_qa.relative_to(ROOT))]=sha(fitter_qa)
    if generated:
        base=ROOT/'outputs/directional_recoverability_engineering_v1';relative='generated_run'
        ids=[f'generated_{i:02}' for i in range(11)]
    else:
        qa_path=ROOT/'outputs/affine_capacity_comparison_engineering_v1/verification_PRIVATE.json'
        qa=read(qa_path);assert qa['passed'] and qa['generated_fixture'] and qa['records']==66
        assert qa['actual_local_solver_calls']==55
        for p,h in qa['input_sha256'].items():assert sha(ROOT/p)==h
        for p,h in qa['artifact_sha256'].items():assert sha(qa_path.parent/p)==h
        assert qa['versions']==versions()
        bindings[str(qa_path.relative_to(ROOT))]=sha(qa_path)
        base=ROOT/'outputs/ffhq_directional_recoverability_v1';relative='cases';ids=IDS
        assert read(base/'assessment_PRIVATE.json')['verification_sha256']==sha(base/'verification_PRIVATE.json')
    baseline_verification=read(base/'verification_PRIVATE.json');assert baseline_verification['passed']
    bindings[str((base/'verification_PRIVATE.json').relative_to(ROOT))]=sha(base/'verification_PRIVATE.json')
    out.mkdir()
    write(out/'execution_plan_PRIVATE.json',dict(generated_fixture=generated,source_ids=ids,
        baseline_root=str(base),relative_run=relative,input_sha256=bindings,versions=versions(),
        planned_cases=66,maximum_local_solver_calls=55,baseline_fits=0,tree_fits=0,
        controls=target.NAMES,lower=target.LOWER.tolist(),upper=target.UPPER.tolist()))
    calls=[];original=target.least_squares
    def counted(fun,start,**kw):
        assert len(calls)<55
        np.testing.assert_array_equal(start,[1.,1.,1.,1.,0.])
        np.testing.assert_array_equal(kw['bounds'],[target.LOWER,target.UPPER])
        assert kw['method']=='trf' and kw['loss']=='linear' and kw['max_nfev']==500
        assert kw['ftol']==kw['xtol']==kw['gtol']==1e-10
        calls.append(True)
        write(out/'solver_accounting_PRIVATE.json',dict(local_solver_calls_started=len(calls),maximum=55,baseline_fits=0,tree_fits=0))
        print(f'Five-control local fit {len(calls)}/55',flush=True)
        return original(fun,start,**kw)
    try:
        cases=comparison.load_baseline(base,relative,baseline_verification['artifact_sha256'],ids,generated_fixture=generated)
        target.least_squares=counted
        records=comparison.execute(cases,out/'candidate')
        assert len(calls)<=55 and len(records)==66
        write(out/'execution_complete_PRIVATE.json',dict(generated_fixture=generated,records=66,
            actual_local_solver_calls=len(calls),new_baseline_fits=0,tree_fits=0,model_ready=False))
        assert all(sha(ROOT/p)==h for p,h in bindings.items())
        for p,h in baseline_verification['artifact_sha256'].items():assert sha(base/p)==h
        if generated:
            for case,record in zip(cases,records):
                folder=out/'candidate'/case['source_id']
                with np.load(folder/(case['role']+'.npz'),allow_pickle=False) as pack:
                    output=pack['output'] if 'output' in pack.files else None
                assert independent.verify_case(case,record,output)
            assert independent.verify_summary(records,read(out/'candidate/summary.json'))
            assert len(calls)==55
            write(out/'verification_PRIVATE.json',dict(passed=True,generated_fixture=True,records=66,
                actual_local_solver_calls=55,baseline_fits=0,tree_fits=0,independent_case_checks=66,
                independent_frozen_gate_replay=True,input_sha256=bindings,versions=versions(),
                artifact_sha256={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}))
            print('PASS: generated66matched cases/55candidate fits/0baseline fits; independent replay complete.',flush=True)
        else:print('Real comparison complete; independent verification pending.',flush=True)
    except Exception as error:
        write(out/'failure_PRIVATE.json',dict(status='failed_preserved',error_type=type(error).__name__,error=str(error),local_solver_calls=len(calls)))
        raise
    finally:target.least_squares=original


if __name__=='__main__':main()
