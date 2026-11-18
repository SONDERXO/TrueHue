"""Execute the one fixed artificial study, preserving every artifact."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,math,platform,subprocess,sys
from importlib.metadata import version
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.linear_leaf_generated import run_generated_once,LAMBDA
from src.model_training.portable_linear_leaf_tree import LinearLeafTree,f32
from src.model_training.linear_leaf_scalar_check import coefficients,predict
from src.model_training.linear_leaf_fixtures import fixtures,NAMES,row,THREE

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def close(a,b):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
def sse(rows,values):return math.fsum((a-b)**2 for r,p in zip(rows,values) for a,b in zip(r['y'],p))
def main():
    if sys.argv[1:]!=['--execute-generated-only']:raise SystemExit('Explicit generated-only flag required')
    design=ROOT/'outputs/linear_leaf_generated_design_v1';plan=read(design/'plan_PRIVATE.json')
    assert read(design/'verification_PRIVATE.json')['plan_sha256']==sha(design/'plan_PRIVATE.json')
    assert plan['generated_interface_names']==NAMES and plan['lambda_fixed']==LAMBDA==.01 and not plan['real_fit_allowed']
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
    files=['src/model_training/'+n+'.py' for n in ['portable_linear_leaf_tree','linear_leaf_generated','linear_leaf_scalar_check','linear_leaf_fixtures']]+['tests/test_linear_leaf_generated.py','scripts/check_linear_leaf_generated.py','outputs/linear_leaf_generated_design_v1/plan_PRIVATE.json']
    bindings={n:sha(ROOT/n) for n in files};out=ROOT/'outputs/linear_leaf_generated_v1';out.mkdir()
    write(out/'execution.json',dict(generated_only=True,code_sha256=bindings,design_sha256=sha(design/'plan_PRIVATE.json'),versions=dict(python=platform.python_version(),numpy=version('numpy'))))
    try:
        test=subprocess.run([sys.executable,'-m','pytest','tests/test_linear_leaf_generated.py','-q','-p','no:cacheprovider','--junitxml='+str(out/'generated_tests.xml')],cwd=ROOT,capture_output=True,text=True)
        (out/'generated_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
        if test.returncode:raise RuntimeError('Generated engineering tests failed')
        scenarios,nuisance=fixtures();reports={};saved={};checks=0;worst=0.
        for name,(topology,rows) in scenarios.items():
            tree,replay=run_generated_once(out/name,topology,rows,NAMES);model=LinearLeafTree(tree);saved[name]=(tree,replay)
            for leaf in set(replay['leaves']):
                rs=[r for r,l in zip(rows,replay['leaves']) if l==leaf];expected=coefficients(rs)
                for actual,wanted in zip(tree['nodes'][leaf]['coefficients'],expected):
                    for a,b in zip(actual,wanted):close(a,b);worst=max(worst,abs(a-b));checks+=1
            for r,p,leaf in zip(rows,replay['predictions'],replay['leaves']):
                ownleaf,own=predict(tree,r['x']);assert ownleaf==leaf
                for a,b in zip(own,p):close(a,b);worst=max(worst,abs(a-b));checks+=1
                assert model.predict_one(r['x'])==LinearLeafTree(json.loads(json.dumps(tree))).predict_one(r['x'])
            mean=[math.fsum(r['y'][j] for r in rows)/len(rows) for j in range(3)]
            reports[name]=dict(rows=len(rows),raw_SSE=sse(rows,replay['predictions']),analytical_constant_SSE=sse(rows,[mean]*len(rows)))
        tree,_=saved['separable'];model=LinearLeafTree(tree);c=tree['nodes'][0]['coefficients']
        assert reports['separable']['raw_SSE']<reports['separable']['analytical_constant_SSE'] and c[1][1]<0 and c[2][2]<0
        close(c[1][2],0);close(c[2][1],0)
        interpolation=[]
        for u in [-.1,.1]:
            for v in [-.1,.1]:
                x=row(u,v,[1.,1.,1.])['x'];native=model.predict_one(x);scalar=predict(tree,x)[1]
                for a,b in zip(native,scalar):close(a,b);checks+=1
                interpolation.append(dict(x=[u,v],prediction=native))
        try:model.predict_one(row(10,0,[1.,1.,1.])['x'])
        except ValueError:negative_rejected=True
        else:raise AssertionError('Negative extrapolated control not rejected')
        positive=model.predict_one(row(-10,0,[1.,1.,1.])['x']);assert positive[1]>2.
        try:run_generated_once(out/'expected_empty_failure',THREE,[row(0,0,[1.,1.,1.])],NAMES)
        except ValueError:assert read(out/'expected_empty_failure/status.json')['status']=='FAILED_PRESERVED_NO_RETRY'
        else:raise AssertionError('Empty leaf accepted')
        nuisance_model=LinearLeafTree(saved['nuisance_fit'][0]);held=[r for r in nuisance if r['source_offset']!=[0.,0.]]
        assert len(nuisance)==36 and len(held)==32
        means=[math.fsum(r['y'][j] for r in scenarios['nuisance_fit'][1])/4 for j in range(3)]
        predictions=[nuisance_model.predict_one(r['x']) for r in held];groups=defaultdict(set)
        for r in nuisance:groups[tuple(f32(r['x'][j]) for j in [5,6])].add(tuple(r['y']))
        offsets=[]
        for offset in sorted({tuple(r['source_offset']) for r in held}):
            rs=[r for r in held if tuple(r['source_offset'])==offset];ps=[nuisance_model.predict_one(r['x']) for r in rs]
            offsets.append(dict(source_offset=offset,raw_SSE=sse(rs,ps),per_control_SSE=[math.fsum((r['y'][j]-p[j])**2 for r,p in zip(rs,ps)) for j in range(3)],identity_deviation=[p[j]-1 for r,p in zip(rs,ps) if r['edit']==[0.,0.] for j in range(3)]))
        confound=dict(records=36,fit=4,unseen_offset=32,conflicting_identical_float32_coordinate_groups=sum(len(s)>1 for s in groups.values()),unseen_raw_SSE=sse(held,predictions),constant_mean_unseen_SSE=sse(held,[means]*len(held)),offsets=offsets,
            unchanged_source_identity_control_changes=sum(any(abs(v-1)>1e-12 for v in nuisance_model.predict_one(r['x'])) for r in held if r['edit']==[0.,0.]),inference_role_used=False)
        for table in [bindings,plan['input_sha256']]:
            for n,h in table.items():assert sha(ROOT/n)==h
        result=dict(passed=True,engineering='PASS',affine_mechanism='PASS',source_confounds=confound,scenarios=reports,interpolation=interpolation,negative_control_rejected=negative_rejected,positive_extrapolated_controls=positive,
            independent_scalar_values_checked=checks,max_abs_scalar_difference=worst,real_fit_qualified=False,real_fits=0,photo_arrays=0,model_adopted=False)
        write(out/'results.json',result);write(out/'verification.json',dict(passed=True,results_sha256=sha(out/'results.json'),code_sha256=bindings,real_fit_qualified=False,real_fits=0,photo_arrays=0))
        print(test.stdout);print(json.dumps(dict(engineering='PASS',mechanism='PASS',confounds=confound,real_fit_qualified=False),indent=2))
    except BaseException as error:write(out/'failure.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error)));raise
if __name__=='__main__':main()
