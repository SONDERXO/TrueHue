"""Common native alpha/support comparison; old controls retain old provenance."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
P=ROOT/'outputs/aligned_correction_preparation_v1';M=ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json';OUT=ROOT/'outputs/aligned_action_tree_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))

def summarize(rows):
    result=dict(attempts=len(rows),mask_available=sum(r['mask_status']=='available' for r in rows),region_scored=sum(r['reference_available'] for r in rows),methods={})
    for name in ('identity','parent_controls_new_alpha','aligned_tree'):
        s=dict(prediction_available=sum(r['paths'][name]['prediction_available'] for r in rows),changed=sum(r['paths'][name]['changed_channels']>0 for r in rows))
        rr=[r for r in rows if r['reference_available']]
        s['region_harms']=sum(r['paths'][name]['region_metrics']['rgb8_mae_codes']>r['input_region_metrics']['rgb8_mae_codes'] for r in rr)
        s['region_benefits']=sum(r['paths'][name]['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes'] for r in rr)
        for region,eligible in [('region_metrics',rr),('scene_metrics',rows)]:
            for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                s[region+'_'+metric]=float(np.mean([r['paths'][name][region][metric] for r in eligible])) if eligible else None
                keys={r['subject_id'] for r in eligible}
                s['equal_key_'+region+'_'+metric]=float(np.mean([np.mean([r['paths'][name][region][metric] for r in eligible if r['subject_id']==k]) for k in keys])) if keys else None
        result['methods'][name]=s
    common=[r for r in rows if r['reference_available'] and all(r['paths'][n]['prediction_available'] for n in ('parent_controls_new_alpha','aligned_tree'))]
    result['both_predictions_region_scored']=len(common)
    result['both_predictions_region_mae']={n:float(np.mean([r['paths'][n]['region_metrics']['rgb8_mae_codes'] for r in common])) if common else None for n in ('identity','parent_controls_new_alpha','aligned_tree')}
    return result

def main():
    if OUT.exists():raise FileExistsError(OUT)
    model=read(M);prepared=read(P/'results_PRIVATE.json');pred={r['case_id']:r for r in model['predictions']}
    OLD=ROOT/'outputs/image_loss_action_tree_comparison_v1/results_PRIVATE.json'
    old={(r['suite'],r['case_id']):r for r in read(OLD)['records']}
    bound=dict(model['input_sha256']);bound.update({str(p):sha(p) for p in [M,OLD,Path(__file__),ROOT/'src/model_training/blended_recovery_targets.py',ROOT/'src/model_training/photographic_target_diagnostic.py']})
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir();records=[];boards=[];chosen=set();mst=[]
    for r in prepared['records']:
        cid=r['case_id'];folder=OUT/cid;folder.mkdir();q=pred[cid];suite='fold_working256' if r['cohort']=='development' else 'fallback_native224';prior=old[suite,cid]
        image=rgb(r['scene_path']);reference=rgb(r['reference_path']);alpha=np.load(r['alpha_path'],allow_pickle=False) if r['alpha_path'] and r['status']=='available' else np.zeros(image.shape[:2],float)
        scoring=cv2.imread(r['scoring_path'],0)>0 if r['reference_support_available'] else None
        protection=cv2.imread(r['protected_path'],0)>0 if r['protected_path'] else np.zeros(alpha.shape,bool)
        oldparams=prior['paths'].get('action_tree',{}).get('parameters') if prior['features'] is not None else None
        ready=r['status']=='available' and r['alpha_path'] is not None
        record=dict(case_id=cid,source_case=r['source_case'],subject_id=r['subject_id'],cohort=r['cohort'],recipe=r['recipe'],layer=r['layer'],mask_status=r['status'],mask_reason=r.get('reason'),
            image_path=r['scene_path'],reference_path=r['reference_path'],alpha_path=r['alpha_path'],protected_path=r['protected_path'],scoring_path=r['scoring_path'],reference_available=scoring is not None,
            input_region_metrics=r['input_region_metrics'],input_scene_metrics=r['input_scene_metrics'],new_features=q['features'],old_features=prior['features'],old_feature_suite=suite,
            mst_prediction=q['mst_prediction'],requires_glasses_choice=r.get('requires_glasses_choice'),paths={},output_paths={},scientific_admission=False)
        images={}
        for name,params in [('identity',[1.,1.,1.]),('parent_controls_new_alpha',oldparams if ready else None),('aligned_tree',q['parameters'] if ready else None)]:
            output=render_rgb8(image,alpha,params) if params is not None else image.copy()
            assert np.array_equal(output[alpha==0],image[alpha==0]) and np.array_equal(output[protection],image[protection])
            save(folder/(name+'.png'),output);images[name]=output
            record['output_paths'][name]=str(folder/(name+'.png'))
            record['paths'][name]=dict(parameters=params,prediction_available=params is not None,changed_channels=int(np.count_nonzero(output!=image)),region_metrics=metrics(output,reference,scoring) if scoring is not None else None,scene_metrics=metrics(output,reference,np.ones(alpha.shape,bool)))
        if r['recipe']=='clean' and q['mst_prediction'] is not None:
            mst.append(dict(case_id=cid,cohort=r['cohort'],subject_id=r['subject_id'],score=q['mst_prediction']['score'],label=float(r['source_mst_exact_decimal']),absolute_error=abs(q['mst_prediction']['score']-float(r['source_mst_exact_decimal']))))
        first=r['layer']!='clean' and ready and (r['cohort'],r['layer']) not in chosen
        if r['recipe']=='clean' or first or cid=='eval_22__colour_warm':
            chosen.add((r['cohort'],r['layer']));overlay=image.copy();sel=alpha>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8)
            panels=[reference,image,overlay,images['parent_controls_new_alpha'],images['aligned_tree']]
            title=np.full((30,image.shape[1]*5,3),255,np.uint8)
            cv2.putText(title,cid+' ref|input|new region|old controls+new alpha|aligned tree',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
            save(folder/'board.png',np.vstack([title,np.hstack(panels)]));boards.append(str((folder/'board.png').relative_to(OUT)))
        records.append(record)
    assert len(records)==756
    summary={c:{layer:summarize([r for r in records if r['cohort']==c and r['layer']==layer]) for layer in ('clean','core','composite_stress_design')} for c in ('development','later')}
    result=dict(summary=summary,records=records,boards=boards,clean_MST_records=mst,clean_MST_mae={c:float(np.mean([r['absolute_error'] for r in mst if r['cohort']==c])) if any(r['cohort']==c for r in mst) else None for c in ('development','later')},new_fits=0,production_adopted=False)
    write(OUT/'results_PRIVATE.json',result);write(OUT/'input_sha256_PRIVATE.json',bound);assert all(sha(p)==h for p,h in bound.items())
    sheets=OUT/'contact_sheets';sheets.mkdir()
    for start in range(0,len(boards),4):
        panels=[]
        for path in boards[start:start+4]:
            im=rgb(OUT/path);panels.append(cv2.resize(im,(1200,round(im.shape[0]*1200/im.shape[1]))))
        save(sheets/f'{start//4:02d}.png',np.vstack(panels))
    for cohort,layers in summary.items():
        for layer,s in layers.items():
            print(cohort,layer,'attempts',s['attempts'],'mask available',s['mask_available'],'region scored',s['region_scored'])
            for name,m in s['methods'].items():print(name,'MAE',m['region_metrics_rgb8_mae_codes'],'changed',m['changed'],'harms',m['region_harms'])

if __name__=='__main__':main()
