"""No-refit nested gate/scaling/logit, operational renderer and confusion audit."""
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
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1';CAND=ROOT/'outputs/correction_gate_experiment_v1';OUT=ROOT/'outputs/correction_gate_assessment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    v=read(CAND/'results_PRIVATE.json');old=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    preds={r['case_id']:r for r in old['records']};folds={f['held_key']:f for f in v['folds']};tracechecks=0
    for held,f in folds.items():
        model=f['model'];trace=f['training_trace'];x=np.array([r['features'] for r in trace]);weights=np.array(model['weights'])
        expected={k for k,r in rows.items() if r['subject_id']!=held and r['features'] is not None}
        assert {r['case_id'] for r in trace}==expected and held not in model['training_keys']
        for t in trace:
            r=rows[t['case_id']];m=old['mapping_models'][t['mapping_id']]
            assert not {held,r['subject_id']}&set(m['training_keys'])
            assert t['label']==int(r['case']['layer']!='clean')
            p=predict(m['model'],r['features']);expected_f=dict(r['features'],input_mst_score=p['score'])
            assert t['features']==[expected_f[k] for k in CONTINUOUS_FEATURES];tracechecks+=1
        mean=np.average(x,axis=0,weights=weights);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean)
        scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=weights));scale=np.where(scale==0,1.,scale)
        np.testing.assert_allclose(mean,model['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(scale,model['scale'],atol=1e-12,rtol=0)
        for key in model['training_keys']:
            for label in [0,1]:
                mass=sum(weights[i] for i,r in enumerate(trace) if r['subject_id']==key and r['label']==label)
                assert abs(mass-len(trace)/(2*len(model['training_keys'])))<1e-10
    boards=[];replays=0;logits=0;fp=fn=0
    for r in v['records']:
        source=rows[r['case_id']]
        if r['status']=='unavailable_original':assert r['gate'] is None;continue
        folder=PARENT/source['source_case'];pair=folder/source['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
        if r['gate'] is not None:
            model=folds[r['subject_id']]['model'];vector=preds[r['case_id']]['features'];assert vector==r['features']
            logit=math.fsum((float(x)-mu)/sd*c for x,mu,sd,c in zip(vector,model['mean'],model['scale'],model['coefficient']))+model['intercept']
            assert abs(logit-r['gate']['logit'])<1e-12
            apply=logit>0;assert apply==r['gate']['apply_correction'];logits+=1
            fp+=r['layer']=='clean' and apply;fn+=r['layer']!='clean' and not apply
            expected=preds[r['case_id']]['parameters'] if apply else [1.,1.,1.];assert r['parameters']==expected
        else:assert r['parameters']==[1.,1.,1.]
        output=render_rgb8(image,mask.astype(float),r['parameters']);saved=cv2.cvtColor(cv2.imread(str(CAND/(r['case_id']+'.png'))),cv2.COLOR_BGR2RGB)
        assert np.array_equal(output,saved) and np.array_equal(output[~mask],image[~mask]);assert metrics(saved,reference,mask)==r['gated_metrics'];replays+=1
        if r['layer']=='clean':
            previous=cv2.cvtColor(cv2.imread(str(pair/'prediction.png')),cv2.COLOR_BGR2RGB)
            panel=np.concatenate([cv2.resize(cv2.cvtColor(im,cv2.COLOR_RGB2BGR),(160,160),interpolation=cv2.INTER_NEAREST) for im in [reference,previous,saved]],axis=1)
            title=np.full((27,480,3),255,np.uint8);cv2.putText(title,source['source_case']+' original / ungated / gated',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);boards.append(np.concatenate([title,panel]))
    assert fp==v['confusion']['clean_false_positive_corrections'] and fn==v['confusion']['synthetic_false_negative_noops']
    for n,h in read(CAND/'input_sha256_PRIVATE.json').items():assert sha(Path(n))==h
    for n,h in read(CAND/'sha256.json').items():assert sha(CAND/n)==h
    OUT.mkdir(parents=True)
    for i in range(0,len(boards),10):cv2.imwrite(str(OUT/f'clean_{i//10+1:02d}_PRIVATE.png'),np.concatenate(boards[i:i+10]))
    report=dict(nested_training_feature_checks=tracechecks,weighted_scaling_and_mass_checks=10,independent_held_logit_checks=logits,
        renderer_metric_replays=replays,independent_clean_false_positives=fp,independent_synthetic_false_negatives=fn,refits=0,source_hashes_unchanged=True)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
