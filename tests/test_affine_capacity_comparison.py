import copy
import numpy as np
import pytest
from src.evaluation import affine_capacity_comparison as compare
from src.evaluation import affine_capacity_verification as verify
from src.evaluation import directional_recoverability as old


def neutral_cases():
    cases=[]
    for index in range(11):
        image=np.random.default_rng(index).integers(20,230,(4,4,3),dtype=np.uint8)
        alpha=np.ones((4,4));alpha[0,:]=0
        protected=np.zeros((4,4),bool);protected[0,:]=True
        source=dict(source_id=f'generated_{index:02}',reference=image,alpha=alpha,protected=protected,generated_fixture=True)
        record,im,output=old.run_case(source,'identity') # Exact neutral baseline, no baseline fit.
        for role in compare.ROLES:
            baseline=copy.deepcopy(record);baseline['role']=role
            cases.append(dict(source_id=source['source_id'],role=role,generated_fixture=True,
                reference=image.copy(),image=im.copy(),alpha=alpha.copy(),protected=protected.copy(),
                baseline_output=output.copy(),baseline=baseline))
    return cases


def test_exact_witness_candidate_replay_and_immutability():
    case=neutral_cases()[0];before=case['image'].copy()
    record,output=compare.run_case(case)
    assert verify.verify_case(case,record,output)
    assert record['baseline_witness']['RGB8_exact']
    np.testing.assert_array_equal(case['image'],before)


def test_corrupt_saved_output_or_metric_rejected_before_fit():
    case=neutral_cases()[0];case['baseline_output'][1,1,0]+=1
    with pytest.raises(ValueError):compare.run_case(case,fitter=lambda *a,**k:pytest.fail('Must not fit'))
    case=neutral_cases()[0];case['baseline']['regions']['primary']['output']['RGB']=1
    with pytest.raises(ValueError):compare.run_case(case,fitter=lambda *a,**k:pytest.fail('Must not fit'))


def test_hash_barrier_rejects_before_decode(tmp_path,monkeypatch):
    p=tmp_path/'declared.bin';p.write_bytes(b'corrupt')
    monkeypatch.setattr(np,'load',lambda *a,**k:pytest.fail('No decoding before hash barrier'))
    with pytest.raises(ValueError):compare.load_baseline(tmp_path,'cases',{'declared.bin':'0'*64},[str(i) for i in range(11)],generated_fixture=True)


def test_unavailable_no_fallback_and_coverage_failure():
    case=neutral_cases()[0]
    def unavailable(*a,**k):return dict(status='unavailable_probe',parameters=None,generated_fixture=True,model_ready=False)
    record,output=compare.run_case(case,fitter=unavailable)
    assert output is None and record['regions']['primary']['output'] is None
    assert verify.verify_case(case,record,output)
    summary=compare.summarize([record])
    assert summary['status']=='NOT_ADVANCED' and not summary['checks']['coverage']
    assert verify.verify_summary([record],summary)


def test_frozen_gate_regressions_not_pooled_away():
    records=[compare.run_case(c)[0] for c in neutral_cases()]
    summary=compare.summarize(records)
    assert summary['status']=='NOT_ADVANCED' # Exact equality supplies no exposure improvement.
    assert verify.verify_summary(records,summary)
    for r in records:
        if r['role']=='exposure_under':
            r['regions']['primary']['improvement_over_baseline']={'RGB':1.,'DE':1.}
    summary=compare.summarize(records)
    assert summary['status']=='NUMERIC_CAPACITY_ELIGIBLE_ONLY'
    for r in records:
        if r['role']=='colour_only':r['regions']['primary']['improvement_over_baseline']['DE']=-.1
    summary=compare.summarize(records)
    assert summary['status']=='NOT_ADVANCED'
    assert verify.verify_summary(records,summary)


def test_failure_preserved_and_no_overwrite(tmp_path):
    cases=neutral_cases();calls=[]
    def injected(*args,**kwargs):
        calls.append(True)
        if len(calls)==2:raise RuntimeError('injected failure')
        return compare.target.fit_rgb8_target(*args,**kwargs)
    dest=tmp_path/'result'
    with pytest.raises(RuntimeError):compare.execute(cases,dest,fitter=injected)
    assert (dest/'failure.json').exists() and (dest/'generated_00/identity.json').exists()
    with pytest.raises(FileExistsError):compare.execute(cases,dest)


def test_corrupt_summary_detected():
    records=[compare.run_case(c)[0] for c in neutral_cases()]
    summary=compare.summarize(records);summary['status']='NUMERIC_CAPACITY_ELIGIBLE_ONLY'
    with pytest.raises(AssertionError):verify.verify_summary(records,summary)
