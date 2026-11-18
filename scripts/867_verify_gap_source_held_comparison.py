"""Independent fold joins/support/dual-region replay; no optimizer imports."""
from pathlib import Path
import json,hashlib,importlib.util,math,struct
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10),(a,b)

def alpha_from_mask(mask,protected,width):
    allowed=(mask>0)&~protected
    distance=cv2.distanceTransform(allowed.astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
    t=np.clip(distance/max(2,math.ceil(width*.03)),0,1).astype(float)
    alpha=t*t*(3-2*t);alpha[~allowed]=0;return alpha

def replay(image,alpha,controls):
    result=np.empty_like(image)
    for j,gain in enumerate([controls[1],1.,controls[2]]):
        values=image[:,:,j].astype(float)/255
        changed=np.minimum(1.,np.maximum(0.,np.power(values,controls[0])*gain))
        result[:,:,j]=np.round(255*((1-alpha)*values+alpha*changed)).astype(np.uint8)
    return result

def metrics(image,reference,mask):
    assert mask.dtype==bool and mask.any()
    return dict(RGB=float(np.abs(image[mask].astype(float)-reference[mask]).mean()),
        DE=float(deltaE_ciede2000(rgb2lab(image[mask]/255),rgb2lab(reference[mask]/255)).mean()))

def verify_summary(predictions,summary):
    for context in ['primary','fixed_diagnostic']:
        for role in ['identity','exposure_under','exposure_over','colour_cool']:
            rows=[r for r in predictions if r['role']==role];record=summary[context]['by_role'][role]
            assert len(rows)==11 and record['cases']==11
            groups={r['source'] for r in rows};assert len(groups)==record['sources']==11
            delta=[r[context]['input']['DE']-r[context]['output']['DE'] for r in rows]
            close(record['source_equal_DE_improvement'],sum(delta)/11)
            close(record['worst_DE_improvement'],min(delta))
            assert record['DE_benefits']==sum(v>1e-10 for v in delta)
            assert record['DE_harms']==sum(v < -1e-10 for v in delta)
            assert record['numerical_equal']==sum(abs(v)<=1e-10 for v in delta)
            for prefix in ['input','output']:close(record[prefix+'_RGB'],sum(r[context][prefix]['RGB'] for r in rows)/11)

def main():
    out=ROOT/'outputs/histogram_gap_source_held_comparison_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    execution=read(out/'execution_plan_PRIVATE.json');plan=execution['plan']
    for table in [plan['input_sha256'],execution['code_sha256']]:
        for name,h in table.items():assert sha(ROOT/name)==h
    path=ROOT/'scripts/863_verify_histogram_gap_training_feasibility.py'
    spec=importlib.util.spec_from_file_location('independent_gap_fit',path);verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1';rows={r['case_id']:r for r in read(prep/'rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(ROOT/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    parents=read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json');models=read(out/'models_PRIVATE.json')
    assert len(models)==11 and read(out/'all_fits_verified_PRIVATE.json')['passed']
    for i,(model,parent,fold) in enumerate(zip(models,parents,plan['folds'])):
        assert model['definition']==parent['definition']==fold and model['reused']==(i==0)
        folder=out/fold['held_publisher_group'];snapshot=read(folder/'fitting_inputs_PRIVATE.json')
        assert len(snapshot)==40 and [r['case_id'] for r in snapshot]==fold['fitting_cases']
        for saved in snapshot:
            original=rows[saved['case_id']];gap=gaps[saved['case_id']]
            expected=original['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gap['features'][n]))[0] for n in plan['feature_names'][16:]]
            assert saved['x']==expected and saved['y']==original['nominal_controls']
            assert saved['source']==original['publisher_group']!=fold['held_publisher_group'] and saved['role']==original['experimental_role']
        assert sha(folder/'candidate_PRIVATE.json')==model['candidate_sha256']
        assert read(folder/'candidate_PRIVATE.json')==model['tree']
        replay_record=read(folder/'training_replay_PRIVATE.json');assert all(replay_record['settings'][k]==v for k,v in plan['settings'].items())
        verifier.verify(model['tree'],parent['tree'],snapshot,replay_record,plan['feature_names'])
    assert sha(out/plan['reuse']['fold']/'candidate_PRIVATE.json')==plan['reuse']['sha256']
    supports={}
    for item in plan['support_sources']:
        source=Path(item['annotation']);folder=out/'supports'/item['source_id'];receipt=read(folder/'manifest_PRIVATE.json')
        assert sha(source/'manifest.json')==item['manifest_sha256']
        for name,entry in item['declared_files'].items():assert sha(source/name)==entry['sha256']
        assert sha(ROOT/item['categories_path'])==item['categories_sha256']
        old=cv2.imread(str(source/'correction_mask.png'),0);measurement=cv2.imread(str(source/'measurement_mask.png'),0)
        p=cv2.imread(str(source/'protected_mask.png'),0)>0;automatic=cv2.imread(str(source/'automatic_correction_mask.png'),0)>0
        cat=cv2.imread(str(ROOT/item['categories_path']),0);manual_removed=automatic&(old==0)
        possible=np.isin(cat,[7,8])&~p&~manual_removed
        _,labels=cv2.connectedComponents(((old>0)|possible).astype(np.uint8),connectivity=8)
        selected=set(np.unique(labels[old>0]))-{0};expected=(old>0)|(possible&np.isin(labels,list(selected)))
        actual=cv2.imread(str(folder/'correction_mask.png'),0);assert np.array_equal(actual>0,expected)
        assert not actual[p].any() and not actual[manual_removed].any()
        for name in ['measurement_mask.png','protected_mask.png']:assert (folder/name).read_bytes()==(source/name).read_bytes()
        alpha=np.load(folder/'alpha.npy',allow_pickle=False);assert np.array_equal(alpha,alpha_from_mask(actual,p,item['face_width']))
        assert np.array_equal(np.load(source/'correction_alpha.npy',allow_pickle=False),alpha_from_mask(old,p,item['face_width']))
        for name,h in receipt['files'].items():assert sha(folder/name)==h
        supports[item['source']]=dict(alpha=alpha,mask=alpha>0,protected=p,
            old_alpha=np.load(source/'correction_alpha.npy',allow_pickle=False))
    assert len(supports)==11 and read(out/'all_supports_sealed_PRIVATE.json')['passed']
    predictions=read(out/'predictions_PRIVATE.json');assert len(predictions)==44 and {p['case_id'] for p in predictions}==set(rows)
    public=read(out/'review_public.json');assert public['protocol_id']==plan['protocol_id'] and len(public['cases'])==44
    byreview={c['id']:c for c in public['cases']};assert len(byreview)==44 and set(byreview)=={p['review_id'] for p in predictions}
    bygroup={m['definition']['held_publisher_group']:m for m in models}
    parent_predictions={r['case_id']:r for r in read(ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/predictions_PRIVATE.json')}
    for p in predictions:
        r=rows[p['case_id']];model=bygroup[r['publisher_group']];assert p['case_id'] in model['definition']['evaluation_cases']
        assert p['source']==r['publisher_group'] and p['role']==r['experimental_role']
        values=r['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gaps[p['case_id']]['features'][n]))[0] for n in plan['feature_names'][16:]]
        leaf,controls=verifier.route(model['tree'],values);assert leaf==p['leaf'] and controls==p['controls']
        assert p['parameter_absolute_error']==[abs(a-b) for a,b in zip(controls,r['nominal_controls'])]
        parent=parent_predictions[p['case_id']]
        assert p['saved_parent_original_region']==dict(output_RGB=parent['output_RGB'],output_DE=parent['output_DE'])
        close(p['fixed_diagnostic']['input']['RGB'],parent['input_RGB']);close(p['fixed_diagnostic']['input']['DE'],parent['input_DE'])
        path=Path(r['pixels_file']);assert path.resolve()==(prep/p['case_id']/'paired_pixels.npz').resolve() and sha(path)==r['pixels_sha256']
        with np.load(path,allow_pickle=False) as pack:
            image=pack['input_rgb8'];ref=pack['reference_rgb8'];protected=pack['protected'];support=supports[r['publisher_group']]
            assert np.array_equal(protected,support['protected'])
            assert np.array_equal(pack['alpha'],support['old_alpha']) and np.array_equal(pack['scoring_mask'],support['old_alpha']>0)
            bit=hashlib.sha256((plan['protocol_id']+p['case_id']).encode()).digest()[-1]&1
            assert p['output_panel']==('A' if bit else 'B');case=byreview[p['review_id']]
            assert case['kind']==('identity' if r['experimental_role']=='identity' else 'distorted')
            input_panel='B' if bit else 'A'
            assert np.array_equal(cv2.imread(str(out/case[input_panel]))[:,:,::-1],image)
            if case['R']:assert np.array_equal(cv2.imread(str(out/case['R']))[:,:,::-1],ref)
            for context,alpha,mask,path in [('primary',support['alpha'],support['mask'],out/case[p['output_panel']]),
                ('fixed_diagnostic',pack['alpha'],pack['scoring_mask'],out/'fixed_diagnostic'/(p['review_id']+'.png'))]:
                output=cv2.imread(str(path))[:,:,::-1];assert np.array_equal(output,replay(image,alpha,controls))
                assert np.array_equal(output[protected],image[protected]) and np.array_equal(output[alpha==0],image[alpha==0])
                assert p[context]['scoring_pixels']==int(mask.sum()) and p[context]['changed_pixels']==int(np.any(output!=image,axis=2).sum())
                for prefix,data in [('input',image),('output',output)]:
                    calculated=metrics(data,ref,mask)
                    for key in ['RGB','DE']:close(calculated[key],p[context][prefix][key])
    summary=read(out/'summary_PRIVATE.json');verify_summary(predictions,summary)
    assert read(out/'role_ledger_PRIVATE.json')==read(prep/'role_ledger_PRIVATE.json') and len(read(out/'role_ledger_PRIVATE.json'))==48
    assert read(out/'status_PRIVATE.json')['new_fits']==10
    for name,h in plan['input_sha256'].items():assert sha(ROOT/name)==h
    result=dict(passed=True,fitting_routes=440,held_routes=44,support_replays=11,render_metric_replays=88,
        exact_candidate_reuse=True,reference_regions_kept_separate=True,visual_status='PENDING',model_ready=False,refits=0,
        artifact_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()})
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS:440fit/44heldroutes,11supports,88dual-context renders/metrics; visual review pending')

if __name__=='__main__':main()
