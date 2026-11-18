"""Independent scalar scaling/normal-equation/prediction/metric replay; no refits."""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import hashlib,json,math,statistics
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_contextual_validation_v1'
DESIGN=ROOT/'outputs/calibration_design_review_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    plan=read(OUT/'execution_plan_PRIVATE.json');assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    result=read(OUT/'results_PRIVATE.json')
    rows=read(ROOT/'outputs/reviewed_feature_control_contract_v1/calibration_rows_PRIVATE.json');indexed={r['case_id']:r for r in rows}
    definitions=read(DESIGN/'validation_folds_PRIVATE.json');old=read(DESIGN/'proposed_validation_plan_PRIVATE.json')
    comparator={r['case_id']:r for r in old['saved_comparator_predictions']};predicted={r['case_id']:r for r in result['predictions']}
    assert len(result['folds'])==result['mapping_fits']==10 and len(predicted)==len(result['predictions'])==len(rows)==30
    close=lambda a,b:math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
    errors=[]
    for definition,fold in zip(definitions,result['folds']):
        assert all(definition[k]==fold[k] for k in definition)
        held=fold['held_subject'];train=[indexed[c] for c in fold['fitting_cases']]
        assert len(train)==27 and len(fold['evaluation_cases'])==3 and all(r['subject_id']!=held for r in train)
        counts=Counter(r['subject_id'] for r in train);assert len(counts)==9
        weights=[1/counts[r['subject_id']] for r in train];total=sum(weights)
        model=fold['model'];names=model['features'];assert names==result['features'] and len(names)==4 and model['alpha']==1.
        x=[[r['features'][n] for n in names] for r in train];y=[float(Decimal(r['source_mst_exact_decimal'])) for r in train]
        means=[];scales=[]
        for j in range(4):
            values=[row[j] for row in x]
            mean=sum(w*v for w,v in zip(weights,values))/total
            if max(values)==min(values):mean=values[0]
            sd=math.sqrt(sum(w*(v-mean)**2 for w,v in zip(weights,values))/total)
            means.append(mean);scales.append(sd or 1.)
        assert all(close(a,b) for a,b in zip(means,model['mean'])) and all(close(a,b) for a,b in zip(scales,model['scale']))
        intercept=sum(w*v for w,v in zip(weights,y))/total;assert close(intercept,model['intercept'])
        z=[[(row[j]-means[j])/scales[j] for j in range(4)] for row in x]
        coefficients=model['coefficient']
        # Positive ridge penalty makes this normal-equation solution unique.
        for j in range(4):
            lhs=sum((sum(w*row[j]*row[k] for w,row in zip(weights,z))+(1 if j==k else 0))*coefficients[k] for k in range(4))
            rhs=sum(w*row[j]*(target-intercept) for w,row,target in zip(weights,z,y))
            assert close(lhs,rhs)
        for case in fold['evaluation_cases']:
            row=indexed[case];p=predicted[case];assert row['subject_id']==held==p['subject_id']
            assert all(row[k]==p[k] for k in ['condition','source_mst_exact_decimal'])
            raw=intercept+sum(((row['features'][n]-means[j])/scales[j])*coefficients[j] for j,n in enumerate(names))
            score=min(10.,max(1.,raw));target=float(Decimal(row['source_mst_exact_decimal']))
            assert close(raw,p['raw_mst_score']) and close(score,p['mst_score'])
            assert p['clipped']==(p['raw_mst_score']!=p['mst_score']) and close(abs(score-target),p['absolute_error'])
            oldp=comparator[case]
            assert p['saved_isotonic_score']==oldp['predicted_mst_score'] and p['saved_isotonic_error']==oldp['absolute_error']
            assert p['saved_median_score']==oldp['median_baseline'] and p['saved_median_error']==oldp['baseline_absolute_error']
            outside=[n for j,n in enumerate(names) if not min(r['features'][n] for r in train)<=row['features'][n]<=max(r['features'][n] for r in train)]
            assert p['outside_training_marginals']==outside
            errors.append(case)
    assert len(set(errors))==len(errors)==30
    def metrics(own,saved):
        grouped=defaultdict(list)
        for r in own:grouped[r['subject_id']].append(r)
        assert saved['attempts']==saved['available_predictions']==len(own) and saved['unavailable_predictions']==0
        assert close(saved['image_MAE'],statistics.mean(r['absolute_error'] for r in own))
        assert close(saved['equal_subject_MAE'],statistics.mean(statistics.mean(r['absolute_error'] for r in group) for group in grouped.values()))
        assert close(saved['saved_isotonic_MAE'],statistics.mean(r['saved_isotonic_error'] for r in own))
        assert close(saved['saved_median_MAE'],statistics.mean(r['saved_median_error'] for r in own))
        assert saved['maximum_absolute_error']==max(r['absolute_error'] for r in own)
        assert saved['clipped_predictions']==sum(r['clipped'] for r in own)
        for s,group in grouped.items():
            assert close(saved['within_subject_prediction_ranges'][s],max(r['mst_score'] for r in group)-min(r['mst_score'] for r in group))
    own=result['predictions'];metrics(own,result['metrics'])
    for c,m in result['by_condition'].items():metrics([r for r in own if r['condition']==c],m)
    for s,m in result['by_subject'].items():metrics([r for r in own if r['subject_id']==s],m)
    gate=plan['frozen_gates'];tol=gate['comparison_tolerance'];m=result['metrics']
    expected=dict(full_coverage=True,
        overall_better_than_isotonic=m['equal_subject_MAE']<gate['equal_subject_MAE_strictly_below']-tol,
        overall_better_than_median=m['equal_subject_MAE']<gate['median_MAE_strictly_below']-tol,
        no_condition_worse=all(v['image_MAE']<=gate['condition_MAE_not_above'][c]+tol for c,v in result['by_condition'].items()),
        maximum_error_not_worse=m['maximum_absolute_error']<=gate['maximum_absolute_error_not_above']+tol)
    assert expected==result['advancement_checks'] and result['development_advancement_passed']==all(expected.values())
    assert not any(result[k] for k in ['calibration_admitted','training_admitted','PPR_application_qualified','runtime_adopted','all_data_fit'])
    assert result['new_PPR_scores']==result['correction_tree_fits']==0
    paths=[Path(__file__),OUT/'execution_plan_PRIVATE.json',OUT/'results_PRIVATE.json',DESIGN/'application_coverage_PRIVATE.json']
    dest.write_text(json.dumps(dict(passed=True,normal_equations_and_training_only_scaling=10,
        independent_prediction_replays=30,all_metrics_and_prospective_gates_verified=True,
        extra_estimator_fits=0,new_PPR_predictions=0,tree_fits=0,original_image_reads=0,holdout_bytes_read=0,
        input_sha256={str(p):sha(p) for p in paths}),indent=2),encoding='utf-8')
    print('PASS:10training-only scalings/normal equations,30raw-clipped predictions, allmetrics and frozen gates; no refits.')


if __name__=='__main__':main()
