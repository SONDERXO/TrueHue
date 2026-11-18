"""Generated fits, masks and arrays only. Never call real entry-point main."""
from pathlib import Path
import importlib.util,json,threading,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
import cv2,numpy as np
import pytest
from src.model_training.gap_source_held_workflow import fit_models,prepare_support,score_context,aggregate,read,write,sha,load_verifier
from src.model_training.gap_training_feasibility import join_inputs,run_once
from src.correction.seamless_blend import inward_alpha
from src.demo.oblique_comparison_review import handler

ROOT=Path(__file__).resolve().parents[1]
def independent(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def fitting_setup(tmp_path):
    names=[f'old_{i}' for i in range(16)]+[f'gap_{i}' for i in range(6)];records={};audited=[]
    targets={'identity':([1.,1.,1.],0.),'under':([.7,1.,1.],.25),'over':([1.4,1.,1.],.75),'cool':([1.,1.04,1.],1.)}
    for source in ['s0','s1']:
        for role,(target,value) in targets.items():
            case=source+'__'+role
            records[case]=dict(case_id=case,publisher_group=source,experimental_role=role,status='available',generated_fixture=False,input_vector_float32=[0.]*16,nominal_controls=target)
            audited.append(dict(case_id=case,source=source,role=role,generated_fixture=False,features=dict(zip(names[16:],[value]+[0.]*5))))
    folds=[dict(held_publisher_group=s,fitting_cases=[c for c,r in records.items() if r['publisher_group']!=s],evaluation_cases=[c for c,r in records.items() if r['publisher_group']==s]) for s in ['s0','s1']]
    axis=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,feature_names=names[:16],target_names=['gamma','red_gain','blue_gain'],nodes=[dict(kind='leaf',values=[1.,1.,1.])])
    parents=[dict(definition=f,tree=axis) for f in folds]
    f=folds[0];subset={c:records[c] for c in f['fitting_cases']}
    local=dict(feature_names=names,new_feature_names=names[16:],excluded_group='s0',fitting_records=[dict(case_id=c,source=r['publisher_group'],role=r['experimental_role']) for c,r in subset.items()])
    snapshot=join_inputs(local,subset,audited);reuse=tmp_path/'reuse'
    run_once(reuse,snapshot,names,axis,dict(generated_only=True))
    plan=dict(folds=folds,feature_names=names,protocol_id='GENERATED_ONLY',reuse=dict(fold='s0',sha256=sha(reuse/'candidate_PRIVATE.json')))
    return plan,parents,records,audited,reuse

def test_all_fits_barrier_exact_reuse_and_one_new_fit(tmp_path):
    plan,parents,records,audited,reuse=fitting_setup(tmp_path);out=tmp_path/'out';out.mkdir();calls=[]
    def counted(*args,**kwargs):calls.append(args[0].name);return run_once(*args,**kwargs)
    models=fit_models(out,plan,parents,records,audited,reuse,load_verifier(ROOT),fit_run=counted)
    assert calls==['s1'] and len(models)==2 and models[0]['reused'] and not models[1]['reused']
    assert sha(out/'s0/candidate_PRIVATE.json')==sha(reuse/'candidate_PRIVATE.json')
    assert read(out/'all_fits_verified_PRIVATE.json')['passed']
    with pytest.raises(FileExistsError):fit_models(out,plan,parents,records,audited,reuse,load_verifier(ROOT),fit_run=counted)
    assert calls==['s1']

def test_fit_failure_prevents_completion_and_keeps_first(tmp_path):
    plan,parents,records,audited,reuse=fitting_setup(tmp_path);out=tmp_path/'out';out.mkdir();calls=[]
    def failed(*args,**kwargs):calls.append(1);raise RuntimeError('generated failure')
    with pytest.raises(RuntimeError):fit_models(out,plan,parents,records,audited,reuse,load_verifier(ROOT),fit_run=failed)
    assert calls==[1] and (out/'s0/candidate_PRIVATE.json').exists() and not (out/'all_fits_verified_PRIVATE.json').exists()

