"""No-fit replay of per-input features, projected masks, actions and scores."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.contextual_mst_experiment import FEATURES,predict
from src.model_training.whole_scene_features import scene_features,SCENE_FEATURES
from src.correction.continuous_mst_candidate import CONTINUOUS_FEATURES
from src.model_training.split_control_candidate import predict_split
from src.model_training.correction_gate_candidate import gate_decision
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
from src.skin_masking.fixed_face_input_bridge import native_projection
P=ROOT/'outputs/input_derived_mask_check_v1';E=ROOT/'outputs/input_derived_correction_v1';O=ROOT/'outputs/input_derived_assessment_v1';ORIGINAL=ROOT/'outputs/frozen_split_subject_check_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def main():
    if O.exists():raise FileExistsError(O)
    v=read(E/'results_PRIVATE.json');records={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']};model=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    old={r['case_id']:r for r in read(ROOT/'outputs/frozen_split_subject_evaluation_v1/results_PRIVATE.json')['records']};originals={r['case_id']:r for r in read(ORIGINAL/'results_PRIVATE.json')['records']}
    assert all(sha(Path(p))==h for p,h in read(E/'input_sha256_PRIVATE.json').items());assert all(sha(E/n)==h for n,h in read(E/'sha256.json').items())
    featurechecks=0;renders=0;maskchecks=0;cleanchecks=0;cleanreports=[]
    for r in v['records']:
        cid=r['case_id'];sid=r['source_case'];s=records[cid];image=rgb(Path(s['source_path']));reference=rgb(ORIGINAL/sid/'source.jpeg');folder=E/cid
        assert sha(Path(s['source_path']))==s['source_sha256'];assert s['subject_key'] not in model['training_keys']
        refmask=cv2.imread(str(ORIGINAL/sid/'native_grid.png'),0)>0 if r['reference_available'] else np.zeros(image.shape[:2],bool)
        mask=np.zeros(image.shape[:2],bool)
        if s['status']=='success':
            working=cv2.imread(str(P/cid/'input.png'));rawmask=cv2.imread(str(P/cid/'measurement_mask.png'),0);native,_=native_projection(rawmask,s['input_bridge']);assert np.array_equal(native,cv2.imread(str(P/cid/'native_grid.png'),0));mask=native>0;maskchecks+=1
            x0,y0,x1,y1=s['input_bridge']['native_bounds'];nativeinput=image[y0:y1,x0:x1];assert np.array_equal(nativeinput,cv2.imread(str(P/cid/'native_crop.png'))[:,:,::-1]);assert np.array_equal(cv2.resize(nativeinput,(256,256),interpolation=cv2.INTER_LINEAR),working[:,:,::-1])
            stat=compute_masked_lab_statistics(working,rawmask);assert stat['valid']
            f=dict(zip(FEATURES,[stat['ita_degrees'],stat['mean_l_star'],stat['mean_a_star'],stat['mean_b_star']]));assert all(f[n]==s['measurement_report']['features'][n] for n in FEATURES)
            mst=predict(model['ridge'],f);sf=scene_features(image);f['input_mst_score']=mst['score'];vector=[f[n] for n in CONTINUOUS_FEATURES]+[sf[n] for n in SCENE_FEATURES]
            assert vector==r['features'] and mst==r['mst_prediction'];assert gate_decision(model['gate'],vector)==r['gate'];assert predict_split(model['split'],vector)==r['paths']['input_ungated']['parameters'];featurechecks+=1
        else:assert r['features'] is None and r['gate'] is None
        assert r['paths']['input_gated']['parameters']==(r['paths']['input_ungated']['parameters'] if r['gate'] and r['gate']['apply_correction'] else None)
        if r['gate'] is None:assert r['paths']['input_ungated']['parameters'] is None
        assert int(mask.sum())==r['predicted_native_pixels']
        if r['reference_available']:assert int((mask&refmask).sum())==r['support_intersection'] and int((mask|refmask).sum())==r['support_union']
        for name,p in r['paths'].items():
            applied=refmask if name.startswith('borrowed') else mask
            if name.startswith('borrowed'):
                oldname='split_ungated' if name.endswith('ungated') else 'split_gated';assert p['parameters']==old[cid].get('paths',{}).get(oldname,{}).get('parameters')
            output=render_rgb8(image,applied.astype(float),p['parameters']) if p['parameters'] is not None else image.copy()
            assert np.array_equal(output,rgb(folder/(name+'.png')));assert np.array_equal(output[~applied],image[~applied]);assert metrics(output,reference,np.ones(image.shape[:2],bool))==p['scene_metrics']
            assert (metrics(output,reference,refmask) if r['reference_available'] else None)==p['reference_metrics'];assert int(np.count_nonzero(output!=image))==p['changed_channels']
            changed=np.any(output!=image,axis=2);assert int(changed.sum())==p['changed_native_pixels']
            assert (int((changed&~refmask).sum()) if r['reference_available'] else None)==p['changed_pixels_outside_reference'];renders+=1
        if r['recipe']=='clean':
            original=originals[sid];same=s['status']==original['status'];same_mask=None
            if s['status']=='success' and original['status']=='success':same_mask=np.array_equal(mask,refmask);assert same_mask;assert s['input_bridge']==original['input_bridge'];assert r['features']==old[cid]['features'];assert r['gate']==old[cid]['gate']
            assert same;cleanchecks+=1;cleanreports.append(dict(case_id=cid,same_status=same,same_mask=same_mask))
    assert len(v['records'])==336
    O.mkdir();(O/'verification_PRIVATE.json').write_text(json.dumps(dict(attempts=336,feature_replays=featurechecks,native_mask_replays=maskchecks,render_metric_replays=renders,clean_pipeline_repeats=cleanchecks,clean_records=cleanreports,source_hashes_verified=True,fit_count=0),indent=2),encoding='utf-8')
    print('Verified',featurechecks,'features/masks,',renders,'outputs and',cleanchecks,'clean pipeline repeats; no fits.')
if __name__=='__main__':main()
