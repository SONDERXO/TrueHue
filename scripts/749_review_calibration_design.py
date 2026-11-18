"""Metadata-only calibration-design evidence; no estimators or fits invoked."""
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from decimal import Decimal
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
import numpy as np
OUT=ROOT/'outputs/calibration_design_review_v1'
BASE=ROOT/'outputs/reviewed_feature_control_contract_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    if OUT.exists():raise FileExistsError('Preserve review or partial outputs')
    bound={}
    def load(path):bound[str(path)]=sha(path);return read(path)
    rows=load(BASE/'calibration_rows_PRIVATE.json')
    app=load(ROOT/'outputs/shared_core_mst_features_v1/complete_development_rows_PRIVATE.json')
    mapping=load(ROOT/'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')
    diagnosis=load(ROOT/'outputs/shared_core_mst_features_v1/constant_score_diagnosis_PRIVATE.json')
    iso=load(ROOT/'outputs/refined_mst_assessment_v1/results_PRIVATE.json')
    old_design=load(ROOT/'outputs/refined_mst_grouped_design_v1/rows_PRIVATE.json')
    folds=load(ROOT/'outputs/refined_mst_grouped_design_v1/folds_PRIVATE.json')
    historical_rows=load(ROOT/'outputs/exploratory_real_mst_preparation_v1/rows_PRIVATE.json')
    historical=load(ROOT/'outputs/exploratory_real_mst_results_v1/results_PRIVATE.json')
    for p in [Path(__file__),ROOT/'src/ita_estimation/contextual_mst_experiment.py',
              ROOT/'docs/exploratory-real-mst-results-2026-11-06.md',ROOT/'docs/continuous-mst-correction-protocol-2026-11-06.md']:
        bound[str(p)]=sha(p)
    assert len(rows)==len(old_design)==len(historical_rows)==30 and len(app)==14 and len(folds)==10
    old_by={r['case_id']:r for r in old_design};hist_by={r['case_id']:r for r in historical_rows}
    pred_by={p['case_id']:p for p in iso['predictions']};assert set(pred_by)==set(old_by)
    same_sources=0
    for r in rows:
        previous=old_by[r['case_id']];history=hist_by[r['case_id']]
        for key in ['subject_id','condition','source_sha256','source_mst_exact_decimal','features','annotation_manifest_sha256']:
            assert r[key]==previous[key]
        assert all(r[k]==history[k] for k in ['subject_id','condition','source_sha256','source_mst_exact_decimal'])
        same_sources+=1
        p=pred_by[r['case_id']];assert p['input_ita_degrees']==r['features']['input_ita_degrees']
        assert p['source_mst_exact_decimal']==r['source_mst_exact_decimal']
    def pair_counts(records):
        counts=dict(all_unordered_pairs=0,same_subject_excluded=0,equal_score_excluded=0,
                    distinct_subject_score_pairs=0,monotone_order_violations=0,consistent_pairs=0,equal_ITA_pairs=0)
        witnesses=[]
        for a,b in combinations(records,2):
            counts['all_unordered_pairs']+=1
            if a['subject_id']==b['subject_id']:counts['same_subject_excluded']+=1;continue
            delta_score=Decimal(a['source_mst_exact_decimal'])-Decimal(b['source_mst_exact_decimal'])
            if delta_score==0:counts['equal_score_excluded']+=1;continue
            counts['distinct_subject_score_pairs']+=1
            dx=a['features']['input_ita_degrees']-b['features']['input_ita_degrees']
            if dx==0:counts['equal_ITA_pairs']+=1
            elif (dx>0)==(delta_score>0):
                counts['monotone_order_violations']+=1
                witnesses.append(dict(cases=[a['case_id'],b['case_id']],subjects=[a['subject_id'],b['subject_id']],
                    conditions=[a['condition'],b['condition']],ITA=[a['features']['input_ita_degrees'],b['features']['input_ita_degrees']],
                    source_scores=[a['source_mst_exact_decimal'],b['source_mst_exact_decimal']],score_gap=float(abs(delta_score))))
            else:counts['consistent_pairs']+=1
        assert counts['monotone_order_violations']+counts['consistent_pairs']+counts['equal_ITA_pairs']==counts['distinct_subject_score_pairs']
        return counts,witnesses
    overall,witnesses=pair_counts(rows)
    condition={};features=['input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star']
    for c in sorted({r['condition'] for r in rows}):
        group=[r for r in rows if r['condition']==c];stats,_=pair_counts(group)
        scores=np.array([float(Decimal(r['source_mst_exact_decimal'])) for r in group])
        condition[c]=dict(stats,observations=len(group),negative_b_means=sum(r['features']['input_mean_b_star']<0 for r in group),
            below_L50=sum(r['features']['input_mean_l_star']<50 for r in group),
            descriptive_feature_score_correlations={f:float(np.corrcoef([r['features'][f] for r in group],scores)[0,1]) for f in features})
    pooled=[r for r in rows if diagnosis['plateau_ITA_bounds'][0]<=r['features']['input_ita_degrees']<=diagnosis['plateau_ITA_bounds'][1]]
    subject_counts={s:sum(r['subject_id']==s for r in rows) for s in {r['subject_id'] for r in rows}}
    pooled_mean=sum(float(Decimal(r['source_mst_exact_decimal']))/subject_counts[r['subject_id']] for r in pooled)/sum(1/subject_counts[r['subject_id']] for r in pooled)
    assert len(pooled)==19 and math.isclose(pooled_mean,diagnosis['constant_score'],rel_tol=1e-12)
    collisions=[]
    for a,b in combinations(rows,2):
        if a['source_mst_exact_decimal']!=b['source_mst_exact_decimal'] and all(a['features'][f]==b['features'][f] for f in features):
            collisions.append([a['case_id'],b['case_id']])
    labels=defaultdict(list)
    for r in rows:labels[r['subject_id']].append(r)
    summary=dict(passed=True,rows=30,publisher_subjects=10,conditions=3,
        overall_pairwise_order=overall,by_condition=condition,pooled_observations=19,
        plateau_weighted_reference_mean=pooled_mean,originals_matched_to_historical_contextual_study=same_sources,
        historical_predictions=historical['metrics']['ita_lab_ridge']['available_predictions'],
        historical_equal_subject_MAE=historical['metrics']['ita_lab_ridge']['equal_subject_MAE'],
        current_contextual_performance=None,exact_four_feature_conflicting_score_collisions=collisions,
        data_separability_claim=False,single_photo_identifiability_proved=False,
        new_fits=0,new_mapping_predictions=0,image_reads=0,holdout_bytes_read=0)
    OUT.mkdir()
    (OUT/'evidence_PRIVATE.json').write_text(json.dumps(dict(summary=summary,
        monotone_conflict_witnesses=witnesses,proposed_fixed_features=features,
        source_groups={s:[r['case_id'] for r in group] for s,group in labels.items()},
        current_saved_comparator_metrics=iso['metrics'],current_saved_comparator_conditions=iso['by_condition'],
        input_sha256=bound),indent=2),encoding='utf-8')
    (OUT/'validation_folds_PRIVATE.json').write_text(json.dumps(folds,indent=2),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
