"""Replay all44 cached-grid inputs/targets/features and photo-held folds."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.manual_refinement import verify_export
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.whole_scene_features import scene_features
from src.model_training.green_distribution_features import green_distribution_features
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=P/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bound=read(P/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    rows=read(P/'rows_PRIVATE.json');folds=read(P/'folds_PRIVATE.json');plan=read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json');mapping=read(ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')
    assert len(rows)==len({r['case_id'] for r in rows})==44 and all(r['status']=='available' for r in rows)
    endpoint_samples=0
    for r in rows:
        folder=Path(r['annotation']);verify_export(folder);assert sha(folder/'manifest.json')==r['annotation_manifest_sha256']
        q=r['recipe'];g=q['gamma'];controls=[1/g,q['red_gain']**(-1/g),q['blue_gain']**(-1/g)];assert controls==r['nominal_controls']
        clean=cv2.imread(str(folder/'photo_used.png'))[:,:,::-1];unit=clean/255.;forward=np.clip(unit**g*[q['red_gain'],1.,q['blue_gain']],0,1);expected=np.rint(255*forward).astype(np.uint8)
        assert sha(r['pixels_file'])==r['pixels_sha256']
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            np.testing.assert_array_equal(pack['input_rgb8'],expected);np.testing.assert_array_equal(pack['reference_rgb8'],clean)
            for key,name in [('measurement_mask','measurement_mask.png'),('correction_mask','correction_mask.png')]:np.testing.assert_array_equal(pack[key],cv2.imread(str(folder/name),0))
            np.testing.assert_array_equal(pack['alpha'],np.load(folder/'correction_alpha.npy',allow_pickle=False));np.testing.assert_array_equal(pack['scoring_mask'],pack['alpha']>0);assert not pack['alpha'][pack['protected']].any()
            stats=compute_masked_lab_statistics(expected[:,:,::-1].copy(),pack['measurement_mask'],1000);assert stats==r['statistics']
            features={'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']};features.update(green_distribution_features(expected[:,:,::-1].copy(),pack['measurement_mask'])['features']);features.update(scene_features(expected))
            score=float(np.interp(stats['ita_degrees'],mapping['ita_knots'],mapping['mst_score_knots']));features['input_mst_score']=score
            np.testing.assert_allclose([features[n] for n in plan['feature_names']],[r['features'][n] for n in plan['feature_names']],rtol=1e-12,atol=1e-12)
            np.testing.assert_array_equal(np.array([features[n] for n in plan['feature_names']],np.float32),r['input_vector_float32'])
            endpoint_samples+=int(np.count_nonzero(((expected==0)|(expected==255))&~((clean==0)|(clean==255))))
    groups={r['publisher_group'] for r in rows};assert len(groups)==len(folds)==11
    for f in folds:
        assert f['fitting_cases']==[r['case_id'] for r in rows if r['publisher_group']!=f['held_publisher_group']]
        assert f['evaluation_cases']==[r['case_id'] for r in rows if r['publisher_group']==f['held_publisher_group']]
        assert len(f['fitting_cases'])==40 and len(f['evaluation_cases'])==4
    ledger=read(P/'role_ledger_PRIVATE.json');assert len(ledger)==48 and sum(r['status'].startswith('excluded') for r in ledger)==4
    dest.write_text(json.dumps(dict(passed=True,pixel_recipe_replays=44,same_geometry_support_replays=44,feature_values_replayed=704,mapping_values_independently_interpolated=44,nominal_targets_checked=44,photo_held_folds=11,new_endpoint_channel_samples=endpoint_samples,original_photo_reads=0,image_model_calls=0,fits=0,holdout_reads=0,input_sha256={str(p):sha(p) for p in [P/'rows_PRIVATE.json',P/'folds_PRIVATE.json',P/'mapping_application_PRIVATE.json',Path(__file__)]}),indent=2)+'\n')
    print('PASS:44 recipes/targets/supports/features,704 values,11 held-photo folds; new endpoint channels',endpoint_samples)

if __name__=='__main__':main()
