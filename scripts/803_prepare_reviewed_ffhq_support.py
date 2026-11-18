"""Prepare explicit cached-mask review tasks; no inference or original reads."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.labelled_measurement import digest,write,seal,verify
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.seamless_blend import apply_blended
PARENT=ROOT/'outputs/ffhq_mask_support_v1'
OUT=ROOT/'outputs/reviewed_ffhq_support_tasks_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    if OUT.exists():raise FileExistsError('Preserve completed or partial preparation')
    decisions_path=ROOT/'outputs/existing_ffhq_reference_decisions_v1/decisions_PRIVATE.json'
    decisions=read(decisions_path)['rows'];records={r['id']:r for r in read(PARENT/'results.json')['records']}
    inventory=read(PARENT/'sha256.json');bound={}
    def bind(p):bound[str(p)]=digest(p);return bound[str(p)]
    for p in [decisions_path,PARENT/'results.json',PARENT/'sha256.json',Path(__file__),ROOT/'docs/ffhq-reviewed-support-preparation-protocol-2026-11-11.md',ROOT/'src/correction/seamless_blend.py',ROOT/'src/ita_estimation/compute_ita.py']:
        bind(p)
    assert digest(PARENT/'results.json')==inventory['results.json']
    accepted=[r for r in decisions if r['reference_appearance_decision']=='acceptable']
    assert len(decisions)==12 and len(accepted)==11 and all(r['source_id']!='29863' for r in accepted)
    names=['input.png','candidate_mask.png','correction_mask.png','baseline_mask.png','alpha.npy']
    for d in accepted:
        r=records[d['source_id']]
        assert r['measurement_status']=='success' and r['correction_status']=='technical_success'
        for name in names:assert bind(PARENT/d['source_id']/name)==r['file_sha256'][name]
    method=dict(schema_version='truehue_reviewed_ffhq_working256_support_method_v1',coordinates='exact_cached_whole_frame_256_not_native_anchor',measurement='explicit_manual_facial_skin_min1000',correction='explicit_manual_face_visible_neck_identity_annotation',protection_seed='historical_none_explicit_zero_not_object_validation',empirical_MST_transfer='not_established',implementation_sha256={p:h for p,h in bound.items() if p.endswith('.py')})
    method_id=hashlib.sha256(json.dumps(method,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    OUT.mkdir();write(OUT/'method.json',dict(method=method,method_sha256=method_id));tasks=[];checks=[]
    for d in accepted:
        ident=d['source_id'];r=records[ident];old=PARENT/ident;case='ffhq_'+ident+'__reference';dest=OUT/case;dest.mkdir()
        image=cv2.imread(str(old/'input.png'));m=cv2.imread(str(old/'candidate_mask.png'),0);c=cv2.imread(str(old/'correction_mask.png'),0)
        baseline=cv2.imread(str(old/'baseline_mask.png'),0);p=np.zeros_like(m)
        assert image.shape==(256,256,3) and m.shape==c.shape==p.shape==(256,256)
        _,xx=np.nonzero(baseline);width=int(xx.max()-xx.min()+1)
        neutral,alpha,_=apply_blended(image,c,(1.,1.,1.),face_width=width,protected=p>0)
        np.testing.assert_array_equal(alpha,np.load(old/'alpha.npy',allow_pickle=False));np.testing.assert_array_equal(neutral,image)
        stats=compute_masked_lab_statistics(image,m,1000);assert stats['valid']
        for name,a in [('photo_used.png',image),('measurement_mask.png',m),('correction_mask.png',c),('protected_mask.png',p)]:assert cv2.imwrite(str(dest/name),a)
        np.save(dest/'correction_alpha.npy',alpha,allow_pickle=False)
        report=dict(schema_version='truehue_photographic_support_task_v1',case_id=case,frame='FFHQ '+ident,role='original_reference',publisher_group='ffhq_source_'+ident,subject_id=None,provided_mst_label=None,method_sha256=method_id,input_bridge=dict(coordinates='whole_frame_256_cached',native_projection_claimed=False,original_source_id=ident),face_width=width,reference_preference=d,original_case_status='historical_technical_success_not_support_approval',measurement_review='pending',correction_review='pending',measurement_statistics=stats,generated_fixture=False,training_admitted=False,calibration_admitted=False,model_calls=0,initial_protection='historical_none_zero_seed',source_cache_sha256={name:r['file_sha256'][name] for name in names})
        write(dest/'report.json',report);seal(dest);verify(dest)
        tasks.append(dict(case_id=case,folder=case,manifest_sha256=digest(dest/'manifest.json')))
        checks.append(dict(source_id=ident,exact_alpha_replay=True,identity_exact=True,seed_statistics=stats,mask_review_pending=True))
    presentation=dict(title='TrueHue | FFHQ restoration-reference support',description='Review the measurement and correction selections for each accepted original. Identity display only; no brightness model runs.',warning='29863 excluded: original underexposed. Facial skin for measurement; face/visible neck for correction. Whole-frame256 detail; mark unjudgeable if needed.',display_zoom=1)
    write(OUT/'queue.json',dict(tasks=tasks,blocked=[dict(case_id='ffhq_29863__reference',reason='user_rejected_underexposed_reference')],presentation=presentation))
    assert all(digest(p)==h for p,h in bound.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,all_decisions=12,accepted_tasks=11,rejected_reference='29863',checks=checks,input_sha256=bound,original_photo_reads=0,model_calls=0,tree_fits=0,holdout_reads=0,actual_new_annotations=0))
    print('PASS:11 cached dual-mask tasks;29863 excluded;11 exact alpha/identity replays;0 real saves.')

if __name__=='__main__':main()
