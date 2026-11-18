"""One fixed key-held gate experiment; no new upstream or correction-tree fits."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.correction_gate_candidate import fit_gate,gate_decision
from src.ita_estimation.contextual_mst_experiment import predict
from src.correction.continuous_mst_candidate import continuous_model_features,CONTINUOUS_FEATURES
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1';OUT=ROOT/'outputs/correction_gate_experiment_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def confusion(rr):
    available=[r for r in rr if r.get('gate') is not None]
    clean=[r for r in available if r['layer']=='clean'];distorted=[r for r in available if r['layer']!='clean']
    fp=sum(r['gate']['apply_correction'] for r in clean);fn=sum(not r['gate']['apply_correction'] for r in distorted)
    return dict(attempts=len(rr),available_decisions=len(available),unavailable=len(rr)-len(available),
        clean_available=len(clean),clean_false_positive_corrections=fp,clean_true_negative_noops=len(clean)-fp,
        synthetic_available=len(distorted),synthetic_false_negative_noops=fn,synthetic_true_positive_corrections=len(distorted)-fn,
        clean_false_positive_rate=fp/len(clean) if clean else None,synthetic_miss_rate=fn/len(distorted) if distorted else None,
        always_correct_baseline=dict(clean_false_positives=len(clean),synthetic_false_negatives=0),
        always_unchanged_baseline=dict(clean_false_positives=0,synthetic_false_negatives=len(distorted)))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={str(PARENT/n):h for n,h in read(PARENT/'sha256.json').items()}
    for rel in ['scripts/492_run_correction_gate.py','src/model_training/correction_gate_candidate.py','docs/correction-gate-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    plan=read(PARENT/'plan_PRIVATE.json');old=read(PARENT/'results_PRIVATE.json');rows=read(PARENT/'prepared_rows_PRIVATE.json')
    preds={r['case_id']:r for r in old['records']};mapping=old['mapping_models'];folds=[];records=[]
    OUT.mkdir(parents=True)
    for fold in old['folds']:
        held=fold['held_key'];train=[];x=[];labels=[];keys=[]
        for r in rows:
            if r['subject_id']==held or r['features'] is None:continue
            mid='|'.join(sorted({held,r['subject_id']}));model=mapping[mid]
            assert not {held,r['subject_id']}&set(model['training_keys'])
            mst=predict(model['model'],r['features']);f=continuous_model_features(r['features'],mst,
                measurement_contract_sha256=plan['contract_sha256'],estimator_measurement_contract_sha256=plan['contract_sha256'])
            vector=[f[k] for k in CONTINUOUS_FEATURES];label=int(r['case']['layer']!='clean')
            x.append(vector);labels.append(label);keys.append(r['subject_id']);train.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],mapping_id=mid,features=vector,label=label))
        payload,model=fit_gate(x,labels,keys)
        exported=np.array([gate_decision(payload,vector)['logit'] for vector in x])
        np.testing.assert_allclose(exported,model.decision_function((np.array(x)-payload['mean'])/payload['scale']),atol=1e-12,rtol=0)
        folds.append(dict(held_key=held,training_trace=train,model=payload,feature_names=list(CONTINUOUS_FEATURES),held_cases=fold['held_cases']))
        for key in fold['held_cases']:
            prior=preds[key];r=next(r for r in rows if r['case_id']==key)
            if prior['status']=='unavailable_original':
                records.append(dict(case_id=key,subject_id=held,condition=r['condition'],layer=r['case']['layer'],status='unavailable_original',gate=None));continue
            folder=PARENT/r['source_case'];pair=folder/r['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
            ref=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            decision=gate_decision(payload,prior['features']) if prior['features'] is not None else None
            apply=decision is not None and decision['apply_correction'];parameters=prior['parameters'] if apply else [1.,1.,1.]
            output=render_rgb8(image,mask.astype(float),parameters)
            assert np.array_equal(output[~mask],image[~mask])
            if not apply:assert np.array_equal(output,image)
            assert cv2.imwrite(str(OUT/(key+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            records.append(dict(case_id=key,subject_id=held,condition=r['condition'],layer=r['case']['layer'],
                status='correction_applied' if apply else 'gate_noop' if decision is not None else 'unavailable_features_noop',gate=decision,
                features=prior['features'],parameters=parameters,input_metrics=prior['input_metrics'],ungated_metrics=prior['predicted_metrics'],
                gated_metrics=metrics(output,ref,mask),changed_channel_samples=int(np.count_nonzero(output!=image))))
    summary={}
    for layer in ['clean','core','composite_stress_design']:
        attempted=[r for r in records if r['layer']==layer];scored=[r for r in attempted if 'gated_metrics' in r]
        report=dict(attempts=len(attempted),scored=len(scored),changed_clean=sum(r['changed_channel_samples']>0 for r in scored) if layer=='clean' else None,
            gated_harm_vs_input=sum(r['gated_metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored))
        for method in ['input','ungated','gated']:
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                report[method+'_'+metric]=float(np.mean([r[method+'_metrics'][metric] for r in scored]))
                report['equal_key_'+method+'_'+metric]=float(np.mean([np.mean([r[method+'_metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}]))
        summary[layer]=report
    result=dict(summary=summary,confusion=confusion(records),by_condition={c:confusion([r for r in records if r['condition']==c]) for c in sorted({r['condition'] for r in records})},
        by_layer={layer:confusion([r for r in records if r['layer']==layer]) for layer in summary},
        records=records,folds=folds,gate_fits=10,new_mst_fits=0,new_correction_tree_fits=0,new_target_fits=0,admissions=0,production_adopted=False)
    for name,value in [('results_PRIVATE.json',result),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(dict(confusion=result['confusion'],summary=summary),indent=2))


if __name__=='__main__':main()
