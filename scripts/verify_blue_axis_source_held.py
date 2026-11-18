"""Independent scalar fit and pixel verification. No optimizer imported."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blue_axis_verification import verify,route

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10)
def replay_all(root,out,plan):
    root=Path(root);out=Path(out)
    spec=importlib.util.spec_from_file_location('independent_pixels',root/'scripts/867_verify_gap_source_held_comparison.py')
    pixel=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixel)
    prep=root/'outputs/blue_axis_preparation_v1';records={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
    models=read(out/'models_PRIVATE.json');assert len(models)==len(plan['folds'])==11
    assert read(out/'all_fits_verified_PRIVATE.json')==dict(passed=True,folds=11,new_fits=10,reused_fits=1)
    for i,(m,fold) in enumerate(zip(models,plan['folds'])):
        assert m['definition']==fold and m['reused']==(i==0) and m['directory']==fold['held_publisher_group']
        folder=out/m['directory'];assert sha(folder/'candidate_PRIVATE.json')==m['candidate_sha256']
        rows=read(folder/'fitting_inputs_PRIVATE.json');assert [r['case_id'] for r in rows]==fold['fitting_cases']
        for row in rows:
            r=records[row['case_id']];assert row=={k:r[k] for k in ['case_id','source','role','x','y']}
            assert r['generated_fixture'] is False and r['status']=='available' and r['source']!=fold['held_publisher_group']
        checked=verify(read(folder/'candidate_PRIVATE.json'),rows,read(folder/'training_replay_PRIVATE.json'),plan['feature_names'],fold['held_publisher_group'])
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

    predictions=read(out/'predictions_PRIVATE.json');public=read(out/'review_draft_PRIVATE.json')
    assert len(predictions)==66 and {p['case_id'] for p in predictions}==set(records)
    anon={c:f'case-{i+1:02}' for i,c in enumerate(plan['anonymous_case_order'])}
    assert [c['id'] for c in public['cases']]==[anon[c] for c in plan['review_order']]
    assert public['protocol_id']==plan['protocol_id']
    byid={c['id']:c for c in public['cases']};bygroup={m['definition']['held_publisher_group']:m for m in models}
    declared={r['case_id']:r for r in plan['declared_pixel_containers']};refs={}
    for r in records.values():
        if r['role']!='identity':continue
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            assert np.array_equal(pack['input_rgb8'],pack['reference_rgb8']);refs[r['source']]=pack['input_rgb8']
    for p in predictions:
        r=records[p['case_id']];m=bygroup[r['source']];d=declared[p['case_id']]
        assert p['source']==r['source'] and p['role']==r['role'] and p['case_id'] in m['definition']['evaluation_cases']
        leaf,controls=route(read(out/m['directory']/'candidate_PRIVATE.json'),r['x'])
        assert p['leaf']==leaf and p['controls']==controls and p['parameter_absolute_error']==[abs(a-b) for a,b in zip(controls,r['y'])]
        assert p['review_id']==anon[p['case_id']];case=byid[p['review_id']]
        assert case['kind']==('identity' if r['role']=='identity' else 'distorted')
        for k in ['A','B','R']:assert case[k]==(None if k=='R' and r['role']=='identity' else f'review_assets/{p["review_id"]}_{k}.png')
        bit=hashlib.sha256((plan['protocol_id']+p['case_id']).encode()).digest()[-1]&1
        assert p['output_panel']==('A' if bit else 'B')
        path=Path(r['pixels_file']);expectedroot=root/('outputs/blue_axis_preparation_v1' if d['new_blue_pack'] else 'outputs/reviewed_ffhq_restoration_preparation_v1')
        assert path.resolve()==Path(d['path']).resolve()==(expectedroot/r['case_id']/'paired_pixels.npz').resolve()
        assert sha(path)==r['pixels_sha256']==d['sha256']
        with np.load(path,allow_pickle=False) as pack:
            image=pack['input_rgb8'];ref=pack['reference_rgb8'];alpha,protected,oldp=supports[r['source']]
            assert image.dtype==ref.dtype==np.uint8 and image.shape==ref.shape==(256,256,3) and np.array_equal(ref,refs[r['source']])
            if d['new_blue_pack']:assert set(pack.files)=={'input_rgb8','reference_rgb8'}
            else:assert np.array_equal(pack['protected'],oldp)
            output=pixel.replay(image,alpha,controls)
            assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
            for panel,arr in [(p['output_panel'],output),('B' if bit else 'A',image),('R',ref)]:
                assert np.array_equal(cv2.imread(str(out/'review_assets'/f'{p["review_id"]}_{panel}.png'))[:,:,::-1],arr)
            metric=p['primary'];assert metric['protected_unchanged'] and metric['zero_alpha_unchanged']
            assert metric['changed_pixels']==int(np.any(output!=image,axis=2).sum()) and metric['scoring_pixels']==int((alpha>0).sum())
            for prefix,arr in [('input',image),('output',output)]:
                actual=pixel.metrics(arr,ref,alpha>0)
                for key in ['RGB','DE']:close(actual[key],metric[prefix][key])
    summary=read(out/'summary_PRIVATE.json');assert (summary['attempted'],summary['available'],summary['excluded'])==(72,66,6)
    families=['exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase'];means={}
    for role in ['identity']+families:
        own=[p for p in predictions if p['role']==role];s=summary['primary']['by_role'][role]
        assert len(own)==len({p['source'] for p in own})==s['cases']==s['sources']==11
        d=[p['primary']['input']['DE']-p['primary']['output']['DE'] for p in own];means[role]=math.fsum(d)/11
        close(s['source_equal_DE_improvement'],means[role]);close(s['worst_DE_improvement'],min(d))
        assert s['DE_benefits']==sum(x>1e-10 for x in d) and s['DE_harms']==sum(x< -1e-10 for x in d) and s['numerical_equal']==sum(abs(x)<=1e-10 for x in d)
        for prefix in ['input','output']:close(s[prefix+'_RGB'],math.fsum(p['primary'][prefix]['RGB'] for p in own)/11)
    numeric=all(means[r]>0 for r in families)
    assert summary['numeric_families_pass']==numeric and not summary['model_ready']
    assert summary['visual_status']==('PENDING_READINESS_AND_REUSE_AUDIT' if numeric else 'NOT_REQUIRED_NUMERICAL_FAILURE')
    assert not (out/'review_public.json').exists()
    assert read(out/'role_ledger_PRIVATE.json')==read(prep/'role_ledger_PRIVATE.json')
    assert read(out/'status_PRIVATE.json')==dict(status='COMPLETE_PENDING_INDEPENDENT_VERIFICATION',new_fits=10,reused_fits=1,held_controls=66,renders=66)
    return dict(passed=True,fitting_routes=660,held_routes=66,render_metric_replays=66,support_replays=11,exact_first_reuse=True,numeric_families_pass=numeric,model_ready=False)

def main():
    out=ROOT/'outputs/blue_axis_source_held_comparison_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(out/'execution_plan_PRIVATE.json');plan=execution['plan']
    for table in [plan['input_sha256'],plan['inherited_input_sha256'],execution['code_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    result=replay_all(ROOT,out,plan)
    result['artifact_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    if not result['numeric_families_pass']:
        with (out/'final_development_assessment_PRIVATE.json').open('x',encoding='utf-8') as f:json.dump(dict(status='FAIL_CLOSED_NOT_ADOPTED',visual_review_not_requested=True),f)
    print('Verified660fit/66held/66renders/11supports; '+('numerically eligible, readiness pending' if result['numeric_families_pass'] else 'numerical failure closed'))
if __name__=='__main__':main()
