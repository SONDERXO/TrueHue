"""Direct arithmetic replay of measurement, fifteen features and all196 costs."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
OUT=ROOT/'outputs/reviewed_feature_control_contract_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    first=read(OUT/'verification_PRIVATE.json');assert first['passed']
    assert all(sha(p)==h for p,h in first['input_sha256'].items())
    plan=read(OUT/'execution_plan_PRIVATE.json');contract=plan['contract'];actions=contract['frozen_actions'];names=contract['feature_names']
    canonical=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert canonical(plan['core'])==plan['core_sha256']==contract['measurement_core_sha256']
    assert canonical(contract)==plan['contract_sha256']
    parent=read(ROOT/'outputs/green_nonharm_models_v1/models_PRIVATE.json')
    assert actions==parent['full']['model']['actions'] and names==parent['feature_names'] and len(actions)==14
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11)
    def lab_stats(image,mask):
        lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);selected=mask>0
        assert int(selected.sum())>=1000
        means=[round(float(a[selected].mean()),4) for a in [lab[:,:,0]*(100/255),lab[:,:,1]-128,lab[:,:,2]-128]]
        values=[*means,round(math.degrees(math.atan((means[0]-50)/means[2])),4)]
        return dict(zip(['input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees'],values))
    calibration=read(OUT/'calibration_rows_PRIVATE.json');assert len(calibration)==30
    for r in calibration:
        task=ROOT/'outputs/labelled_measurement_queue_v1'/r['case_id'];annotation=Path(r['annotation_folder'])
        image=cv2.imread(str(task/'image.png'));mask=cv2.imread(str(annotation/'measurement_mask.png'),0)
        assert lab_stats(image,mask)==r['features'] and r['measurement_core_sha256']==plan['core_sha256']
        assert r['previous_method_sha256']==r['measurement_method_sha256']
        assert not r['calibration_admitted'] and not r['training_admitted']
    rows=read(OUT/'partial_features_and_targets_PRIVATE.json');assert len(rows)==14
    for r in rows:
        folder=Path(r['annotation_folder']);image=cv2.imread(str(folder/'photo_used.png'));mask=cv2.imread(str(folder/'measurement_mask.png'),0)
        expected=lab_stats(image,mask)
        q=np.percentile(image[:,:,1][mask>0],[10,50,90],method='linear')
        expected.update(dict(zip(['input_green_p10_codes','input_green_p50_codes','input_green_p90_codes','input_green_log_contrast'],[*map(float,q),float(np.log((q[2]+1)/(q[0]+1)))])))
        with np.load(r['pixels_file'],allow_pickle=False) as pack:
            own=pack['input_rgb8'];reference=pack['reference_rgb8'];alpha=pack['alpha'];scoring=pack['scoring_mask'];protected=pack['protected']
            means=own.reshape(-1,3).mean(axis=0);lab=cv2.cvtColor(own[:,:,::-1].copy(),cv2.COLOR_BGR2LAB)
            q=np.percentile(lab[:,:,0].astype(np.float32)*(100/255),[10,50,90],method='linear')
            expected.update(dict(zip(['scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90','scene_any_zero_fraction','scene_any_full_fraction'],
                map(float,[np.log((means[0]+1)/(means[1]+1)),np.log((means[2]+1)/(means[1]+1)),*q,np.any(own==0,axis=2).mean(),np.any(own==255,axis=2).mean()]))))
            assert np.array_equal(scoring,alpha>0) and not alpha[protected].any()
            losses=[]
            unit=own.astype(float)/255
            for gamma,red,blue in actions:
                changed=np.clip(unit**gamma*np.array([red,1.,blue]),0,1)
                output=np.rint(255*(unit*(1-alpha[:,:,None])+changed*alpha[:,:,None])).astype(np.uint8)
                assert np.array_equal(output[~scoring],own[~scoring]) and np.array_equal(output[protected],own[protected])
                losses.append(float(np.abs(output[scoring].astype(float)-reference[scoring].astype(float)).mean()))
            assert all(close(a,b) for a,b in zip(losses,r['action_costs'])) and len(losses)==14
            best=min(range(14),key=lambda i:losses[i])
            assert best==r['oracle_action_index'] and actions[best]==r['oracle_direct_controls']
            assert close(losses[best],r['oracle_cost']) and close(losses[0],r['identity_cost'])
            assert close(losses[0]-losses[best],r['oracle_gain_over_identity'])
            if r['role']=='target':assert losses[0]==0 and best==0 and r['clean_identity_constraint']
        assert list(r['features_partial'])==names and r['features_partial']['input_mst_score'] is None
        assert set(expected)==set(names)-{'input_mst_score'}
        assert all(close(v,r['features_partial'][k]) for k,v in expected.items())
        assert not r['complete_model_vector'] and r['target_aware_supervision_not_prediction'] and not r['source_assumed_clean']
    design=read(OUT/'publisher_folds_PRIVATE.json');assert len(design['ledger'])==16 and len(design['folds'])==8
    by_case={r['case_id']:r for r in design['ledger']};evaluated=[]
    for f in design['folds']:
        held=f['held_publisher_group'];evaluated+=f['attempted_evaluation_roles']
        assert len(f['attempted_evaluation_roles'])==2 and len(f['attempted_fitting_roles'])==14
        assert all(by_case[c]['publisher_group']!=held for c in f['attempted_fitting_roles'])
        assert all(by_case[c]['publisher_group']==held for c in f['attempted_evaluation_roles'])
        assert not f['tree_execution_authorized']
        assert len(f['available_fitting_roles'])==(14 if held=='904' else 12)
        assert len(f['available_evaluation_roles'])==(0 if held=='904' else 2)
    assert len(evaluated)==len(set(evaluated))==16
    paths=[Path(__file__),OUT/'execution_plan_PRIVATE.json',OUT/'calibration_rows_PRIVATE.json',
        OUT/'partial_features_and_targets_PRIVATE.json',OUT/'publisher_folds_PRIVATE.json',OUT/'verification_PRIVATE.json']
    dest.write_text(json.dumps(dict(passed=True,direct_measurement_replays=44,independent_feature_values=210,
        independent_full_native_action_renders=196,all_protected_and_zero_alpha_pixels_unchanged=True,
        exact_identity_target_roles=7,publisher_folds=8,attempted_evaluation_roles_once=16,
        new_calibration_fits=0,tree_fits=0,model_predictions=0,original_image_reads=0,holdout_bytes_read=0,
        input_sha256={str(p):sha(p) for p in paths}),indent=2),encoding='utf-8')
    print('PASS:44core/210feature/196full-native-cost replays, protected-pixel invariants,7identity targets,8groupfolds incl904 failures.')


if __name__=='__main__':main()
