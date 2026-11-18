"""One frozen generated-prior study, with independent vectorized checks."""
from pathlib import Path
import hashlib,json,math,platform,subprocess,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.conditional_reference_prior import build_once,build_generated_prior,ConditionalReferencePrior
from src.model_training.conditional_prior_fixtures import references,reference,trend,transform,quantize,ROLES,offset_probes
from src.model_training.conditional_prior_numpy_check import table as numpy_table,describe as numpy_describe

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def main():
    if sys.argv[1:]!=['--execute-generated-only']:raise SystemExit('Explicit generated-only flag required')
    design=ROOT/'outputs/conditional_prior_generated_design_v1';plan=read(design/'plan_PRIVATE.json')
    assert read(design/'verification_PRIVATE.json')['plan_sha256']==sha(design/'plan_PRIVATE.json')
    assert plan['green_bins']==8 and plan['generated_fitting_sources']==['A','B','C'] and not plan['real_prior_fit_allowed'] and not plan['tree_fit_allowed']
    files=['src/model_training/'+n+'.py' for n in ['conditional_reference_prior','conditional_prior_fixtures','conditional_prior_numpy_check']]+['scripts/check_conditional_reference_prior_generated.py','tests/test_conditional_reference_prior.py','outputs/conditional_prior_generated_design_v1/plan_PRIVATE.json']
    hashes={n:sha(ROOT/n) for n in files}
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
    out=ROOT/'outputs/conditional_reference_prior_generated_v1';out.mkdir()
    write(out/'execution.json',dict(generated_only=True,code_sha256=hashes,design_sha256=sha(design/'plan_PRIVATE.json'),versions=dict(python=platform.python_version(),numpy=version('numpy'))))
    try:
        tests=subprocess.run([sys.executable,'-m','pytest','tests/test_conditional_reference_prior.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
        (out/'generated_tests.txt').write_text(tests.stdout+tests.stderr,encoding='utf-8')
        if tests.returncode:raise RuntimeError('Generated tests failed; preserve this attempt')
        sources=references();write(out/'reference_sources.json',sources)
        artifact=build_once(out/'prior',sources,['A','B','C'],['H']);prior=ConditionalReferencePrior(artifact);own=numpy_table(sources,['A','B','C']);checks=0;worst=0.
        def close(a,b):
            nonlocal checks,worst
            assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12);checks+=1;worst=max(worst,abs(a-b))
        assert own['source_counts']==artifact['source_counts']
        for a,b in zip(artifact['bins'],own['bins']):
            assert a['index']==b['index'] and len(a['contributors'])==len(b['contributors'])
            if a['mean']:
                for x,y in zip(a['mean'],b['mean']):close(x,y)
                for c,d in zip(a['contributors'],b['contributors']):
                    assert c['source']==d['source'] and c['pixels']==d['pixels']
                    for x,y in zip(c['mean'],d['mean']):close(x,y)
            else:assert b['mean'] is None
        records=[]
        def record(kind,name,values,**extra):
            d=prior.describe(values);other=numpy_describe(artifact,values)
            assert d.keys()==other.keys()
            for k in d:
                if k in ['positive_fraction','supported_fraction','mean_red_residual','mean_blue_residual'] and d[k] is not None:close(d[k],other[k])
                else:assert d[k]==other[k]
            assert ConditionalReferencePrior(json.loads(json.dumps(artifact))).describe(values)==d
            r=dict(kind=kind,name=name,pixels=values,descriptor=d,**extra);records.append(r);return r
        for source in sources:
            for role,(red,blue) in ROLES.items():
                r=record('ideal',source['source']+'_'+role,transform(source['pixels'],red,blue),source=source['source'],role=role,expected_edit=[math.log(red),math.log(blue)])
                close(r['descriptor']['mean_red_residual'],math.log(red));close(r['descriptor']['mean_blue_residual'],math.log(blue))
        offset_identity=[]
        for i,probe in enumerate(offset_probes()):
            r=record('source_offset',str(i),probe['pixels'],offset=probe['offset'],role=probe['role'],expected_edit=probe['expected_edit'])
            for j,k in enumerate(['mean_red_residual','mean_blue_residual']):close(r['descriptor'][k]-probe['expected_edit'][j],probe['offset'][j])
            if probe['role']=='identity':offset_identity.append(dict(offset=probe['offset'],residual=[r['descriptor']['mean_red_residual'],r['descriptor']['mean_blue_residual']]))
        g=.3125;pixel=lambda u:[g*math.exp(u),g,g*math.exp(-.1)]
        witness=[reference('P',[pixel(.1)]),reference('Q',[pixel(.3)]*100)]
        wa=build_generated_prior(witness,['P','Q'],[]);witness[1]['pixels']*=100;wb=build_generated_prior(witness,['P','Q'],[])
        close(wa['bins'][2]['mean'][0],.2);close(wa['bins'][2]['mean'][1],-.1)
        for a,b in zip(wa['bins'][2]['mean'],wb['bins'][2]['mean']):close(a,b)
        write(out/'weighting_witness.json',dict(before=wa,after_repetition=wb,pooled_pixel_red_mean=(.1+100*.3)/101,algorithm_unchanged=True))
        unsupported=[.8125*math.exp(.1),.8125,.8125*math.exp(-.1)]
        for name,values in [('missing_only',[unsupported]),('partial',[unsupported,trend(2),[0,.3,.2]]),('zero',[[0,0,0]]),('empty',[]),('boundaries',[[.1,.125,.1],[.5,1.,.5],[.1,0.,.1]])]:record('availability',name,values)
        h=sources[-1]['pixels'];stress=[('identity',1.,1.,1.),('gamma_under',1.,1.,1/.7),('gamma_over',1.,1.,.7),('red_decrease',245/255,1.,1.),('blue_decrease',1.,245/255,1.),('blue_increase',1.,255/245,1.),('under_red',245/255,1.,1/.7)]
        stress_pairs=[]
        for name,red,blue,gamma in stress:
            values=transform(h,red,blue,gamma);continuous=record('stress',name+'_continuous',values);rounded=record('stress',name+'_quantized',quantize(values))
            stress_pairs.append(dict(name=name,continuous=continuous['descriptor'],quantized=rounded['descriptor']))
        base=[[.99,.6875,.98]];before=prior.describe(base);stretched=transform(base,1.,255/245);clip=[]
        for name,values in [('continuous',stretched),('quantized',quantize(stretched))]:
            r=record('clipping',name,values);clip.append(dict(mode=name,blue_residual_shift=r['descriptor']['mean_blue_residual']-before['mean_blue_residual'],ideal_log_gain=math.log(255/245)))
        assert base[0][2]*255/245>1
        try:build_once(out/'expected_allzero_failure',[reference('ZERO',[[0,0,0]])],['ZERO'],[])
        except ValueError:assert read(out/'expected_allzero_failure/status.json')['status']=='FAILED_PRESERVED_NO_RETRY'
        else:raise AssertionError('All-zero reference accepted')
        assert sum(r['kind']=='ideal' for r in records)==16 and sum(r['kind']=='source_offset' for r in records)==36 and sum(r['kind']=='stress' for r in records)==14
        write(out/'probe_records.json',records)
        result=dict(engineering='PASS',conditional_trend_mechanism='PASS',ideal_records=16,source_offset_records=36,stress_records=14,availability_records=5,clipping_records=2,
            independent_scalar_values_checked=checks,max_abs_difference=worst,source_offset_identity_residuals=offset_identity,source_offset_identities_nonzero=sum(any(abs(v)>1e-12 for v in r['residual']) for r in offset_identity),
            residual_bias_tracks_unmodeled_offset=True,source_weighting_verified=True,held_payload_leakage_tests_passed=True,stress_pairs=stress_pairs,clipping=clip,
            empty_fraction_convention='zero_for_empty_count_denominator;residuals_null',real_prior_fit_qualified=False,real_prior_fits=0,correction_tree_fits=0,real_arrays=0,new_ratings=0,model_adopted=False)
        for table in [hashes,plan['input_sha256']]:
            for n,h in table.items():assert sha(ROOT/n)==h
        write(out/'results.json',result);write(out/'verification.json',dict(passed=True,results_sha256=sha(out/'results.json'),probe_records_sha256=sha(out/'probe_records.json'),code_sha256=hashes,real_prior_fit_qualified=False,real_arrays=0))
        print(tests.stdout);print(json.dumps(dict(engineering='PASS',ideal='PASS',scalar_values=checks,maxdifference=worst,nonzero_source_offset_identities=result['source_offset_identities_nonzero'],clipping=clip,real_prior_fit_qualified=False),indent=2))
    except BaseException as error:write(out/'failure.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
if __name__=='__main__':main()
