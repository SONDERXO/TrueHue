"""Finalize all96development attempts with saved occlusion logits and identity support."""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.skin_masking.correction_preview import render_preview
from src.model_training.aligned_correction_support import project_alpha
P=ROOT/'outputs/group_diversity_parent_screen_v1';OUT=ROOT/'outputs/group_diversity_final_masks_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    target=OUT/'results_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve finalized masks')
    prep=read(OUT/'preparation_PRIVATE.json');run=read(OUT/'inference.json');bound=dict(read(OUT/'inference_plan.json')['input_sha256'])
    assert run['plan_sha256']==sha(OUT/'inference_plan.json')
    bound.update(read(OUT/'worker_binding_PRIVATE.json')['input_sha256'])
    for p in (Path(__file__),OUT/'preparation_PRIVATE.json',OUT/'inference.json',OUT/'worker_binding_PRIVATE.json',ROOT/'docs/group-diversity-occlusion-protocol-2026-11-08.md'):bound[str(p)]=sha(p)
    for rel in ('src/skin_masking/correction_preview.py','src/skin_masking/continuous_correction.py','src/skin_masking/clear_lens_correction.py','src/skin_masking/full_face_support.py','src/skin_masking/face_neck_support.py','src/correction/seamless_blend.py','src/model_training/aligned_correction_support.py'):
        p=ROOT/rel;bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());pred={r['image_id']:r for r in run['records']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm'];records=[];boards=[]
    for old in prep['records']:
        r=dict(old);cid=r['case_id'];parentfolder=P/cid;folder=OUT/cid
        r.update(status='unavailable',final_masking_available=False,raw_features=None,stage='parent_measurement',
            measurement_native_path=None,alpha_path=None,protected_path=None,MST=None)
        scene=cv2.imread(str(parentfolder/'scene_input.png'));bound[str(parentfolder/'scene_input.png')]=sha(parentfolder/'scene_input.png')
        diagnostic=np.zeros(scene.shape[:2],np.uint8);alpha=np.zeros(scene.shape[:2],float)
        parent_native=cv2.imread(str(parentfolder/'parent_native.png'),0) if (parentfolder/'parent_native.png').exists() else np.zeros(scene.shape[:2],np.uint8)
        if old['status']=='inference_ready':
            r['stage']='final_masking'
            try:
                q=pred[cid]
                if q['status']!='success':raise ValueError(q.get('reason','FaceOcc inference failed'))
                lp=OUT/q['logits_path'];assert sha(lp)==q['logits_sha256'];bound[str(lp)]=sha(lp)
                logits=np.load(lp,allow_pickle=False);image=cv2.imread(str(parentfolder/'input.png'));facial=cv2.imread(str(parentfolder/'parent_mask.png'),0)
                points=np.load(parentfolder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(parentfolder/'categories.png'),0)
                def cached(aligned):
                    assert np.array_equal(aligned,cv2.imread(str(folder/'aligned.png')));return logits
                result=evaluate_parent(SimpleNamespace(report=r['parent_report'],image=image,mask=facial),points,template,cached)
                r['measurement_report']=result.report
                if result.mask is not None:
                    assert cv2.imwrite(str(folder/'measurement_mask.png'),result.mask)
                    diagnostic,account=native_projection(result.mask,r['input_bridge']);r['native_measurement_accounting']=account
                    path=folder/'measurement_native.png';assert cv2.imwrite(str(path),diagnostic);r['measurement_native_path']=str(path)
                if result.matrix is None:raise ValueError(result.report.get('reason','No valid FaceOcc mapping'))
                visible=map_visible_mask((logits>0).astype(np.uint8)*255,image.shape[:2],result.matrix)
                preview=render_preview(image,facial,categories,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
                assert np.array_equal(preview.output,image)
                alpha,protected=project_alpha(preview.alpha,preview.protected,r['input_bridge'])
                np.save(folder/'correction_alpha_normalized.npy',preview.alpha,allow_pickle=False)
                np.save(folder/'correction_alpha_native.npy',alpha,allow_pickle=False)
                assert cv2.imwrite(str(folder/'protected_native.png'),protected.astype(np.uint8)*255)
                assert cv2.imwrite(str(folder/'visible_face.png'),visible)
                r.update(alpha_path=str(folder/'correction_alpha_native.npy'),protected_path=str(folder/'protected_native.png'),
                    correction_report=preview.report,requires_glasses_choice=preview.report['requires_glasses_choice'],
                    native_correction_pixels=int(np.count_nonzero(alpha)),native_protected_pixels=int(protected.sum()))
                if result.report['status']!='success':raise ValueError(result.report.get('reason','Final measurement failed'))
                if not np.any(alpha):raise ValueError('No native correction support')
                f=result.report['features'];r['raw_features']={k:f[k] for k in ('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star')}
                r.update(status='available',stage='prepared',final_masking_available=True);r.pop('reason',None)
            except (ValueError,RuntimeError,cv2.error) as e:r['reason']=str(e)
        # Diagnostic alpha/masks on failed inputs are shown but never usable or applied.
        panels=[scene]
        for mask in (parent_native>0,diagnostic>0,alpha>0):
            overlay=scene.copy();overlay[mask]=np.rint(.5*overlay[mask]+.5*np.array([0,255,0])).astype(np.uint8);panels.append(overlay)
        title=np.full((28,896,3),255,np.uint8)
        cv2.putText(title,cid+' '+r['status']+' original|parent|finalmeasure|support DIAGNOSTIC',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.39,(0,0,0),1)
        bp=folder/'board.png';assert cv2.imwrite(str(bp),np.vstack([title,np.hstack(panels)]));boards.append(str(bp));records.append(r)
    ready=[r for r in records if r['status']=='available'];byband={}
    for band in sorted({r['score_interval'] for r in records}):
        rr=[r for r in records if r['score_interval']==band];byband[band]=dict(attempts=len(rr),available=sum(r['status']=='available' for r in rr))
    summary=dict(attempts=96,parent_passes=83,FaceOcc_forwards=run['forwards'],available=len(ready),
        failures_by_reason=dict(Counter(r.get('reason','unspecified') for r in records if r['status']!='available')),
        groups_with_all_three_final_passes=sum(all(r['status']=='available' for r in records if r['subject_key']==key) for key in {r['subject_key'] for r in records}),
        by_descriptive_interval=byband,requires_glasses_choice=sum(bool(r.get('requires_glasses_choice')) for r in ready),
        native_measurement_min=min(r['native_measurement_accounting']['selected_native_grid_locations'] for r in ready),
        native_measurement_max=max(r['native_measurement_accounting']['selected_native_grid_locations'] for r in ready),
        new_fits=0,holdout_image_reads=0,scientific_admissions=0,actual_skin_validity='unverified')
    assert len(records)==96 and run['forwards']<=83 and all(sha(p)==h for p,h in bound.items())
    result=dict(summary=summary,records=records,boards=boards,measurement_contract_sha256=prep['measurement_contract_sha256'],
        input_framing='actual_input_native1p5_to256_raw_parent_and_FaceOcc',production_adopted=False)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'final_input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    sheets=OUT/'contact_sheets';sheets.mkdir()
    for start in range(0,len(boards),4):assert cv2.imwrite(str(sheets/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in boards[start:start+4]]))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><title>Private final mask screen</title><h1>All96development attempts</h1><p>Original, parent, final measurement, correction support. Failed-row masks/support are diagnostic only. No skin ground truth, no correction model.</p>'+''.join('<img style="max-width:100%" src="'+str(Path(p).relative_to(OUT)).replace('\\','/')+'">' for p in boards),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
