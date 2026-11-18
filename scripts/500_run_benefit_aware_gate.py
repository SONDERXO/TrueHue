"""One leakage-separated correction-benefit gate experiment; no outer-label reuse."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from collections import Counter
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.contextual_mst_experiment import FEATURES,_ridge,predict
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.whole_scene_features import SCENE_FEATURES
from src.model_training.target_scaled_tree import fit_target_scaled_tree
from src.model_training.portable_tree import PortableTree
from src.model_training.correction_gate_candidate import fit_gate,gate_decision
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
PARENT=ROOT/'outputs/whole_scene_correction_v1';PRIOR=ROOT/'outputs/scene_gate_comparison_v1';OUT=ROOT/'outputs/benefit_aware_gate_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
NAMES=CONTINUOUS_FEATURES+SCENE_FEATURES


def main():
    if OUT.exists():raise FileExistsError(OUT)
    mappings_path=ROOT/'outputs/nested_correction_diagnostic_v1/results_PRIVATE.json'
    originals_path=ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json'
    bindings={str(package/n):h for package in [PARENT,PRIOR] for n,h in read(package/'sha256.json').items()}
    for p in [mappings_path,originals_path]:bindings[str(p)]=sha(p)
    for rel in ['scripts/500_run_benefit_aware_gate.py','docs/benefit-aware-gate-protocol-2026-11-06.md',
        'src/ita_estimation/contextual_mst_experiment.py','src/model_training/target_scaled_tree.py','src/model_training/correction_gate_candidate.py']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    rows=read(PARENT/'prepared_rows_PRIVATE.json');indexed={r['case_id']:r for r in rows};parent=read(PARENT/'results_PRIVATE.json');outer_preds={r['case_id']:r for r in parent['records']}
    prior={r['case_id']:r for r in read(PRIOR/'results_PRIVATE.json')['records']['scene_gate']}
    originals={r['case_id']:r for r in read(originals_path)['records']}
    clean=[]
    for r in rows:
        if r['case']['id']=='clean' and r['features'] is not None:
            o=originals[r['source_case']]
            assert all(r['features'][k]==o['measurement_report']['features'][k] for k in FEATURES)
            clean.append(dict(case_id=r['source_case'],subject_id=r['subject_id'],source_mst_exact_decimal=o['source_mst_exact_decimal'],features=r['features']))
    original_mst=read(mappings_path)['mapping_models'];new_mst={};correctors={};runtime_trees={}
    def mst(excluded):
        key='|'.join(sorted(excluded))
        if key in original_mst:return key,original_mst[key]['model']
        if key not in new_mst:
            train=[r for r in clean if r['subject_id'] not in excluded]
            assert len(excluded)==3 and len({r['subject_id'] for r in train})==7
            new_mst[key]=dict(excluded_keys=sorted(excluded),training_cases=[r['case_id'] for r in train],training_keys=sorted({r['subject_id'] for r in train}),model=_ridge(train,FEATURES))
        return key,new_mst[key]['model']
    def vector(r,excluded):
        mid,model=mst(excluded);p=predict(model,r['features']);f=dict(r['features'],input_mst_score=p['score'])
        return mid,[f[k] for k in CONTINUOUS_FEATURES]+[r['scene_features'][k] for k in SCENE_FEATURES]
    def corrector(excluded):
        key='|'.join(sorted(excluded))
        if key not in correctors:
            trace=[];x=[];y=[]
            for r in rows:
                if r['subject_id'] in excluded or r['features'] is None or r['target'] is None:continue
                mid,vec=vector(r,excluded|{r['subject_id']});x.append(vec);y.append(r['target']);trace.append(dict(case_id=r['case_id'],mapping_id=mid,features=vec))
            payload,model,meta=fit_target_scaled_tree(x,y,NAMES,dict(excluded_keys=sorted(excluded),benefit_label_corrector_only=True))
            tree=PortableTree(payload);np.testing.assert_allclose(tree.predict(x),model.predict(x)*meta['applied_scale']+meta['fitting_target_mean'],atol=1e-12,rtol=0)
            correctors[key]=dict(excluded_keys=sorted(excluded),training_trace=trace,tree=payload,normalization=meta)
            runtime_trees[key]=tree
        return key,runtime_trees[key]
    cache={}
    def pixels(r):
        key=r['case_id']
        if key not in cache:
            folder=PARENT/r['source_case'];pair=folder/r['case']['id']
            cache[key]=(cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB),
                cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB),cv2.imread(str(folder/'mask.png'),0)>0)
        return cache[key]
    OUT.mkdir(parents=True)
    write(OUT/'plan_PRIVATE.json',dict(input_sha256=bindings,status='frozen_before_fits',benefit_rule='strict positive RGB8 MAE reduction',feature_names=list(NAMES)))
    folds=[];records=[];gatefits=0
    for outer in parent['folds']:
        held=outer['held_key'];trace=[];x=[];labels=[];keys=[]
        for r in rows:
            if r['subject_id']==held or r['features'] is None:continue
            excluded={held,r['subject_id']};cid,tree=corrector(excluded);mid,vec=vector(r,excluded)
            controls=tree.predict_one(vec);image,reference,mask=pixels(r);output=render_rgb8(image,mask.astype(float),controls)
            error=float(np.abs(output[mask].astype(float)-reference[mask]).mean());input_error=r['input_metrics']['rgb8_mae_codes'];label=int(input_error>error)
            x.append(vec);labels.append(label);keys.append(r['subject_id'])
            trace.append(dict(case_id=r['case_id'],subject_id=r['subject_id'],inner_corrector_id=cid,mapping_id=mid,
                features=vec,predicted_parameters=controls,input_mae=input_error,inner_predicted_mae=error,label=label))
        counts=Counter(zip(keys,labels));allkeys=set(keys);missing=[k for k in allkeys if any((k,c) not in counts for c in (0,1))]
        if missing:gate=None;reason='benefit_class_unavailable_for_training_key'
        else:
            gate,model=fit_gate(x,labels,keys);gatefits+=1;reason=None
            np.testing.assert_allclose([gate_decision(gate,v)['logit'] for v in x],model.decision_function((np.array(x)-gate['mean'])/gate['scale']),atol=1e-12,rtol=0)
        folds.append(dict(held_key=held,training_trace=trace,model=gate,unavailable_reason=reason,missing_class_keys=missing,held_cases=outer['held_cases']))
        for key in outer['held_cases']:
            r=indexed[key];p=outer_preds[key]
            if p['methods'] is None:
                records.append(dict(case_id=key,subject_id=held,layer=r['case']['layer'],condition=r['condition'],status='unavailable_original',gate=None));continue
            f=p['methods']['face_plus_scene']['features'];decision=gate_decision(gate,f) if gate is not None and f is not None else None
            apply=decision is not None and decision['apply_correction'];controls=p['methods']['face_plus_scene']['parameters'] if apply else [1.,1.,1.]
            image,reference,mask=pixels(r);output=render_rgb8(image,mask.astype(float),controls)
            assert np.array_equal(output[~mask],image[~mask])
            if not apply:assert np.array_equal(output,image)
            assert cv2.imwrite(str(OUT/(key+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            ungated=p['methods']['face_plus_scene']['metrics'];outer_gain=p['input_metrics']['rgb8_mae_codes']-ungated['rgb8_mae_codes']
            records.append(dict(case_id=key,subject_id=held,layer=r['case']['layer'],condition=r['condition'],
                status='applied' if apply else 'noop' if decision is not None else 'unavailable_noop',gate=decision,features=f,parameters=controls,
                input_metrics=p['input_metrics'],ungated_metrics=ungated,prior_metrics=prior[key]['metrics'],
                metrics=metrics(output,reference,mask),outer_correction_gain_for_evaluation_only=outer_gain,changed_channels=int(np.count_nonzero(output!=image))))
        print('outer benefit gate '+held+' complete',flush=True)
    summary={}
    for layer in ['clean','core','composite_stress_design']:
        attempted=[r for r in records if r['layer']==layer];scored=[r for r in attempted if 'metrics' in r];available=[r for r in scored if r['gate'] is not None]
        info=dict(attempts=len(attempted),scored=len(scored),available_gate_decisions=len(available),
            harm_vs_input=sum(r['metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
            clean_changed=sum(r['changed_channels']>0 for r in scored) if layer=='clean' else None,
            useful_corrections_missed=sum(not r['gate']['apply_correction'] and r['outer_correction_gain_for_evaluation_only']>0 for r in available),
            harmful_corrections_avoided=sum(not r['gate']['apply_correction'] and r['outer_correction_gain_for_evaluation_only']<0 for r in available),
            synthetic_membership_misses=sum(not r['gate']['apply_correction'] for r in available) if layer!='clean' else None)
        for method in ['input_metrics','ungated_metrics','prior_metrics','metrics']:
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                info[method+'_'+metric]=float(np.mean([r[method][metric] for r in scored]))
                info['equal_key_'+method+'_'+metric]=float(np.mean([np.mean([r[method][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}]))
        summary[layer]=info
    result=dict(summary=summary,folds=folds,records=records,new_mst_models=new_mst,inner_correctors=correctors,
        new_mst_fits=len(new_mst),inner_correction_tree_fits=len(correctors),gate_fits=gatefits,new_outer_correction_fits=0,new_target_fits=0,admissions=0,production_adopted=False)
    write(OUT/'results_PRIVATE.json',result)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    write(OUT/'sha256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps(dict(summary=summary,new_mst_fits=len(new_mst),inner_corrector_fits=len(correctors),gate_fits=gatefits),indent=2),flush=True)


if __name__=='__main__':main()
