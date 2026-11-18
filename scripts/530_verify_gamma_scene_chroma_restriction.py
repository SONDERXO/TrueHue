"""No-fit audit of eleven gamma artifacts and all saved comparison outputs."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.split_control_candidate import predict_split
from src.model_training.gamma_scene_chroma_restriction import EXCLUDED
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def main():
    P=ROOT/'outputs/gamma_scene_chroma_models_v1/models_PRIVATE.json';E=ROOT/'outputs/gamma_scene_chroma_comparison_v3';O=ROOT/'outputs/gamma_scene_chroma_assessment_v1'
    if O.exists():raise FileExistsError(O)
    models=read(P);v=read(E/'results_PRIVATE.json');rows={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')};baseline=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json');basefolds={r['held_key']:r for r in baseline['folds']};basepred={r['case_id']:r for r in baseline['records']};full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    oldnative={r['case_id']:r for r in read(ROOT/'outputs/frozen_split_subject_evaluation_v1/results_PRIVATE.json')['records']};before={r['case_id']:r for r in read(ROOT/'outputs/input_derived_correction_v1/results_PRIVATE.json')['records']};after={r['case_id']:r for r in read(ROOT/'outputs/detector_appearance_correction_v1/results_PRIVATE.json')['records']}
    assert all(sha(Path(p))==h for p,h in models['input_sha256'].items());assert all(sha(Path(p))==h for p,h in read(E/'input_sha256_PRIVATE.json').items())
    leafchecks=0;trainingroutes=0;foldbycase={}
    items=[(f['model'],f['training_cases'],f['training_features'],basefolds[f['held_key']]['model']) for f in models['folds']]+[(models['full_model'],models['full_training_cases'],models['full_training_features'],full['split'])]
    for payload,cases,x,prior in items:
        assert payload['heads']['gains']==prior['heads']['gains'];tree=payload['heads']['gamma']['tree'];excluded={payload['feature_names'].index(n) for n in EXCLUDED};assert not any(n['feature'] in excluded for n in tree['nodes'] if n['kind']=='split');portable=PortableTree(tree);y=np.array([rows[c]['target'][0] for c in cases]);norm=payload['heads']['gamma']['normalization']
        assert np.allclose([y.mean()],norm['mean'],rtol=0,atol=1e-12) and np.allclose([y.std()],norm['population_std'],rtol=0,atol=1e-12)
        leaves=np.array([portable.leaf_id(row) for row in x]);trainingroutes+=len(x)
        for leaf in set(leaves.tolist()):assert abs(y[leaves==leaf].mean()-tree['nodes'][leaf]['values'][0])<1e-12;leafchecks+=1
    for f in models['folds']:
        assert f['training_cases']==basefolds[f['held_key']]['training_cases'] and f['training_features']==basefolds[f['held_key']]['training_features'];assert all(rows[c]['subject_id']!=f['held_key'] for c in f['training_cases'])
        for cid in f['held_cases']:foldbycase[cid]=f['model']
    replays=0;features=0;clean={}
    for r in v['records']:
        suite=r['suite'];cid=r['case_id'];prior=basepred[cid] if suite=='fold_working256' else oldnative[cid] if suite=='borrowed_native224' else before[cid] if suite=='input_native224' else after[cid]
        assert r['features']==prior.get('features') and r['gate']==prior.get('gate')
        if r['image_path'] is None:assert not r['reference_available'];continue
        image=rgb(r['image_path']);reference=rgb(r['reference_path']);mask=cv2.imread(r['mask_path'],0)>0 if r['mask_path'] else np.zeros(image.shape[:2],bool);refmask=cv2.imread(r['reference_mask_path'],0)>0 if r['reference_available'] else None
        params=predict_split(foldbycase[cid] if suite=='fold_working256' else models['full_model'],r['features']) if r['features'] is not None else None
        if params is not None:assert params[1:]==r['paths']['old_ungated']['parameters'][1:];features+=1
        for name in ['new_ungated','new_gated']:
            p=r['paths'][name];expected=params if name=='new_ungated' or (r['gate'] and r['gate']['apply_correction']) else None;assert p['parameters']==expected
            output=render_rgb8(image,mask.astype(float),expected) if expected is not None else image.copy();assert np.array_equal(output,rgb(E/suite/cid/(name+'.png')));assert np.array_equal(output[~mask],image[~mask]);assert int(np.count_nonzero(output!=image))==p['changed_channels']
            assert (metrics(output,reference,refmask) if refmask is not None else None)==p['reference_metrics'];assert (metrics(output,reference,np.ones(mask.shape,bool)) if r['input_scene_metrics'] is not None else None)==p['scene_metrics'];assert np.array_equal(output,rgb(r['old_output_paths']['old_'+name[4:]]))==p['byte_identical_old'];replays+=1
        if r['recipe']=='clean' and r['reference_available'] and suite!='fold_working256':clean.setdefault(cid,[]).append(sha(E/suite/cid/'new_gated.png'))
    assert len(v['records'])==1428 and all(len(h)==3 and len(set(h))==1 for h in clean.values())
    O.mkdir();(O/'verification_PRIVATE.json').write_text(json.dumps(dict(gamma_artifacts=11,leaf_mean_checks=leafchecks,training_route_checks=trainingroutes,feature_prediction_replays=features,render_metric_replays=replays,native_clean_duplicate_checks=len(clean),frozen_gains_and_gates_verified=True,source_hashes_unchanged=True,new_fits=0),indent=2),encoding='utf-8');print('Verified',trainingroutes,'training routes,',leafchecks,'leaf means,',features,'feature predictions and',replays,'renders.')
if __name__=='__main__':main()
