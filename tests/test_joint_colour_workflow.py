"""Generated workflow/safety/review fixtures, isolated in temporary directories."""
from pathlib import Path
from copy import deepcopy
import importlib.util,json,hashlib,threading,time,sys
from http.server import ThreadingHTTPServer
from urllib.request import urlopen,Request
from urllib.error import HTTPError
import cv2,numpy as np,pytest
from src.model_training.joint_colour_workflow import fit_all,fitting_rows,seal_support,after_fit_barrier
from src.model_training.joint_colour_training import run_once
from src.correction.seamless_blend import inward_alpha
from src.demo.joint_colour_review import handler,assess_saved

def fixture():
    path=Path(__file__).with_name('test_joint_colour_training.py')
    spec=importlib.util.spec_from_file_location('toy281',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    p,base,audit,baseline=m.fixture();records={};gaps={}
    for b in base:
        records[b['case_id']]=dict(case_id=b['case_id'],publisher_group=b['source'],experimental_role=b['role'],
            generated_fixture=False,status='available',input_vector_float32=b['x'][:16],nominal_controls=b['y'])
        gaps[b['case_id']]=dict(source=b['source'],role=b['role'],generated_fixture=False,features=dict(zip(p['feature_names'][16:22],b['x'][16:])))
    sources=['GENERATED_source0','GENERATED_source1'];folds=[]
    for source in sources:
        folds.append(dict(held_publisher_group=source,fitting_cases=[b['case_id'] for b in base if b['source']!=source],evaluation_cases=[b['case_id'] for b in base if b['source']==source]))
    plan=dict(feature_names=p['feature_names'],folds=folds,protocol_id='GENERATED_ONLY',reuse=dict(fold=sources[0]))
    parents=[dict(definition=f,tree=baseline) for f in folds]
    return plan,parents,records,gaps,audit

def test_generated_twofold_exact_reuse_and_fit_barrier(tmp_path):
    plan,parents,records,gaps,audit=fixture();reuse=tmp_path/'GENERATED_first'
    rows=fitting_rows(plan,plan['folds'][0],records,gaps,audit)
    run_once(reuse,rows,plan['feature_names'],parents[0]['tree'],dict(generated_fixture_only=True))
    plan['reuse']['sha256']=hashlib.sha256((reuse/'candidate_PRIVATE.json').read_bytes()).hexdigest()
    out=tmp_path/'comparison';out.mkdir();calls=[]
    def counted(*args):calls.append(True);return run_once(*args)
    models=fit_all(out,plan,parents,records,gaps,audit,reuse,fit=counted)
    assert len(calls)==1 and len(models)==2 and (out/models[0]['directory']/'candidate_PRIVATE.json').read_bytes()==(reuse/'candidate_PRIVATE.json').read_bytes()
    events=[]
    result=after_fit_barrier(out,plan,models,lambda:events.append('supports') or {},lambda _:events.append('score') or 'done')
    assert result=='done' and events==['supports','score']

def test_incomplete_barrier_prevents_support_or_scoring(tmp_path):
    (tmp_path/'all_fits_verified_PRIVATE.json').write_text(json.dumps(dict(passed=True,folds=1)))
    def forbidden():raise RuntimeError('support read')
    with pytest.raises(AssertionError):after_fit_barrier(tmp_path,dict(folds=[{},{}]),[{},{}],forbidden,forbidden)

def support_fixture(root,shape=12):
    old=root/'old';src=root/'selected';annotation=root/'annotation'
    for p in [old,src,annotation]:p.mkdir()
    c=np.zeros((shape,shape),np.uint8);c[2:11,2:11]=255;c[5,5]=0
    oldp=np.zeros_like(c);oldp[3,3]=255;c[3,3]=0
    automatic=c.copy();automatic[5,5]=255
    cv2.imwrite(str(annotation/'automatic_correction_mask.png'),automatic);cv2.imwrite(str(annotation/'correction_mask.png'),c)
    (annotation/'manifest.json').write_text(json.dumps(dict(files={n:dict(sha256=hashlib.sha256((annotation/n).read_bytes()).hexdigest()) for n in ['automatic_correction_mask.png','correction_mask.png']})))
    m=np.full_like(c,255)
    newc=c.copy();newc[1,2:9]=255;newp=oldp.copy();newp[7:9,7:9]=255;newc[newp>0]=0
    for folder,mask,p in [(old,c,oldp),(src,newc,newp)]:
        for n,a in [('correction_mask.png',mask),('measurement_mask.png',m),('protected_mask.png',p)]:cv2.imwrite(str(folder/n),a)
        alpha,_=inward_alpha(mask,face_width=30,protected=p>0);np.save(folder/'alpha.npy',alpha)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    oldfiles={p.name:digest(p) for p in old.iterdir()};(old/'manifest_PRIVATE.json').write_text(json.dumps(dict(source_annotation=str(annotation))))
    selectedfiles={p.name:digest(p) for p in src.iterdir()};(src/'approval.json').write_text('{}')
    item=dict(source='GENERATED_source',source_id='GENERATED',face_width=30,old_support_directory='old',old_files=oldfiles,protection_rule='old_subset_new',
        selected=dict(directory='selected',receipt='approval.json',receipt_sha256=digest(src/'approval.json'),files=selectedfiles,alpha_filename='alpha.npy',manual_assisted=True))
    return item,newc,newp

def test_new_protection_superset_measurement_removal_and_exact_seal(tmp_path):
    item,newc,newp=support_fixture(tmp_path);out=tmp_path/'out'
    s=seal_support(tmp_path,out,item)
    assert np.array_equal(s['protected'],newp>0) and not s['mask'][5,5] and s['protected'][7,7]
    assert not s['alpha'][s['protected']].any() and s['receipt']['measurement_unchanged']

@pytest.mark.parametrize('fault',['measurement','old_protection','manual_removal'])
def test_bad_support_rejected(tmp_path,fault):
    item,c,p=support_fixture(tmp_path);src=tmp_path/'selected'
    if fault=='measurement':cv2.imwrite(str(src/'measurement_mask.png'),np.zeros_like(c))
    elif fault=='old_protection':p[3,3]=0;cv2.imwrite(str(src/'protected_mask.png'),p)
    else:c[5,5]=255;cv2.imwrite(str(src/'correction_mask.png'),c)
    for n in item['selected']['files']:item['selected']['files'][n]=hashlib.sha256((src/n).read_bytes()).hexdigest()
    with pytest.raises(AssertionError):seal_support(tmp_path,tmp_path/'out',item)

def review_fixture(folder):
    public=dict(protocol_id='GENERATED_REVIEW',cases=[dict(id='id',kind='identity',A='review_assets/a.png',B='review_assets/b.png',R=None),
        dict(id='dist',kind='distorted',A='review_assets/a.png',B='review_assets/b.png',R='review_assets/r.png')])
    (folder/'review_public.json').write_text(json.dumps(public));(folder/'review_assets').mkdir()
    for n in ['a.png','b.png','r.png']:cv2.imwrite(str(folder/'review_assets'/n),np.zeros((8,8,3),np.uint8))
    value=dict(protocol_id=public['protocol_id'],display=dict(browser='GENERATED',resolution='8x8',os_scale='unknown',colour_settings='unknown'),ratings={})
    return public,value

def test_partial_cannot_pass_or_read_private_results(tmp_path):
    public,saved=review_fixture(tmp_path);(tmp_path/'ratings').mkdir();(tmp_path/'ratings/r.json').write_text(json.dumps(saved))
    with pytest.raises(ValueError,match='All44'):assess_saved(tmp_path,'r.json')
    saved['ratings']['id']=dict(identity='noticeable_change',reason='GENERATED_ONLY')
    (tmp_path/'ratings/r.json').write_text(json.dumps(saved))
    result=assess_saved(tmp_path,'r.json')
    assert result['development_status']=='FAIL_CLOSED_NOT_ADOPTED' and not result['scores_or_controls_unblinded'] and result['unreviewed_cases']==['dist']

def test_http_save_reload_download_payload_earlyclose_and_private_denial(tmp_path):
    _,saved=review_fixture(tmp_path)
    server=ThreadingHTTPServer(('127.0.0.1',0),handler(tmp_path));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        page=urlopen(base+'/').read();assert b'updateReviewClosure' in page
        assert json.loads(urlopen(base+'/latest').read()) is None
        saved['ratings']['id']=dict(identity='noticeable_change',reason='GENERATED_ONLY')
        req=Request(base+'/save',data=json.dumps(saved).encode(),headers={'Content-Type':'application/json'})
        response=json.loads(urlopen(req).read());assert response['saved'] and not response['complete']
        for _ in range(50):
            status=json.loads(urlopen(base+'/review-status').read())
            if status['closed']:break
            time.sleep(.01)
        assert status['closed'];latest=json.loads(urlopen(base+'/latest').read());assert latest['ratings']==saved['ratings']
        assert assess_saved(tmp_path,response['revision'])['scores_or_controls_unblinded'] is False
        for private in ['summary_PRIVATE.json','predictions_PRIVATE.json','early_identity_failure_PRIVATE.json']:
            with pytest.raises(HTTPError) as e:urlopen(base+'/'+private)
            assert e.value.code==404
        with pytest.raises(HTTPError) as e:urlopen(req)
        assert e.value.code==409
    finally:server.shutdown();server.server_close();thread.join()

def test_generated_full11fold44case_primary_pipeline_and_independent_replay(tmp_path,monkeypatch):
    import scripts.run_joint_colour_source_held as runner
    import scripts.verify_joint_colour_source_held as independent
    import shutil
    from src.model_training.gap_source_held_workflow import render
    # Entire pseudo-workspace is generated under pytest temp; no real metadata/pixels.
    p,parents0,_,_,_=fixture();names=p['feature_names'];baseline=parents0[0]['tree']
    records=[];gaps=[];joint=[];support_items=[];root=tmp_path
    prep=root/'outputs/reviewed_ffhq_restoration_preparation_v1';prep.mkdir(parents=True)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    roles=['identity','exposure_under','exposure_over','colour_cool']
    for s in range(11):
        source=f'GENERATED_source{s:02}';box=root/f'GENERATED_support{s}';box.mkdir()
        item,_,_=support_fixture(box,shape=256)
        item['source']=source;item['source_id']=f'GENERATED_{s}'
        item['old_support_directory']=str(Path(box.name)/'old')
        item['selected']['directory']=str(Path(box.name)/'selected')
        if s!=10:
            item['selected']=dict(directory=str(Path(box.name)/'old'),receipt='manifest_PRIVATE.json',receipt_sha256=digest(box/'old/manifest_PRIVATE.json'),
                files=item['old_files'],alpha_filename='alpha.npy',manual_assisted=False)
            item['protection_rule']='exact_old'
        support_items.append(item)
        protected=cv2.imread(str(box/'old/protected_mask.png'),0)>0
        ref=np.full((256,256,3),[120+s,90+s,70+s],np.uint8)
        for k,role in enumerate(roles):
            case=f'GENERATED_{s}_{role}';folder=prep/case;folder.mkdir();path=folder/'paired_pixels.npz'
            forward=[{1:1/.7,2:.7}.get(k,1.),1/1.04 if k==3 else 1.,1.]
            image=render(ref,np.ones((256,256)),forward)
            np.savez_compressed(path,input_rgb8=image,reference_rgb8=ref,protected=protected)
            x=[float(k),float(s)]+[0.]*20;y=[{1:.7,2:1/.7}.get(k,1.),1.04 if k==3 else 1.,1.]
            records.append(dict(case_id=case,publisher_group=source,experimental_role=role,generated_fixture=False,status='available',input_vector_float32=x[:16],nominal_controls=y,pixels_file=str(path),pixels_sha256=digest(path)))
            gaps.append(dict(case_id=case,source=source,role=role,generated_fixture=False,features=dict(zip(names[16:22],x[16:]))))
            h=[1.,1.,0.]+[0.]*256;h[3+k]=1.
            joint.append(dict(case_id=case,source=source,role=role,generated_fixture=False,old22=x,available=True,features=h))
    folds=[]
    for s in range(11):
        source=f'GENERATED_source{s:02}'
        folds.append(dict(held_publisher_group=source,fitting_cases=[r['case_id'] for r in records if r['publisher_group']!=source],evaluation_cases=[r['case_id'] for r in records if r['publisher_group']==source]))
    parents=[dict(definition=f,tree=baseline) for f in folds]
    def store(rel,obj):
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj))
    store('outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',records)
    store('outputs/reviewed_ffhq_restoration_preparation_v1/role_ledger_PRIVATE.json',[dict(generated_fixture_only=True,case=i) for i in range(48)])
    store('outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',gaps)
    store('outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json',joint)
    store('outputs/histogram_gap_source_held_comparison_v1/models_PRIVATE.json',parents)
    plan=dict(protocol_id='GENERATED_FULL_ONLY',feature_names=names,folds=folds,reuse=dict(fold=folds[0]['held_publisher_group']),
        support_sources=support_items,anonymous_id_case_order=[r['case_id'] for r in records],
        review_order=[r['case_id'] for r in records if r['experimental_role']=='identity']+[r['case_id'] for r in records if r['experimental_role']!='identity'],
        declared_pixel_containers=[dict(case_id=r['case_id'],path=r['pixels_file'],sha256=r['pixels_sha256']) for r in records],
        families=roles[1:],input_sha256={},output_directory='outputs/joint_colour_source_held_comparison_v1')
    first=root/'outputs/joint_log_colour_training_feasibility_v1'
    snapshot=fitting_rows(plan,folds[0],{r['case_id']:r for r in records},{r['case_id']:r for r in gaps},joint)
    run_once(first,snapshot,names,baseline,dict(generated_fixture_only=True))
    plan['reuse'].update(path=str((first/'candidate_PRIVATE.json').relative_to(root)),sha256=digest(first/'candidate_PRIVATE.json'))
    store('outputs/joint_colour_source_held_design_v1/plan_PRIVATE.json',plan)
    store('outputs/joint_colour_source_held_design_v1/verification_PRIVATE.json',dict(plan_sha256=digest(root/'outputs/joint_colour_source_held_design_v1/plan_PRIVATE.json')))
    store('outputs/joint_colour_workflow_engineering_v1/verification_PRIVATE.json',dict(passed=True,runtime_versions=runner.versions(),input_sha256={}))
    scripts=root/'scripts';scripts.mkdir();shutil.copyfile(Path(__file__).resolve().parents[1]/'scripts/867_verify_gap_source_held_comparison.py',scripts/'867_verify_gap_source_held_comparison.py')
    monkeypatch.setattr(runner,'ROOT',root);monkeypatch.setattr(sys,'argv',['run','--execute-fixed-development'])
    runner.main()
    result=independent.replay_all(root,root/plan['output_directory'],plan)
    assert result['passed'] and result['fitting_routes']==440 and result['render_metric_replays']==44 and result['manual59807_protection_superset']
