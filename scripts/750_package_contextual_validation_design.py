"""Freeze one proposed validation recipe and matched comparators, without fitting."""
from pathlib import Path
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/calibration_design_review_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    target=OUT/'proposed_validation_plan_PRIVATE.json'
    if target.exists():raise FileExistsError('Preserve plan')
    evidence=read(OUT/'evidence_PRIVATE.json');assert evidence['summary']['passed']
    bound=dict(evidence['input_sha256'])
    assert all(sha(p)==h for p,h in bound.items())
    rows=read(ROOT/'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json')
    folds=read(OUT/'validation_folds_PRIVATE.json')
    old=read(ROOT/'outputs/refined_mst_assessment_v1/results_PRIVATE.json')
    assert len(rows)==30 and len(folds)==10 and len(old['predictions'])==30
    by_case={r['case_id']:r for r in rows};scored=[]
    for f in folds:
        assert len(f['fitting_cases'])==27 and len(f['evaluation_cases'])==3
        assert all(by_case[c]['subject_id']!=f['held_subject'] for c in f['fitting_cases'])
        assert all(by_case[c]['subject_id']==f['held_subject'] for c in f['evaluation_cases'])
        assert math.isclose(sum(f['fitting_weights'].values()),9,abs_tol=1e-12)
        scored+=f['evaluation_cases']
    assert len(set(scored))==len(scored)==30
    thresholds=dict(equal_subject_MAE_strictly_below=old['metrics']['equal_subject_MAE'],
        median_MAE_strictly_below=old['metrics']['baseline_equal_subject_MAE'],
        condition_MAE_not_above={k:v['image_MAE'] for k,v in old['by_condition'].items()},
        maximum_absolute_error_not_above=max(r['absolute_error'] for r in old['predictions']),comparison_tolerance=1e-12)
    for path in [Path(__file__),OUT/'evidence_PRIVATE.json',OUT/'validation_folds_PRIVATE.json',
                 ROOT/'docs/contextual-reviewed-mst-validation-protocol-2026-11-10.md']:
        bound[str(path)]=sha(path)
    plan=dict(status='proposed_not_executed',candidate='existing_ITA_L_a_b_subject_weighted_standardized_ridge_alpha1',
        features=evidence['proposed_fixed_features'],alpha=1.,intercept='weighted_training_mean_unpenalized',
        planned_fits=10,planned_predictions=30,all_data_fit=False,photographic_prediction=False,
        closed_isotonic_fits_reused=False,saved_comparator_predictions=old['predictions'],development_advancement=thresholds,
        final_predictor='decision_tree_unchanged',method_scope='explicit_contextual_MST_extension_not_scalar_lookup',
        execution_authorized_by_this_packaging=False,new_fits=0,new_predictions=0,holdout_bytes_read=0,input_sha256=bound)
    target.write_text(json.dumps(plan,indent=2),encoding='utf-8')
    print('Prepared proposed single-candidate10fold contextual validation with exact30case comparators and fixed gates; zero fits.')


if __name__=='__main__':main()
