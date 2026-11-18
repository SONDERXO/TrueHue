"""Shared measurement replay, fifteen partial features and frozen-action targets.

No calibration/tree fitting or correction prediction; target-aware cost minima
are explicit supervision diagnostics and never called model accuracy.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.manual_refinement import verify_export,digest
from src.demo.labelled_measurement import write
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.whole_scene_features import scene_features
from src.model_training.green_distribution_features import green_distribution_features
from src.model_training.aligned_correction_support import blended_action_costs

OUT=ROOT/'outputs/reviewed_feature_control_contract_v1'
PIXELS=ROOT/'outputs/reviewed_photographic_pixels_v1'
CALIB=ROOT/'outputs/refined_mst_grouped_design_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve existing or partial preparation')
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    bound={}
    def bind(p):bound[str(p)]=digest(p);return bound[str(p)]
    for receipt_path in [PIXELS/'independent_verification_PRIVATE.json',PIXELS/'review_PRIVATE.json',CALIB/'review_and_fold_verification_PRIVATE.json']:
        receipt=read(receipt_path);assert receipt['passed'];bind(receipt_path)
        # Metadata-only receipts can include image files. Verify those that are
        # actually needed below; never follow an original-image metadata path.
        for p,h in receipt['input_sha256'].items():
            if Path(p).suffix.lower() in ('.json','.md','.py','.npz'):
                assert bind(p)==h
    parent_path=ROOT/'outputs/green_nonharm_models_v1/models_PRIVATE.json';parent=read(parent_path);bind(parent_path)
    actions=parent['full']['model']['actions'];names=parent['feature_names']
    assert len(actions)==14 and actions[0]==[1.,1.,1.] and len(names)==16
    assert parent['maximum_depth']==4 and names[4]=='input_mst_score'
    code=['src/ita_estimation/compute_ita.py','src/skin_masking/native_anchor_bridge.py',
          'src/model_training/whole_scene_features.py','src/model_training/green_distribution_features.py',
          'src/model_training/aligned_correction_support.py','src/correction/seamless_blend.py',
          'src/distortion_generation/paper_gamma.py']
    codes={p:bind(ROOT/p) for p in code}
    core=dict(schema_version='truehue_reviewed_native_measurement_core_v1',
        geometry='cached_exact_native_anchor_1p5_square_then_linear_256',
        input='uint8_BGR_assumed_or_historically_verified_sRGB_producer_provenance_per_instance',
        mask='explicit_user_reviewed_facial_skin_binary_nonzero',minimum_selected_pixels=1000,
        lab='OpenCV_BGR2LAB_uint8_to_float32_L100over255_a_minus128_b_minus128_mean_round4',
        ita='atan((rounded_L-50)/rounded_b)_degrees_round4_abs_b_ge_1e-6',
        opencv_version=cv2.__version__,numpy_version=np.__version__,
        implementation_sha256={p:h for p,h in codes.items() if 'compute_ita' in p or 'native_anchor' in p},
        scope='shared_computation_only_not_outer_pipeline_or_empirical_MST_transfer')
    core_id=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    contract=dict(schema_version='truehue_reviewed_photographic_feature_control_v1',measurement_core_sha256=core_id,
        feature_names=names,source_features='own_normalized_measurement_and_own_full_RGB8_scene_only',
        missing_mst='null_required_fresh_artifact_no_imputation',frozen_actions=actions,
        actions_origin_sha256=digest(parent_path),maximum_tree_depth=4,
        operator='native_RGB8_direct_gamma_gain_clip_projected_alpha_blend_rint',
        scoring='all_positive_application_alpha_all_channels_RGB_code_MAE_no_subsample',
        target_selection='first_minimum_in_frozen_catalogue_identity_index0',
        correspondence='declared_same_publisher_pixel_grid_not_registration_validation',
        target_identity='accepted_editor_frame_references_itself_source_not_assumed_clean',
        implementation_sha256=codes,calibration_fits_authorized_here=0,tree_fits_authorized_here=0)
    contract_id=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    protocol=ROOT/'docs/reviewed-photographic-feature-target-contract-2026-11-10.md';bind(protocol);bind(Path(__file__))
    OUT.mkdir()
    write(OUT/'execution_plan_PRIVATE.json',dict(core=core,core_sha256=core_id,contract=contract,contract_sha256=contract_id,input_sha256=bound))
    calibration=[]
    old=ROOT/'outputs/native_mst_measurement_readiness_v1'
    old_inventory={k.replace('\\','/'):v for k,v in read(old/'artifact_sha256_PRIVATE.json').items()};bind(old/'artifact_sha256_PRIVATE.json')
    calibration_rows=read(CALIB/'rows_PRIVATE.json');assert len(calibration_rows)==30
    for row in calibration_rows:
        task=ROOT/'outputs/labelled_measurement_queue_v1'/row['case_id'];verify_export(task)
        annotation=Path(row['annotation_folder']);verify_export(annotation)
        assert bind(annotation/'manifest.json')==row['annotation_manifest_sha256']
        assert bind(task/'manifest.json')==row['task_manifest_sha256']
        for p in [task/'image.png',annotation/'measurement_mask.png',annotation/'annotation.json']:bind(p)
        image=cv2.imread(str(task/'image.png'));mask=cv2.imread(str(annotation/'measurement_mask.png'),0)
        native_path=old/row['case_id']/'native_input.png'
        assert bind(native_path)==old_inventory[row['case_id']+'/native_input.png']
        assert np.array_equal(image,cv2.resize(cv2.imread(str(native_path)),(256,256),interpolation=cv2.INTER_LINEAR))
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        assert all(stats[k.removeprefix('input_')]==v for k,v in row['features'].items())
        calibration.append(dict(row,measurement_core_sha256=core_id,computational_replay_exact=True,
            previous_method_sha256=row['measurement_method_sha256'],producer='historical_Stellenbosch_JPEG_assumed_sRGB_cached_BGR8'))
    prepared=[]
    pixels=read(PIXELS/'records_PRIVATE.json');audit=read(ROOT/'outputs/photographic_support_review_audit_v1/audit_PRIVATE.json')
    annotations={r['case_id']:r for r in audit['latest']}
    for row in pixels['records']:
        folder=Path(annotations[row['case_id']]['annotation']);verify_export(folder)
        assert bind(folder/'manifest.json')==row['annotation_manifest_sha256']
        for p in [folder/'photo_used.png',folder/'measurement_mask.png',folder/'report.json']:bind(p)
        image=cv2.imread(str(folder/'photo_used.png'));mask=cv2.imread(str(folder/'measurement_mask.png'),0)
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats==row['input_measurement_statistics']
        greens=green_distribution_features(image,mask);assert greens['valid']
        path=Path(row['pixels_file']);assert bind(path)==row['pixels_sha256']
        with np.load(path,allow_pickle=False) as pack:
            own=pack['input_rgb8'];reference=pack['reference_rgb8'];alpha=pack['alpha'];scoring=pack['scoring_mask']
            assert np.array_equal(scoring,alpha>0) and not alpha[pack['protected']].any()
            features={'input_'+k:stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
            features.update(scene_features(own));features.update(greens['features'])
            assert set(features)==set(names)-{'input_mst_score'} and all(np.isfinite(list(features.values())))
            costs=blended_action_costs(own,reference,alpha,scoring,actions)
            selected=int(np.argmin(costs))
            if row['role']=='target':assert np.array_equal(own,reference) and costs[0]==0 and selected==0
        prepared.append(dict(case_id=row['case_id'],frame=row['frame'],role=row['role'],publisher_group=row['publisher_group'],
            measurement_core_sha256=core_id,previous_support_method_sha256=row['support_method_sha256'],
            feature_control_contract_sha256=contract_id,features_partial={n:(None if n=='input_mst_score' else features[n]) for n in names},
            missing_features=['input_mst_score'],complete_model_vector=False,
            action_costs=costs,oracle_action_index=selected,oracle_direct_controls=actions[selected],
            oracle_cost=costs[selected],identity_cost=costs[0],oracle_gain_over_identity=costs[0]-costs[selected],
            target_aware_supervision_not_prediction=True,clean_identity_constraint=row['role']=='target',
            source_assumed_clean=False,pixels_file=row['pixels_file'],pixels_sha256=row['pixels_sha256'],
            annotation_folder=str(folder),annotation_manifest_sha256=row['annotation_manifest_sha256'],
            provided_mst_label=None,training_admitted=False,calibration_admitted=False))
    ledger=[dict(case_id=r['case_id'],frame=r['frame'],publisher_group=r['publisher_group'],status='prepared_missing_MST') for r in prepared]
    ledger += [dict(r,publisher_group=r['frame'].split('_')[0]) for r in pixels['blocked_roles']]
    assert len(prepared)==14 and len(ledger)==16
    groups=sorted({r['publisher_group'] for r in ledger});folds=[]
    for held in groups:
        available_train=[r['case_id'] for r in prepared if r['publisher_group']!=held]
        available_eval=[r['case_id'] for r in prepared if r['publisher_group']==held]
        folds.append(dict(held_publisher_group=held,available_fitting_roles=available_train,available_evaluation_roles=available_eval,
            attempted_fitting_roles=[r['case_id'] for r in ledger if r['publisher_group']!=held],
            attempted_evaluation_roles=[r['case_id'] for r in ledger if r['publisher_group']==held],
            unavailable_evaluation_roles=[r['case_id'] for r in pixels['blocked_roles'] if r['frame'].split('_')[0]==held],
            tree_execution_authorized=False))
    assert len(folds)==8
    write(OUT/'calibration_rows_PRIVATE.json',calibration)
    write(OUT/'partial_features_and_targets_PRIVATE.json',prepared)
    write(OUT/'publisher_folds_PRIVATE.json',dict(ledger=ledger,folds=folds))
    assert all(digest(p)==h for p,h in bound.items())
    write(OUT/'verification_PRIVATE.json',dict(passed=True,computational_measurement_replays=44,
        calibration_rows=30,photographic_roles=14,available_features_per_role=15,complete_16vectors=0,
        action_catalogue_size=14,action_cost_values=196,target_aware_catalogue_minima=14,
        continuous_target_optimizations=0,new_calibration_fits=0,tree_fits=0,correction_predictions=0,
        publisher_groups=8,blocked_roles=2,original_TIFF_or_JPEG_reads=0,holdout_bytes_read=0,
        core_sha256=core_id,contract_sha256=contract_id,input_sha256=bound))
    print('PASS: 44 exact core replays, 14x15 partial features, 196 fixed-action costs and 14 supervision minima,8 group folds; MST missing and no tree fit.')
    print('Source oracle selections:',[(r['frame'],r['oracle_action_index'],round(r['identity_cost'],4),round(r['oracle_cost'],4)) for r in prepared if r['role']=='source'])


if __name__=='__main__':main()
