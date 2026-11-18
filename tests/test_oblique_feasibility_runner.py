"""Generated-only orchestration checks; never invoke either script's main."""
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
runner=load('845_run_oblique_training_feasibility.py')
verifier=load('846_verify_oblique_training_feasibility.py')

def axis():
    return dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',
        threshold_dtype='float64',comparison='<=',root=0,feature_names=['x'],
        target_names=['gamma','red_gain','blue_gain'],nodes=[
            dict(kind='split',feature=0,threshold=0.,left=1,right=2),
            dict(kind='leaf',values=[1.,1.,1.]),dict(kind='leaf',values=[1.4,1.,1.])])

def test_generated_roundtrip_and_refuse_restart(tmp_path):
    out=tmp_path/'attempt';x=[[-2.],[-1.],[1.],[2.]]
    y=[[1.,1.,1.],[1.,1.,1.],[1.4,1.,1.],[1.4,1.,1.]];roles=['identity']*4
    runner.run_arrays(out,axis(),x,y,roles,dict(generated_only=True))
    read=lambda n:json.loads((out/n).read_text())
    result=verifier.verify_arrays(axis(),read('initial_oblique_PRIVATE.json'),read('candidate_PRIVATE.json'),
        read('optimization_PRIVATE.json'),x,y,roles)
    assert result['passed'] and result['final']['SSE']==0
    with pytest.raises(FileExistsError):runner.run_arrays(out,axis(),x,y,roles,{})
    report=read('optimization_PRIVATE.json');report['final_SSE']=99
    with pytest.raises(AssertionError):
        verifier.verify_arrays(axis(),read('initial_oblique_PRIVATE.json'),read('candidate_PRIVATE.json'),report,x,y,roles)

def test_failed_attempt_preserved_without_retry(tmp_path):
    calls=[]
    def fail(*args,**kwargs):calls.append(1);raise ValueError('generated failure')
    out=tmp_path/'failed'
    with pytest.raises(ValueError):runner.run_arrays(out,axis(),[[-1.]],[[1.,1.,1.]],['identity'],{},trainer=fail)
    assert len(calls)==1
    assert json.loads((out/'run_status_PRIVATE.json').read_text())['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):runner.run_arrays(out,axis(),[],[],[],{},trainer=fail)
    assert len(calls)==1

def test_bindings_reject_change_and_escape(tmp_path):
    p=tmp_path/'bound';p.write_text('before');bindings={'bound':runner.sha(p)}
    runner.check_bindings(tmp_path,bindings)
    p.write_text('after')
    with pytest.raises(ValueError):runner.check_bindings(tmp_path,bindings)
    with pytest.raises(ValueError):runner.check_bindings(tmp_path,{'../escape':'bad'})

def test_cap_before_leaf_refresh_is_reported():
    initial=runner.from_axis_tree(axis());y=[[1.1,1.,1.]];x=[[-1.]]
    report=dict(initial_SSE=.01,final_SSE=.01,status='time_cap',SSE_history=[dict(event='initial',SSE=.01)])
    result=verifier.verify_arrays(axis(),initial,initial,report,x,y,['identity'])
    assert result['classification']=='CAPPED_NO_STRICT_FITTING_IMPROVEMENT'
    assert result['populated_leaf_mean_max_residual']>.09
