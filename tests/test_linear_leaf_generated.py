"""Artificial vectors only; runtime/training correctness and frozen mechanism."""
from copy import deepcopy
import json,math,subprocess,sys
import pytest
from src.model_training.portable_linear_leaf_tree import LinearLeafTree
from src.model_training.linear_leaf_generated import fit_supplied_tree,solve_leaf
from src.model_training.linear_leaf_scalar_check import coefficients,predict
from src.model_training.linear_leaf_fixtures import fixtures,NAMES,ONE,THREE,row

def close(a,b):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)

@pytest.mark.parametrize('scenario',list(fixtures()[0]))
def test_independent_scalar_coefficients_and_predictions(scenario):
    topology,rows=fixtures()[0][scenario];before=deepcopy((topology,rows));tree,replay=fit_supplied_tree(topology,rows,NAMES);model=LinearLeafTree(tree)
    assert before==(topology,rows)
    for leaf in set(replay['leaves']):
        selected=[r for r,l in zip(rows,replay['leaves']) if l==leaf];expected=coefficients(selected)
        for a,b in zip(tree['nodes'][leaf]['coefficients'],expected):
            for c,d in zip(a,b):close(c,d)
    for r,p,l in zip(rows,replay['predictions'],replay['leaves']):
        ownleaf,own=predict(tree,r['x']);assert ownleaf==l
        for a,b in zip(p,own):close(a,b)
        assert LinearLeafTree(json.loads(json.dumps(tree))).predict_one(r['x'])==model.predict_one(r['x'])

def test_axis_separation_neutral_constant_exposure_and_interpolation():
    scenarios,_=fixtures();tree,replay=fit_supplied_tree(*scenarios['separable'],NAMES);c=tree['nodes'][0]['coefficients']
    assert c[1][1]<0 and c[2][2]<0;close(c[1][2],0);close(c[2][1],0)
    rows=scenarios['separable'][1];sse=sum((a-b)**2 for r,p in zip(rows,replay['predictions']) for a,b in zip(r['y'],p));baseline=sum((a-1.)**2 for r in rows for a in r['y']);assert sse<baseline
    for u in [-.1,.1]:
        for v in [-.1,.1]:
            x=row(u,v,[1.,1.,1.])['x'];own=predict(tree,x)[1];actual=LinearLeafTree(tree).predict_one(x)
            for a,b in zip(own,actual):close(a,b)
    for scenario in ['neutral','three_leaf']:
        topology,rs=scenarios[scenario];t,replay=fit_supplied_tree(topology,rs,NAMES)
        for r,p in zip(rs,replay['predictions']):
            if scenario=='neutral' or r['x'][13]!=128:
                for a,b in zip(r['y'],p):close(a,b)

def test_rank_conflict_and_extrapolation_are_not_hidden():
    scenarios,_=fixtures();t,r=fit_supplied_tree(*scenarios['conflicting'],NAMES)
    assert r['predictions'][0]==r['predictions'][1] and r['predictions'][0]!=scenarios['conflicting'][1][0]['y']
    t,_=fit_supplied_tree(*scenarios['separable'],NAMES);model=LinearLeafTree(t)
    with pytest.raises(ValueError,match='Nonpositive'):model.predict_one(row(10,0,[1.,1.,1.])['x'])
    assert model.predict_one(row(-10,0,[1.,1.,1.])['x'])[1]>2.

@pytest.mark.parametrize('fault',['schema','target','feature_names','leaf_indices','coeff_width','nonfinite_coeff','cycle','shared','unreachable','deep'])
def test_invalid_artifacts_rejected(fault):
    t,_=fit_supplied_tree(ONE,[row(0,0,[1.,1.,1.])],NAMES)
    if fault=='schema':t['schema_version']='old'
    elif fault=='target':t['target_names'].reverse()
    elif fault=='feature_names':t['feature_names'][5]='wrong'
    elif fault=='leaf_indices':t['leaf_feature_indices']=[6,5]
    elif fault=='coeff_width':t['nodes'][0]['coefficients'][0].append(1.)
    elif fault=='nonfinite_coeff':t['nodes'][0]['coefficients'][0][0]=float('inf')
    elif fault in ['cycle','shared']:
        leaf=deepcopy(t['nodes'][0]);t['nodes']=[dict(kind='split',feature=0,threshold=0.,left=0 if fault=='cycle' else 1,right=1),leaf]
    elif fault=='unreachable':t['nodes'].append(deepcopy(t['nodes'][0]))
    else:
        leaf=deepcopy(t['nodes'][0]);nodes=[]
        for i in range(5):nodes.extend([dict(kind='split',feature=0,threshold=0.,left=2*i+1,right=2*i+2),deepcopy(leaf)])
        nodes.append(leaf);t['nodes']=nodes
    with pytest.raises(ValueError):LinearLeafTree(t)

@pytest.mark.parametrize('fault',['nonfinite','negative_target','wrong_width','non_generated','empty_leaf'])
def test_invalid_training_refused(fault):
    rows=[row(0,0,[1.,1.,1.])];topology=ONE
    if fault=='nonfinite':rows[0]['x'][0]=float('nan')
    elif fault=='negative_target':rows[0]['y'][0]=0
    elif fault=='wrong_width':rows[0]['x'].pop()
    elif fault=='non_generated':rows[0]['generated_fixture']=False
    else:topology=THREE
    with pytest.raises(ValueError):fit_supplied_tree(topology,rows,NAMES)

def test_runtime_rounding_tie_immutability_and_bad_input():
    scenarios,_=fixtures();t,_=fit_supplied_tree(*scenarios['three_leaf'],NAMES);model=LinearLeafTree(t)
    x=row(0,0,[1.,1.,1.],80+1e-8)['x'];assert model.leaf_id(x)==1
    t['nodes'][1]['coefficients'][0][0]=99;assert model.predict_one(x)[0]!=99
    artifact=model.artifact();artifact['nodes'][1]['coefficients'][0][0]=88;assert model.predict_one(x)[0]!=88
    with pytest.raises(ValueError):model.predict_one(x[:-1])
    x[0]=float('inf')
    with pytest.raises(ValueError):model.predict_one(x)

def test_runtime_and_scalar_verifier_import_without_array_optimizer():
    code="import sys;from src.model_training.portable_linear_leaf_tree import LinearLeafTree;from src.model_training.linear_leaf_scalar_check import coefficients;assert 'numpy' not in sys.modules;assert 'sklearn' not in sys.modules"
    assert subprocess.run([sys.executable,'-c',code],capture_output=True).returncode==0

def test_failed_generated_run_preserved_and_no_overwrite(tmp_path):
    from src.model_training.linear_leaf_generated import run_generated_once
    out=tmp_path/'expected_failure'
    with pytest.raises(ValueError):run_generated_once(out,THREE,[row(0,0,[1.,1.,1.])],NAMES)
    assert json.loads((out/'status.json').read_text())['status']=='FAILED_PRESERVED_NO_RETRY'
    before=(out/'status.json').read_bytes()
    with pytest.raises(FileExistsError):run_generated_once(out,ONE,[row(0,0,[1.,1.,1.])],NAMES)
    assert (out/'status.json').read_bytes()==before
