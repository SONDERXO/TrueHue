"""Reconstruct cached support and prepare fitting/reserved green features only."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.model_training.green_distribution_features import green_distribution_features,ADDITIONS
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.fixed_face_input_bridge import native_projection
OUT=ROOT/'outputs/fitting_green_features_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial preparation')
    bound={};inherited={};access={}
    def read(rel):
        p=ROOT/rel;h=sha(p)
        if str(p) in inherited:assert inherited[str(p)]==h,(str(p),'metadata hash mismatch')
        bound[str(p)]=h;return json.loads(p.read_text())
    m=read('outputs/colour_nonharm_models_v1/models_PRIVATE.json');inherited.update(m['input_sha256'])
    mv=read('outputs/colour_nonharm_models_v1/verification_PRIVATE.json');assert mv['passed'] and mv['model_sha256']==sha(ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    ready=read('outputs/green_channel_design_readiness_v1/readiness_PRIVATE.json');rv=read('outputs/green_channel_design_readiness_v1/verification_PRIVATE.json')
    assert rv['passed'] and rv['readiness_sha256']==sha(ROOT/'outputs/green_channel_design_readiness_v1/readiness_PRIVATE.json')
    a=read('outputs/aligned_correction_preparation_v1/results_PRIVATE.json');e=read('outputs/expanded_correction_inputs_v1/results_PRIVATE.json')
    metadata={r['case_id']:r for r in a['records']+e['records']}
    clean=read('outputs/group_diversity_final_masks_v1/results_PRIVATE.json');cleanrows={r['case_id']:r for r in clean['records']}
    runs={name:{r['image_id']:r for r in read('outputs/'+name+'/inference.json')['records']} for name in ['group_diversity_final_masks_v1','expanded_correction_inputs_v1']}
    code=['src/model_training/green_distribution_features.py','src/ita_estimation/faceocc_veto_candidate.py',
          'src/ita_estimation/compute_ita.py','src/skin_masking/faceocc_coordinates.py',
          'src/skin_masking/faceocc_mediapipe_bridge.py','src/skin_masking/fixed_face_input_bridge.py',
          'src/model_training/facial_endpoint_features.py','scripts/682_prepare_fitting_green_features.py',
          'docs/green-channel-correction-design-2026-11-09.md','docs/green-channel-design-readiness-2026-11-09.md']
    for rel in code:
        p=ROOT/rel;h=sha(p)
        if str(p) in inherited:assert inherited[str(p)]==h
        bound[str(p)]=h
    def check(path,kind,require=True):
        p=Path(path);h=sha(p)
        if require:assert str(p) in inherited,(str(p),'missing inherited binding')
        if str(p) in inherited:assert inherited[str(p)]==h,(str(p),'hash mismatch')
        bound[str(p)]=h;access[str(p)]=kind;return p
    template=loadmat(check(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat','alignment_template'))['lm']
    assert {r['case_id'] for r in ready['assets']}==set(m['full']['training_cases'])|{r['case_id'] for r in m['full']['reserved_clean_vectors']}
    OUT.mkdir();(OUT/'rows').mkdir();records=[]
    try:
        for j,asset in enumerate(ready['assets'],1):
            cid=asset['case_id'];r=metadata[cid]
            image=cv2.imread(str(check(asset['image_path'],'input_image')));mp=Path(asset['mask_path'])
            mask=cv2.imread(str(check(mp,'normalized_measurement_mask',require=asset['inherited_mask_sha256'] is not None)),0)
            details=dict(method='inherited_normalized_mask_hash')
            if asset['inherited_mask_sha256'] is None:
                clean_case=r['recipe']=='clean';parentfolder=Path(asset['image_path']).parent
                source=cleanrows[r['source_case']] if clean_case else r
                folder='group_diversity_final_masks_v1' if clean_case else 'expanded_correction_inputs_v1'
                q=runs[folder][r['source_case'] if clean_case else cid];assert q['status']=='success'
                lp=check(ROOT/'outputs'/folder/q['logits_path'],'cached_faceocc_logits');assert sha(lp)==q['logits_sha256']
                logits=np.load(lp,allow_pickle=False)
                parent=cv2.imread(str(check(parentfolder/'parent_mask.png','cached_parent_mask')),0)
                points=np.load(check(parentfolder/'landmarks.npy','cached_landmarks'),allow_pickle=False)
                aligned,matrix,_=align_input(image,points,template)
                np.testing.assert_array_equal(matrix,np.asarray(source['matrix']))
                ap=mp.parent/'aligned.png'
                np.testing.assert_array_equal(aligned,cv2.imread(str(check(ap,'cached_alignment'))))
                expected,_,report=combine_saved(image,parent,logits,matrix)
                assert report['status']=='success'
                np.testing.assert_array_equal(expected,mask)
                details=dict(method='exact_reconstruction_from_inherited_cached_artifacts',
                    parent_mask_path=str(parentfolder/'parent_mask.png'),landmarks_path=str(parentfolder/'landmarks.npy'),
                    logits_path=str(lp),alignment_path=str(ap),matrix=matrix.tolist())
            native_path=Path(r['measurement_native_path']);native_bound=str(native_path) in inherited
            native=cv2.imread(str(check(native_path,'native_measurement_mask',require=native_bound)),0)
            projected,_=native_projection(mask,r['input_bridge']);np.testing.assert_array_equal(projected,native)
            s=compute_masked_lab_statistics(image,mask,1000);assert s['valid']
            for name in ('mean_l_star','mean_a_star','mean_b_star','ita_degrees'):assert s[name]==r['raw_features']['input_'+name],(cid,name)
            features=green_distribution_features(image,mask);assert features['valid']
            row=dict(case_id=cid,role=asset['role'],subject_id=r['subject_id'],recipe=r['recipe'],
                source_case=cid.split('__',1)[0],image_path=asset['image_path'],mask_path=str(mp),
                native_mask_path=str(native_path),native_mask_historically_bound=native_bound,
                input_bridge=r['input_bridge'],provenance=details,raw_features=r['raw_features'],**features)
            (OUT/'rows'/(cid+'_PRIVATE.json')).write_text(json.dumps(row,indent=2));records.append(row)
            if j%100==0:print('Prepared',j,'/910',flush=True)
        fitting=[r for r in records if r['role']=='fitting'];cleans={r['source_case']:r for r in fitting if r['recipe']=='clean'}
        pairs=[]
        for r in fitting:
            if r['recipe']=='clean':continue
            base=cleans.get(r['source_case'])
            if base is None:continue
            family='colour_only' if r['recipe'] in ('colour_cool','colour_warm','stress_color_none') else ('exposure_only' if r['recipe'].startswith(('exposure_','stress_exposure_')) else 'combined')
            pairs.append(dict(case_id=r['case_id'],source_case=r['source_case'],recipe=r['recipe'],family=family,
                delta={n:r['features'][n]-base['features'][n] for n in ADDITIONS}))
        behaviour={}
        for recipe in sorted({p['recipe'] for p in pairs}):
            rr=[p for p in pairs if p['recipe']==recipe]
            behaviour[recipe]=dict(pairs=len(rr),features={})
            for n in ADDITIONS:
                values=[p['delta'][n] for p in rr]
                behaviour[recipe]['features'][n]=dict(min=min(values),median=float(np.median(values)),max=max(values),lower=sum(v<0 for v in values),equal=sum(v==0 for v in values),higher=sum(v>0 for v in values))
        summary=dict(prepared_rows=len(records),fitting_rows=len(fitting),reserved_clean_rows=len(records)-len(fitting),
            inherited_normalized_masks=sum(r['provenance']['method']=='inherited_normalized_mask_hash' for r in records),
            reconstructed_normalized_masks=sum(r['provenance']['method']!='inherited_normalized_mask_hash' for r in records),
            historically_bound_native_masks=sum(r['native_mask_historically_bound'] for r in records),
            raw_feature_checks=4*len(records),training_clean_pairs=len(pairs),actual_file_reads=len(access),
            new_fits=0,new_model_forwards=0,evaluation_feature_rows=0,holdout_image_reads=0)
        assert len(records)==910 and len(fitting)==890
        assert all(sha(p)==h for p,h in bound.items())
        (OUT/'features_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records,source_pairs=pairs,
            fitting_pair_behaviour=behaviour,feature_names=list(ADDITIONS),input_sha256=bound,access_scope=access,
            disposition='Prepared; independent feature/provenance verification and readiness assessment pending.'),indent=2,allow_nan=False))
        print(json.dumps(summary,indent=2));print('Pair behaviour',json.dumps(behaviour,indent=2))
    except Exception:
        (OUT/'failure_PRIVATE.json').write_text(json.dumps(dict(completed_rows=len(records),failure=traceback.format_exc(),input_sha256=bound),indent=2));raise
if __name__=='__main__':main()
