"""Artificial actual-record contract fixtures only; no scientific dataset reads."""
from copy import deepcopy
import json,math,subprocess,sys
import pytest
from src.model_training.fixed_branch_linear_leaf_training import join_actual,fit_once,topology
from src.model_training.fixed_branch_linear_leaf_verification import verify
from src.model_training.portable_linear_leaf_tree import f32
from src.model_training.linear_leaf_fixtures import NAMES

def fixture(no_signal=False):
    nodes=[dict(kind='split',feature=0,threshold=.5,left=1,right=2),dict(kind='leaf'),dict(kind='split',feature=0,threshold=1.5,left=3,right=4),dict(kind='leaf'),dict(kind='split',feature=0,threshold=3.5,left=5,right=8),dict(kind='split',feature=0,threshold=2.5,left=6,right=7),dict(kind='leaf'),dict(kind='leaf'),dict(kind='split',feature=0,threshold=4.5,left=9,right=10),dict(kind='leaf'),dict(kind='leaf')]
    roles=['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase'];records=[];leaves=[]
    for s in range(10):
        for k,role in enumerate(roles):
            route={1:(0,1),2:(1,3),5:((4,9) if s%2==0 else (5,10))}.get(k,(2,6) if s%2==0 else (3,7));x=[0.]*281;x[0]=float(route[0]);x[1]=float(s)
            if not no_signal:x[5]=f32((-.2 if k==3 else 0)+.005*s);x[6]=f32((-.2 if k==4 else 0)-.003*s)
            y=[.7 if k==1 else 1/.7 if k==2 else 1.,255/245 if k==3 else 1.,255/245 if k==4 else 245/255 if k==5 else 1.]
            records.append(dict(case_id=f'GENERATED_{s}_{role}',source=f'GENERATED_source{s}',role=role,x=x,y=y,generated_fixture=False,status='available'));leaves.append(route[1])
    for leaf in [1,3,6,7,9,10]:
        ys=[r['y'] for r,l in zip(records,leaves) if l==leaf];nodes[leaf]['values']=[math.fsum(y[j] for y in ys)/len(ys) for j in range(3)]
    scaffold=dict(nodes=nodes,feature_names=NAMES)
    snapshot=[{k:r[k] for k in ['case_id','source','role','x','y']} for r in records]
    bindings=[dict(case_id=r['case_id'],source=r['source'],role=r['role'],nominal=r['y']) for r in records]
    plan=dict(fitting_cases=[r['case_id'] for r in records],excluded_source='GENERATED_HELD',leaf_coordinates=[5,6],lambda_fixed=.01,feature_names=NAMES,topology=topology(scaffold))
    replay=dict(candidate_predictions=[nodes[l]['values'] for l in leaves],candidate_leaves=leaves)
    return plan,records,snapshot,bindings,scaffold,replay

def test_join_filters_held_before_access_and_preserves_false_provenance():
    p,r,s,b,_,_=fixture();before=deepcopy((p,r,s,b));rows=join_actual(p,r+[dict(case_id='GENERATED_HELD_MALFORMED')],s,b)
    assert before==(p,r,s,b) and len(rows)==60 and all(row['generated_fixture'] is False for row in rows)

@pytest.mark.parametrize('fault',['missing','duplicate','source','role','generated','status','prefix','nonfinite','target','held','snapshot','bindings'])
def test_bad_join_refused(fault):
    p,r,s,b,_,_=fixture()
    if fault=='missing':r.pop()
    elif fault=='duplicate':r.append(deepcopy(r[0]))
    elif fault=='source':r[0]['source']='wrong'
    elif fault=='role':r[0]['role']='wrong'
    elif fault=='generated':r[0]['generated_fixture']=True
    elif fault=='status':r[0]['status']='missing'
    elif fault=='prefix':r[0]['x']=r[0]['x'].copy();r[0]['x'][5]+=1
    elif fault=='nonfinite':r[0]['x'][5]=float('nan')
    elif fault=='target':r[0]['y']=[0,1,1]
    elif fault=='held':p['excluded_source']=r[0]['source']
    elif fault=='snapshot':s=s[::-1]
    else:b.pop()
    with pytest.raises(ValueError):join_actual(p,r,s,b)

@pytest.fixture(scope='module')
def fitted(tmp_path_factory):
    p,r,s,b,sc,base=fixture();rows=join_actual(p,r,s,b);out=tmp_path_factory.mktemp('GENERATED_fixed_leaf')/'fit'
    fit_once(out,p,rows,sc,base,dict(generated_fixture_only=True));load=lambda n:json.loads((out/n).read_text())
    return p,rows,sc,base,load('candidate_PRIVATE.json'),load('replay_PRIVATE.json')

def test_sixtyrow_six_solve_native_scalar_export_and_gates(fitted):
    report=verify(*fitted)
    assert report['classification']=='FITTING_LEAF_RESPONSE_PASS' and report['coefficients_checked']==54 and report['predictions_checked']==60
    assert report['checks']['exposure_nominal'] and report['held_predictions']==report['branch_fits']==0

@pytest.mark.parametrize('fault',['coefficient','prediction','branch','roster','settings','baseline','provenance'])
def test_independent_verifier_detects_corruption(fitted,fault):
    p,rows,sc,base,candidate,replay=deepcopy(fitted)
    if fault=='coefficient':next(n for n in candidate['nodes'] if n['kind']=='linear_leaf')['coefficients'][1][0]+=.1
    elif fault=='prediction':replay['predictions'][0][0]+=.1
    elif fault=='branch':candidate['nodes'][0]['threshold']+=.1
    elif fault=='roster':rows[0]['case_id']='wrong'
    elif fault=='settings':replay['lambda_fixed']=.1
    elif fault=='baseline':base['candidate_predictions'][0]=[2,2,2]
    else:rows[0]['generated_fixture']=True
    with pytest.raises(AssertionError):verify(p,rows,sc,base,candidate,replay)

def test_no_colour_signal_stops_not_a_false_pass(tmp_path):
    p,r,s,b,sc,base=fixture(no_signal=True);rows=join_actual(p,r,s,b);out=tmp_path/'constant'
    fit_once(out,p,rows,sc,base,dict(generated_fixture_only=True));candidate=json.loads((out/'candidate_PRIVATE.json').read_text());replay=json.loads((out/'replay_PRIVATE.json').read_text())
    assert verify(p,rows,sc,base,candidate,replay)['classification']=='FITTING_LEAF_RESPONSE_STOP'

def test_solver_failure_preserved_no_retry(tmp_path):
    p,r,s,b,sc,base=fixture();rows=join_actual(p,r,s,b);calls=[]
    def broken(x,y):calls.append(True);raise RuntimeError('GENERATED solver failure')
    out=tmp_path/'failed'
    with pytest.raises(RuntimeError):fit_once(out,p,rows,sc,base,{},solver=broken)
    assert len(calls)==1 and json.loads((out/'status_PRIVATE.json').read_text())['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):fit_once(out,p,rows,sc,base,{})

def test_verifier_imports_without_array_optimizer_or_runtime():
    code="import sys;from src.model_training.fixed_branch_linear_leaf_verification import verify;assert 'numpy' not in sys.modules;assert 'sklearn' not in sys.modules;assert 'src.model_training.portable_linear_leaf_tree' not in sys.modules"
    assert subprocess.run([sys.executable,'-c',code],capture_output=True).returncode==0
