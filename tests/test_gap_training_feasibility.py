"""Generated-only fitting/join/independent-export verification."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from src.model_training.gap_training_feasibility import join_inputs,run_once,SETTINGS

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gap_independent',ROOT/'scripts/863_verify_histogram_gap_training_feasibility.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)

def generated():
    names=[f'old{i}' for i in range(16)]+[f'gap{i}' for i in range(6)]
    rows=[]
    for i,v in enumerate([0.,0.,.25,.25,.75,.75,1.,1.]):
        target=[.7,1.,1.] if v<.5 else [1.4,1.05,1.03]
        rows.append(dict(case_id=f'toy-{i}',source=f'source-{i//2}',role='under' if v<.5 else 'over',x=[0.]*16+[v]+[0.]*5,y=target))
    baseline=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=names[:16],target_names=['gamma','red_gain','blue_gain'],nodes=[dict(kind='leaf',values=[1.05,1.025,1.015])])
    return names,rows,baseline

def join_fixture():
    names,rows,_=generated();plan=dict(feature_names=names,new_feature_names=names[16:],excluded_group='excluded',
        fitting_records=[dict(case_id=r['case_id'],source=r['source'],role=r['role']) for r in rows])
    old={r['case_id']:dict(case_id=r['case_id'],publisher_group=r['source'],experimental_role=r['role'],
        status='available',generated_fixture=False,input_vector_float32=r['x'][:16],nominal_controls=r['y']) for r in rows}
    audited=[dict(case_id=r['case_id'],source=r['source'],role=r['role'],generated_fixture=False,features=dict(zip(names[16:],r['x'][16:]))) for r in rows]
    return plan,old,audited,rows

def test_ordered_join_skips_held_descriptors_and_preserves_old_values():
    plan,old,audited,expected=join_fixture();before=deepcopy(old)
    audited.insert(0,{'case_id':'excluded-row'}) # No features: accessing it would fail.
    assert join_inputs(plan,old,list(reversed(audited)))==expected
    assert old==before

@pytest.mark.parametrize('fault',['duplicate','missing','generated','role','order','nonfinite','range','old_float','held_source'])
def test_invalid_join_rejected(fault):
    plan,old,audited,_=join_fixture();case=plan['fitting_records'][0]['case_id']
    if fault=='duplicate':audited.append(deepcopy(audited[0]))
    if fault=='missing':audited.pop()
    if fault=='generated':old[case]['generated_fixture']=True
    if fault=='role':audited[0]['role']='wrong'
    if fault=='order':audited[0]['features']=dict(reversed(list(audited[0]['features'].items())))
    if fault=='nonfinite':audited[0]['features']['gap0']=float('nan')
    if fault=='range':audited[0]['features']['gap0']=1.1
    if fault=='old_float':old[case]['input_vector_float32'][0]=.1
    if fault=='held_source':old[case]['publisher_group']='excluded'
    with pytest.raises(ValueError):join_inputs(plan,old,audited)

def test_generated_22input_single_fit_export_means_and_restart_refusal(tmp_path):
    from sklearn.tree import DecisionTreeRegressor
    names,rows,baseline=generated();calls=[]
    class Counted:
        def __init__(self,**settings):
            assert settings==SETTINGS;self.model=DecisionTreeRegressor(**settings)
        def fit(self,x,y):calls.append(1);self.model.fit(x,y)
        def __getattr__(self,name):return getattr(self.model,name)
    out=tmp_path/'attempt';run_once(out,rows,names,baseline,dict(generated_only=True),factory=Counted)
    read=lambda name:json.loads((out/name).read_text())
    result=verifier.verify(read('candidate_PRIVATE.json'),baseline,rows,read('training_replay_PRIVATE.json'),names)
    assert calls==[1] and result['passed'] and result['added_features_used']
    assert result['classification']=='STRICT_FITTING_IMPROVEMENT' and result['candidate']['SSE']<1e-25
    with pytest.raises(FileExistsError):run_once(out,rows,names,baseline,{},factory=Counted)
    assert calls==[1]
    corrupted=read('training_replay_PRIVATE.json');corrupted['sklearn_predictions'][0][0]+=1
    with pytest.raises(AssertionError):verifier.verify(read('candidate_PRIVATE.json'),baseline,rows,corrupted,names)

def test_failed_fit_preserved_no_retry(tmp_path):
    names,rows,baseline=generated();calls=[]
    class Failed:
        def __init__(self,**settings):pass
        def fit(self,*args):calls.append(1);raise RuntimeError('generated failure')
    out=tmp_path/'failed'
    with pytest.raises(RuntimeError):run_once(out,rows,names,baseline,{},factory=Failed)
    assert calls==[1] and json.loads((out/'status_PRIVATE.json').read_text())['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):run_once(out,rows,names,baseline,{},factory=Failed)
    assert calls==[1]

def test_invalid_snapshot_stops_before_fit(tmp_path):
    names,rows,baseline=generated();rows[0]['x'].pop()
    def forbidden(**settings):raise AssertionError('Must not construct estimator')
    with pytest.raises(ValueError):run_once(tmp_path/'bad',rows,names,baseline,{},factory=forbidden)
