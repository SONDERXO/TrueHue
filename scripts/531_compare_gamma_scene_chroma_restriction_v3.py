"""Matched saved-case comparisons; no fitting/inference in this stage."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.split_control_candidate import predict_split
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=ROOT/'outputs/gamma_scene_chroma_comparison_v3'
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def save(p,a):assert cv2.imwrite(str(p),cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
def summarize(rows):
    result=dict(attempts=len(rows),reference_scored=sum(r['reference_available'] for r in rows),features_available=sum(r['features'] is not None for r in rows),paths={})
    rr=[r for r in rows if r['reference_available']]
    for path in ['old_ungated','old_gated','new_ungated','new_gated']:
        s=dict(reference_harms=sum(r['paths'][path]['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes'] for r in rr),changed_cases=sum(r['paths'].get(path,{}).get('changed_channels',0)>0 for r in rows))
        for region in ['reference_metrics','scene_metrics']:
            scored=rr if region=='reference_metrics' else [r for r in rows if path in r['paths'] and r['paths'][path]['scene_metrics'] is not None]
            for metric in ['rgb8_mae_codes','relative_deltaE00_mean']:
                s[region+'_'+metric]=float(np.mean([r['paths'][path][region][metric] for r in scored])) if scored else None
                s['equal_key_'+region+'_'+metric]=float(np.mean([np.mean([r['paths'][path][region][metric] for r in scored if r['subject_id']==k]) for k in {r['subject_id'] for r in scored}])) if scored else None
        s['scene_harms']=sum(r['paths'][path]['scene_metrics']['rgb8_mae_codes']>r['input_scene_metrics']['rgb8_mae_codes'] for r in rows if r['input_scene_metrics'] is not None)
        result['paths'][path]=s
    return result

def main():
    if OUT.exists():raise FileExistsError(OUT)
    MP=ROOT/'outputs/gamma_scene_chroma_models_v1/models_PRIVATE.json';models=read(MP);split=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json');rows={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')};foldmodels={f['held_key']:f['model'] for f in models['folds']};foldbycase={cid:f['held_key'] for f in models['folds'] for cid in f['held_cases']}
    original=ROOT/'outputs/frozen_split_subject_check_v1';oldnative=ROOT/'outputs/frozen_split_subject_evaluation_v1';before=ROOT/'outputs/input_derived_correction_v1';after=ROOT/'outputs/detector_appearance_correction_v1';oldrecords={r['case_id']:r for r in read(oldnative/'results_PRIVATE.json')['records']};afterrecords=read(after/'results_PRIVATE.json')['records'];beforemasks={r['case_id']:r for r in read(ROOT/'outputs/input_derived_mask_check_v1/results_PRIVATE.json')['records']};aftermasks={r['case_id']:r for r in read(ROOT/'outputs/detector_appearance_merged_v1/results_PRIVATE.json')['records']}
    paths=[MP,Path(__file__),ROOT/'docs/gamma-scene-chroma-restriction-protocol-2026-11-07.md',ROOT/'src/model_training/split_control_candidate.py',ROOT/'src/model_training/blended_recovery_targets.py',ROOT/'src/model_training/photographic_target_diagnostic.py',ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json',oldnative/'results_PRIVATE.json',before/'results_PRIVATE.json',after/'results_PRIVATE.json']
    bindings={str(p):sha(p) for p in paths};assert all(sha(Path(p))==h for p,h in models['input_sha256'].items());OUT.mkdir();records=[];boards=[];chosen=set()
    def process(suite,cid,subject,layer,recipe,vector,gate,payload,imagepath,refpath,maskpath,refmaskpath,oldpaths,inputref,inputscene,oldoutputpaths):
        folder=OUT/suite/cid;folder.mkdir(parents=True);available=refmaskpath is not None
        r=dict(suite=suite,case_id=cid,subject_id=subject,layer=layer,recipe=recipe,features=vector,gate=gate,reference_available=available,input_reference_metrics=inputref,input_scene_metrics=inputscene,paths=dict(oldpaths),image_path=str(imagepath) if imagepath else None,reference_path=str(refpath) if refpath else None,mask_path=str(maskpath) if maskpath else None,reference_mask_path=str(refmaskpath) if refmaskpath else None,old_output_paths={k:str(v) for k,v in oldoutputpaths.items()})
        if imagepath is None:records.append(r);return
        for p in [imagepath,refpath,maskpath,refmaskpath]+list(oldoutputpaths.values()):
            if p is not None:bindings[str(p)]=sha(p)
        image=rgb(imagepath);reference=rgb(refpath);mask=cv2.imread(str(maskpath),0)>0 if maskpath else np.zeros(image.shape[:2],bool);refmask=cv2.imread(str(refmaskpath),0)>0 if available else None
        parameters=predict_split(payload,vector) if vector is not None else None
        if parameters is not None:assert parameters[1:]==oldpaths['old_ungated']['parameters'][1:]
        apply=gate is not None and gate['apply_correction'];newimages={}
        for name,params in [('new_ungated',parameters),('new_gated',parameters if apply else None)]:
            output=render_rgb8(image,mask.astype(float),params) if params is not None else image.copy();assert np.array_equal(output[~mask],image[~mask]);save(folder/(name+'.png'),output);newimages[name]=output
            priorname='old_'+name[4:];same=np.array_equal(output,rgb(oldoutputpaths[priorname]));oldpath=oldpaths[priorname]
            r['paths'][name]=dict(parameters=params,reference_metrics=oldpath['reference_metrics'] if same else (metrics(output,reference,refmask) if available else None),scene_metrics=oldpath['scene_metrics'] if same else (metrics(output,reference,np.ones(mask.shape,bool)) if inputscene is not None else None),changed_channels=int(np.count_nonzero(output!=image)),byte_identical_old=same)
        clean=recipe=='clean' and available;focal=cid=='eval_22__colour_warm';first=suite!='fold_working256' and layer in ['core','composite_stress_design'] and vector is not None and (suite,layer) not in chosen
        if clean or focal or first:
            chosen.add((suite,layer));oldgated=rgb(oldoutputpaths['old_gated']);panels=[reference,image,oldgated,newimages['new_gated']];w=image.shape[1]*4;title=np.full((26,w,3),255,np.uint8);cv2.putText(title,suite+' '+cid+' reference | input | old gated | new gated',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.38,(0,0,0),1);save(folder/'board.png',np.vstack([title,np.hstack(panels)]));boards.append((suite,cid))
        records.append(r)
    for r in split['records']:
        cid=r['case_id'];row=rows[cid]
        if 'paths' not in r:
            process('fold_working256',cid,r['subject_id'],r['layer'],r['recipe'],None,None,foldmodels[foldbycase[cid]],None,None,None,None,{},None,None,{});continue
        folder=ROOT/'outputs/whole_scene_correction_v1'/r['source_case'];pair=folder/r['recipe'];oldpaths={}
        for short in ['ungated','gated']:
            p=r['paths']['split_'+short];oldpaths['old_'+short]=dict(parameters=p['parameters'],reference_metrics=p['metrics'],scene_metrics=None,changed_channels=p['changed_channels'])
        process('fold_working256',cid,r['subject_id'],r['layer'],r['recipe'],r['features'],r['gate'],foldmodels[foldbycase[cid]],pair/'input.png',folder/'reference.png',folder/'mask.png',folder/'mask.png',oldpaths,r['input_metrics'],None,{k:ROOT/'outputs/split_control_comparison_v1'/('split_'+k[4:])/(cid+'.png') for k in oldpaths})
    for suite,package in [('borrowed_native224',after),('input_native224',before),('fallback_native224',after)]:
        for r in read(package/'results_PRIVATE.json')['records']:
            cid=r['case_id'];sid=r['source_case'];borrowed=suite=='borrowed_native224';prior=oldrecords[cid] if borrowed else r;vec=prior['features'];gate=prior.get('gate');maskrow=beforemasks[cid] if suite=='input_native224' else aftermasks[cid]
            refmask=original/sid/'native_grid.png' if r['reference_available'] else None
            maskpath=refmask if borrowed else ((ROOT/'outputs/input_derived_mask_check_v1'/cid/'native_grid.png' if suite=='input_native224' else Path(maskrow['artifact_root'])/'native_grid.png') if maskrow['status']=='success' else None)
            prefix='borrowed_' if borrowed else 'input_';oldpaths={'old_'+s:r['paths'][prefix+s] for s in ['ungated','gated']}
            process(suite,cid,r['subject_id'],r['layer'],r['recipe'],vec,gate,models['full_model'],Path(maskrow['source_path']),original/sid/'source.jpeg',maskpath,refmask,oldpaths,r['paths']['unchanged']['reference_metrics'],r['paths']['unchanged']['scene_metrics'],{'old_'+s:package/cid/(prefix+s+'.png') for s in ['ungated','gated']})
        print(suite+' complete',flush=True)
    (OUT/'records_PRIVATE.json').write_text(json.dumps(records,indent=2,allow_nan=False),encoding='utf-8')
    summary={suite:{layer:summarize([r for r in records if r['suite']==suite and r['layer']==layer]) for layer in ['clean','core','composite_stress_design']} for suite in ['fold_working256','borrowed_native224','input_native224','fallback_native224']}
    result=dict(summary=summary,records=records,boards=boards,new_fits=0,new_inference=0,admissions=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8');assert all(sha(Path(p))==h for p,h in bindings.items())
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><h1>Private gamma-only scene-chroma restriction</h1><p>Reference | distorted input | old gated | new gated. Development comparisons; not production adoption.</p>'+''.join('<img width="100%" src="'+s+'/'+c+'/board.png">' for s,c in boards),encoding='utf-8');print('Saved',len(records),'attempts and',len(boards),'fixed boards.')
if __name__=='__main__':main()
