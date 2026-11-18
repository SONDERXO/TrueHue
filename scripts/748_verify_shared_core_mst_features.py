"""Independent PAVA/feature completion replay, including constant-score diagnosis."""
from pathlib import Path
from collections import Counter
import importlib.util,hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
OUT=ROOT/'outputs/shared_core_mst_features_v1'
BASE=ROOT/'outputs/reviewed_feature_control_contract_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    plan=read(OUT/'execution_plan_PRIVATE.json');summary=read(OUT/'execution_summary_PRIVATE.json')
    assert summary['passed'] and plan['new_calibration_fits']==summary['new_external_mapping_fits']==1
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    artifact=read(OUT/'mapping_PRIVATE.json');rows=read(BASE/'calibration_rows_PRIVATE.json')
    partial=read(BASE/'partial_features_and_targets_PRIVATE.json');complete=read(OUT/'complete_development_rows_PRIVATE.json')
    frozen=read(BASE/'execution_plan_PRIVATE.json');names=frozen['contract']['feature_names']
    assert len(rows)==30 and len(partial)==len(complete)==14
    counts=Counter(r['subject_id'] for r in rows);weights={r['case_id']:1/counts[r['subject_id']] for r in rows}
    assert artifact['case_weights']==weights and artifact['fitting_cases']==[r['case_id'] for r in rows]
    assert artifact['fitting_subjects']==sorted(counts) and sum(counts.values())==30
    assert artifact['measurement_core_sha256']==frozen['core_sha256'] and artifact['feature_control_contract_sha256']==frozen['contract_sha256']
    assert artifact['calibration_rows_sha256']==sha(BASE/'calibration_rows_PRIVATE.json')
    assert all(artifact[k] is False for k in ['empirical_transfer_validated','calibration_admitted','training_admitted','runtime_adopted'])
    # Reuse the separate stdlib verifier algorithm, never the candidate estimator.
    reference_path=ROOT/'scripts/732_verify_refined_mst_assessment.py'
    spec=importlib.util.spec_from_file_location('independent_weighted_PAVA',reference_path)
    reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
    xs,ys=reference.reconstruct(rows,weights)
    ax,ay=artifact['ita_knots'],artifact['mst_score_knots']
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11)
    for x,y in zip(xs,ys):assert close(reference.interpolate(ax,ay,x),y)
    for x,y in zip(ax,ay):assert close(reference.interpolate(xs,ys,x),y)
    by_case={r['case_id']:r for r in partial};scores=[];inputs=[]
    for r in complete:
        old=by_case[r['case_id']];features=r['features'];ita=old['features_partial']['input_ita_degrees']
        value=reference.interpolate(xs,ys,ita)
        assert close(features['input_mst_score'],value) and list(features)==names
        assert all(features[k]==v for k,v in old['features_partial'].items() if k!='input_mst_score')
        assert r['mst_prediction']['outside_fitting_support']==(ita<xs[0] or ita>xs[-1])
        assert r['mst_prediction']['endpoint_clipped']==r['mst_prediction']['outside_fitting_support']
        assert close(r['mst_prediction']['score'],value)
        assert r['mapping_artifact_sha256']==sha(OUT/'mapping_PRIVATE.json')
        assert r['input_vector_float32']==np.array([features[k] for k in names],np.float32).tolist()
        assert np.isfinite(r['input_vector_float32']).all() and r['complete_development_vector'] and r['complete_model_vector']
        assert r['missing_features']==[] and not r['qualified_for_runtime'] and not r['empirical_mst_transfer_validated']
        assert not r['training_admitted'] and not r['calibration_admitted'] and r['provided_mst_label'] is None
        for k in ['action_costs','oracle_action_index','oracle_direct_controls','oracle_cost','identity_cost','oracle_gain_over_identity','clean_identity_constraint']:
            assert r[k]==old[k]
        scores.append(features['input_mst_score']);inputs.append(ita)
    assert len(set(scores))==1
    value=scores[0];cover=[(x,y) for x,y in zip(xs,ys) if close(y,value)]
    plateau=[min(x for x,y in cover),max(x for x,y in cover)]
    assert all(plateau[0]<=x<=plateau[1] for x in inputs)
    diagnosis=dict(distinct_photographic_MST_scores=len(set(scores)),constant_score=value,
        photographic_ITA_range=[min(inputs),max(inputs)],plateau_ITA_bounds=plateau,
        calibration_observations_in_plateau=sum(plateau[0]<=x<=plateau[1] for x in xs),
        outside_support=0,missing_value_imputation=False,
        consequence='MST_feature_cannot_supply_a_split_or_demonstrate_conditioning_on_this_photographic_batch',
        task_impossibility_claim=False,automatic_mapping_repair_selected=False)
    (OUT/'constant_score_diagnosis_PRIVATE.json').write_text(json.dumps(diagnosis,indent=2),encoding='utf-8')
    paths=[Path(__file__),reference_path,OUT/'execution_plan_PRIVATE.json',OUT/'mapping_PRIVATE.json',OUT/'execution_summary_PRIVATE.json',
        OUT/'complete_development_rows_PRIVATE.json',OUT/'constant_score_diagnosis_PRIVATE.json',BASE/'partial_features_and_targets_PRIVATE.json']
    dest.write_text(json.dumps(dict(passed=True,independent_PAVA_replays=1,checked_MST_scores=14,
        checked_feature_values=224,prior_210_feature_values_unchanged=True,all196_action_costs_unchanged=True,
        constant_MST_feature_confirmed=True,new_tree_fits=0,original_image_reads=0,holdout_bytes_read=0,
        input_sha256={str(p):sha(p) for p in paths}),indent=2),encoding='utf-8')
    print('PASS: independent PAVA solution and14scores/224featurevalues; all14scores share genuine fitted plateau, not clipping or imputation.')
    print(json.dumps(diagnosis,indent=2))


if __name__=='__main__':main()
