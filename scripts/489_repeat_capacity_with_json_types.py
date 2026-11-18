"""One unlimited-depth capacity comparison against the original five-feature tree."""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.model_training.capacity_tree_candidate import fit_capacity_tree
from src.model_training.portable_tree import PortableTree
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
FEATURE_NAMES=CONTINUOUS_FEATURES
PARENT=ROOT/'outputs/nested_correction_diagnostic_v1';OUT=ROOT/'outputs/correction_capacity_comparison_v2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={str(PARENT/n):h for n,h in read(PARENT/'sha256.json').items()}
    for rel in ['src/model_training/capacity_tree_candidate.py','scripts/489_repeat_capacity_with_json_types.py','docs/correction-capacity-comparison-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    old=read(PARENT/'results_PRIVATE.json');rows={r['case_id']:r for r in read(PARENT/'prepared_rows_PRIVATE.json')}
    predictions={r['case_id']:r for r in old['records']};folds=[];records=[]
    OUT.mkdir(parents=True)
    training_checks=[]
    for f in old['folds']:
        trace=f['training_feature_trace'];x=[t['features'] for t in trace];rr=[rows[t['case_id']] for t in trace];y=[r['target'] for r in rr]
        keys=[r['subject_id'] for r in rr];layers=[r['case']['layer'] for r in rr]
        payload,model,meta=fit_capacity_tree(x,y,FEATURE_NAMES,dict(held_key=f['held_key'],single_capacity_candidate=True));tree=PortableTree(payload)
        np.testing.assert_allclose(tree.predict(x),model.predict(x)*meta['applied_scale']+meta['fitting_target_mean'],atol=1e-12,rtol=0)
        np.testing.assert_allclose(np.mean(y,axis=0),meta['fitting_target_mean'],atol=1e-12,rtol=0)
        cleanchecks=[]
        for t,r in zip(trace,rr):
            if r['case']['layer']!='clean':continue
            parameters=tree.predict_one(t['features']);folder=PARENT/r['source_case']
            image=cv2.cvtColor(cv2.imread(str(folder/'clean/input.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            output=render_rgb8(image,mask.astype(float),parameters)
            cleanchecks.append(dict(case_id=r['case_id'],parameters=parameters,exact_neutral_controls=parameters==[1.,1.,1.],changed_channels=int(np.count_nonzero(output!=image))))
        training_checks.append(dict(held_key=f['held_key'],fitting_rows=len(x),clean_checks=cleanchecks,depth=int(model.get_depth()),leaves=int(model.get_n_leaves())))
        folds.append(dict(held_key=f['held_key'],training_cases=f['training_cases'],tree=payload,normalization=meta))
        for key in f['held_cases']:
            prior=predictions[key];r=rows[key]
            if prior['status']=='unavailable_original':records.append(prior);continue
            folder=PARENT/r['source_case'];pair=folder/r['case']['id']
            image=cv2.cvtColor(cv2.imread(str(pair/'input.png')),cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(folder/'reference.png')),cv2.COLOR_BGR2RGB);mask=cv2.imread(str(folder/'mask.png'),0)>0
            vector=prior['features']
            parameters=tree.predict_one(vector) if vector is not None else None
            output=render_rgb8(image,mask.astype(float),parameters) if parameters is not None else image.copy()
            assert np.array_equal(output[~mask],image[~mask])
            path=OUT/(key+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            saved=cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB);assert np.array_equal(saved,output)
            records.append(dict(case_id=key,subject_id=r['subject_id'],layer=r['case']['layer'],status=prior['status'],parameters=parameters,features=vector,
                baseline_metrics=prior['predicted_metrics'],candidate_metrics=metrics(saved,reference,mask),input_metrics=prior['input_metrics'],changed_channel_samples=int(np.count_nonzero(saved!=image))))
    summary={}
    for layer in ['clean','core','composite_stress_design']:
        attempted=[r for r in records if r['layer']==layer];scored=[r for r in attempted if 'candidate_metrics' in r]
        report=dict(attempts=len(attempted),scored=len(scored),candidate_harm_vs_input=sum(r['candidate_metrics']['rgb8_mae_codes']>r['input_metrics']['rgb8_mae_codes'] for r in scored),
            clean_changed=sum(r['changed_channel_samples']>0 for r in scored) if layer=='clean' else None)
        for method in ['input','baseline','candidate']:
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                report[method+'_'+metric]=float(np.mean([r[method+'_metrics'][metric] for r in scored]))
                report['equal_key_'+method+'_'+metric]=float(np.mean([np.mean([r[method+'_metrics'][metric] for r in scored if r['subject_id']==key]) for key in {r['subject_id'] for r in scored}]))
        summary[layer]=report
    result=dict(summary=summary,records=records,folds=folds,feature_names=list(FEATURE_NAMES),training_checks=training_checks,new_correction_fits=10,new_mst_fits=0,new_target_fits=0,admissions=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
    assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
