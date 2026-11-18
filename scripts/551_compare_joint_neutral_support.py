"""Frozen zero-fit joint policy on all saved contexts; private outputs only."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.joint_neutral_support import prepare_policy,predict_policy
from src.model_training.split_control_candidate import predict_split
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics

OUT=ROOT/'outputs/joint_neutral_support_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def save(p,a):
    assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))

def summarize(rows):
    summary=dict(attempts=len(rows),features_available=sum(r['features'] is not None for r in rows),
        support_abstentions=sum(r['policy'] is not None and not r['policy']['supported'] for r in rows),methods={})
    for method in ('input','retained','policy_ungated','policy_gated'):
        values=[r for r in rows if r['paths'].get(method,{}).get('reference_metrics') is not None]
        scenes=[r for r in rows if r['paths'].get(method,{}).get('scene_metrics') is not None]
        s=dict(reference_scored=len(values),changed_cases=sum(r['paths'].get(method,{}).get('changed_channels',0)>0 for r in rows),
            reference_harms=sum(r['paths'][method]['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes'] for r in values),
            scene_harms=sum(r['paths'][method]['scene_metrics']['rgb8_mae_codes']>r['input_scene_metrics']['rgb8_mae_codes'] for r in scenes))
        for region,scored in [('reference_metrics',values),('scene_metrics',scenes)]:
            for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                s[region+'_'+metric]=float(np.mean([r['paths'][method][region][metric] for r in scored])) if scored else None
                keys={r['subject_id'] for r in scored}
                s['equal_key_'+region+'_'+metric]=float(np.mean([np.mean([r['paths'][method][region][metric] for r in scored if r['subject_id']==k]) for k in keys])) if scored else None
        summary['methods'][method]=s
    rr=[r for r in rows if r['reference_available']]
    beneficial=[r for r in rr if r['paths']['retained']['reference_metrics']['rgb8_mae_codes']<r['input_reference_metrics']['rgb8_mae_codes']]
    summary['retained_beneficial_actions']=len(beneficial)
    summary['retained_beneficial_actions_now_unchanged']=sum(r['paths']['policy_gated']['changed_channels']==0 for r in beneficial)
    return summary

def main():
    if OUT.exists():raise FileExistsError(OUT)
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json'
    F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json'
    T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    C=ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json'
    folds=read(S)['folds'];full=read(F);table={r['case_id']:r for r in read(T)};context=read(C)['records']
    bound={};policies={};payloads={}
    def bind(p):
        if p is not None:bound[str(p)]=sha(p)
    for p in [S,F,T,C,Path(__file__),ROOT/'src/model_training/joint_neutral_support.py',
        ROOT/'src/model_training/portable_tree.py',ROOT/'src/model_training/split_control_candidate.py',
        ROOT/'src/model_training/blended_recovery_targets.py',ROOT/'src/model_training/photographic_target_diagnostic.py',
        ROOT/'docs/joint-neutral-support-protocol-2026-11-07.md']:bind(p)
    fitting_clean_checks=0
    for key,model,cases,features in [(f['held_key'],f['model'],f['training_cases'],f['training_features']) for f in folds]+[('full',full['split'],full['training_cases'],full['training_features'])]:
        keys={table[c]['subject_id'] for c in cases}
        if key!='full':assert key not in keys
        flags=[table[c]['case']['id']=='clean' for c in cases]
        assert all(table[c]['target']==[1.,1.,1.] for c,flag in zip(cases,flags) if flag)
        policy=prepare_policy(model,features,flags);policies[key]=policy;payloads[key]=model
        for x,flag in zip(features,flags):
            if flag:
                d=predict_policy(model,policy,x);assert d['supported'] and d['parameters']==[1.,1.,1.];fitting_clean_checks+=1
    assert not set(full['training_keys']) & {r['subject_id'] for r in context if r['suite']!='fold_working256'}
    OUT.mkdir();records=[];boards=[];chosen=set()
    for c in context:
        r={k:c[k] for k in ('suite','case_id','subject_id','layer','recipe','features','reference_available','input_reference_metrics','input_scene_metrics','image_path','reference_path','mask_path','reference_mask_path')}
        key=c['subject_id'] if c['suite']=='fold_working256' else 'full';vector=c['features']
        d=predict_policy(payloads[key],policies[key],vector) if vector is not None else None
        r.update(policy=d,gate=c['gate'],paths={},output_paths={})
        if c['image_path'] is None:records.append(r);continue
        for p in [c['image_path'],c['reference_path'],c['mask_path'],c['reference_mask_path']]+list(c['old_output_paths'].values()):bind(p)
        if vector is not None:assert predict_split(payloads[key],vector)==c['paths']['old_ungated']['parameters']
        image=rgb(c['image_path']);reference=rgb(c['reference_path']);mask=cv2.imread(c['mask_path'],0)>0 if c['mask_path'] else np.zeros(image.shape[:2],bool)
        refmask=cv2.imread(c['reference_mask_path'],0)>0 if c['reference_available'] else None
        r['paths']['input']=dict(reference_metrics=c['input_reference_metrics'],scene_metrics=c['input_scene_metrics'],changed_channels=0)
        r['paths']['retained']=c['paths']['old_gated']
        folder=OUT/c['suite']/c['case_id'];folder.mkdir(parents=True);images={}
        for method,apply in [('policy_ungated',True),('policy_gated',bool(c['gate'] and c['gate']['apply_correction']))]:
            params=d['parameters'] if apply and d is not None else [1.,1.,1.]
            output=render_rgb8(image,mask.astype(float),params)
            assert np.array_equal(image[~mask],output[~mask]);save(folder/(method+'.png'),output);images[method]=output
            r['output_paths'][method]=str(folder/(method+'.png'))
            r['paths'][method]=dict(parameters=params,changed_channels=int(np.count_nonzero(image!=output)),
                reference_metrics=metrics(output,reference,refmask) if refmask is not None else None,
                scene_metrics=metrics(output,reference,np.ones(mask.shape,bool)) if c['input_scene_metrics'] is not None else None)
        clean=c['recipe']=='clean' and c['reference_available'] and c['suite'] in ('fold_working256','fallback_native224')
        first=c['layer'] in ('core','composite_stress_design') and vector is not None and (c['suite'],c['layer']) not in chosen
        focal=c['case_id']=='eval_22__colour_warm'
        if clean or first or focal:
            chosen.add((c['suite'],c['layer']))
            panels=[reference,image,rgb(c['old_output_paths']['old_gated']),images['policy_ungated'],images['policy_gated']]
            title=np.full((28,image.shape[1]*5,3),255,np.uint8)
            cv2.putText(title,c['suite']+' '+c['case_id']+' ref | input | retained | policy no gate | policy gated',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.36,(0,0,0),1)
            save(folder/'board.png',np.vstack([title,np.hstack(panels)]));boards.append(str((folder/'board.png').relative_to(OUT)))
        records.append(r)
    assert len(records)==1428
    summary={suite:{layer:summarize([r for r in records if r['suite']==suite and r['layer']==layer]) for layer in ('clean','core','composite_stress_design')} for suite in ('fold_working256','borrowed_native224','input_native224','fallback_native224')}
    result=dict(summary=summary,records=records,boards=boards,policies=policies,fitting_clean_checks=fitting_clean_checks,new_fits=0,new_mask_forwards=0,admissions=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><title>Private joint policy review</title><h1>Development only</h1><p>Reference | input | retained | joint policy without gate | joint policy with retained gate</p>'+''.join('<img width="100%" src="'+p+'">' for p in boards),encoding='utf-8')
    for suite,layers in summary.items():
        for layer,s in layers.items():
            print(suite,layer,'support abstentions',s['support_abstentions'],'benefits lost',s['retained_beneficial_actions_now_unchanged'],'/',s['retained_beneficial_actions'])
            for name,m in s['methods'].items():print(name,'MAE',m['reference_metrics_rgb8_mae_codes'],'changed',m['changed_cases'],'harms',m['reference_harms'])
    print('Saved',len(records),'records;',len(boards),'boards;',fitting_clean_checks,'repeated fitting clean checks.')

if __name__=='__main__':main()
