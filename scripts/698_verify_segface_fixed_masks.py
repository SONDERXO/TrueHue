"""Independent saved-logit decode, mask/metric replay and fixed acceptance."""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import runpy,json,hashlib
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/segface_fixed_mask_comparison_v1';P=ROOT/'outputs/aligned_correction_preparation_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not (OUT/'verification_PRIVATE.json').exists()
    ns=runpy.run_path(str(ROOT/'scripts/697_assess_segface_fixed_masks.py'))
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    prep={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']}
    inference={r['image_id']:r for r in read(P/'inference.json')['records']}
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    actual=read(ROOT/'outputs/stellenbosch_reference_points_import_v1/actual_export_PRIVATE.json')
    template=ns['loadmat'](ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    aliases=['background','neck','skin','clothes','left_ear','right_ear','left_brow','right_brow','left_eye','right_eye','nose','mouth','lower_lip','upper_lip','hair','glasses','hat','earring','necklace']
    from src.skin_masking.face_parsing_experiment import LABELS
    mapping=np.array([LABELS.index(n) for n in aliases],np.uint8)
    assert mapping.tolist()==[0,14,1,16,7,8,2,3,4,5,10,11,13,12,17,6,18,9,15]
    totals=Counter();transitions=[];successes=0;checks=0;usable_points=Counter();usable_retained=True
    for r in d['records']:
        if r['review_id']=='review_06':assert r['status']=='failed' and not r['points'];continue
        key=r['review_id'];source=prep[r['case_id']];folder=Path(source['scene_path']).parent;target=OUT/key
        logits=np.load(ROOT/'outputs/segface_fixed_masks_v1'/key/'logits.npy',allow_pickle=False)
        assert logits.shape==(19,512,512) and np.isfinite(logits).all()
        cat=mapping[logits.argmax(0)[1::2,1::2]]
        assert np.array_equal(cat,cv2.imread(str(target/'categories.png'),0))
        assert np.array_equal(cat,np.load(ROOT/'outputs/segface_fixed_masks_v1'/key/'categories.npy',allow_pickle=False))
        image=cv2.imread(str(folder/'input.png'));points=np.load(folder/'landmarks.npy',allow_pickle=False)
        assert np.array_equal(image,cv2.imread(str(target/'parser_input.png')))
        try:
            parent=ns['build_semantic_face_coverage'](image,points,cat).mask
            parent[ns['nostril_guard']((256,256),points)]=0
        except ValueError:parent=np.zeros((256,256),np.uint8)
        assert np.array_equal(parent,cv2.imread(str(target/'parent_mask.png'),0))
        stats=ns['compute_masked_lab_statistics'](image,parent,1000);assert stats==r['parent_statistics']
        final=None;success=False
        if stats['valid']:
            q=inference[r['case_id']];lp=P/q['logits_path'];assert sha(lp)==q['logits_sha256']
            result=ns['evaluate_parent'](SimpleNamespace(report=dict(status='success'),image=image,mask=parent),points,template,lambda _:np.load(lp,allow_pickle=False))
            assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')))
            assert result.report==r['measurement_report'];final=result.mask;success=result.report['status']=='success'
            assert np.array_equal(final,cv2.imread(str(target/'measurement_mask.png'),0))
        assert success==(r['status']=='success');successes+=success
        if r['baseline_status']=='available' and not success:usable_retained=False
        native=np.zeros((224,224),np.uint8) if final is None else ns['native_projection'](final,source['input_bridge'])[0]
        assert np.array_equal(native,cv2.imread(str(target/'native_grid.png'),0))
        new=native>0;old=cv2.imread(source['measurement_native_path'],0)>0;b=bindings[key];x0,y0,x1,y1=b['native_bounds']
        patch=cv2.imread(str(ROOT/'outputs/stellenbosch_skin_patch_import_v2'/(key+'_patch.png')),0)>0
        full=np.zeros((224,224),bool);full[y0:y1,x0:x1]=patch
        for name,mask,status in [('baseline',old,r['baseline_status']=='available'),('candidate',new,success)]:
            count=int(np.count_nonzero(mask&full));assert count==r[name+'_diagnostic_patch']
            assert r[name+'_usable_patch']==(count if status else 0)
            totals[name+'_diagnostic']+=count;totals[name+'_usable']+=count if status else 0
        user=next(q for q in actual['rows'] if q['review_id']==key)
        for p,saved in zip(user['points'],r['points'],strict=True):
            x=x0+p['x'];y=y0+p['y'];a=bool(old[y,x]);c=bool(new[y,x])
            assert saved['x']==x and saved['y']==y and saved['label']==p['label'] and saved['baseline_diagnostic']==a and saved['candidate_diagnostic']==c
            if p['label']=='uncertain':continue
            kind='skin' if p['label']=='skin' else 'unwanted'
            totals[kind+'_old']+=a;totals[kind+'_new']+=c
            usable_points[kind+'_old']+=a if r['baseline_status']=='available' else 0
            usable_points[kind+'_new']+=c if success else 0
            transitions.append(dict(review_id=key,label=p['label'],x=x,y=y,baseline=a,candidate=c,
                point_polygon_conflict=kind=='unwanted' and bool(full[y,x]),newly_included=not a and c))
        assert not parent[~np.isin(cat,[1,10])].any() and not parent[ns['nostril_guard']((256,256),points)].any()
        checks+=1
    new_bad=[r for r in transitions if r['label']!='skin' and r['newly_included']]
    gates=dict(increased_skin_points=totals['skin_new']>totals['skin_old'],increased_diagnostic_patch=totals['candidate_diagnostic']>totals['baseline_diagnostic'],
        increased_usable_skin_points=usable_points['skin_new']>usable_points['skin_old'],increased_usable_patch=totals['candidate_usable']>totals['baseline_usable'],
        zero_new_unwanted_points=not new_bad,zero_new_definite_unwanted_points=not [r for r in new_bad if not r['point_polygon_conflict']],retained_usable_measurements=usable_retained)
    assert successes==d['summary']['candidate_successes'] and totals['candidate_diagnostic']==d['summary']['diagnostic_patch_new'] and totals['candidate_usable']==d['summary']['usable_patch_new']
    assert totals['skin_new']==d['summary']['points']['diagnostic']['skin_new'] and totals['unwanted_new']==d['summary']['points']['diagnostic']['unwanted_new']
    for p,h in bound.items():assert sha(p)==h
    hashes={str(p):sha(p) for p in OUT.rglob('*') if p.is_file()}
    report=dict(passed=True,cases_replayed=checks,class_ids_checked=19,totals=dict(totals),usable_point_totals=dict(usable_points),
        point_transitions=transitions,new_unwanted_points=new_bad,acceptance=gates,all_requirements_pass=all(gates.values()),
        result_sha256=sha(OUT/'results_PRIVATE.json'),input_hashes=len(bound),output_sha256=hashes,verifier_sha256=sha(Path(__file__)),
        new_model_forwards=0,new_fits=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ('point_transitions','output_sha256')},indent=2))
if __name__=='__main__':main()
