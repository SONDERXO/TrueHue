"""No-refit prospective fixed-support evaluation of the frozen bundle."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.contextual_mst_experiment import FEATURES,predict
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.model_training.split_control_candidate import predict_split
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.photographic_target_diagnostic import case_matrix,distort,metrics
from src.model_training.blended_recovery_targets import render_rgb8
P=ROOT/'outputs/frozen_split_subject_check_v1';OUT=ROOT/'outputs/frozen_split_subject_evaluation_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def save(p,a):assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
def summary(rows):
    rr=[r for r in rows if 'paths' in r];result=dict(attempts=len(rows),scored=len(rr),feature_available=sum(r.get('features') is not None for r in rows),paths={})
    for name in ['unchanged','split_ungated','split_gated']:
        result['paths'][name]=dict(harms=sum(r['paths'][name]['metrics']['rgb8_mae_codes']>r['paths']['unchanged']['metrics']['rgb8_mae_codes'] for r in rr),changed=sum(r['paths'][name]['changed_channels']>0 for r in rr))
        for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
            result['paths'][name][metric]=float(np.mean([r['paths'][name]['metrics'][metric] for r in rr])) if rr else None
            result['paths'][name]['equal_key_'+metric]=float(np.mean([np.mean([r['paths'][name]['metrics'][metric] for r in rr if r['subject_id']==k]) for k in {r['subject_id'] for r in rr}])) if rr else None
    return result
def main():
    if OUT.exists():raise FileExistsError(OUT)
    M=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json';model=read(M);sources=read(P/'results_PRIVATE.json')['records']
    assert not set(model['training_keys']) & {r['subject_key'] for r in sources}
    assert all(sha(Path(p))==h for p,h in model['input_sha256'].items())
    bound={str(P/n):h for n,h in read(P/'sha256.json').items()};bound[str(M)]=sha(M);bound[str(Path(__file__))]=sha(Path(__file__))
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir();records=[];mst=[];boards=[]
    chosen=['clean','combined_cool_under','stress_combined_over']
    for original in sources:
        sid=original['case_id'];folder=OUT/sid;folder.mkdir();source=rgb(P/sid/'source.jpeg')
        supported=original['status']=='success'
        if supported:
            reference=rgb(P/sid/'input.png');mask=cv2.imread(str(P/sid/'measurement_mask.png'),0)>0
            x0,y0,x1,y1=original['input_bridge']['native_bounds']
            ms=predict(model['ridge'],original['measurement_report']['features']);mst.append(dict(case_id=sid,subject_id=original['subject_key'],prediction=ms,label=original['source_mst_exact_decimal'],absolute_error=abs(ms['score']-float(original['source_mst_exact_decimal']))))
        for case in case_matrix():
            cid=sid+'__'+case['id'];pair=folder/case['id'];pair.mkdir();scene,recipe,role=distort(source,np.ones(source.shape[:2]),case);save(pair/'scene_input.png',scene)
            row=dict(case_id=cid,source_case=sid,subject_id=original['subject_key'],layer=case['layer'],recipe=case['id'],status='unavailable_original',features=None)
            if supported:
                image=cv2.resize(scene[y0:y1,x0:x1],(256,256),interpolation=cv2.INTER_LINEAR);save(pair/'input.png',image)
                stats=compute_masked_lab_statistics(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask.astype(np.uint8)*255)
                f=dict(zip(FEATURES,[stats['ita_degrees'],stats['mean_l_star'],stats['mean_a_star'],stats['mean_b_star']])) if stats['valid'] else None
                vector=None;prediction=None;gate=None;params=None
                if f is not None:
                    prediction=predict(model['ridge'],f);base=dict(f,input_mst_score=prediction['score']);sf=scene_features(scene)
                    vector=[base[n] for n in CONTINUOUS_FEATURES]+[sf[n] for n in SCENE_FEATURES];params=predict_split(model['split'],vector);gate=gate_decision(model['gate'],vector)
                row.update(status='available' if vector is not None else 'unavailable_features_noop',features=vector,statistics=stats,mst_prediction=prediction,gate=gate,paths={})
                images=[]
                for name,p in [('unchanged',None),('split_ungated',params),('split_gated',params if gate and gate['apply_correction'] else None)]:
                    output=render_rgb8(image,mask.astype(float),p) if p is not None else image.copy();assert np.array_equal(output[~mask],image[~mask]);save(pair/(name+'.png'),output)
                    row['paths'][name]=dict(parameters=p,metrics=metrics(output,reference,mask),changed_channels=int(np.count_nonzero(output!=image)));images.append(output)
                if case['id'] in chosen:
                    title=np.full((24,1024,3),255,np.uint8);cv2.putText(title,cid+' reference | input | ungated | gated',(4,17),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                    save(pair/'board.png',np.vstack([title,np.hstack([reference]+images)]));boards.append((cid,Path(sid)/case['id']/'board.png'))
            elif case['id'] in chosen:
                board=cv2.resize(source,(768,768));cv2.putText(board,'UNAVAILABLE: '+sid,(8,30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,0,0),2);save(pair/'board.png',board);boards.append((cid,Path(sid)/case['id']/'board.png'))
            records.append(row)
        print(sid+' evaluated, original '+original['status'],flush=True)
    result=dict(summary={layer:summary([r for r in records if r['layer']==layer]) for layer in ['clean','core','composite_stress_design']},records=records,original_mst=mst,mst_summary=dict(attempts=24,available=len(mst),mae=float(np.mean([r['absolute_error'] for r in mst])) if mst else None),new_fits=0,admissions=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><h1>Private frozen subject check</h1>'+''.join('<p>'+cid+'</p><img width="100%" src="'+p.as_posix()+'">' for cid,p in boards),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=result['summary'],mst=result['mst_summary']),indent=2))
if __name__=='__main__':main()
