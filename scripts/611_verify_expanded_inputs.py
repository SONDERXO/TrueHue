"""Replay all generated scenes, cached masks and projections; zero new forwards/fits."""
from pathlib import Path
from types import SimpleNamespace
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.model_training.photographic_target_diagnostic import distort,case_matrix
from src.model_training.whole_scene_features import scene_features
from src.skin_masking.fixed_face_input_bridge import crop_face,native_projection
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.skin_masking.correction_preview import render_preview
from src.model_training.aligned_correction_support import project_alpha
OUT=ROOT/'outputs/expanded_correction_inputs_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'final_input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    run=read(OUT/'inference.json');assert run['plan_sha256']==sha(OUT/'inference_plan.json');pred={r['image_id']:r for r in run['records']}
    plan=read(OUT/'frozen_plan_PRIVATE.json');expected={r['case_id']:r for r in plan['pending_distortions']}
    clean={r['case_id']:r for r in read(ROOT/'outputs/group_diversity_final_masks_v1/results_PRIVATE.json')['records']}
    recipes={r['id']:r for r in case_matrix()};template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    counts=dict(records=0,source_decodes=0,scene_replays=0,crop_replays=0,parent_mask_replays=0,service_replays=0,native_projections=0,scoring_replays=0)
    sources={};outputs={}
    for r in d['records']:
        assert r['subject_id'] not in plan['closed_holdout_keys'] and not r['training_admitted'] and not r['calibration_admitted'] and not r['scientific_admission']
        counts['records']+=1
        if r['recipe']=='clean':continue
        item=expected[r['case_id']];assert r['source_sha256']==item['source_sha256'] and r['source_case']==item['source_case']
        if r['source_case'] not in sources:
            assert sha(r['source_path'])==r['source_sha256'];sources[r['source_case']]=rgb(r['source_path']);counts['source_decodes']+=1
        reference=sources[r['source_case']];assert np.array_equal(reference,rgb(r['reference_path']))
        generated,details,_=distort(reference,np.ones(reference.shape[:2]),recipes[r['recipe']]);scene=rgb(r['scene_path'])
        assert np.array_equal(scene,generated) and r['distortion']==details and r['scene_features']==scene_features(scene);counts['scene_replays']+=1
        folder=OUT/'cases'/r['case_id'];applied=np.zeros(scene.shape[:2],float)
        if (folder/'native_input.png').exists():
            native,bridge=crop_face(cv2.cvtColor(scene,cv2.COLOR_RGB2BGR),r['input_bridge']['source256_face_box'])
            assert bridge==r['input_bridge'] and np.array_equal(native,cv2.imread(str(folder/'native_input.png')))
            image=cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR);assert np.array_equal(image,cv2.imread(str(folder/'input.png')));counts['crop_replays']+=1
        if (folder/'parent_mask.png').exists():
            points=np.load(folder/'landmarks.npy',allow_pickle=False);cat=cv2.imread(str(folder/'categories.png'),0)
            mask=build_semantic_face_coverage(image,points,cat).mask
            if r['parent_report']['stage']=='nostril_measurement':mask[nostril_guard((256,256),points)]=0
            assert np.array_equal(mask,cv2.imread(str(folder/'parent_mask.png'),0))
            assert compute_masked_lab_statistics(image,mask,1000)==r['parent_report']['statistics'];counts['parent_mask_replays']+=1
        if r['case_id'] in pred and pred[r['case_id']]['status']=='success':
            p=pred[r['case_id']];lp=OUT/p['logits_path'];assert sha(lp)==p['logits_sha256'];logits=np.load(lp,allow_pickle=False)
            result=evaluate_parent(SimpleNamespace(report=r['parent_report'],image=image,mask=mask),points,template,lambda _:logits)
            assert result.report==r['measurement_report'] and np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')))
            native,_=native_projection(result.mask,r['input_bridge']);assert np.array_equal(native,cv2.imread(r['measurement_native_path'],0));counts['service_replays']+=1
            visible=map_visible_mask((logits>0).astype(np.uint8)*255,(256,256),result.matrix)
            preview=render_preview(image,mask,cat,points,visible,glasses='uncertain',parameters=(1.,1.,1.));assert np.array_equal(preview.output,image)
            alpha,protection=project_alpha(preview.alpha,preview.protected,r['input_bridge'])
            np.testing.assert_array_equal(alpha,np.load(r['alpha_path'],allow_pickle=False));assert np.array_equal(protection,cv2.imread(r['protected_path'],0)>0) and not alpha[protection].any()
            assert preview.report==r['correction_report'];counts['native_projections']+=1
            available=result.report['status']=='success' and bool(alpha.any());assert (r['status']=='available')==available
            if available:
                assert r['raw_features']=={k:result.report['features'][k] for k in r['raw_features']};applied=alpha
            else:assert r['raw_features'] is None
        else:assert r['status']!='available' and r['raw_features'] is None
        origin=clean[r['source_case']];cleanalpha=np.load(origin['alpha_path'],allow_pickle=False)
        scoring=(cleanalpha>0)|(applied>0);assert np.array_equal(scoring,cv2.imread(r['scoring_path'],0)>0)
        assert int(scoring.sum())==r['input_region_metrics']['scoring_pixels']
        assert abs(float(np.abs(scene[scoring].astype(float)-reference[scoring].astype(float)).mean())-r['input_region_metrics']['rgb8_mae_codes'])<1e-12;counts['scoring_replays']+=1
        for p in folder.iterdir():
            if p.is_file():outputs[str(p)]=sha(p)
        if counts['scene_replays']%130==0:print('Verified',counts['scene_replays'],'/1040',flush=True)
    assert counts['records']==1136 and counts['source_decodes']==80 and counts['scene_replays']==1040
    assert counts['service_replays']==sum(p['status']=='success' for p in pred.values())
    result=dict(passed=True,checks=counts,source_hashes=len(bound),generated_file_sha256=outputs,new_fits=0,new_model_forwards=0,
        holdout_image_reads=0,result_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='generated_file_sha256'},indent=2))

if __name__=='__main__':main()
