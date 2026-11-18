"""Exactly one authorized external development mapping fit and fourteen scores."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import sklearn
from sklearn.isotonic import IsotonicRegression
from src.ita_estimation.shared_core_mst import predict_score

BASE=ROOT/'outputs/reviewed_feature_control_contract_v1'
OUT=ROOT/'outputs/shared_core_mst_features_v1'


def main():
    import hashlib
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
    if OUT.exists():raise FileExistsError('Preserve completed/partial mapping execution')
    bound={}
    for receipt_path in [BASE/'review_PRIVATE.json',BASE/'independent_verification_PRIVATE.json']:
        receipt=read(receipt_path);assert receipt['passed'];bound[str(receipt_path)]=sha(receipt_path)
        for p,h in receipt['input_sha256'].items():assert sha(p)==h;bound[p]=h
    for path in [BASE/'execution_plan_PRIVATE.json',BASE/'calibration_rows_PRIVATE.json',BASE/'partial_features_and_targets_PRIVATE.json',
                 ROOT/'src/ita_estimation/shared_core_mst.py',Path(__file__),ROOT/'docs/reviewed-photographic-feature-target-contract-2026-11-10.md']:
        bound[str(path)]=sha(path)
    previous=read(BASE/'execution_plan_PRIVATE.json');calibration=read(BASE/'calibration_rows_PRIVATE.json');partial=read(BASE/'partial_features_and_targets_PRIVATE.json')
    core=previous['core_sha256'];contract=previous['contract_sha256'];names=previous['contract']['feature_names']
    assert len(calibration)==30 and len(partial)==14 and len(names)==16
    counts=Counter(r['subject_id'] for r in calibration);assert len(counts)==10 and set(counts.values())=={3}
    labels=defaultdict(set)
    for row in calibration:
        assert row['measurement_core_sha256']==core and row['status']=='available'
        assert row['user_review']=='reviewed_selection' and not row['calibration_admitted'] and not row['training_admitted']
        labels[row['subject_id']].add(row['source_mst_exact_decimal'])
    assert all(len(v)==1 for v in labels.values())
    for row in partial:
        assert row['measurement_core_sha256']==core and row['feature_control_contract_sha256']==contract
        assert row['features_partial']['input_mst_score'] is None and row['provided_mst_label'] is None
    OUT.mkdir()
    write(OUT/'execution_plan_PRIVATE.json',dict(new_calibration_fits=1,photographic_scores=14,tree_fits=0,
        measurement_core_sha256=core,feature_control_contract_sha256=contract,sklearn_version=sklearn.__version__,
        fitting_cases=[r['case_id'] for r in calibration],fitting_subjects=sorted(counts),
        photographic_inputs_used_for_fitting=False,closed_loso_assessment_rerun=False,input_sha256=bound))
    x=np.array([r['features']['input_ita_degrees'] for r in calibration],float)
    y=np.array([float(Decimal(r['source_mst_exact_decimal'])) for r in calibration],float)
    weights=np.array([1/counts[r['subject_id']] for r in calibration],float)
    estimator=IsotonicRegression(increasing=False,out_of_bounds='clip').fit(x,y,sample_weight=weights)
    artifact=dict(schema_version='truehue_shared_core_development_mst_v1',status='development_unvalidated_transfer',
        measurement_core_sha256=core,feature_control_contract_sha256=contract,
        ita_knots=estimator.X_thresholds_.tolist(),mst_score_knots=estimator.y_thresholds_.tolist(),
        target='original_decimal_publisher_MST_score_no_category_rounding',fitting_cases=[r['case_id'] for r in calibration],
        fitting_subjects=sorted(counts),subject_row_counts=dict(counts),case_weights=dict(zip([r['case_id'] for r in calibration],weights.tolist())),
        calibration_rows_sha256=sha(BASE/'calibration_rows_PRIVATE.json'),outside_range='clip_to_fitted_endpoints',
        training_data='external_reviewed_Stellenbosch_native_manual30',application_data='reviewed_PPR_source_and_editor_roles',
        producer_provenance='assumed_sRGB_JPEG_calibration_vs_historically_ICC_checked_PPR_RGB8_application',
        empirical_transfer_validated=False,calibration_admitted=False,training_admitted=False,runtime_adopted=False,
        prior_assessment_reference=str(ROOT/'outputs/refined_mst_assessment_v1/results_PRIVATE.json'),
        prior_assessment_is_not_new_validation=True)
    write(OUT/'mapping_PRIVATE.json',artifact);model_hash=sha(OUT/'mapping_PRIVATE.json')
    completed=[]
    for row in partial:
        features=dict(row['features_partial']);ita=features['input_ita_degrees']
        prediction=predict_score(artifact,ita,measurement_core_sha256=core,feature_control_contract_sha256=contract)
        assert np.isclose(prediction['score'],float(estimator.predict([ita])[0]),rtol=1e-12,atol=1e-12)
        features['input_mst_score']=prediction['score'];vector=np.array([features[n] for n in names],np.float32)
        assert vector.shape==(16,) and np.isfinite(vector).all()
        result=dict(row);result.pop('features_partial')
        result.update(features=features,input_vector_float32=vector.tolist(),missing_features=[],complete_model_vector=True,
            mapping_artifact_sha256=model_hash,mst_prediction=prediction,mst_prediction_input='own_input_ita_only',
            complete_development_vector=True,qualified_for_runtime=False,empirical_mst_transfer_validated=False)
        completed.append(result)
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'complete_development_rows_PRIVATE.json',completed)
    summary=dict(passed=True,new_external_mapping_fits=1,calibration_images=30,calibration_subjects=10,
        new_mst_scores=14,complete_development_16vectors=14,qualified_runtime_vectors=0,
        outside_support=sum(r['mst_prediction']['outside_fitting_support'] for r in completed),
        score_range=[min(r['features']['input_mst_score'] for r in completed),max(r['features']['input_mst_score'] for r in completed)],
        correction_tree_fits=0,corrected_image_predictions=0,closed_loso_reruns=0,original_image_reads=0,holdout_bytes_read=0,
        calibration_admitted=False,training_admitted=False,runtime_adopted=False,input_sha256=bound)
    write(OUT/'execution_summary_PRIVATE.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':main()
