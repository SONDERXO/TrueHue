"""Independent scalar normal-equation/prediction/metric replay; zero fits."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import math
import statistics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/combined_reviewed_mst_validation_v1'
DESIGN=ROOT/'outputs/combined_reviewed_mst_design_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve verification')
    execution=read(OUT/'execution_plan_PRIVATE.json')
    assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    result=read(OUT/'results_PRIVATE.json')
    rows={r['case_id']:r for r in read(DESIGN/'rows_PRIVATE.json')}
    definitions=read(DESIGN/'folds_PRIVATE.json')
    design=read(DESIGN/'proposed_validation_PRIVATE.json')
    predicted={p['case_id']:p for p in result['predictions']}
    assert len(predicted)==len(result['predictions'])==60 and result['mapping_fits']==len(result['folds'])==10
    def close(a,b):
        assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)
    def score(model,feature):
        raw=model['intercept']+sum((feature[f]-m)/s*c for f,m,s,c in zip(model['features'],model['mean'],model['scale'],model['coefficient']))
        return raw,min(10,max(1,raw))
    for definition,fold in zip(definitions,result['folds']):
        assert fold['definition']==definition
        model=fold['model'];names=model['features']
        training=[rows[c] for c in definition['fitting_cases']]
        assert len(training)==54 and all(r['subject_id']!=fold['held_subject'] for r in training)
        weights=[1/6]*54;total=sum(weights)
        x=[[r['features'][f] for f in names] for r in training]
        y=[float(Decimal(r['source_mst_exact_decimal'])) for r in training]
        mean=[sum(w*row[i] for w,row in zip(weights,x))/total for i in range(4)]
        scale=[math.sqrt(sum(w*(row[i]-mean[i])**2 for w,row in zip(weights,x))/total) or 1 for i in range(4)]
        intercept=sum(w*v for w,v in zip(weights,y))/total
        for actual,expected in zip(model['mean'],mean):close(actual,expected)
        for actual,expected in zip(model['scale'],scale):close(actual,expected)
        close(model['intercept'],intercept)
        z=[[(row[i]-mean[i])/scale[i] for i in range(4)] for row in x]
        # Verify recorded coefficients solve the independently assembled equations.
        for i in range(4):
            left=sum((sum(w*row[i]*row[j] for w,row in zip(weights,z))+(i==j))*model['coefficient'][j] for j in range(4))
            right=sum(w*row[i]*(value-intercept) for w,row,value in zip(weights,z,y))
            close(left,right)
        labels={r['subject_id']:float(Decimal(r['source_mst_exact_decimal'])) for r in training}
        median=statistics.median(labels.values());close(fold['median_baseline'],median)
        lower={f:min(r['features'][f] for r in training) for f in names}
        upper={f:max(r['features'][f] for r in training) for f in names}
        for case in definition['evaluation_cases']:
            p=predicted[case];row=rows[case]
            assert p['subject_id']==row['subject_id']==fold['held_subject']
            assert p['condition']==row['condition'] and p['source_mst_exact_decimal']==row['source_mst_exact_decimal']
            label=float(Decimal(row['source_mst_exact_decimal']))
            for prefix,model_to_check in [('candidate',model),('comparator',definition['saved_600_only_comparator']['model'])]:
                raw,clipped=score(model_to_check,row['features'])
                close(p[prefix+'_raw'],raw);close(p[prefix+'_score'],clipped)
                close(p[prefix+'_error'],abs(clipped-label))
                assert p[prefix+'_clipped']==(raw!=clipped)
            close(p['median_score'],median);close(p['median_error'],abs(median-label))
            assert p['outside_fitting_marginals']==[f for f in names if not lower[f]<=row['features'][f]<=upper[f]]
    def verify_metrics(group,stored):
        subjects=defaultdict(list)
        for p in group:subjects[p['subject_id']].append(p)
        assert stored['attempts']==len(group) and stored['subjects']==len(subjects)
        for prefix in ('candidate','comparator','median'):
            close(stored[prefix+'_MAE'],statistics.mean(statistics.mean(p[prefix+'_error'] for p in g) for g in subjects.values()))
            close(stored[prefix+'_maximum_error'],max(p[prefix+'_error'] for p in group))
        assert stored['candidate_clips']==sum(p['candidate_clipped'] for p in group)
        for subject,g in subjects.items():close(stored['candidate_within_subject_ranges'][subject],max(p['candidate_score'] for p in g)-min(p['candidate_score'] for p in g))
    predictions=result['predictions'];verify_metrics(predictions,result['metrics'])
    for key,field in [('by_condition','condition'),('by_illumination','illumination'),('by_subject','subject_id')]:
        for value,metrics in result[key].items():verify_metrics([p for p in predictions if p[field]==value],metrics)
    old=[p for p in predictions if p['illumination']=='600'];new=[p for p in predictions if p['illumination']=='1200'];t=design['comparison_tolerance']
    avg=lambda group,key:statistics.mean(p[key+'_error'] for p in group)
    checks=dict(full_coverage=set(predicted)==set(rows),overall_better_than_comparator=avg(predictions,'candidate')<avg(predictions,'comparator')-t,
        overall_better_than_median=avg(predictions,'candidate')<avg(predictions,'median')-t,
        new_1200_better_than_comparator=avg(new,'candidate')<avg(new,'comparator')-t,
        each_old_condition_nonworse=all(avg([p for p in old if p['condition']==c],'candidate')<=limit+t for c,limit in design['saved_600_condition_limits'].items()),
        combined_maximum_nonworse=max(p['candidate_error'] for p in predictions)<=max(p['comparator_error'] for p in predictions)+t,
        old_maximum_nonworse=max(p['candidate_error'] for p in old)<=design['saved_600_maximum_error_limit']+t)
    assert checks==result['advancement_checks'] and all(checks.values())==result['development_advancement_passed']
    assert all(result[k] is False for k in ('calibration_admitted','training_admitted','PPR_application_qualified','runtime_adopted','all_data_fit'))
    # Old-condition saved comparator predictions must replay the closed assessment exactly.
    original={p['case_id']:p for p in read(ROOT/'outputs/reviewed_contextual_validation_v1/results_PRIVATE.json')['predictions']}
    for p in old:
        close(p['comparator_raw'],original[p['case_id']]['raw_mst_score'])
        close(p['comparator_score'],original[p['case_id']]['mst_score'])
    assert all(sha(p)==h for p,h in execution['input_sha256'].items())
    report=dict(passed=True,normal_equations_checked=10,candidate_predictions_checked=60,comparator_predictions_checked=60,
                original_comparator_replays=30,all_metrics_and_frozen_checks=True,new_fits=0,new_predictions=0,
                tolerance=1e-10,photo_bytes_read=0,holdout_reads=0,results_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:10 scalar normal-equation/scaling replays;120 prediction checks;30 original comparator replays;all metrics and gates.')


if __name__=='__main__':
    main()
