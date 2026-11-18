"""No-fit audit: nested training targets/equations and fixed-control action replay."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.signed_benefit_gate import signed_benefit_decision
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.split_control_candidate import predict_split
from src.model_training.blended_recovery_targets import render_rgb8
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def equation(model,x,y,keys):
    x=np.array(x);y=np.array(y);w=np.array(model['weights']);mean=np.average(x,axis=0,weights=w);mean=np.where(np.ptp(x,axis=0)==0,x[0],mean);scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=w));scale=np.where(scale==0,1.,scale)
    np.testing.assert_allclose(mean,model['mean'],atol=1e-12,rtol=0);np.testing.assert_allclose(scale,model['scale'],atol=1e-12,rtol=0);z=(x-mean)/scale;intercept=np.average(y,weights=w);assert abs(intercept-model['intercept'])<1e-12
    np.testing.assert_allclose((z.T@(w[:,None]*z)+np.eye(x.shape[1]))@np.array(model['coefficient']),z.T@(w*(y-intercept)),atol=1e-8,rtol=1e-10)
    for k in set(keys):
        for sign in [False,True]:assert np.isclose(sum(w[i] for i in range(len(x)) if keys[i]==k and (y[i]>0)==sign),len(x)/(len(set(keys))*2))
def main():
    E=ROOT/'outputs/signed_benefit_gate_comparison_v1';O=ROOT/'outputs/signed_benefit_gate_assessment_v1';M=ROOT/'outputs/signed_benefit_gate_models_v1/models_PRIVATE.json'
    if O.exists():raise FileExistsError(O)
    m=read(M);v=read(E/'results_PRIVATE.json');parent=read(ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json');original=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json');full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json');context={ (r['suite'],r['case_id']):r for r in read(ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json')['records']};table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    assert all(sha(Path(p))==h for p,h in m['input_sha256'].items());assert all(sha(Path(p))==h for p,h in read(E/'input_sha256_PRIVATE.json').items());nested=0
    for f,old in zip(m['folds'],parent['folds']):
        assert f['held_key']==old['held_key'];trace=old['training_trace'];gains=[t['input_mae']-t['inner_predicted_mae'] for t in trace];assert gains==f['training_signed_benefits'];assert [t['case_id'] for t in trace]==f['training_cases'];equation(f['model'],[t['features'] for t in trace],gains,[t['subject_id'] for t in trace]);assert f['model']['weights']==old['model']['weights']
        for t,gain in zip(trace,gains):
            excluded={f['held_key'],t['subject_id']};assert len(excluded)==2 and set(t['mapping_id'].split('|'))==excluded;inner=parent['inner_correctors'][t['inner_corrector_id']];assert set(inner['excluded_keys'])==excluded;assert int(gain>0)==t['label'];nested+=1
    innerchecks=0
    for inner in parent['inner_correctors'].values():
        excluded=set(inner['excluded_keys'])
        for t in inner['training_trace']:
            k=table[t['case_id']]['subject_id'];assert k not in excluded and set(t['mapping_id'].split('|'))==excluded|{k};innerchecks+=1
    preds={r['case_id']:r for r in original['records']};gain=[preds[c]['input_metrics']['rgb8_mae_codes']-preds[c]['paths']['split_ungated']['metrics']['rgb8_mae_codes'] for c in m['full_training_cases']];assert gain==m['full_training_signed_benefits'];equation(m['full_signed'],full['gate_features'],gain,[table[c]['subject_id'] for c in m['full_training_cases']]);assert m['full_signed']['weights']==m['full_matched_binary']['weights']
    foldsigned={f['held_key']:f['model'] for f in m['folds']};foldbinary={f['held_key']:f['model'] for f in parent['folds']};splitfold={f['held_key']:f['model'] for f in original['folds']};renders=0;features=0
    for r in v['records']:
        c=context[r['suite'],r['case_id']];assert r['features']==c['features'];fold=r['suite']=='fold_working256'
        if r['features'] is not None:
            assert signed_benefit_decision(foldsigned[r['subject_id']] if fold else m['full_signed'],r['features'])==r['signed_decision'];assert gate_decision(foldbinary[r['subject_id']] if fold else m['full_matched_binary'],r['features'])==r['matched_binary_decision'];assert predict_split(splitfold[r['subject_id']] if fold else full['split'],r['features'])==c['paths']['old_ungated']['parameters'];features+=1
            if not fold:assert r['subject_id'] not in m['full_signed']['training_keys']
        else:assert r['signed_decision'] is None and r['matched_binary_decision'] is None
        if r['image_path'] is None:assert not r['reference_available'];continue
        image=rgb(r['image_path']);reference=rgb(r['reference_path']);mask=cv2.imread(r['mask_path'],0)>0 if r['mask_path'] else np.zeros(image.shape[:2],bool);refmask=cv2.imread(r['reference_mask_path'],0)>0 if r['reference_available'] else None
        for name,decision in [('signed',r['signed_decision']),('matched_binary',r['matched_binary_decision'])]:
            apply=decision is not None and decision['apply_correction'];p=r['paths'][name];assert p['parameters']==(c['paths']['old_ungated']['parameters'] if apply else None);output=render_rgb8(image,mask.astype(float),p['parameters']) if apply else image.copy();assert np.array_equal(output,rgb(E/r['suite']/r['case_id']/(name+'.png')));assert np.array_equal(output[~mask],image[~mask]);assert np.array_equal(output,rgb(r['ungated_output_path']) if apply else image)
            expectedref=c['paths']['old_ungated']['reference_metrics'] if apply else c['input_reference_metrics'];expectedscene=c['paths']['old_ungated']['scene_metrics'] if apply else c['input_scene_metrics'];assert p['reference_metrics']==expectedref and p['scene_metrics']==expectedscene
            error=np.abs(output.astype(np.int16)-reference.astype(np.int16));assert p['changed_channels']==int(np.count_nonzero(output!=image))
            if refmask is not None:assert abs(float(error[refmask].mean())-p['reference_metrics']['rgb8_mae_codes'])<1e-12
            if p['scene_metrics'] is not None:assert abs(float(error.mean())-p['scene_metrics']['rgb8_mae_codes'])<1e-12
            renders+=1
    assert len(v['records'])==1428
    O.mkdir();(O/'verification_PRIVATE.json').write_text(json.dumps(dict(signed_normal_equations=11,nested_training_gain_checks=nested,inner_training_exclusion_checks=innerchecks,feature_control_action_checks=features,render_metric_selection_and_rgb_replays=renders,all_controls_frozen=True,inherited_ciede2000_metrics_bound_to_byte_identical_validated_sources=True,new_fits=0,new_inference=0),indent=2),encoding='utf-8');print('Verified11equations,',nested,'nested gains,',innerchecks,'inner exclusions,',features,'actions and',renders,'outputs.')
if __name__=='__main__':main()
