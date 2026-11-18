"""Build actual-input separate masks/alpha and native scoring, without fitting."""
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
OUT=ROOT/'outputs/aligned_correction_preparation_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Finalized; no regeneration')
    plan=read(OUT/'plan_PRIVATE.json');prep=read(OUT/'preparation_PRIVATE.json');inference=read(OUT/'inference.json');request=OUT/'inference_plan.json'
    assert inference['plan_sha256']==sha(request)
    worker=read(OUT/'worker_binding_PRIVATE.json');assert all(sha(p)==h for p,h in worker['input_sha256'].items())
    bound=dict(plan['input_sha256']);bound.update(worker['input_sha256'])
    for p in [Path(__file__),OUT/'plan_PRIVATE.json',OUT/'preparation_PRIVATE.json',OUT/'inference.json',OUT/'worker_binding_PRIVATE.json']:bound[str(p)]=sha(p)
    predictions={r['image_id']:r for r in inference['records']};template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm'];rows=[]
    for old in prep['records']:
        r=dict(old,raw_features=None,measurement_contract_sha256=plan['measurement_contract_sha256'],scientific_admission=False)
        folder=OUT/'cases'/r['case_id'];scene=rgb(r['scene_path']);r['scene_features']=scene_features(scene)
        r['alpha_path']=r['protected_path']=r['measurement_native_path']=None
        if r['status']=='inference_ready':
            pred=predictions[r['case_id']]
            try:
                if pred['status']!='success':raise ValueError(pred.get('reason','FaceOcc failed'))
                lp=OUT/pred['logits_path'];assert sha(lp)==pred['logits_sha256'];bound[str(lp)]=sha(lp)
                logits=np.load(lp,allow_pickle=False);image=cv2.imread(str(folder/'input.png'));facial=cv2.imread(str(folder/'parent_mask.png'),0)
                points=np.load(folder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
                parent=SimpleNamespace(report=r['parent_report'],image=image,mask=facial)
                measurement=evaluate_parent(parent,points,template,lambda _:logits)
                r['measurement_report']=measurement.report
                if measurement.mask is not None:
                    save(folder/'measurement_mask.png',measurement.mask)
                    native,_=native_projection(measurement.mask,r['input_bridge']);save(folder/'measurement_native.png',native);r['measurement_native_path']=str(folder/'measurement_native.png')
                visible=map_visible_mask((logits>0).astype(np.uint8)*255,image.shape[:2],measurement.matrix)
                preview=render_preview(image,facial,categories,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
                assert np.array_equal(preview.output,image)
                alpha,protected=project_alpha(preview.alpha,preview.protected,r['input_bridge'])
                if not np.any(alpha):raise ValueError('No native correction support')
                np.save(folder/'correction_alpha_normalized.npy',preview.alpha,allow_pickle=False)
                np.save(folder/'correction_alpha_native.npy',alpha,allow_pickle=False)
                save(folder/'protected_native.png',protected.astype(np.uint8)*255)
                save(folder/'correction_mask_normalized.png',preview.support.correction_mask)
                save(folder/'protected_normalized.png',preview.protected.astype(np.uint8)*255)
                save(folder/'visible_face.png',visible)
                r.update(alpha_path=str(folder/'correction_alpha_native.npy'),protected_path=str(folder/'protected_native.png'),correction_report=preview.report,
                    requires_glasses_choice=preview.report['requires_glasses_choice'],correction_native_pixels=int(np.count_nonzero(alpha)),protected_native_pixels=int(protected.sum()),
                    feather_native_pixels=int(((alpha>0)&(alpha<1)).sum()))
                if measurement.report['status']!='success':raise ValueError(measurement.report.get('reason','Facial measurement failed'))
                f=measurement.report['features'];r['raw_features']={k:f[k] for k in ('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star')}
                r.update(status='available',stage='prepared')
            except (ValueError,RuntimeError,cv2.error) as e:r.update(status='failed',stage='final_masking',reason=str(e),raw_features=None)
        rows.append(r)
    clean={r['source_case']:r for r in rows if r['recipe']=='clean'}
    boards=[];chosen=set()
    for r in rows:
        folder=OUT/'cases'/r['case_id'];im=rgb(r['scene_path']);ref=rgb(r['reference_path']);origin=clean[r['source_case']]
        alpha=np.load(r['alpha_path'],allow_pickle=False) if r['alpha_path'] else np.zeros(im.shape[:2],float)
        reference_available=origin['status']=='available' and origin['alpha_path'] is not None
        scoring=(np.load(origin['alpha_path'],allow_pickle=False)>0)|(alpha>0) if reference_available else None
        r['reference_support_available']=reference_available;r['scoring_path']=None
        if scoring is not None:
            save(folder/'scoring_union.png',scoring.astype(np.uint8)*255);r['scoring_path']=str(folder/'scoring_union.png')
        r['input_region_metrics']=metrics(im,ref,scoring) if scoring is not None else None
        r['input_scene_metrics']=metrics(im,ref,np.ones(im.shape[:2],bool))
        for p in [r['scene_path'],r['reference_path'],r['alpha_path'],r['protected_path'],r['measurement_native_path'],r['scoring_path']]:
            if p is not None:bound[p]=sha(p)
        first=r['layer']!='clean' and r['status']=='available' and (r['cohort'],r['layer']) not in chosen
        if r['recipe']=='clean' or first or r['case_id']=='eval_22__colour_warm':
            chosen.add((r['cohort'],r['layer']))
            measurement=im.copy();mask=cv2.imread(r['measurement_native_path'],0)>0 if r['measurement_native_path'] else np.zeros(alpha.shape,bool)
            measurement[~mask]=35;overlay=im.copy();selected=alpha>0
            overlay[selected]=np.rint(.6*im[selected]+.4*np.array([0,255,0])).astype(np.uint8)
            protection=im.copy();guard=cv2.imread(r['protected_path'],0)>0 if r['protected_path'] else np.zeros(alpha.shape,bool)
            protection[guard]=np.rint(.6*im[guard]+.4*np.array([255,0,255])).astype(np.uint8)
            title=np.full((30,im.shape[1]*5,3),255,np.uint8)
            cv2.putText(title,r['case_id']+' '+r['status']+' ref|input|measurement|correction|protected',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.36,(0,0,0),1)
            board=folder/'mask_board.png';save(board,cv2.cvtColor(np.vstack([title,np.hstack([ref,im,measurement,overlay,protection])]),cv2.COLOR_RGB2BGR));boards.append(str(board.relative_to(OUT)))
        write(folder/'report_PRIVATE.json',r)
        for name in ('input.png','parent_mask.png','categories.png','landmarks.npy','matrix.json','measurement_mask.png','correction_alpha_normalized.npy','correction_mask_normalized.png','protected_normalized.png','visible_face.png'):
            p=folder/name
            if p.exists():bound[str(p)]=sha(p)
    summary={c:dict(attempts=sum(r['cohort']==c for r in rows),available=sum(r['cohort']==c and r['status']=='available' for r in rows),clean_available=sum(r['cohort']==c and r['recipe']=='clean' and r['status']=='available' for r in rows),region_scored=sum(r['cohort']==c and r['reference_support_available'] for r in rows)) for c in ('development','later')}
    result=dict(summary=summary,records=rows,boards=boards,measurement_contract_sha256=plan['measurement_contract_sha256'],new_predictive_fits=0,FaceOcc_forwards=inference['forwards'],production_adopted=False,training_admitted=False,calibration_admitted=False)
    write(OUT/'results_PRIVATE.json',result);write(OUT/'final_input_sha256_PRIVATE.json',bound)
    assert all(sha(p)==h for p,h in bound.items())
    sheets=OUT/'mask_contact_sheets';sheets.mkdir()
    for start in range(0,len(boards),4):
        arrays=[]
        for p in boards[start:start+4]:
            a=cv2.imread(str(OUT/p));arrays.append(cv2.resize(a,(1200,round(a.shape[0]*1200/a.shape[1]))))
        save(sheets/f'{start//4:02d}.png',np.vstack(arrays))
    print(json.dumps(summary,indent=2));print('Mask boards',len(boards),'no fits.')

if __name__=='__main__':main()
