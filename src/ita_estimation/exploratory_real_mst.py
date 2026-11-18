"""Explicitly unadmitted development diagnostic, separate from qualified fitting."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import math
from .contextual_mst_experiment import FEATURES, METHODS, _ridge, _metrics, predict


def validate(rows):
    if not rows:raise ValueError('Attempt rows required')
    ids=set();labels={}
    for r in rows:
        if any(not isinstance(r.get(k),str) or not r[k] for k in ['case_id','subject_id','condition']):
            raise ValueError('Case, publisher key and condition required')
        if r['case_id'] in ids:raise ValueError('Duplicate case')
        ids.add(r['case_id'])
        if r.get('calibration_admitted') is not False or r.get('training_admitted') is not False or r.get('actual_skin_validity')!='unverified':
            raise ValueError('This diagnostic must preserve explicit unadmitted/unverified status')
        try:
            if not isinstance(r['source_mst_exact_decimal'],str):raise ValueError('Exact decimal string required')
            score=Decimal(r['source_mst_exact_decimal'])
        except (KeyError,InvalidOperation) as e:raise ValueError('Invalid source score') from e
        if not score.is_finite() or not 1<=score<=10:raise ValueError('Invalid source score')
        if r['subject_id'] in labels and labels[r['subject_id']]!=score:raise ValueError('Inconsistent source score')
        labels[r['subject_id']]=score
        if r.get('status')=='available':
            f=r.get('features')
            if not isinstance(f,dict) or set(f)!=set(FEATURES):raise ValueError('Exact input-only features required')
            if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) for v in f.values()):raise ValueError('Finite features required')
            if not -90<=f[FEATURES[0]]<=90 or not 0<=f[FEATURES[1]]<=100 or any(not -128<=f[k]<=127 for k in FEATURES[2:]):raise ValueError('Invalid measured range')
        elif r.get('status')!='unavailable' or r.get('features') is not None or not isinstance(r.get('reason'),str) or not r['reason']:
            raise ValueError('Unavailable outcome requires reason and no features')
    if len(labels)<3:raise ValueError('At least three publisher keys required')


def evaluate(rows):
    """Fit exactly two fixed ridges per key; never declare calibration admission."""
    validate(rows);folds=[];records=[]
    for held in sorted({r['subject_id'] for r in rows}):
        train=[r for r in rows if r['subject_id']!=held and r['status']=='available']
        test=[r for r in rows if r['subject_id']==held]
        if not train:raise ValueError('No fitting measurements')
        models=dict(ita_lab_ridge=_ridge(train,FEATURES),ita_only_ridge=_ridge(train,FEATURES[:1]))
        scores={r['subject_id']:float(Decimal(r['source_mst_exact_decimal'])) for r in train}
        ordered=sorted(scores.values());n=len(ordered);median=(ordered[(n-1)//2]+ordered[n//2])/2
        folds.append(dict(held_subject=held,training_subjects=sorted(scores),training_cases=[r['case_id'] for r in train],
            evaluation_cases=[r['case_id'] for r in test],models=models,median_baseline=median))
        for r in test:
            p={m:None for m in METHODS}
            if r['status']=='available':
                p.update({m:predict(model,r['features']) for m,model in models.items()})
                p['subject_median']=dict(raw=median,score=median)
            records.append(dict(case_id=r['case_id'],subject_id=held,condition=r['condition'],
                source_mst_exact_decimal=r['source_mst_exact_decimal'],status=r['status'],
                unavailable_reason=r.get('reason'),predictions=p))
    def metrics(rr):return {m:_metrics(rr,m) for m in METHODS}
    def interval(r):
        s=Decimal(r['source_mst_exact_decimal'])
        return '[1,3)' if s<3 else '[3,5)' if s<5 else '[5,7)' if s<7 else '[7,9)' if s<9 else '[9,10]'
    return dict(experiment='unadmitted_real_mst_development_v1',exploratory_authorized=True,
        scientific_validation=False,calibration_admissions=0,training_admissions=0,production_adopted=False,
        mapping_ridge_fits=2*len(folds),correction_tree_fits=0,folds=folds,records=records,metrics=metrics(records),
        by_condition={c:metrics([r for r in records if r['condition']==c]) for c in sorted({r['condition'] for r in records})},
        by_descriptive_score_interval={c:metrics([r for r in records if interval(r)==c]) for c in sorted({interval(r) for r in records})})
