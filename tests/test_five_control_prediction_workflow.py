from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor
from src.model_training import five_control_prediction_workflow as work
from src.model_training.five_control_prediction_fixtures import build
from src.model_training.five_control_prediction_verification import verify_fit
from src.model_training.portable_five_control_tree import FiveControlTree,export,SCHEMA,TARGETS,f32
from src.model_training.gap_training_feasibility import SETTINGS


def fixture():
    names=[f'feature_{i}' for i in range(281)]
    plan,cases,mapping=build(names,SETTINGS,side=4)
    identities={c['source_id']:fake(c['image'],c['measurement'],mapping,names)[0] for c in cases if c['role']=='identity'}
    return plan,cases,mapping,identities


def fake(image,measurement,mapping,names):
    values=[f32(float(v)) for v in image.mean(axis=(0,1))]
    return [values[j%3] for j in range(281)],{'generated_test_extractor':True}


def prepared():
    p,c,m,i=fixture();return p,c,work.prepare_features(c,p['feature_names'],m,i,extractor=fake)


def payload(offset):
    return dict(schema_version=SCHEMA,feature_names=['x'],target_names=TARGETS,input_dtype='float32',
        threshold_dtype='float64',comparison='<=',root=0,nodes=[dict(kind='leaf',values=[1.,1.,1.,1.,offset])])


@pytest.mark.parametrize('offset',[-.3,-.1,0.,.3])
def test_signed_and_zero_offset_runtime(offset):
    assert FiveControlTree(payload(offset)).predict_one([0.])[-1]==offset


@pytest.mark.parametrize('kind',['negative_gain','offset_range','nan','schema','targets','cycle','unreachable'])
def test_invalid_tree_rejected(kind):
    p=payload(0.)
    if kind=='negative_gain':p['nodes'][0]['values'][1]=-1
    if kind=='offset_range':p['nodes'][0]['values'][-1]=.4
    if kind=='nan':p['nodes'][0]['values'][0]=float('nan')
    if kind=='schema':p['schema_version']='truehue_regression_tree_v1'
    if kind=='targets':p['target_names']=list(reversed(TARGETS))
    if kind=='cycle':p['nodes']=[dict(kind='split',feature=0,threshold=0.,left=0,right=0)]
    if kind=='unreachable':p['nodes'].append(dict(kind='leaf',values=[1,1,1,1,0]))
    with pytest.raises(ValueError):FiveControlTree(p)


def test_float32_tie_and_immutable_copy():
    p=payload(0.);p['nodes']=[dict(kind='split',feature=0,threshold=.5,left=1,right=2),
        dict(kind='leaf',values=[1,1,1,1,-.1]),dict(kind='leaf',values=[1,1,1,1,.1])]
    t=FiveControlTree(p);p['nodes'][1]['values'][-1]=.2
    assert t.predict_one([.5])[-1]==-.1
    assert t.predict_one([.5000000001])[-1]==-.1 # float32 rounds back to the split tie.
    assert t.predict_one([.50001])[-1]==.1


def test_all_identity_checks_precede_nonidentity():
    p,c,m,i=fixture();calls=[];kind={id(v['image']):v['role'] for v in c}
    def spy(image,*args):calls.append(kind[id(image)]);return fake(image,*args)
    rows=work.prepare_features(c,p['feature_names'],m,i,extractor=spy)
    assert calls[:11]==['identity']*11 and len(rows)==66


def test_identity_mismatch_stops_before_nonidentity_or_fit(tmp_path):
    p,c,m,i=fixture();i[c[0]['source_id']][0]+=1;calls=[]
    def factory(**kwargs):calls.append(True);pytest.fail('No fit on identity mismatch')
    with pytest.raises(ValueError):work.execute(p,c,m,i,tmp_path/'bad',extractor=fake,factory=factory)
    assert not calls and (tmp_path/'bad/failure.json').exists() and not (tmp_path/'bad/models').exists()


def test_nonidentity_failure_stops_all_fits(tmp_path):
    p,c,m,i=fixture();bad=id(next(v for v in c if v['role']=='combined_under')['image'])
    def extractor(image,*args):
        if id(image)==bad:raise ValueError('unavailable generated feature')
        return fake(image,*args)
    with pytest.raises(ValueError):work.execute(p,c,m,i,tmp_path/'bad',extractor=extractor,
        factory=lambda **kw:pytest.fail('No fit on incomplete features'))
    assert not (tmp_path/'bad/models').exists()


