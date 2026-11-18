"""Independent scalar-order/statistic and prospective-plan verification; no fits."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,math,statistics
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/calibration_design_review_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    evidence=read(OUT/'evidence_PRIVATE.json');plan=read(OUT/'proposed_validation_plan_PRIVATE.json')
    assert all(sha(p)==h for p,h in evidence['input_sha256'].items())
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    rows=read(ROOT/'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json')
    def count(own):
        eligible=bad=0
        for lighter in own:
            for darker in own:
                if lighter['subject_id']==darker['subject_id']:continue
                if Decimal(lighter['source_mst_exact_decimal'])>=Decimal(darker['source_mst_exact_decimal']):continue
                eligible+=1
                if lighter['features']['input_ita_degrees']<darker['features']['input_ita_degrees']:bad+=1
        return eligible,bad
    eligible,bad=count(rows)
    assert eligible==396 and bad==136
    assert (eligible,bad)==(evidence['summary']['overall_pairwise_order']['distinct_subject_score_pairs'],evidence['summary']['overall_pairwise_order']['monotone_order_violations'])
    for c,summary in evidence['summary']['by_condition'].items():
        subset=[r for r in rows if r['condition']==c]
        assert count(subset)==(summary['distinct_subject_score_pairs'],summary['monotone_order_violations'])
        target=[float(Decimal(r['source_mst_exact_decimal'])) for r in subset];ym=statistics.mean(target)
        for name,corr in summary['descriptive_feature_score_correlations'].items():
            x=[r['features'][name] for r in subset];xm=statistics.mean(x)
            scalar=sum((a-xm)*(b-ym) for a,b in zip(x,target))/math.sqrt(sum((a-xm)**2 for a in x)*sum((b-ym)**2 for b in target))
            assert math.isclose(scalar,corr,rel_tol=1e-12,abs_tol=1e-12)
    assert plan['new_fits']==plan['new_predictions']==0 and plan['planned_fits']==10 and plan['planned_predictions']==30
    assert plan['alpha']==1 and plan['features']==['input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star']
    assert not plan['execution_authorized_by_this_packaging'] and not plan['all_data_fit'] and not plan['photographic_prediction']
    iso=read(ROOT/'outputs/refined_mst_assessment_v1/results_PRIVATE.json')
    assert plan['saved_comparator_predictions']==iso['predictions']
    assert plan['development_advancement']['equal_subject_MAE_strictly_below']==iso['metrics']['equal_subject_MAE']
    assert plan['development_advancement']['condition_MAE_not_above']=={k:v['image_MAE'] for k,v in iso['by_condition'].items()}
    paths=[Path(__file__),OUT/'evidence_PRIVATE.json',OUT/'validation_folds_PRIVATE.json',OUT/'proposed_validation_plan_PRIVATE.json']
    dest.write_text(json.dumps(dict(passed=True,distinct_subject_score_pairs=396,scalar_order_violations=136,
        all_condition_counts_correlations_verified=True,matched_saved_comparators=30,
        prospective_fixed_candidate=True,new_fits=0,new_predictions=0,image_reads=0,holdout_bytes_read=0,
        input_sha256={str(p):sha(p) for p in paths}),indent=2),encoding='utf-8')
    print('PASS:136/396 conflicts, allcondition correlations/counts, matched30comparators and fixed candidate plan verified; zero fits.')


if __name__=='__main__':main()