def support_setup(tmp_path):
    source=tmp_path/'source';source.mkdir();c=np.zeros((256,256),np.uint8);c[80:180,80:180]=255
    m=c.copy();automatic=c.copy();automatic[110:115,75:80]=255
    protected=np.zeros_like(c);protected[100:105,72:75]=255
    cat=np.zeros_like(c);cat[90:150,70:80]=7;cat[79,80:180]=17
    for n,a in [('correction_mask.png',c),('measurement_mask.png',m),('protected_mask.png',protected),('automatic_correction_mask.png',automatic)]:assert cv2.imwrite(str(source/n),a)
    alpha,_=inward_alpha(c,face_width=100,protected=protected>0);np.save(source/'correction_alpha.npy',alpha)
    declared={p.name:dict(sha256=sha(p)) for p in source.iterdir()};write(source/'manifest.json',dict(files=declared))
    assert cv2.imwrite(str(tmp_path/'categories.png'),cat)
    item=dict(source='generated',source_id='generated',annotation=str(source),manifest_sha256=sha(source/'manifest.json'),declared_files=declared,
        categories_path='categories.png',categories_sha256=sha(tmp_path/'categories.png'),face_width=100,already_approved_exact_preview=False)
    return source,item,c,m,protected,automatic,cat

def test_sealed_support_independent_rule_alpha_and_veto(tmp_path):
    source,item,c,m,p,automatic,cat=support_setup(tmp_path);out=tmp_path/'out';out.mkdir()
    result=prepare_support(tmp_path,out,item);folder=out/'supports/generated'
    new=cv2.imread(str(folder/'correction_mask.png'),0)>0;removed=(automatic>0)&(c==0)
    assert np.all(new[c>0]) and not new[p>0].any() and not new[removed].any()
    assert np.isin(cat[new&(c==0)],[7,8]).all()
    assert (folder/'measurement_mask.png').read_bytes()==(source/'measurement_mask.png').read_bytes()
    verifier=independent('867_verify_gap_source_held_comparison.py')
    assert np.array_equal(result['alpha'],verifier.alpha_from_mask(new.astype(np.uint8)*255,p>0,100))
    with pytest.raises(FileExistsError):prepare_support(tmp_path,out,item)

def test_changed_support_manifest_refused(tmp_path):
    source,item,*_=support_setup(tmp_path);out=tmp_path/'out';out.mkdir()
    (source/'correction_mask.png').write_bytes(b'changed')
    with pytest.raises(AssertionError):prepare_support(tmp_path,out,item)

def test_two_scoring_regions_keep_one_control_vector_and_protection():
    image=np.full((8,8,3),120,np.uint8);image[2]=180;reference=np.full_like(image,140)
    old=np.zeros((8,8));old[3:5,3:5]=1;new=np.zeros_like(old);new[2:6,2:6]=1
    p=np.zeros_like(old,dtype=bool);p[2,2]=True;new[p]=0;controls=[1.15,1.02,1.]
    a,ma=score_context(image,reference,new,new>0,p,controls);b,mb=score_context(image,reference,old,old>0,p,controls)
    verifier=independent('867_verify_gap_source_held_comparison.py')
    assert ma['scoring_pixels']==15 and mb['scoring_pixels']==4
    assert np.array_equal(a,verifier.replay(image,new,controls)) and np.array_equal(b,verifier.replay(image,old,controls))
    assert np.array_equal(a[p],image[p]) and np.array_equal(b[p],image[p])

def test_source_equal_aggregation_keeps_context_separate():
    rows=[dict(role='under',source=s,primary=dict(input=dict(RGB=1,DE=d),output=dict(RGB=1,DE=1)),fixed_diagnostic=dict(input=dict(RGB=1,DE=1),output=dict(RGB=1,DE=2))) for s,d in [('a',5),('a',5),('b',1)]]
    assert aggregate(rows,'primary')['under']['source_equal_DE_improvement']==2.
    assert aggregate(rows,'fixed_diagnostic')['under']['source_equal_DE_improvement']==-1.

