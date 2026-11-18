"""No-refit audit of matched scene gates and shared correction outputs."""
import hashlib,json,math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.ita_estimation.contextual_mst_experiment import predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
PARENT=ROOT/'outputs/whole_scene_correction_v1';CAND=ROOT/'outputs/scene_gate_comparison_v1';OUT=ROOT/'outputs/scene_gate_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    v=read(CAND/'results_PRIVATE.json');old=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    preds={r['case_id']:r for r in old['records']};folds={f['held_key']:f for f in v['folds']}
    mappings=read(ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json')['mapping_models']
    traces=scalechecks=logitchecks=renderchecks=0
    for held,fold in folds.items():
        expected={k for k,r in rows.items() if r['subject_id']!=held and r['features'] is not None}
        assert {r['case_id'] for r in fold['training_trace']}==expected
        for t in fold['training_trace']:
            r=rows[t['case_id']];model=mappings[t['mapping_id']]
            assert not {held,r['subject_id']}&set(model['training_keys'])
            mst=predict(model['model'],r['features']);features=dict(r['features'],input_mst_score=mst['score'])
            assert t['facial_features']==[features[k] for k in CONTINUOUS_FEATURES]
            assert t['scene_features']==[r['scene_features'][k] for k in SCENE_FEATURES] and t['label']==int(r['case']['layer']!='clean');traces+=1
        for method,art in fold['models'].items():
            trace=fold['training_trace'];model=art['model'];assert held not in model['training_keys']
            x=np.array([r['facial_features']+(r['scene_features'] if method=='scene_gate' else []) for r in trace]);w=np.array(model['weights'])
            mu=np.average(x,axis=0,weights=w);mu=np.where(np.ptp(x,axis=0)==0,x[0],mu)
            sd=np.sqrt(np.average((x-mu)**2,axis=0,weights=w));sd=np.where(sd==0,1.,sd)
            np.testing.assert_allclose(mu,model['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(sd,model['scale'],atol=1e-12,rtol=0)
            for key in model['training_keys']:
                for label in [0,1]:
                    assert abs(sum(w[i] for i,t in enumerate(trace) if t['subject_id']==key and t['label']==label)-len(trace)/(2*len(model['training_keys'])))<1e-10
            scalechecks+=1
    indexed={method:{r['case_id']:r for r in rr} for method,rr in v['records'].items()};confusions={}
    for method,rr in v['records'].items():
        fp=fn=0
        for r in rr:
            if r['status']=='unavailable_original':assert r['gate'] is None;continue
            row=rows[r['case_id']];folder=PARENT/row['source_case'];pair=folder/row['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            if r['gate'] is not None:
                art=folds[r['subject_id']]['models'][method]['model'];vector=preds[r['case_id']]['methods']['face_only' if method=='face_gate' else 'face_plus_scene']['features'];assert vector==r['features']
                logit=math.fsum((float(x)-mean)/sd*c for x,mean,sd,c in zip(vector,art['mean'],art['scale'],art['coefficient']))+art['intercept']
                assert abs(logit-r['gate']['logit'])<1e-12;apply=logit>0;assert apply==r['gate']['apply_correction'];logitchecks+=1
                fp+=r['layer']=='clean' and apply;fn+=r['layer']!='clean' and not apply
                expected=preds[r['case_id']]['methods']['face_plus_scene']['parameters'] if apply else [1.,1.,1.]
                assert r['parameters']==expected
            else:assert r['parameters']==[1.,1.,1.]
            replay=render_rgb8(image,mask.astype(float),r['parameters']);saved=cv2.cvtColor(cv2.imread(str(CAND/method/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
            assert np.array_equal(replay,saved) and np.array_equal(saved[~mask],image[~mask]);assert metrics(saved,reference,mask)==r['metrics'];renderchecks+=1
            if r['gate'] is None or not r['gate']['apply_correction']:assert np.array_equal(saved,image)
        assert fp==v['summary'][method]['confusion']['clean_false_positive'] and fn==v['summary'][method]['confusion']['synthetic_false_negative']
        confusions[method]=dict(false_positive=fp,false_negative=fn)
    boards=[]
    for key,row in rows.items():
        if row['case']['id'] not in ['clean','combined_cool_under','stress_combined_under']:continue
        folder=PARENT/row['source_case'];pair=folder/row['case']['id']
        if row['status']=='unavailable_original':
            scene=cv2.imread(str(pair/'scene_input.png'));board=np.full((176,800,3),255,np.uint8);board[:160,:160]=cv2.resize(scene,(160,160));cv2.putText(board,key+' unavailable original',(168,30),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        else:
            images=[cv2.imread(str(folder/'reference.png')),cv2.imread(str(pair/'input.png')),cv2.imread(str(pair/'face_plus_scene.png')),
                    cv2.imread(str(CAND/'face_gate'/(key+'.png'))),cv2.imread(str(CAND/'scene_gate'/(key+'.png')))]
            board=np.concatenate([cv2.resize(im,(160,160),interpolation=cv2.INTER_NEAREST) for im in images],axis=1)
            label=np.full((28,800,3),255,np.uint8);cv2.putText(label,key+' ref/input/ungated/facegate/scenegate',(2,20),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1);board=np.concatenate([label,board])
        # Equal height for retained original-failure boards.
        if board.shape[0]!=188:board=cv2.copyMakeBorder(board,0,188-board.shape[0],0,0,cv2.BORDER_CONSTANT,value=(255,255,255))
        boards.append(board)
    for n,h in read(CAND/'input_sha256_PRIVATE.json').items():assert sha(Path(n))==h
    for n,h in read(CAND/'sha256.json').items():assert sha(CAND/n)==h
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'contact_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    report=dict(nested_training_trace_checks=traces,weighted_scaling_and_class_mass_checks=scalechecks,independent_held_logits=logitchecks,
        renderer_metric_replays=renderchecks,independent_confusion=confusions,preselected_boards=len(boards),refits=0,all_sources_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