def test_held_payload_not_accessed():
    p,c,rows=prepared();fold=p['folds'][0]
    class Poison(dict):
        def __getitem__(self,key):
            if key!='case_id':raise AssertionError('Held payload accessed')
            return super().__getitem__(key)
    protected=[Poison(case_id=r['case_id']) if r['source_id']==fold['held_source_id'] else r for r in rows]
    selected=work.select_fitting(protected,fold,generated_fixture=True)
    assert len(selected)==60 and fold['held_source_id'] not in {r['source_id'] for r in selected}


def test_provenance_and_invalid_signed_control_rejected_before_any_fit(tmp_path):
    p,c,rows=prepared();rows[0]['generated_fixture']=False
    with pytest.raises(ValueError):work.fit_all(p,rows,tmp_path/'models',factory=lambda **kw:pytest.fail('No mixed provenance fit'))
    assert not (tmp_path/'models').exists()
    rows[0]['generated_fixture']=True;rows[0]['y'][0]=-1
    with pytest.raises(ValueError):work.fit_all(p,rows,tmp_path/'models')


def test_export_and_independent_leafmeans_one_generated_fit():
    p,c,rows=prepared();fold=p['folds'][0];fit=work.select_fitting(rows,fold,generated_fixture=True)
    x=np.asarray([r['x'] for r in fit],np.float32);y=np.asarray([r['y'] for r in fit])
    model=DecisionTreeRegressor(**SETTINGS).fit(x,y)
    tree=export(model,p['feature_names'],{'generated_fixture':True})
    replay=dict(settings=model.get_params(deep=False),fit_calls=1,held_predictions=0,
        predictions=model.predict(x).tolist(),leaves=model.apply(x).tolist(),
        constant_controls=[sum(r['y'][j] for r in fit)/60 for j in range(5)])
    assert verify_fit(tree,fit,replay,fold,p['feature_names'],SETTINGS)['scalar_fitting_routes']==60
    leaf=next(n for n in tree['nodes'] if n['kind']=='leaf');leaf['values'][0]+=.01
    with pytest.raises(AssertionError):verify_fit(tree,fit,replay,fold,p['feature_names'],SETTINGS)


def test_missing_all_fits_barrier_prevents_held_payload_access(tmp_path):
    p,c,rows=prepared()
    with pytest.raises(FileNotFoundError):work.predict_held(p,rows,[],tmp_path)
    work.write(tmp_path/'all_fits_verified.json',dict(passed=True,fit_calls=1,models=[]))
    with pytest.raises(ValueError):work.predict_held(p,rows,[],tmp_path)


def records():
    return [dict(case_id=f'{i}_{role}',role=role,regions={'primary':{
        'input':{'RGB':5.,'DE':3.},'tree':{'RGB':1.,'DE':1.},'constant':{'RGB':7.,'DE':4.}}})
        for i in range(11) for role in work.ROLES]


def test_gate_all_roles_and_both_comparators():
    r=records();assert work.summary(r)['status']=='NUMERIC_PREDICTION_ELIGIBLE_ONLY'
    for v in r:
        if v['role']=='colour_only':v['regions']['primary']['tree']['DE']=3.1
    assert work.summary(r)['status']=='NOT_ADVANCED'
    r=records()
    for v in r:
        if v['role']=='exposure_over':v['regions']['primary']['constant']['RGB']=.5
    assert work.summary(r)['status']=='NOT_ADVANCED'
    assert work.summary(records()[:-1])['status']=='NOT_ADVANCED'


def test_no_overwrite_or_partial_failure_deletion(tmp_path):
    p,c,m,i=fixture();dest=tmp_path/'result';dest.mkdir();(dest/'keep').write_text('keep')
    with pytest.raises(FileExistsError):work.execute(p,c,m,i,dest,extractor=fake)
    assert (dest/'keep').read_text()=='keep'


def test_portable_rejects_nonfinite_features():
    with pytest.raises(ValueError):FiveControlTree(payload(0.)).predict_one([float('inf')])


def test_partial_fit_failure_keeps_verified_first_fit(tmp_path):
    p,c,rows=prepared();calls=[]
    def factory(**kwargs):
        calls.append(True)
        if len(calls)==2:raise RuntimeError('injected second-fold failure')
        return DecisionTreeRegressor(**kwargs)
    with pytest.raises(RuntimeError):work.fit_all(p,rows,tmp_path/'models',factory=factory)
    assert (tmp_path/'models/generated_00/tree.json').exists()
    assert json.loads((tmp_path/'models/failure.json').read_text())['completed_verified_fits']==1
    assert not (tmp_path/'models/all_fits_verified.json').exists()
    with pytest.raises(FileExistsError):work.fit_all(p,rows,tmp_path/'models')