def test_diagnostic_files_not_served_to_reviewer(tmp_path):
    public=dict(protocol_id='GENERATED',cases=[dict(id='c',kind='identity',A='a.png',B='b.png',R=None)])
    write(tmp_path/'review_public.json',public);(tmp_path/'fixed_diagnostic').mkdir();(tmp_path/'fixed_diagnostic/hidden.png').write_bytes(b'private')
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(tmp_path));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with pytest.raises(urllib.error.HTTPError):urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/fixed_diagnostic/hidden.png')
    finally:server.shutdown();server.server_close()

def test_secondary_results_cannot_rescue_primary_failure():
    module=independent('869_assess_saved_gap_review.py')
    families=['exposure_under','exposure_over','colour_cool']
    summary=dict(primary=dict(by_role={r:dict(source_equal_DE_improvement=-1.) for r in families}),fixed_diagnostic=dict(by_role={r:dict(source_equal_DE_improvement=10.) for r in families}))
    public=dict(protocol_id='GENERATED',cases=[dict(id='c',kind='identity')])
    saved=dict(protocol_id='GENERATED',display={k:'test' for k in ['browser','resolution','os_scale','colour_settings']},ratings={'c':dict(identity='no_noticeable_change',reason='')})
    result=module.assess_saved(public,saved,[dict(review_id='c',case_id='generated',role='identity',output_panel='A')],summary)
    assert result['development_status']=='NOTREADY' and not result['fixed_diagnostic_can_rescue']
    saved['ratings']={}
    with pytest.raises(ValueError):module.assess_saved(public,saved,[],summary)

def test_generated_two_fold_dual_context_end_to_end(tmp_path):
    from src.model_training.portable_tree import PortableTree
    plan,parents,records,audited,reuse=fitting_setup(tmp_path);out=tmp_path/'comparison';out.mkdir()
    models=fit_models(out,plan,parents,records,audited,reuse,load_verifier(ROOT))
    supports={}
    for source in ['s0','s1']:
        source_root=tmp_path/('fixture_'+source);source_root.mkdir()
        original,item,*_=support_setup(source_root);item.update(source=source,source_id=source)
        supports[source]=(prepare_support(source_root,out,item),np.load(original/'correction_alpha.npy',allow_pickle=False))
    write(out/'all_supports_sealed_PRIVATE.json',dict(passed=True))
    verifier=independent('867_verify_gap_source_held_comparison.py');gaps={r['case_id']:r for r in audited}
    image=np.repeat(np.tile(np.arange(256,dtype=np.uint8),(256,1))[:,:,None],3,axis=2);reference=np.full_like(image,140)
    rendered=0
    for model in models:
        tree=PortableTree(model['tree'])
        for case in model['definition']['evaluation_cases']:
            r=records[case];x=r['input_vector_float32']+list(gaps[case]['features'].values());controls=tree.predict_one(x)
            support,oldalpha=supports[r['publisher_group']]
            for alpha in [support['alpha'],oldalpha]:
                output,report=score_context(image,reference,alpha,alpha>0,support['protected'],controls)
                assert np.array_equal(output,verifier.replay(image,alpha,controls))
                for prefix,data in [('input',image),('output',output)]:
                    expected=verifier.metrics(data,reference,alpha>0)
                    assert report[prefix]==expected
                rendered+=1
    assert rendered==16

def test_preapproved_example_requires_exact_mask_alpha_replay(tmp_path):
    source,item,*_=support_setup(tmp_path);out=tmp_path/'first';out.mkdir()
    first=prepare_support(tmp_path,out,item);approved=tmp_path/'outputs/approved_ear_support_integration_v1/generated';approved.mkdir(parents=True)
    (approved/'correction_mask.png').write_bytes((out/'supports/generated/correction_mask.png').read_bytes())
    np.save(approved/'correction_alpha.npy',first['alpha'])
    write(approved/'manifest_PRIVATE.json',dict(files={p.name:sha(p) for p in approved.iterdir()}))
    item['already_approved_exact_preview']=True;second=tmp_path/'second';second.mkdir()
    result=prepare_support(tmp_path,second,item);assert np.array_equal(result['alpha'],first['alpha'])
    np.save(approved/'correction_alpha.npy',np.zeros_like(first['alpha']))
    third=tmp_path/'third';third.mkdir()
    with pytest.raises(AssertionError):prepare_support(tmp_path,third,item)
