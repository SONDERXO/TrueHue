"""Reconstruct prepared variants, masks, targets and routing without tree fits."""
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.table2_composite import SETTINGS
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.evaluation.mask_support_quality import support_retention
h=importlib.import_module('256_compare_clean_control_tree_depth')


def main():
    out=ROOT/'outputs/primary_training_preparation_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(out/'plan.json');rows=h.read(out/'attempts.json');assert len(rows)==104 and len({r['pair_id'] for r in rows})==104
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),plan['measurement_contract_sha256'])
    verified_masks=0;verified_targets=0
    old=ROOT/'outputs/three_variant_training_candidates_v1'
    old_rows={r['pair_id']:r for r in map(__import__('json').loads,(old/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    parity=0
    for r in rows:
        reference=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB)
        ref_mask=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        if r['variant']=='identity':
            assert r['paper_target']==[1.,1.,1.] and r['lane']=='approved_original_control' and r['existing_approval_only']
            assert r['input_path']==r['reference_path'] and r['input_mask_path']==r['reference_mask_path'];continue
        assert not r['training_eligible'] and r['exact_input_mask_review']=='pending'
        values=SETTINGS[r['severity']];floating=reference.astype(float)/255
        if r['variant'] in ('exposure','combined'):
            floating=(floating**values['gamma']-.5)*(1+values['contrast']/100)+.5+values['brightness']/255
        if r['variant'] in ('color','combined'):floating+=np.array([values['cyan_red'],0,values['yellow_blue']])/255
        clipped=(floating<0)|(floating>1)
        assert int(clipped[ref_mask].any(axis=1).sum())==r['clipping']['clipped_pixels']
        assert int(clipped[ref_mask].sum())==r['clipping']['clipped_channel_samples']
        generated=reference.copy();generated[ref_mask]=np.rint(np.clip(floating[ref_mask],0,1)*255).astype(np.uint8)
        image=cv2.imread(str(ROOT/r['input_path']));np.testing.assert_array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),generated)
        assert h.digest(ROOT/r['input_path'])==r['input_sha256'] and h.digest(ROOT/r['input_mask_path'])==r['input_mask_sha256']
        mask=cv2.imread(str(ROOT/r['input_mask_path']),0)
        if r['measurement']['status']=='success':
            x,y,w,height=r['measurement']['face_box'];crop=image[y:y+height,x:x+w]
            points=np.load(out/'geometry'/(r['source_id']+'_'+r['variant']+'_landmarks.npy'))
            candidate=create_candidate_mask_bgr(crop);exclusion=build_feature_exclusion_mask(crop,points,dilation=0)
            local,_=exclude_complete_mouth(cv2.bitwise_and(keep_largest_connected_component(candidate),cv2.bitwise_not(exclusion)),points)
            expected=np.zeros_like(mask);expected[y:y+height,x:x+w]=local;np.testing.assert_array_equal(mask,expected);verified_masks+=1
            stats=compute_masked_lab_statistics(crop,local,1000);assert stats==r['measurement']['statistics']
            features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
            assert features==r['features'] and facial_endpoint_features(image,mask>0)['features']==r['endpoint_features']
            assert support_retention(ref_mask,mask>0,mask>0)==r['support_screen']
            fit=r['target_fit']
            if fit['parameters'] is not None:
                gamma,red,blue=fit['parameters'];selected=(mask>0)&ref_mask
                output=np.clip((generated.astype(float)/255)**(1/gamma)*[red,1,blue],0,1)
                residual=float(np.sqrt(np.mean((output[selected]-reference[selected].astype(float)/255)**2)))
                assert abs(residual-fit['float_rgb_rmse'])<1e-12 and int(selected.sum())==fit['selected_pixels']
                assert r['paper_target']==[1/gamma,red,blue];verified_targets+=1
                lane='clipped_stress_pending_mask_review' if r['clipping']['clipped_pixels'] else 'primary_pending_exact_mask_review' if r['support_screen']['screen_pass'] else 'unclipped_mask_screen_hold'
                assert lane==r['lane']
        previous=old_rows.get(r['source_image_id']+'__'+r['variant'])
        if previous:
            np.testing.assert_array_equal(image,cv2.imread(str(ROOT/previous['input_path'])))
            np.testing.assert_array_equal(mask,cv2.imread(str(ROOT/previous['input_mask_path']),0));parity+=1
    assert verified_masks==78 and verified_targets==78
    summary=h.read(out/'summary.json')
    for lane,count in summary['lanes'].items():assert sum(r['lane']==lane for r in rows)==count
    queue=h.read(out/'primary_review_queue.json');assert queue==[r for r in rows if r['lane']=='primary_pending_exact_mask_review']
    h.write(target,dict(status='pass',generated_variants_reconstructed=78,rule_masks_and_measurements_reconstructed=verified_masks,
        target_curves_and_residuals_verified=verified_targets,existing_variants_pixel_parity=parity,controls_preserved=26,
        lane_counts_verified=True,new_distorted_admissions=0,correction_tree_fits=0,
        evidence_sha256={p.relative_to(out).as_posix():h.digest(p) for p in out.rglob('*') if p.is_file()}))
    print('PASS: 78 generated variants/masks/targets, 26 controls, all lane holds; old-variant parity',parity)


if __name__=='__main__':main()
