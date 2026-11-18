"""Independent metadata/fit/primary pixel replay; never imports an optimizer."""
from pathlib import Path
import hashlib,importlib.util,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.joint_colour_verification import verify,route
import cv2,numpy as np
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10)

def replay_all(root,out,plan):
    root=Path(root);out=Path(out)
    spec=importlib.util.spec_from_file_location('independent_pixels',root/'scripts/867_verify_gap_source_held_comparison.py')
    pixel=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixel)
    prep=root/'outputs/reviewed_ffhq_restoration_preparation_v1'
    records={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(root/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    joint={r['case_id']:r for r in read(root/'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json')}
    def vector(c):return records[c]['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gaps[c]['features'][n]))[0] for n in plan['feature_names'][16:22]]+[struct.unpack('!f',struct.pack('!f',v))[0] for v in joint[c]['features']]
    parents=read(root/'outputs/histogram_gap_source_held_comparison_v1/models_PRIVATE.json');models=read(out/'models_PRIVATE.json')
    assert len(models)==len(parents)==len(plan['folds'])==11
    assert read(out/'all_fits_verified_PRIVATE.json')==dict(passed=True,folds=11,new_fits=10,reused_fits=1)
    for i,(m,parent,fold) in enumerate(zip(models,parents,plan['folds'])):
        assert m['definition']==parent['definition']==fold and m['reused']==(i==0) and m['directory']==fold['held_publisher_group']
        folder=out/m['directory'];assert sha(folder/'candidate_PRIVATE.json')==m['candidate_sha256']
        rows=read(folder/'fitting_inputs_PRIVATE.json');assert len(rows)==40 and [r['case_id'] for r in rows]==fold['fitting_cases']
        for row in rows:
            r=records[row['case_id']]
            assert row['x']==vector(row['case_id']) and row['y']==r['nominal_controls']
            assert row['source']==r['publisher_group']!=fold['held_publisher_group'] and row['role']==r['experimental_role']
            assert joint[row['case_id']]['generated_fixture'] is False and r['generated_fixture'] is False
        assert read(folder/'baseline_SAVED_PRIVATE.json')==parent['tree']
        checked=verify(read(folder/'candidate_PRIVATE.json'),parent['tree'],rows,read(folder/'training_replay_PRIVATE.json'),plan['feature_names'])
        assert json.loads(json.dumps(checked))==read(folder/'fitting_verification_PRIVATE.json')
    assert sha(out/models[0]['directory']/'candidate_PRIVATE.json')==plan['reuse']['sha256']==sha(root/plan['reuse']['path'])
    supports={};seals=[]
    for item in plan['support_sources']:
        selected=item['selected'];src=root/selected['directory'];old=root/item['old_support_directory'];folder=out/'supports'/item['source_id']
        assert sha(src/selected['receipt'])==selected['receipt_sha256']
        for n,h in selected['files'].items():assert sha(src/n)==h
        for n,h in item['old_files'].items():assert sha(old/n)==h
        for n in ['correction_mask.png','measurement_mask.png','protected_mask.png']:assert (folder/n).read_bytes()==(src/n).read_bytes()
        assert (folder/'alpha.npy').read_bytes()==(src/selected['alpha_filename']).read_bytes()
        assert (folder/'measurement_mask.png').read_bytes()==(old/'measurement_mask.png').read_bytes()
        oldp=cv2.imread(str(old/'protected_mask.png'),0)>0;p=cv2.imread(str(folder/'protected_mask.png'),0)>0
        assert not np.any(oldp&~p)
        if item['protection_rule']=='exact_old':assert np.array_equal(p,oldp)
        else:assert item['protection_rule']=='old_subset_new'
        mask=cv2.imread(str(folder/'correction_mask.png'),0);assert not mask[p].any()
        alpha=np.load(folder/'alpha.npy',allow_pickle=False);assert np.array_equal(alpha,pixel.alpha_from_mask(mask,p,item['face_width']))
        previous=read(old/'manifest_PRIVATE.json');annotation=Path(previous['source_annotation'])
        original_manifest=read(annotation/'manifest.json')
        for n in ['automatic_correction_mask.png','correction_mask.png']:assert sha(annotation/n)==original_manifest['files'][n]['sha256']
        automatic=cv2.imread(str(annotation/'automatic_correction_mask.png'),0)>0;reviewed=cv2.imread(str(annotation/'correction_mask.png'),0)>0
        assert not mask[automatic&~reviewed].any()
        receipt=read(folder/'manifest_PRIVATE.json')
        assert receipt['source']==item['source'] and receipt['selected_directory']==selected['directory']
        assert receipt['selected_receipt_sha256']==selected['receipt_sha256'] and receipt['new_manual_revision']==selected['manual_assisted']
        for n,h in receipt['files'].items():assert sha(folder/n)==h
        assert receipt['measurement_unchanged'] and receipt['manual_removals_preserved'] and receipt['old_protection_retained']
        seals.append(receipt);supports[item['source']]=(alpha,p,oldp)
    assert read(out/'all_supports_sealed_PRIVATE.json')==dict(passed=True,supports=seals)
    predictions=read(out/'predictions_PRIVATE.json');public=read(out/'review_public.json')
    assert len(predictions)==44 and {p['case_id'] for p in predictions}==set(records)
    assert public['protocol_id']==plan['protocol_id'] and len(public['cases'])==44
    anon={c:f'case-{i+1:02}' for i,c in enumerate(plan['anonymous_id_case_order'])}
    assert [c['id'] for c in public['cases']]==[anon[c] for c in plan['review_order']]
    assert all(c['kind']=='identity' for c in public['cases'][:11]) and all(c['kind']=='distorted' for c in public['cases'][11:])
    byid={c['id']:c for c in public['cases']};bygroup={m['definition']['held_publisher_group']:m for m in models}
    declared={r['case_id']:r for r in plan['declared_pixel_containers']}
    for p in predictions:
        r=records[p['case_id']];m=bygroup[r['publisher_group']]
        assert p['source']==r['publisher_group'] and p['role']==r['experimental_role'] and p['case_id'] in m['definition']['evaluation_cases']
        leaf,controls=route(read(out/m['directory']/'candidate_PRIVATE.json'),vector(p['case_id']))
        assert p['leaf']==leaf and p['controls']==controls and p['parameter_absolute_error']==[abs(a-b) for a,b in zip(controls,r['nominal_controls'])]
        assert p['review_id']==anon[p['case_id']];case=byid[p['review_id']]
        assert case['kind']==('identity' if p['role']=='identity' else 'distorted')
        for k in ['A','B','R']:assert case[k]==(None if k=='R' and p['role']=='identity' else f'review_assets/{p["review_id"]}_{k}.png')
        bit=hashlib.sha256((plan['protocol_id']+p['case_id']).encode()).digest()[-1]&1
        assert p['output_panel']==('A' if bit else 'B')
        path=Path(r['pixels_file']);assert path.resolve()==(prep/p['case_id']/'paired_pixels.npz').resolve()==Path(declared[p['case_id']]['path']).resolve()
        assert sha(path)==r['pixels_sha256']==declared[p['case_id']]['sha256']
        with np.load(path,allow_pickle=False) as pack:
            image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha,protected,oldp=supports[p['source']]
            assert image.shape==ref.shape==(256,256,3) and np.array_equal(pack['protected'],oldp)
            output=pixel.replay(image,alpha,controls)
            assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
            assert np.array_equal(cv2.imread(str(out/case[p['output_panel']]))[:,:,::-1],output)
            assert np.array_equal(cv2.imread(str(out/case['B' if bit else 'A']))[:,:,::-1],image)
            if case['R']:assert np.array_equal(cv2.imread(str(out/case['R']))[:,:,::-1],ref)
            metric=p['primary'];assert metric['protected_unchanged'] and metric['zero_alpha_unchanged']
            assert metric['changed_pixels']==int(np.any(output!=image,axis=2).sum()) and metric['scoring_pixels']==int((alpha>0).sum())
            for prefix,arr in [('input',image),('output',output)]:
                actual=pixel.metrics(arr,ref,alpha>0)
                for key in ['RGB','DE']:close(actual[key],metric[prefix][key])
    summary=read(out/'summary_PRIVATE.json');assert summary['attempted']==48 and summary['available']==44 and summary['excluded']==4
    for role in ['identity','exposure_under','exposure_over','colour_cool']:
        own=[p for p in predictions if p['role']==role];s=summary['primary']['by_role'][role]
        assert len(own)==len({p['source'] for p in own})==s['cases']==s['sources']==11
        d=[p['primary']['input']['DE']-p['primary']['output']['DE'] for p in own]
        close(s['source_equal_DE_improvement'],math.fsum(d)/11);close(s['worst_DE_improvement'],min(d))
        assert s['DE_benefits']==sum(x>1e-10 for x in d) and s['DE_harms']==sum(x< -1e-10 for x in d) and s['numerical_equal']==sum(abs(x)<=1e-10 for x in d)
        for prefix in ['input','output']:close(s[prefix+'_RGB'],math.fsum(p['primary'][prefix]['RGB'] for p in own)/11)
    numeric=all(summary['primary']['by_role'][r]['source_equal_DE_improvement']>0 for r in plan['families'])
    assert summary['numeric_families_pass']==numeric and not summary['model_ready']
    assert summary['visual_status']==('PENDING' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE')
    assert read(out/'role_ledger_PRIVATE.json')==read(prep/'role_ledger_PRIVATE.json')
    assert read(out/'status_PRIVATE.json')==dict(status='COMPLETE_PENDING_INDEPENDENT_VERIFICATION',new_fits=10,reused_fits=1,held_controls=44,renders=44)
    return dict(passed=True,fitting_routes=440,held_routes=44,render_metric_replays=44,support_replays=11,exact_first_reuse=True,
        manual59807_protection_superset=True,identity_first=True,numeric_families_pass=numeric,refits=0,model_ready=False)

def main():
    out=ROOT/'outputs/joint_colour_source_held_comparison_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(out/'execution_plan_PRIVATE.json');plan=execution['plan']
    for table in [plan['input_sha256'],execution['code_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    result=replay_all(ROOT,out,plan)
    for n,h in plan['input_sha256'].items():assert sha(ROOT/n)==h
    result['artifact_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    if not result['numeric_families_pass']:
        with (out/'final_development_assessment_PRIVATE.json').open('x',encoding='utf-8') as f:json.dump(dict(development_status='FAIL_CLOSED_NOT_ADOPTED',reason='Numerical distorted family requirement failed',visual_review_not_requested=True,model_adopted=False),f,indent=2)
    print('PASS440fit/44held/44renders/11supports; '+('visual review pending' if result['numeric_families_pass'] else 'numerical failure closes candidate'))

if __name__=='__main__':main()
