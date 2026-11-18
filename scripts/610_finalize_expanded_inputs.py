"""Finalize actual-input masks/features/native support; no fitting or correction."""
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
from src.model_training.whole_scene_features import scene_features
from src.model_training.photographic_target_diagnostic import metrics
OUT=ROOT/'outputs/expanded_correction_inputs_v1';C=ROOT/'outputs/group_diversity_final_masks_v1';P=ROOT/'outputs/group_diversity_parent_screen_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Preserve final inputs')
    prep=read(OUT/'preparation_PRIVATE.json');run=read(OUT/'inference.json');clean=read(C/'results_PRIVATE.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json')
    bound=dict(read(OUT/'inference_plan.json')['input_sha256']);bound.update(read(OUT/'worker_binding_PRIVATE.json')['input_sha256'])
    for p in (Path(__file__),OUT/'preparation_PRIVATE.json',OUT/'inference.json',OUT/'worker_binding_PRIVATE.json',C/'results_PRIVATE.json',C/'verification_PRIVATE.json'):
        bound[str(p)]=sha(p)
    bound.update(read(C/'final_input_sha256_PRIVATE.json'))
    for folder in (OUT/'cases').iterdir():
        for p in folder.iterdir():
            if p.is_file():bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items());pred={r['image_id']:r for r in run['records']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    origins={r['case_id']:r for r in clean['records']};records=[];boards=[];first_recipes=set()
    for old in clean['records']:
        source=old['case_id'];ready=old['status']=='available';scene=P/source/'scene_input.png'
        r=dict(case_id=source+'__clean',source_case=source,subject_id=old['subject_key'],cohort='expanded_development',recipe='clean',layer='clean',
            source_path=old['source_path'],source_sha256=old['source_sha256'],source_mst_exact_decimal=old['source_score'],
            status='available' if ready else 'unavailable_clean_reference',reason=old.get('reason'),scene_path=str(scene),reference_path=str(scene),
            alpha_path=old.get('alpha_path'),protected_path=old.get('protected_path'),measurement_native_path=old.get('measurement_native_path'),
            input_bridge=old.get('input_bridge'),raw_features=old['raw_features'] if ready else None,scene_features=scene_features(rgb(scene)),
            reference_support_available=ready,scoring_path=None,training_admitted=False,calibration_admitted=False,scientific_admission=False)
        if ready:
            alpha=np.load(old['alpha_path'],allow_pickle=False);sp=OUT/'references'/(source+'_clean_scoring.png');assert cv2.imwrite(str(sp),(alpha>0).astype(np.uint8)*255);r['scoring_path']=str(sp)
            r['input_region_metrics']=metrics(rgb(scene),rgb(scene),alpha>0)
        else:r['input_region_metrics']=None
        records.append(r)
    for i,old in enumerate(prep['records'],1):
        r=dict(old,raw_features=None,alpha_path=None,protected_path=None,measurement_native_path=None)
        folder=OUT/'cases'/r['case_id'];scene=rgb(r['scene_path']);origin=origins[r['source_case']]
        diagnostic=np.zeros(scene.shape[:2],np.uint8);alpha=np.zeros(scene.shape[:2],float)
        r['scene_features']=scene_features(scene)
        if old['status']=='inference_ready':
            try:
                prediction=pred[r['case_id']]
                if prediction['status']!='success':raise ValueError(prediction.get('reason','FaceOcc failed'))
                lp=OUT/prediction['logits_path'];assert sha(lp)==prediction['logits_sha256'];bound[str(lp)]=sha(lp);logits=np.load(lp,allow_pickle=False)
                image=cv2.imread(str(folder/'input.png'));facial=cv2.imread(str(folder/'parent_mask.png'),0)
                points=np.load(folder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
                result=evaluate_parent(SimpleNamespace(report=r['parent_report'],image=image,mask=facial),points,template,lambda _:logits)
                assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')));r['measurement_report']=result.report
                if result.mask is not None:
                    assert cv2.imwrite(str(folder/'measurement_mask.png'),result.mask)
                    diagnostic,account=native_projection(result.mask,r['input_bridge']);r['native_measurement_accounting']=account
                    path=folder/'measurement_native.png';assert cv2.imwrite(str(path),diagnostic);r['measurement_native_path']=str(path)
                if result.matrix is None:raise ValueError(result.report.get('reason','No valid mapping'))
                visible=map_visible_mask((logits>0).astype(np.uint8)*255,(256,256),result.matrix)
                preview=render_preview(image,facial,categories,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
                assert np.array_equal(image,preview.output);alpha,protected=project_alpha(preview.alpha,preview.protected,r['input_bridge'])
                np.save(folder/'correction_alpha_native.npy',alpha,allow_pickle=False)
                assert cv2.imwrite(str(folder/'protected_native.png'),protected.astype(np.uint8)*255)
                r.update(alpha_path=str(folder/'correction_alpha_native.npy'),protected_path=str(folder/'protected_native.png'),
                    correction_report=preview.report,requires_glasses_choice=preview.report['requires_glasses_choice'])
                if result.report['status']!='success':raise ValueError(result.report.get('reason','Final measurement failed'))
                if not np.any(alpha):raise ValueError('No native correction support')
                f=result.report['features'];r['raw_features']={k:f[k] for k in ('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star')}
                r.update(status='available',stage='prepared')
            except (ValueError,RuntimeError,cv2.error) as e:r.update(status='failed',stage='final_masking',reason=str(e),raw_features=None)
        usable=alpha if r['status']=='available' else np.zeros_like(alpha)
        cleanalpha=np.load(origin['alpha_path'],allow_pickle=False)
        scoring=(cleanalpha>0)|(usable>0);sp=folder/'scoring_union.png';assert cv2.imwrite(str(sp),scoring.astype(np.uint8)*255)
        r.update(reference_support_available=True,scoring_path=str(sp),scoring_policy='clean_support_union_usable_actual_input_support',
            input_region_metrics=metrics(scene,rgb(r['reference_path']),scoring),
            input_scene_metrics=metrics(scene,rgb(r['reference_path']),np.ones(scene.shape[:2],bool)))
        # Fixed before outcomes: underexposure per source + first source of each recipe.
        if r['recipe']=='exposure_under' or r['recipe'] not in first_recipes:
            first_recipes.add(r['recipe']);panels=[scene]
            for mask in (diagnostic>0,alpha>0):
                p=scene.copy();p[mask]=np.rint(.5*p[mask]+.5*np.array([0,255,0])).astype(np.uint8);panels.append(p)
            title=np.full((28,672,3),255,np.uint8);cv2.putText(title,r['case_id']+' '+r['status']+' input|measure|support DIAGNOSTIC',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
            bp=folder/'board.png';assert cv2.imwrite(str(bp),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR));boards.append(str(bp))
        records.append(r)
        if i%130==0:print('Finalized',i,'/1040',flush=True)
    generated=[r for r in records if r['recipe']!='clean'];ready=[r for r in generated if r['status']=='available']
    summary=dict(new_distorted_attempts=1040,new_distorted_available=len(ready),cached_clean_attempts=96,cached_clean_available=80,
        ledger_records=len(records),FaceOcc_forwards=run['forwards'],parser_forwards=prep['summary']['parser_forwards'],
        by_recipe={recipe:dict(attempts=sum(r['recipe']==recipe for r in generated),available=sum(r['recipe']==recipe for r in ready)) for recipe in sorted(first_recipes)},
        failure_stages=dict(Counter(r['stage'] for r in generated if r['status']!='available')),new_fits=0,holdout_image_reads=0,
        fixed_boards=len(boards),actual_skin_validity='unverified',scientific_admissions=0)
    assert len(records)==1136 and len(boards)==92 and all(sha(p)==h for p,h in bound.items())
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,boards=boards,production_adopted=False),indent=2),encoding='utf-8')
    (OUT/'final_input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    sheets=OUT/'contact_sheets';sheets.mkdir()
    for start in range(0,len(boards),4):assert cv2.imwrite(str(sheets/f'{start//4:02d}.png'),np.vstack([cv2.imread(p) for p in boards[start:start+4]]))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private fixed expanded-input mask review</h1><p>Underexposure for each source plus first source for every recipe; failed-row masks diagnostic only. Not all1040inputs visually inspected.</p>'+''.join('<img style="max-width:100%" src="'+str(Path(p).relative_to(OUT)).replace('\\','/')+'">' for p in boards),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
