"""Artificial schema fixtures only; no scientific dataset IO."""
from copy import deepcopy
from pathlib import Path
import json,subprocess,sys
import pytest
from src.model_training.joint_colour_training import join,run_once
from src.model_training.joint_colour_verification import verify
from src.model_training.joint_log_colour import NAMES
from src.model_training.portable_tree import SCHEMA,PortableTree

NAMES281=[f'generated_old_{i}' for i in range(22)]+list(NAMES)

def fixture():
    base=[];audit=[];roster=[]
    for s in range(2):
        for k,role in enumerate(['identity','exposure_under','exposure_over','colour_cool']):
            case=f'GENERATED_{s}_{k}';source=f'GENERATED_source{s}';x=[float(k),float(s)]+[0.]*20
            y=[{1:.7,2:1/.7}.get(k,1.),1.04 if k==3 else 1.,1.]
            h=[1.,1.,0.]+[0.]*256;h[3+k]=1.
            base.append(dict(case_id=case,source=source,role=role,x=x,y=y))
            audit.append(dict(case_id=case,source=source,role=role,generated_fixture=False,old22=x,available=True,features=h))
            roster.append(dict(case_id=case,source=source,role=role))
    plan=dict(feature_names=NAMES281,fitting_records=roster,excluded_group='GENERATED_HELD')
    baseline=dict(schema_version=SCHEMA,input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,
        feature_names=NAMES281[:22],target_names=['gamma','red_gain','blue_gain'],nodes=[dict(kind='leaf',values=[1.,1.02,1.])])
    return plan,base,audit,baseline

@pytest.fixture(scope='module')
def fitted(tmp_path_factory):
    plan,base,audit,baseline=fixture();rows=join(plan,base,audit)
    out=tmp_path_factory.mktemp('GENERATED_281')/'fit'
    run_once(out,rows,NAMES281,baseline,dict(generated_fixture_only=True))
    load=lambda n:json.loads((out/n).read_text())
    return rows,load('candidate_PRIVATE.json'),baseline,load('training_replay_PRIVATE.json')

def test_join_ignores_held_before_feature_access_and_preserves_inputs():
    plan,b,a,_=fixture();before=deepcopy((plan,b,a));rows=join(plan,b,a+[dict(case_id='GENERATED_HELD_BAD')])
    assert (plan,b,a)==before and all(len(r['x'])==281 for r in rows)
    assert all(r['x'][:22]==s['x'] and r['y']==s['y'] for r,s in zip(rows,b))

@pytest.mark.parametrize('fault',['missing','duplicate','generated','source','role','prefix','held','nonfinite','negative','availability','schema','target','base_duplicate'])
def test_bad_joins_rejected(fault):
    p,b,a,_=fixture()
    if fault=='missing':a.pop()
    elif fault=='duplicate':a.append(deepcopy(a[0]))
    elif fault=='generated':a[0]['generated_fixture']=True
    elif fault=='source':a[0]['source']='wrong'
    elif fault=='role':a[0]['role']='wrong'
    elif fault=='prefix':a[0]['old22']=a[0]['old22'].copy();a[0]['old22'][0]=123.
    elif fault=='held':p['excluded_group']=b[0]['source']
    elif fault=='nonfinite':a[0]['features'][4]=float('nan')
    elif fault=='negative':a[0]['features'][4]=-.1
    elif fault=='availability':a[0]['features'][0]=0.
    elif fault=='schema':p['feature_names']=NAMES281[:-1]
    elif fault=='target':b[0]['y'][0]=0.
    elif fault=='base_duplicate':b.append(deepcopy(b[0]))
    with pytest.raises((ValueError,KeyError)):join(p,b,a)

def test_native_export_scalar_routes_leaf_means_and_json_roundtrip(fitted):
    rows,candidate,baseline,replay=fitted
    report=verify(candidate,baseline,rows,replay,NAMES281)
    assert report['passed'] and report['classification']=='STRICT_FITTING_IMPROVEMENT'
    assert PortableTree(json.loads(json.dumps(candidate))).predict([r['x'] for r in rows])==replay['candidate_predictions']

@pytest.mark.parametrize('fault',['leaf','prediction','settings','graph'])
def test_scalar_verifier_detects_corruption(fitted,fault):
    rows,candidate,baseline,replay=deepcopy(fitted)
    if fault=='leaf':next(n for n in candidate['nodes'] if n['kind']=='leaf')['values'][0]+=.1
    elif fault=='prediction':replay['candidate_predictions'][0][0]+=.1
    elif fault=='settings':replay['settings']['max_depth']=5
    elif fault=='graph':candidate['nodes'][0]=dict(kind='split',feature=0,threshold=0.,left=0,right=0)
    with pytest.raises(AssertionError):verify(candidate,baseline,rows,replay,NAMES281)

def test_failed_fit_preserved_no_retry_and_overwrite_refused(tmp_path):
    p,b,a,baseline=fixture();rows=join(p,b,a);calls=[]
    class Broken:
        def __init__(self,**kw):calls.append(kw)
        def fit(self,x,y):raise RuntimeError('GENERATED failure')
    out=tmp_path/'failed'
    with pytest.raises(RuntimeError):run_once(out,rows,NAMES281,baseline,{},factory=Broken)
    assert len(calls)==1 and json.loads((out/'status_PRIVATE.json').read_text())['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):run_once(out,rows,NAMES281,baseline,{})

def test_verifier_imports_without_optimizer_or_runtime():
    code="""
import builtins
original=builtins.__import__
def guard(name,*args,**kwargs):
 if name.split('.')[0] in ('numpy','sklearn') or name.endswith(('joint_colour_training','portable_tree')):raise RuntimeError(name)
 return original(name,*args,**kwargs)
builtins.__import__=guard
import src.model_training.joint_colour_verification
"""
    result=subprocess.run([sys.executable,'-c',code],cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
