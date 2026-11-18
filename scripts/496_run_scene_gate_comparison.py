"""Twenty fixed gates, matched data and one shared saved scene-aware corrector."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.correction_gate_candidate import fit_gate,gate_decision
from src.ita_estimation.contextual_mst_experiment import predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
PARENT=ROOT/'outputs/whole_scene_correction_v1';OUT=ROOT/'outputs/scene_gate_comparison_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def confusion(records):
    available=[r for r in records if r.get('gate') is not None];clean=[r for r in available if r['layer']=='clean'];distorted=[r for r in available if r['layer']!='clean']
    fp=sum(r['gate']['apply_correction'] for r in clean);fn=sum(not r['gate']['apply_correction'] for r in distorted)
    return dict(attempts=len(records),available=len(available),unavailable=len(records)-len(available),
        clean_available=len(clean),clean_false_positive=fp,clean_noop=len(clean)-fp,
        synthetic_available=len(distorted),synthetic_false_negative=fn,synthetic_detected=len(distorted)-fn,
        clean_false_positive_rate=fp/len(clean) if clean else None,synthetic_miss_rate=fn/len(distorted) if distorted else None,
        always_correct_clean_false_positive=len(clean),always_unchanged_synthetic_false_negative=len(distorted))


def main():
    if OUT.exists():raise FileExistsError(OUT)
    upstream=ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json'
    bindings={str(PARENT/n):h for n,h in read(PARENT/'sha256.json').items()};bindings[str(upstream)]=sha(upstream)
    for rel in ['scripts/496_run_scene_gate_comparison.py','src/model_training/correction_gate_candidate.py','docs/scene-aware-gate-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    old=read(PARENT/'results_PRIVATE.json');rows=read(PARENT/'prepared_rows_PRIVATE.json');preds={r['case_id']:r for r in old['records']}
    mappings=read(upstream)['mapping_models'];folds=[];records=dict(face_gate=[],scene_gate=[])
    OUT.mkdir(parents=True)
    for method in records:(OUT/method).mkdir()
    for fold in old['folds']:
        held=fold['held_key'];traces=[]
        for r in rows:
            if r['subject_id']==held or r['features'] is None:continue
            mid='|'.join(sorted({held,r['subject_id']}));m=mappings[mid];assert not {held,r['subject_id']}&set(m['training_keys'])
            mst=predict(m['model'],r['features']);f=dict(r['features'],input_mst_score=mst['score'])
            traces.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],label=int(r['case']['layer']!='clean'),mapping_id=mid,
                facial_features=[f[k] for k in CONTINUOUS_FEATURES],scene_features=[r['scene_features'][k] for k in SCENE_FEATURES]))
        pair={}
        for method in records:
            x=[t['facial_features']+(t['scene_features'] if method=='scene_gate' else []) for t in traces]
            payload,model=fit_gate(x,[t['label'] for t in traces],[t['subject_id'] for t in traces])
            np.testing.assert_allclose([gate_decision(payload,v)['logit'] for v in x],model.decision_function((np.array(x)-payload['mean'])/payload['scale']),atol=1e-12,rtol=0)
            pair[method]=dict(model=payload,feature_names=list(CONTINUOUS_FEATURES+(SCENE_FEATURES if method=='scene_gate' else ())))
        folds.append(dict(held_key=held,training_trace=traces,held_cases=fold['held_cases'],models=pair))
        for key in fold['held_cases']:
            prior=preds[key];r=next(r for r in rows if r['case_id']==key)
            if prior['methods'] is None:
                for method in records:records[method].append(dict(case_id=key,subject_id=held,condition=r['condition'],layer=r['case']['layer'],status='unavailable_original',gate=None))
                continue
            folder=PARENT/r['source_case'];path=folder/r['case']['id'];image=cv2.cvtColor(cv2.imread(str(path/'input.png')),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            for method,art in pair.items():
                features=prior['methods']['face_only' if method=='face_gate' else 'face_plus_scene']['features']
                gate=gate_decision(art['model'],features) if features is not None else None
                apply=gate is not None and gate['apply_correction'];parameters=prior['methods']['face_plus_scene']['parameters'] if apply else [1.,1.,1.]
                output=render_rgb8(image,mask.astype(float),parameters);assert np.array_equal(output[~mask],image[~mask])
                if not apply:assert np.array_equal(output,image)
                assert cv2.imwrite(str(OUT/method/(key+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records[method].append(dict(case_id=key,subject_id=held,condition=r['condition'],layer=r['case']['layer'],features=features,gate=gate,
                    status='applied' if apply else 'noop' if gate is not None else 'unavailable_features_noop',parameters=parameters,
                    input_metrics=prior['input_metrics'],ungated_metrics=prior['methods']['face_plus_scene']['metrics'],
                    metrics=metrics(output,reference,mask),changed_channels=int(np.count_nonzero(output!=image))))
    summaries={}
    for method,rr in records.items():
        layers={}
        for layer in ['clean','core','composite_stress_design']:
            attempted=[r for r in rr if r['layer']==layer];scored=[r for r in attempted if 'metrics' in r]
            report=dict(attempts=len(attempted),scored=len(scored),harm_vs_input=sum(r['metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
                clean_changed=sum(r['changed_channels']>0 for r in scored) if layer=='clean' else None)
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                report[metric]=float(np.mean([r['metrics'][metric] for r in scored]))
                report['equal_key_'+metric]=float(np.mean([np.mean([r['metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}]))
            layers[layer]=report
        summaries[method]=dict(confusion=confusion(rr),layers=layers,
            by_condition={c:confusion([r for r in rr if r['condition']==c]) for c in sorted({r['condition'] for r in rr})},
            by_layer={l:confusion([r for r in rr if r['layer']==l]) for l in layers})
    result=dict(summary=summaries,folds=folds,records=records,gate_fits=20,new_mst_fits=0,new_correction_tree_fits=0,new_target_fits=0,admissions=0,production_adopted=False)
    for name,value in [('results_PRIVATE.json',result),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'sha256.json').write_text(json.dumps({str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
