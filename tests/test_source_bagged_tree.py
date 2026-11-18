"""Generated-only engineering evidence, never scientific records."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import pytest
from src.model_training.source_bagged_training import fit_ensemble, source_draws, validate_rows, run_once
from src.model_training.source_bagged_verification import verify, mean_predict
from src.model_training.portable_bagged_tree import PortableBaggedTree, SCHEMA

NAMES = ['generated_feature_%d' % i for i in range(22)]


def rows():
    result = []
    for source in range(3):
        for k, role in enumerate(['identity', 'exposure_under', 'exposure_over', 'colour_cool']):
            result.append(dict(case_id=f'GENERATED_{source}_{k}', source=f'GENERATED_{source}', role=role,
                x=[float(source), float(k)]+[0.]*20,
                y=[{1:.7,2:1/.7}.get(k,1.),245/255 if k==3 else 1.,1.]))
    return result


@pytest.fixture(scope='module')
def trained():
    r=rows()
    candidate,replay=fit_ensemble(r,NAMES,'GENERATED_HELD')
    return r,candidate,replay


def test_source_block_bootstrap_and_golden():
    expected=[int.from_bytes(hashlib.sha256(f'42:0:{i}:0'.encode()).digest()[:4],'big')%3 for i in range(3)]
    assert source_draws(3,0)==expected
    assert len(source_draws(10,63))==10
    with pytest.raises(ValueError):source_draws(0,0)
    with pytest.raises(ValueError):source_draws(3,64)


def test_held_exclusion_and_complete_roles():
    with pytest.raises(ValueError):validate_rows(rows(),NAMES,'GENERATED_0')
    with pytest.raises(ValueError):validate_rows(rows()[:-1],NAMES,'HELD')
    r=rows();r[0]['x'][0]=float('nan')
    with pytest.raises(ValueError):validate_rows(r,NAMES,'HELD')


def test_native_roundtrip_scalar_leaf_means_and_nonmutation(trained):
    r,candidate,replay=trained;before=deepcopy(r)
    report=verify(candidate,r,replay,NAMES,'GENERATED_HELD')
    assert report['member_original_fit_routes']==64*12 and report['leaf_mean_checks']>0
    portable=PortableBaggedTree(json.loads(json.dumps(candidate)))
    assert portable.predict([row['x'] for row in r])==replay['mean_predictions']
    assert all(mean_predict(candidate,row['x'])==portable.predict_one(row['x']) for row in r)
    assert before==r


def test_bootstrap_tampering_detected(trained):
    r,candidate,replay=trained;rec=deepcopy(replay)
    rec['members'][0]['occurrence_cases'][0]='GENERATED_HELD'
    with pytest.raises(AssertionError):verify(candidate,r,rec,NAMES,'GENERATED_HELD')


def test_leaf_or_mean_tampering_detected(trained):
    r,candidate,replay=trained
    bad=deepcopy(candidate)
    leaf=next(n for n in bad['members'][0]['nodes'] if n['kind']=='leaf');leaf['values'][0]+=.1
    with pytest.raises(AssertionError):verify(bad,r,replay,NAMES,'GENERATED_HELD')
    rec=deepcopy(replay);rec['mean_predictions'][0][0]+=.01
    with pytest.raises(AssertionError):verify(candidate,r,rec,NAMES,'GENERATED_HELD')


def test_missing_member_and_schema_rejected(trained):
    _,candidate,_=trained
    bad=deepcopy(candidate);bad['members'].pop()
    with pytest.raises(ValueError):PortableBaggedTree(bad)
    bad=deepcopy(candidate);bad['members'][0]['feature_names'][0]='wrong'
    with pytest.raises(ValueError):PortableBaggedTree(bad)
    bad=deepcopy(candidate);bad['aggregation']='median'
    with pytest.raises(ValueError):PortableBaggedTree(bad)


def test_equal_mean_includes_all_members_and_input_float32(trained):
    _,candidate,_=trained;bad=deepcopy(candidate)
    for i,tree in enumerate(bad['members']):
        tree['nodes']=[dict(kind='leaf',values=[.7 if i<32 else 1.3,1.,1.])]
    predictor=PortableBaggedTree(bad)
    assert predictor.predict_one([0.]*22)==[1.,1.,1.]
    for tree in bad['members']:
        tree['nodes']=[dict(kind='split',feature=0,threshold=1.00000003,left=1,right=2),
                       dict(kind='leaf',values=[.7,1.,1.]),dict(kind='leaf',values=[1.3,1.,1.])]
    predictor=PortableBaggedTree(bad)
    assert predictor.predict_one([1.00000004]+[0.]*21)==[.7,1.,1.]
    with pytest.raises(ValueError):predictor.predict_one([False]+[0.]*21)
    with pytest.raises(ValueError):predictor.predict_one([1.]*21)


def test_portable_immutable_copy(trained):
    _,candidate,_=trained;c=deepcopy(candidate);p=PortableBaggedTree(c)
    before=p.predict_one([0.]*22)
    c['members'][0]['nodes'].clear()
    assert p.predict_one([0.]*22)==before


def test_exact_fit_budget_and_no_retry():
    calls=[]
    class Broken:
        def __init__(self,**kwargs):calls.append(kwargs)
        def fit(self,x,y):raise RuntimeError('GENERATED injected failure')
    with pytest.raises(RuntimeError):fit_ensemble(rows(),NAMES,'HELD',factory=Broken)
    assert len(calls)==1


def test_run_refuses_existing_directory(tmp_path):
    destination=tmp_path/'preserve';destination.mkdir();(destination/'marker').write_text('keep')
    with pytest.raises(FileExistsError):run_once(destination,rows(),NAMES,'HELD',{})
    assert (destination/'marker').read_text()=='keep'


def test_runtime_and_scalar_verifier_import_without_numpy_or_sklearn():
    code='''
import builtins
original=builtins.__import__
def guarded(name,*args,**kwargs):
    if name.split('.')[0] in ('numpy','sklearn'):
        raise RuntimeError('forbidden optimizer/runtime dependency')
    return original(name,*args,**kwargs)
builtins.__import__=guarded
import src.model_training.portable_bagged_tree
import src.model_training.source_bagged_verification
'''
    result=subprocess.run([sys.executable,'-c',code],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_comparison_fitting_failure_blocks_all_photo_reads(tmp_path,monkeypatch):
    import scripts.run_source_bagged_development as workflow
    monkeypatch.setattr(workflow,'ROOT',tmp_path)
    monkeypatch.setattr(workflow,'inputs',lambda plan: ({},[]))
    def fail(*args):raise RuntimeError('GENERATED fitting barrier failure')
    monkeypatch.setattr(workflow,'all_fits',fail)
    def forbidden(*args):raise AssertionError('photo support read before fitting barrier')
    monkeypatch.setattr(workflow,'load_supports',forbidden)
    design=tmp_path/'outputs/source_bagged_design_v1';design.mkdir(parents=True)
    (design/'plan_PRIVATE.json').write_text('{}')
    with pytest.raises(RuntimeError,match='barrier failure'):
        workflow.comparison(dict(comparison_output='GENERATED_comparison'))
    status=json.loads((tmp_path/'GENERATED_comparison/status_PRIVATE.json').read_text())
    assert status['status']=='FAILED_PRESERVED_NO_RETRY'
    assert not (tmp_path/'GENERATED_comparison/review_assets').exists()


def test_mutated_first_candidate_blocks_reuse(tmp_path,monkeypatch):
    import scripts.run_source_bagged_development as workflow
    monkeypatch.setattr(workflow,'ROOT',tmp_path)
    design=tmp_path/'outputs/source_bagged_design_v1';design.mkdir(parents=True)
    (design/'plan_PRIVATE.json').write_text('{}')
    first=tmp_path/'GENERATED_first';first.mkdir()
    (first/'candidate_PRIVATE.json').write_text('{}')
    (first/'sealed_PRIVATE.json').write_text(json.dumps(dict(
        plan_sha256=workflow.sha(design/'plan_PRIVATE.json'),candidate_sha256='wrong')))
    out=tmp_path/'GENERATED_comparison';out.mkdir()
    with pytest.raises(AssertionError):workflow.all_fits(out,dict(first_output='GENERATED_first'),{},[])
    assert not (out/'reuse_seal_PRIVATE.json').exists()


def test_real_entrypoints_import_without_fitting(monkeypatch):
    import importlib
    from sklearn.tree import DecisionTreeRegressor
    def forbidden(*args,**kwargs):raise AssertionError('fit during import')
    monkeypatch.setattr(DecisionTreeRegressor,'fit',forbidden)
    for name in ['scripts.prepare_source_bagged_design','scripts.run_source_bagged_development',
                 'scripts.verify_source_bagged_development','scripts.review_source_bagged_development']:
        importlib.reload(importlib.import_module(name))
