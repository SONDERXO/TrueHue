"""One split-head architecture comparison with frozen upstream features and gate."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.split_control_candidate import fit_split_predictors,predict_split
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
PARENT=ROOT/'outputs/whole_scene_correction_v1';GATE=ROOT/'outputs/benefit_aware_gate_v1';OUT=ROOT/'outputs/split_control_comparison_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NAMES=CONTINUOUS_FEATURES+SCENE_FEATURES


def summarize(rr):
    scored=[r for r in rr if 'paths' in r];result=dict(attempts=len(rr),scored=len(scored),paths={})
    for path in ['joint_ungated','joint_gated','split_ungated','split_gated']:
        m=dict(harm_vs_input=sum(r['paths'][path]['metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
            changed_cases=sum(r['paths'][path]['changed_channels']>0 for r in scored))
        for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
            m[metric]=float(np.mean([r['paths'][path]['metrics'][metric] for r in scored])) if scored else None
            m['equal_key_'+metric]=float(np.mean([np.mean([r['paths'][path]['metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}])) if scored else None
        result['paths'][path]=m
    return result


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={str(package/n):h for package in [PARENT,GATE] for n,h in read(package/'sha256.json').items()}
    for rel in ['scripts/502_compare_split_controls.py','src/model_training/split_control_candidate.py','docs/split-control-predictors-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    old=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    preds={r['case_id']:r for r in old['records']};gates={r['case_id']:r for r in read(GATE/'results_PRIVATE.json')['records']}
    OUT.mkdir(parents=True)
    for path in ['split_ungated','split_gated']:(OUT/path).mkdir()
    folds=[];records=[]
    for fold in old['folds']:
        trace=fold['training_feature_trace'];x=[t['features']+[rows[t['case_id']]['scene_features'][k] for k in SCENE_FEATURES] for t in trace]
        y=[rows[t['case_id']]['target'] for t in trace]
        payload,_=fit_split_predictors(x,y,NAMES)
        folds.append(dict(held_key=fold['held_key'],training_cases=fold['training_cases'],training_features=x,model=payload,held_cases=fold['held_cases']))
        for key in fold['held_cases']:
            r=rows[key];prior=preds[key];g=gates[key]
            if prior['methods'] is None:
                records.append(dict(case_id=key,source_case=r['source_case'],subject_id=r['subject_id'],layer=r['case']['layer'],recipe=r['case']['id'],status='unavailable_original'));continue
            folder=PARENT/r['source_case'];pair=folder/r['case']['id'];image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB)
            reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            vector=prior['methods']['face_plus_scene']['features'];parameters=predict_split(payload,vector) if vector is not None else None
            apply=g['gate'] is not None and g['gate']['apply_correction'];gated=parameters if apply and parameters is not None else [1.,1.,1.]
            record=dict(case_id=key,source_case=r['source_case'],subject_id=r['subject_id'],layer=r['case']['layer'],recipe=r['case']['id'],
                status='available' if vector is not None else 'unavailable_features_noop',features=vector,gate=g['gate'],input_metrics=prior['input_metrics'],paths={})
            joint=cv2.cvtColor(cv2.imread(str(pair/'face_plus_scene.png')),cv2.COLOR_BGR2RGB);joint_gated=cv2.cvtColor(cv2.imread(str(GATE/(key+'.png'))),cv2.COLOR_BGR2RGB)
            for name,params in [('split_ungated',parameters),('split_gated',gated)]:
                output=render_rgb8(image,mask.astype(float),params) if params is not None else image.copy()
                assert np.array_equal(output[~mask],image[~mask]);assert cv2.imwrite(str(OUT/name/(key+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                if name=='split_gated' and not apply:assert np.array_equal(output,image)
                record['paths'][name]=dict(parameters=params,metrics=metrics(output,reference,mask),changed_channels=int(np.count_nonzero(output!=image)))
            record['paths']['joint_ungated']=dict(parameters=prior['methods']['face_plus_scene']['parameters'],metrics=prior['methods']['face_plus_scene']['metrics'],changed_channels=int(np.count_nonzero(joint!=image)))
            record['paths']['joint_gated']=dict(parameters=g['parameters'],metrics=g['metrics'],changed_channels=g['changed_channels'])
            records.append(record)
        print('split predictors held '+fold['held_key']+' complete',flush=True)
    mild={}
    indexed={r['case_id']:r for r in records}
    for recipe in ['colour_cool','colour_warm']:
        rr=[r for r in records if r['recipe']==recipe and 'paths' in r];targets=[rows[r['case_id']]['target'][0] for r in rr]
        prediction=[r['paths']['split_ungated']['parameters'][0] for r in rr]
        mild[recipe]=dict(summary=summarize(rr),target_gamma_range=[min(targets),max(targets)],split_predicted_gamma_range=[min(prediction),max(prediction)],
            same_controls_as_clean=sum(r['paths']['split_ungated']['parameters']==indexed[r['source_case']+'__clean']['paths']['split_ungated']['parameters'] for r in rr))
    result=dict(summary={layer:summarize([r for r in records if r['layer']==layer]) for layer in ['clean','core','composite_stress_design']},
        mild_casts=mild,exposure_recipes={recipe:summarize([r for r in records if r['recipe']==recipe]) for recipe in ['exposure_under','exposure_over']},
        folds=folds,records=records,new_head_tree_fits=20,gate_decisions_reused=True,new_gate_fits=0,new_mst_fits=0,new_target_fits=0,admissions=0,production_adopted=False)
    for name,value in [('results_PRIVATE.json',result),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'sha256.json').write_text(json.dumps({str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(result['summary'],indent=2),flush=True)


if __name__=='__main__':main()
