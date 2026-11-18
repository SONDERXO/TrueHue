"""Saved scalar residual/model-assumption review. No fitting or prediction API."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
import math
import statistics as st

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/combined_calibration_residual_review_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve existing or partial review')
    bound={}
    def read(path):
        path=Path(path);raw=path.read_bytes();bound[str(path)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    receipt=read(ROOT/'outputs/combined_reviewed_mst_validation_v1/review_PRIVATE.json')
    assert receipt['verification_passed'] and not receipt['development_advancement_passed']
    for p,h in receipt['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=read(ROOT/'outputs/combined_reviewed_mst_validation_v1/results_PRIVATE.json')
    rows={r['case_id']:r for r in read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')}
    folds={f['held_subject']:f for f in result['folds']}
    records=[]
    for saved in result['predictions']:
        r=dict(saved);source=rows[r['case_id']];label=float(Decimal(source['source_mst_exact_decimal']))
        r['features']=source['features'];r['label']=label
        r['family']=r['condition'].rsplit('_',1)[0]
        r['candidate_signed_error']=r['candidate_score']-label
        r['comparator_signed_error']=r['comparator_score']-label
        r['absolute_error_change']=r['candidate_error']-r['comparator_error']
        fold=folds[r['subject_id']];new=fold['model'];old=fold['definition']['saved_600_only_comparator']['model']
        def affine(m):
            coef=dict(zip(m['features'],[c/s for c,s in zip(m['coefficient'],m['scale'])]))
            intercept=m['intercept']-sum(coef[f]*mean for f,mean in zip(m['features'],m['mean']))
            return coef,intercept
        nc,ni=affine(new);oc,oi=affine(old)
        terms={f:(nc[f]-oc[f])*source['features'][f] for f in nc}
        terms['intercept']=ni-oi
        assert math.isclose(sum(terms.values()),r['candidate_raw']-r['comparator_raw'],abs_tol=1e-10,rel_tol=1e-10)
        r['saved_affine_shift_terms']=terms
        r['shift_terms_are_coordinate_dependent_not_causal']=True
        records.append(r)
    def summary(group):
        return dict(n=len(group),subjects=len({r['subject_id'] for r in group}),
            candidate_MAE=st.mean(r['candidate_error'] for r in group),comparator_MAE=st.mean(r['comparator_error'] for r in group),
            candidate_signed_bias=st.mean(r['candidate_signed_error'] for r in group),comparator_signed_bias=st.mean(r['comparator_signed_error'] for r in group),
            better=sum(r['absolute_error_change']<-1e-12 for r in group),worse=sum(r['absolute_error_change']>1e-12 for r in group),
            equal=sum(abs(r['absolute_error_change'])<=1e-12 for r in group),
            candidate_overestimates=sum(r['candidate_signed_error']>0 for r in group),
            outside_fitting_marginals=sum(bool(r['outside_fitting_marginals']) for r in group))
    pairs=[]
    for subject in sorted(folds):
        for family in ('F_cool','H_warm','L_warm'):
            pair={r['illumination']:r for r in records if r['subject_id']==subject and r['family']==family}
            a,b=pair['600'],pair['1200'];assert a['label']==b['label']
            pairs.append(dict(subject_id=subject,family=family,case_600=a['case_id'],case_1200=b['case_id'],
                reference_label=a['label'],candidate_score_change=b['candidate_score']-a['candidate_score'],
                comparator_score_change=b['comparator_score']-a['comparator_score'],
                l_star_change=b['features']['input_mean_l_star']-a['features']['input_mean_l_star'],
                old_case_absolute_error_change=a['absolute_error_change'],new_case_absolute_error_change=b['absolute_error_change']))
    def pair_summary(group):
        return dict(n=len(group),candidate_decreases=sum(p['candidate_score_change']<0 for p in group),
            comparator_decreases=sum(p['comparator_score_change']<0 for p in group),
            all_l_star_increased=all(p['l_star_change']>0 for p in group),
            candidate_mean_shift=st.mean(p['candidate_score_change'] for p in group),
            comparator_mean_shift=st.mean(p['comparator_score_change'] for p in group),
            candidate_mean_absolute_shift=st.mean(abs(p['candidate_score_change']) for p in group),
            comparator_mean_absolute_shift=st.mean(abs(p['comparator_score_change']) for p in group),
            candidate_shift_range=[min(p['candidate_score_change'] for p in group),max(p['candidate_score_change'] for p in group)])
    def corr(x,y):
        xm,ym=st.mean(x),st.mean(y);den=math.sqrt(sum((v-xm)**2 for v in x)*sum((v-ym)**2 for v in y))
        return sum((a-xm)*(b-ym) for a,b in zip(x,y))/den if den else None
    correlations={}
    for f in next(iter(rows.values()))['features']:
        x=[];y=[]
        for subject in sorted(folds):
            group=[r for r in records if r['subject_id']==subject]
            fm=st.mean(r['features'][f] for r in group);em=st.mean(r['candidate_signed_error'] for r in group)
            x.extend(r['features'][f]-fm for r in group);y.extend(r['candidate_signed_error']-em for r in group)
        correlations[f]=corr(x,y)
    strata={}
    for name,test in [('low_reference_le3',lambda x:x<=3),('middle_reference_gt3_lt7',lambda x:3<x<7),('high_reference_ge7',lambda x:x>=7)]:
        strata[name]=summary([r for r in records if test(r['label'])])
    review=dict(overall=summary(records),by_condition={c:summary([r for r in records if r['condition']==c]) for c in sorted({r['condition'] for r in records})},
        by_subject={s:summary([r for r in records if r['subject_id']==s]) for s in sorted(folds)},
        by_illumination={c:summary([r for r in records if r['illumination']==c]) for c in ('600','1200')},
        descriptive_reference_strata=strata,pairs=pair_summary(pairs),
        pairs_by_family={c:pair_summary([p for p in pairs if p['family']==c]) for c in ('F_cool','H_warm','L_warm')},
        within_subject_centered_error_feature_correlations=correlations,
        correlation_limit='Descriptive repeated observations from ten exposed people; not causal, independent tests or a basis for choosing features.',
        model_assumption='One global affine map in ITA/L/a/b per fold, no illumination invariance constraint; scalar code parity does not supply invariance.',
        new_fits=0,new_predictions=0,image_reads=0,holdout_reads=0,calibration_admitted=False,runtime_adopted=False)
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',review),('residuals_PRIVATE.json',records),('matched_pairs_PRIVATE.json',pairs),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:review[k] for k in ('by_illumination','pairs','pairs_by_family','within_subject_centered_error_feature_correlations')},indent=2))


if __name__=='__main__':main()
