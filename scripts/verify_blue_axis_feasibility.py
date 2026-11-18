"""Independent preparation reconstruction or optimizer-free scalar fitting checks."""
from pathlib import Path
from collections import Counter
from bisect import bisect_right
import hashlib,importlib.util,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def f32(v):return struct.unpack('!f',struct.pack('!f',v))[0]

def independent_features(rgb,mask,mapping,names):
    # Shared previously frozen low-level Lab/scene/green contracts; independent
    # composition, mapping interpolation, gap sets and scalar joint histogram.
    from src.ita_estimation.compute_ita import compute_masked_lab_statistics
    from src.model_training.whole_scene_features import scene_features
    from src.model_training.green_distribution_features import green_distribution_features
    import importlib.util
    stats=compute_masked_lab_statistics(rgb[:,:,::-1].copy(),mask,1000);assert stats['valid']
    old={'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
    old.update(green_distribution_features(rgb[:,:,::-1].copy(),mask)['features']);old.update(scene_features(rgb))
    x=stats['ita_degrees'];xs=mapping['ita_knots'];ys=mapping['mst_score_knots']
    if x<=xs[0]:mst=ys[0]
    elif x>=xs[-1]:mst=ys[-1]
    else:
        i=bisect_right(xs,x)-1;mst=ys[i]+(ys[i+1]-ys[i])*(x-xs[i])/(xs[i+1]-xs[i])
    old['input_mst_score']=mst
    gap=[]
    for c in range(3):
        codes=set(rgb[:,:,c].ravel().tolist())
        for low,high in [(0,127),(128,255)]:
            eligible=set(range(max(low,min(codes)),min(high,max(codes))+1));gap.append(len(eligible-codes)/len(eligible) if eligible else 0.)
    path=Path(__file__).resolve().parent/'check_joint_log_colour_generated.py'
    spec=importlib.util.spec_from_file_location('independent_joint_scalar',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    joint=module.scalar(rgb)
    return [f32(old[n]) for n in names[:16]]+[f32(v) for v in gap+joint]

def verify_preparation(root,out,plan):
    import cv2,numpy as np
    root=Path(root);out=Path(out)
    originals={r['case_id']:r for r in read(root/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read(root/'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    joint={r['case_id']:r for r in read(root/'outputs/joint_log_colour_exposed_audit_v1/features_PRIVATE.json')}
    mapping=read(root/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json');selected={s['source']:s['selected'] for s in plan['support_sources']}
    identities={};masks={};prep=root/'outputs/reviewed_ffhq_restoration_preparation_v1'
    for source in plan['source_references']:
        path=Path(source['identity_container']);assert path.resolve()==(prep/source['identity_case']/'paired_pixels.npz').resolve() and sha(path)==source['identity_sha256']
        with np.load(path,allow_pickle=False) as pack:identities[source['source']]=pack['input_rgb8']
        s=selected[source['source']];folder=root/s['directory']
        assert sha(folder/s['receipt'])==s['receipt_sha256'] and sha(folder/'measurement_mask.png')==s['files']['measurement_mask.png']
        masks[source['source']]=cv2.imread(str(folder/'measurement_mask.png'),0)
        r=originals[source['identity_case']];expected=r['input_vector_float32']+[f32(gaps[r['case_id']]['features'][n]) for n in plan['feature_names'][16:22]]+[f32(v) for v in joint[r['case_id']]['features']]
        reconstructed=independent_features(identities[source['source']],masks[source['source']],mapping,plan['feature_names'])
        # Float64 vs scalar accumulation can differ before float32 rounding;
        # compare histogram numerically, require legacy22 EXACT.
        assert reconstructed[:22]==expected[:22]
        assert all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(reconstructed[22:],expected[22:]))
    rows=read(out/'rows_PRIVATE.json');assert len(rows)==66 and [r['case_id'] for r in rows]==[r['case_id'] for r in plan['cases']]
    newcount=0
    for r,binding in zip(rows,plan['cases']):
        assert r['source']==binding['source'] and r['role']==binding['role'] and r['y']==binding['nominal_controls']
        assert r['status']=='available' and r['generated_fixture'] is False and len(r['x'])==281
        if binding['kind']=='EXACT_OLD_RECORD_REUSE':
            original=originals[r['case_id']]
            expected=original['input_vector_float32']+[f32(gaps[r['case_id']]['features'][n]) for n in plan['feature_names'][16:22]]+[f32(v) for v in joint[r['case_id']]['features']]
            assert r['x']==expected and r['pixels_file']==original['pixels_file'] and r['pixels_sha256']==original['pixels_sha256'] and r['old_record_reused']
        else:
            newcount+=1;path=Path(r['pixels_file']);assert path.resolve()==(out/r['case_id']/'paired_pixels.npz').resolve() and sha(path)==r['pixels_sha256']
            clean=identities[r['source']];b=plan['operations'][r['role']]['blue_gain']
            expected=clean.copy();raw=(clean[:,:,2].astype(float)/255)*b
            expected[:,:,2]=np.rint(np.minimum(1.,np.maximum(0.,raw))*255).astype(np.uint8)
            with np.load(path,allow_pickle=False) as pack:
                actual=pack['input_rgb8'];assert np.array_equal(actual,expected) and np.array_equal(pack['reference_rgb8'],clean)
            assert r['forward_report']==dict(clipped_channel_samples=int((raw>1).sum()),clipped_pixels=int((raw>1).sum()))
            assert not r['old_record_reused'] and r['synthetic_controlled_derivative']
            features=independent_features(actual,masks[r['source']],mapping,plan['feature_names'])
            assert features[:22]==r['x'][:22] and all(math.isclose(a,b,abs_tol=1e-7,rel_tol=1e-7) for a,b in zip(features[22:],r['x'][22:]))
    assert newcount==22 and len(read(out/'role_ledger_PRIVATE.json'))==72
    return dict(passed=True,old44_exact=True,new22_forward_pixels_exact=True,identity11_legacy22_exact=True,
        new22_legacy22_exact=True,all_joint_histograms_scalar_checked=True,histogram_float32_abs_rel_tolerance=1e-7,
        histogram_tolerance_is_numeric_only=True,rows_sha256=sha(out/'rows_PRIVATE.json'),fits=0,predictions=0)

def verify_first(root,out,plan):
    from src.model_training.blue_axis_verification import verify
    root=Path(root);out=Path(out);prep=root/'outputs/blue_axis_preparation_v1'
    receipt=read(out/'execution_plan_PRIVATE.json');pv=read(prep/'verification_PRIVATE.json')
    assert pv['passed'] and pv['rows_sha256']==sha(prep/'rows_PRIVATE.json')==receipt['preparation_rows_sha256']
    assert sha(prep/'verification_PRIVATE.json')==receipt['preparation_verification_sha256']
    allrows=read(prep/'rows_PRIVATE.json')
    wanted=set(plan['first_fitting_cases']);selected={r['case_id']:r for r in allrows if r['case_id'] in wanted}
    rows=read(out/'fitting_inputs_PRIVATE.json');assert [r['case_id'] for r in rows]==plan['first_fitting_cases']
    for r in rows:
        s=selected[r['case_id']];assert r=={k:s[k] for k in ['case_id','source','role','x','y']}
        binding=next(c for c in plan['cases'] if c['case_id']==r['case_id']);assert r['y']==binding['nominal_controls']
    result=verify(read(out/'candidate_PRIVATE.json'),rows,read(out/'training_replay_PRIVATE.json'),plan['feature_names'],plan['first_excluded_source'])
    assert read(out/'status_PRIVATE.json')['fit_calls']==1
    return result

def main():
    if sys.argv[1:] not in [['--preparation'],['--first-fit']]:raise SystemExit('Explicit verification stage required')
    plan=read(ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json')
    out=ROOT/('outputs/blue_axis_preparation_v1' if sys.argv[1]=='--preparation' else 'outputs/blue_axis_first_fit_v1')
    dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    receipt=read(out/'execution_plan_PRIVATE.json')
    for table in [plan['input_sha256'],receipt['code_sha256']]:
        for n,h in table.items():assert sha(ROOT/n)==h
    assert receipt['plan_sha256']==sha(ROOT/'outputs/blue_axis_coverage_design_v1/plan_PRIVATE.json')
    result=verify_preparation(ROOT,out,plan) if sys.argv[1]=='--preparation' else verify_first(ROOT,out,plan)
    result['artifact_sha256']={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print('PREPARATION_VERIFIED' if sys.argv[1]=='--preparation' else result['classification'])
if __name__=='__main__':main()
