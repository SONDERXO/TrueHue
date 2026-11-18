"""Fixed-control action comparison; gates only choose saved correction or identity."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.signed_benefit_gate import signed_benefit_decision
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.blended_recovery_targets import render_rgb8
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/signed_benefit_gate_comparison_v1'
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def summarize(rows):
    scored=[r for r in rows if r['reference_available']];v=dict(attempts=len(rows),reference_scored=len(scored),features_available=sum(r['features'] is not None for r in rows),methods={})
    for name in ['frozen','matched_binary','signed']:
        rr=[r for r in scored if name in r['paths']];s=dict(reference_harms=sum(r['paths'][name]['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes'] for r in rr),changed_cases=sum(r['paths'].get(name,{}).get('changed_channels',0)>0 for r in rows))
        for region in ['reference_metrics','scene_metrics']:
            rs=rr if region=='reference_metrics' else [r for r in rows if name in r['paths'] and r['paths'][name]['scene_metrics'] is not None]
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                s[region+'_'+metric]=float(np.mean([r['paths'][name][region][metric] for r in rs])) if rs else None
                s['equal_key_'+region+'_'+metric]=float(np.mean([np.mean([r['paths'][name][region][metric] for r in rs if r['subject_id']==k]) for k in {r['subject_id'] for r in rs}])) if rs else None
        s['scene_harms']=sum(r['paths'][name]['scene_metrics']['rgb8_mae_codes']>r['input_scene_metrics']['rgb8_mae_codes'] for r in rows if name in r['paths'] and r['input_scene_metrics'] is not None)
        for cost in ['harmful_action_cost','missed_benefit','regret']:
            s['mean_'+cost]=float(np.mean([r['paths'][name][cost] for r in rr])) if rr else None
        v['methods'][name]=s
    gains=[r['signed_decision']['predicted_rgb_mae_gain'] for r in rows if r['signed_decision'] is not None];v['predicted_gain_range']=[min(gains),max(gains)] if gains else None
    return v

def main():
    if OUT.exists():raise FileExistsError(OUT)
    MP=ROOT/'outputs/signed_benefit_gate_models_v1/models_PRIVATE.json';C=ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json';S=ROOT/'outputs/split_benefit_gate_v1/results_PRIVATE.json';models=read(MP);context=read(C)['records'];matched=read(S);foldmodels={f['held_key']:f['model'] for f in models['folds']};binaryfold={f['held_key']:f['model'] for f in matched['folds']};binarypred={r['case_id']:r for r in matched['records']}
    paths=[MP,C,S,Path(__file__),ROOT/'docs/signed-benefit-gate-protocol-2026-11-07.md',ROOT/'src/model_training/signed_benefit_gate.py',ROOT/'src/model_training/correction_gate_candidate.py',ROOT/'src/model_training/blended_recovery_targets.py']
    bindings={str(p):sha(p) for p in paths};assert all(sha(Path(p))==h for p,h in models['input_sha256'].items());OUT.mkdir();records=[];boards=[];chosen=set()
    for c in context:
        suite=c['suite'];cid=c['case_id'];folder=OUT/suite/cid;folder.mkdir(parents=True);vector=c['features'];signed=None;binary=None
        if vector is not None:
            signed=signed_benefit_decision(foldmodels[c['subject_id']] if suite=='fold_working256' else models['full_signed'],vector);binary=gate_decision(binaryfold[c['subject_id']] if suite=='fold_working256' else models['full_matched_binary'],vector)
            if suite=='fold_working256':assert binary==binarypred[cid]['gate']
        r=dict(suite=suite,case_id=cid,subject_id=c['subject_id'],layer=c['layer'],recipe=c['recipe'],features=vector,reference_available=c['reference_available'],input_reference_metrics=c['input_reference_metrics'],input_scene_metrics=c['input_scene_metrics'],image_path=c['image_path'],reference_path=c['reference_path'],mask_path=c['mask_path'],reference_mask_path=c['reference_mask_path'],ungated_output_path=c['old_output_paths'].get('old_ungated'),signed_decision=signed,matched_binary_decision=binary,paths={})
        if c['image_path'] is None:records.append(r);continue
        for p in [c['image_path'],c['reference_path'],c['mask_path'],c['reference_mask_path']]+list(c['old_output_paths'].values()):
            if p is not None:bindings[p]=sha(Path(p))
        image=rgb(c['image_path']);reference=rgb(c['reference_path']);mask=cv2.imread(c['mask_path'],0)>0 if c['mask_path'] else np.zeros(image.shape[:2],bool);newimages={}
        r['paths']['frozen']=dict(c['paths']['old_gated'])
        for name,decision in [('matched_binary',binary),('signed',signed)]:
            apply=decision is not None and decision['apply_correction'];params=c['paths']['old_ungated']['parameters'] if apply else None;assert not apply or params is not None
            output=render_rgb8(image,mask.astype(float),params) if params is not None else image.copy();assert np.array_equal(output[~mask],image[~mask]);assert np.array_equal(output,rgb(c['old_output_paths']['old_ungated']) if apply else image)
            assert cv2.imwrite(str(folder/(name+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR));newimages[name]=output
            reference_metrics=c['paths']['old_ungated']['reference_metrics'] if apply else c['input_reference_metrics'];scene_metrics=c['paths']['old_ungated']['scene_metrics'] if apply else c['input_scene_metrics']
            r['paths'][name]=dict(parameters=params,reference_metrics=reference_metrics,scene_metrics=scene_metrics,changed_channels=int(np.count_nonzero(output!=image)))
        if r['reference_available']:
            inp=c['input_reference_metrics']['rgb8_mae_codes'];ung=c['paths']['old_ungated']['reference_metrics']['rgb8_mae_codes'];gain=inp-ung
            r['evaluation_only_signed_gain']=gain
            for name,p in r['paths'].items():
                actual=p['reference_metrics']['rgb8_mae_codes'];p.update(harmful_action_cost=max(actual-inp,0.),missed_benefit=max(actual-ung,0.),regret=actual-min(inp,ung));assert abs(p['regret']-p['harmful_action_cost']-p['missed_benefit'])<1e-10
        clean=c['recipe']=='clean' and r['reference_available'] and suite in ['fold_working256','fallback_native224'];focal=cid=='eval_22__colour_warm';first=suite!='fold_working256' and c['layer'] in ['core','composite_stress_design'] and vector is not None and (suite,c['layer']) not in chosen
        if clean or focal or first:
            chosen.add((suite,c['layer']));panels=[reference,image,rgb(c['old_output_paths']['old_gated']),newimages['matched_binary'],newimages['signed']];title=np.full((26,image.shape[1]*5,3),255,np.uint8);cv2.putText(title,suite+' '+cid+' ref|input|frozen|binary|signed',(3,17),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);assert cv2.imwrite(str(folder/'board.png'),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR));boards.append((suite,cid))
        records.append(r)
    assert len(records)==1428
    (OUT/'records_PRIVATE.json').write_text(json.dumps(records,indent=2,allow_nan=False),encoding='utf-8')
    summary={suite:{layer:summarize([r for r in records if r['suite']==suite and r['layer']==layer]) for layer in ['clean','core','composite_stress_design']} for suite in ['fold_working256','borrowed_native224','input_native224','fallback_native224']}
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,boards=boards,new_fits=0,new_inference=0,admissions=0,production_adopted=False),indent=2,allow_nan=False),encoding='utf-8');(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><h1>Private signed-benefit gate comparison</h1><p>Reference | input | frozen gate | matched binary | signed benefit. Development only; no skin-truth claim.</p>'+''.join('<img width="100%" src="'+s+'/'+c+'/board.png">' for s,c in boards),encoding='utf-8');print('Saved1428attempts and',len(boards),'fixed boards.')
if __name__=='__main__':main()
