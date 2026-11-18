"""Generated reference-prior checks, with held-payload access traps."""
from copy import deepcopy
import json,math,subprocess,sys
import pytest
from src.model_training.conditional_reference_prior import build_generated_prior,ConditionalReferencePrior,build_once,rgb8
from src.model_training.conditional_prior_fixtures import references,reference,trend,transform,ROLES,offset_probes
from src.model_training.conditional_prior_numpy_check import table,describe

def close(a,b):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
def artifact():return build_generated_prior(references(),['A','B','C'],['H'])
def check_descriptor(a,b):
    assert a.keys()==b.keys()
    for k in a:
        if k in ['positive_fraction','supported_fraction','mean_red_residual','mean_blue_residual'] and a[k] is not None:close(a[k],b[k])
        else:assert a[k]==b[k]

def test_independent_table_and_all_ideal_residuals():
    rs=references();before=deepcopy(rs);a=artifact();own=table(rs,['A','B','C'])
    assert a['source_counts']==own['source_counts']
    for p,q in zip(a['bins'],own['bins']):
        assert p['index']==q['index'] and len(p['contributors'])==len(q['contributors'])
        if p['mean']:
            for x,y in zip(p['mean'],q['mean']):close(x,y)
            for c,d in zip(p['contributors'],q['contributors']):
                assert c['source']==d['source'] and c['pixels']==d['pixels']
                for x,y in zip(c['mean'],d['mean']):close(x,y)
        else:assert q['mean'] is None
    prior=ConditionalReferencePrior(a)
    for r in rs:
        for red,blue in ROLES.values():
            values=transform(r['pixels'],red,blue);d=prior.describe(values);check_descriptor(d,describe(a,values));assert d['available']
            close(d['mean_red_residual'],math.log(red));close(d['mean_blue_residual'],math.log(blue))
    assert rs==before

def test_source_weighting_is_not_pixel_weighting():
    g=.3125
    def pixel(u):return [g*math.exp(u),g,g*math.exp(-.1)]
    rs=[reference('P',[pixel(.1)]),reference('Q',[pixel(.3)]*100)];a=build_generated_prior(rs,['P','Q'],[])
    close(a['bins'][2]['mean'][0],.2);close(a['bins'][2]['mean'][1],-.1)
    rs[1]['pixels']*=100;b=build_generated_prior(rs,['P','Q'],[])
    for x,y in zip(a['bins'][2]['mean'],b['bins'][2]['mean']):close(x,y)
    assert abs(a['bins'][2]['mean'][0]-(.1+100*.3)/101)>.09

class Poison(dict):
    def __getitem__(self,k):
        if k=='pixels':raise RuntimeError('Held pixels accessed')
        return super().__getitem__(k)

def test_held_and_unknown_payloads_never_read():
    rs=references()[:3]+[Poison(source='H'),Poison(source='UNKNOWN')]
    assert build_generated_prior(rs,['A','B','C'],['H'])==artifact()

@pytest.mark.parametrize('fault',['overlap','duplicate_ids','missing','duplicate_reference','distorted','scientific','empty_positive'])
def test_bad_rosters_refused(fault):
    rs=references();ids=['A','B','C'];excluded=['H']
    if fault=='overlap':ids+=['H'];rs[-1]=Poison(source='H')
    elif fault=='duplicate_ids':ids.append('A')
    elif fault=='missing':rs=rs[1:]
    elif fault=='duplicate_reference':rs.append(deepcopy(rs[0]))
    elif fault=='distorted':rs[0]['role']='red_decrease'
    elif fault=='scientific':rs[0]['generated_fixture']=False
    else:rs[0]['pixels']=[[0,0,0]]
    with pytest.raises(ValueError):build_generated_prior(rs,ids,excluded)

def test_missing_zero_empty_boundaries_and_roundtrip_immutable():
    a=artifact();prior=ConditionalReferencePrior(a);unsupported=[.8125*math.exp(.1),.8125,.8125*math.exp(-.1)]
    mixed=[unsupported,trend(2),[0,.3,.2]];d=prior.describe(mixed);check_descriptor(d,describe(a,mixed))
    close(d['positive_fraction'],2/3);close(d['supported_fraction'],1/3);assert d['available']
    for x in [[],[[0,0,0]],[unsupported]]:
        d=prior.describe(x);check_descriptor(d,describe(a,x));assert not d['available'] and d['mean_red_residual'] is None
    boundary=prior.describe([[.1,.125,.1],[.5,1.,.5],[.1,0.,.1]])
    assert boundary['positive_green_bin_counts'][1]==1 and boundary['positive_green_bin_counts'][7]==1 and boundary['zero_channel_pixels']==1
    a['bins'][0]['mean'][0]=100
    x=trend(0);assert abs(prior.describe([x])['mean_red_residual'])<1e-12
    exported=prior.artifact();exported['bins'][0]['mean'][0]=100
    assert ConditionalReferencePrior(json.loads(json.dumps(prior.artifact()))).describe([x])==prior.describe([x])

@pytest.mark.parametrize('fault',['schema','bin_count','bin_index','null','mean','count','overlap','nonfinite'])
def test_bad_prior_artifact_rejected(fault):
    a=artifact()
    if fault=='schema':a['schema_version']='wrong'
    elif fault=='bin_count':a['bins'].pop()
    elif fault=='bin_index':a['bins'][1]['index']=0
    elif fault=='null':a['bins'][7]['mean']=[0.,0.]
    elif fault=='mean':a['bins'][0]['mean'][0]+=.1
    elif fault=='count':a['source_counts']['A']['positive']+=1
    elif fault=='overlap':a['excluded_sources']=['A']
    else:a['bins'][0]['contributors'][0]['mean'][0]=float('inf')
    with pytest.raises(ValueError):ConditionalReferencePrior(a)

@pytest.mark.parametrize('value',[[[-.1,.2,.3]],[[1.1,.2,.3]],[[float('nan'),.2,.3]],[[.1,.2]],[[True,.2,.3]]])
def test_invalid_input_pixels(value):
    with pytest.raises(ValueError):ConditionalReferencePrior(artifact()).describe(value)

def test_offsets_are_reported_not_removed_and_rgb8_adapter():
    a=artifact();prior=ConditionalReferencePrior(a)
    probes=offset_probes();assert len(probes)==36
    for r in probes:
        d=prior.describe(r['pixels']);check_descriptor(d,describe(a,r['pixels']))
        for i,key in enumerate(['mean_red_residual','mean_blue_residual']):close(d[key]-r['expected_edit'][i],r['offset'][i])
    assert rgb8([[0,128,255]])==[[0.,128/255,1.]]
    with pytest.raises(ValueError):rgb8([[0,128.,255]])

def test_failure_preserved_and_existing_output_refused(tmp_path):
    out=tmp_path/'expected_failure'
    with pytest.raises(ValueError):build_once(out,[reference('A',[[0,0,0]])],['A'],[])
    before=(out/'status.json').read_bytes();assert json.loads(before)['status']=='FAILED_PRESERVED_NO_RETRY'
    with pytest.raises(FileExistsError):build_once(out,references(),['A','B','C'],['H'])
    assert before==(out/'status.json').read_bytes()

def test_standalone_prior_has_no_array_or_trainer_import():
    code="import sys;from src.model_training.conditional_reference_prior import ConditionalReferencePrior;assert 'numpy' not in sys.modules;assert 'sklearn' not in sys.modules"
    assert subprocess.run([sys.executable,'-c',code],capture_output=True).returncode==0
