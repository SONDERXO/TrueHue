"""Frozen model with per-distorted-input support, scored on common scene grid."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.contextual_mst_experiment import predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.model_training.split_control_candidate import predict_split
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
P=ROOT/'outputs/input_derived_mask_check_v1';OUT=ROOT/'outputs/input_derived_correction_v1';OLD=ROOT/'outputs/frozen_split_subject_evaluation_v1';ORIGINAL=ROOT/'outputs/frozen_split_subject_check_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def save(p,a):assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
NAMES=['unchanged','borrowed_ungated','borrowed_gated','input_ungated','input_gated']
def summarize(rows):
    summary=dict(attempts=len(rows),input_mask_success=sum(r['mask_status']=='success' for r in rows),features_available=sum(r['features'] is not None for r in rows),reference_available=sum(r['reference_available'] for r in rows),paths={})
    for name in NAMES:
        rr=[r for r in rows if r['reference_available']]
        s=dict(changed_cases=sum(r['paths'][name]['changed_channels']>0 for r in rows),reference_region_harms=sum(r['paths'][name]['reference_metrics']['rgb8_mae_codes']>r['paths']['unchanged']['reference_metrics']['rgb8_mae_codes'] for r in rr),full_scene_harms=sum(r['paths'][name]['scene_metrics']['rgb8_mae_codes']>r['paths']['unchanged']['scene_metrics']['rgb8_mae_codes'] for r in rows))
        for region in ['reference_metrics','scene_metrics']:
            scored=rr if region=='reference_metrics' else rows
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                s[region+'_'+metric]=float(np.mean([r['paths'][name][region][metric] for r in scored])) if scored else None
                s['equal_key_'+region+'_'+metric]=float(np.mean([np.mean([r['paths'][name][region][metric] for r in scored if r['subject_id']==k]) for k in {r['subject_id'] for r in scored}])) if scored else None
        summary['paths'][name]=s
    return summary

def main():
    if OUT.exists():raise FileExistsError(OUT)
    M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';model=read(M)
    old={r['case_id']:r for r in read(OLD/'results_PRIVATE.json')['records']};originals={r['case_id']:r for r in read(ORIGINAL/'results_PRIVATE.json')['records']}
    inputs=read(P/'results_PRIVATE.json')['records'];assert len(inputs)==336
    paths=[M,Path(__file__),ROOT/'docs/input-derived-mask-check-protocol-2026-11-06.md',OLD/'results_PRIVATE.json',ORIGINAL/'results_PRIVATE.json']
    bound={str(p):sha(p) for p in paths};bound.update({str(P/n):h for n,h in read(P/'sha256.json').items()});assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir();records=[];boards=[]
    for r in inputs:
        cid=r['case_id'];sid=r['source_case'];prior=old[cid];original=originals[sid];folder=OUT/cid;folder.mkdir()
        image=rgb(Path(r['source_path']));reference=rgb(ORIGINAL/sid/'source.jpeg');allmask=np.ones(image.shape[:2],bool)
        available=original['status']=='success';refmask=cv2.imread(str(ORIGINAL/sid/'native_grid.png'),0)>0 if available else np.zeros(image.shape[:2],bool)
        inputmask=cv2.imread(str(P/cid/'native_grid.png'),0)>0 if r['status']=='success' else np.zeros(image.shape[:2],bool)
        f=r.get('measurement_report',{}).get('features') if r['status']=='success' else None
        vector=None;mst=None;gate=None;parameters=None
        if f is not None:
            mst=predict(model['ridge'],f);base=dict(f,input_mst_score=mst['score']);sf=scene_features(image);vector=[base[n] for n in CONTINUOUS_FEATURES]+[sf[n] for n in SCENE_FEATURES]
            parameters=predict_split(model['split'],vector);gate=gate_decision(model['gate'],vector)
        row=dict(case_id=cid,source_case=sid,subject_id=r['subject_key'],layer=r['layer'],recipe=r['recipe'],mask_status=r['status'],mask_stage=r['stage'],reason=r.get('reason') or r.get('measurement_report',{}).get('reason'),features=vector,mst_prediction=mst,gate=gate,reference_available=available,
            predicted_native_pixels=int(inputmask.sum()),reference_native_pixels=int(refmask.sum()) if available else None,support_intersection=int((inputmask&refmask).sum()) if available else None,support_union=int((inputmask|refmask).sum()) if available else None,paths={})
        configs=[('unchanged',None,inputmask),('borrowed_ungated',prior.get('paths',{}).get('split_ungated',{}).get('parameters'),refmask),('borrowed_gated',prior.get('paths',{}).get('split_gated',{}).get('parameters'),refmask),('input_ungated',parameters,inputmask),('input_gated',parameters if gate and gate['apply_correction'] else None,inputmask)]
        rendered={}
        for name,params,mask in configs:
            output=render_rgb8(image,mask.astype(float),params) if params is not None else image.copy();assert np.array_equal(output[~mask],image[~mask]);save(folder/(name+'.png'),output);rendered[name]=output
            row['paths'][name]=dict(parameters=params,scene_metrics=metrics(output,reference,allmask),reference_metrics=metrics(output,reference,refmask) if available else None,changed_channels=int(np.count_nonzero(output!=image)),changed_native_pixels=int(np.any(output!=image,axis=2).sum()),changed_pixels_outside_reference=int((np.any(output!=image,axis=2)&~refmask).sum()) if available else None)
        if r['recipe'] in ['clean','combined_cool_under','stress_combined_over']:
            overlay=image.copy();overlay[inputmask]=np.rint(.6*image[inputmask]+.4*np.array([0,255,0])).astype(np.uint8)
            panels=[reference,image,overlay,rendered['borrowed_gated'],rendered['input_gated']];title=np.full((25,1120,3),255,np.uint8)
            cv2.putText(title,cid+' original | input | predicted mask | borrowed gated | input gated',(4,17),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
            save(folder/'board.png',np.vstack([title,np.hstack(panels)]));boards.append(cid)
        records.append(row)
        if len(records)%14==0:print(sid+' common-grid comparison saved',flush=True)
    result=dict(summary={layer:summarize([r for r in records if r['layer']==layer]) for layer in ['clean','core','composite_stress_design']},records=records,new_fits=0,admissions=0,production_adopted=False,renderer='direct original224 native-grid support',scope='development_input_derived_mask_check_NOTskin_truth')
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><h1>Private input-derived mask check</h1><p>Original | distorted input | predicted support | borrowed gated | input-derived gated. Development only.</p>'+''.join('<img width="100%" src="'+cid+'/board.png">' for cid in boards),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bound.items());(OUT/'sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(result['summary'],indent=2))
if __name__=='__main__':main()
