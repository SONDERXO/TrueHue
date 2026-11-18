"""Isolated decimal-score, subject-held experiment. No MST category export."""
from collections import Counter,defaultdict
from decimal import Decimal,InvalidOperation
import math
import re
import numpy as np

FEATURES=('input_ita_degrees','input_mean_l_star','input_mean_a_star','input_mean_b_star')
METHODS=('ita_lab_ridge','ita_only_ridge','subject_median')
VERSION='contextual_mst_decimal_loso_ridge1_v1'

def validate(rows):
    if not rows:raise ValueError('Attempt rows required')
    ids=set();labels={};contracts=set()
    for r in rows:
        for key in ['case_id','subject_id','condition']:
            if not isinstance(r.get(key),str) or not r[key]:raise ValueError('Nonempty case, subject and condition required')
        if r['case_id'] in ids:raise ValueError('Duplicate case ID')
        ids.add(r['case_id'])
        try:
            if not isinstance(r['source_mst_exact_decimal'],str):raise ValueError('Exact decimal string required')
            label=Decimal(r['source_mst_exact_decimal'])
        except (KeyError,InvalidOperation) as error:raise ValueError('Finite decimal score required') from error
        if not label.is_finite() or not Decimal(1)<=label<=Decimal(10):raise ValueError('Score outside1–10')
        subject=r['subject_id']
        if subject in labels and labels[subject]!=label:raise ValueError('Inconsistent subject score')
        labels[subject]=label
        contract=r.get('measurement_contract_sha256','')
        if not isinstance(contract,str) or not re.fullmatch('[0-9a-f]{64}',contract):raise ValueError('Measurement contract SHA required')
        contracts.add(contract)
        if r.get('calibration_admitted') is not True:raise ValueError('Every attempted source must have explicit calibration admission')
        if r.get('status') not in ['available','unavailable']:raise ValueError('Explicit outcome status required')
        features=r.get('features')
        if r['status']=='available':
            if not isinstance(features,dict) or set(features)!=set(FEATURES):raise ValueError('Exactly original ITA/Lab features required')
            if any(isinstance(v,(bool,str)) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in features.values()):raise ValueError('Finite numeric features required')
            if not -90<=features[FEATURES[0]]<=90 or not 0<=features[FEATURES[1]]<=100:raise ValueError('ITA/L ranges invalid')
            if any(not -128<=features[f]<=127 for f in FEATURES[2:]):raise ValueError('Encoded-Lab chroma range invalid')
        elif features is not None or not isinstance(r.get('reason'),str) or not r['reason']:
            raise ValueError('Unavailable measurement needs reason and no features')
    if len(contracts)!=1:raise ValueError('Mixed measurement contracts cannot be pooled')
    if len(labels)<2:raise ValueError('At least two distinct subject IDs required for held-subject evaluation')

def _ridge(training,names):
    counts=Counter(r['subject_id'] for r in training)
    weights=np.array([1/counts[r['subject_id']] for r in training],float)
    x=np.array([[r['features'][f] for f in names] for r in training],float)
    y=np.array([float(Decimal(r['source_mst_exact_decimal'])) for r in training])
    mean=np.average(x,axis=0,weights=weights)
    # Exact constant columns can acquire tiny roundoff in weighted averaging.
    constant=np.ptp(x,axis=0)==0
    mean=np.where(constant,x[0],mean)
    scale=np.sqrt(np.average((x-mean)**2,axis=0,weights=weights));scale=np.where(scale==0,1.,scale)
    z=(x-mean)/scale;intercept=float(np.average(y,weights=weights))
    coefficient=np.linalg.solve(z.T@(weights[:,None]*z)+np.eye(len(names)),z.T@(weights*(y-intercept)))
    return dict(features=list(names),mean=mean.tolist(),scale=scale.tolist(),coefficient=coefficient.tolist(),intercept=intercept,
        alpha=1.0,subject_total_weight=1.0,training_subject_row_counts=dict(counts))

def predict(model,features):
    value=float(np.dot((np.array([features[f] for f in model['features']])-model['mean'])/model['scale'],model['coefficient'])+model['intercept'])
    return dict(raw=value,score=float(np.clip(value,1,10)))

def _metrics(rows,method):
    subjects=defaultdict(list);errors=[];predictions=defaultdict(list)
    for r in rows:
        p=r['predictions'][method]
        if p is None:continue
        error=abs(p['score']-float(Decimal(r['source_mst_exact_decimal'])))
        errors.append(error);subjects[r['subject_id']].append(error);predictions[r['subject_id']].append(p['score'])
    return dict(attempts=len(rows),available_predictions=len(errors),unavailable_predictions=len(rows)-len(errors),
        attempted_subjects=len({r['subject_id'] for r in rows}),predicted_subjects=len(subjects),
        image_MAE=float(np.mean(errors)) if errors else None,
        equal_subject_MAE=float(np.mean([np.mean(v) for v in subjects.values()])) if subjects else None,
        within_subject_prediction_ranges={k:max(v)-min(v) for k,v in predictions.items() if len(v)>1})

def evaluate_subject_held(rows):
    """Real rows require prior admission; calling this fits two regressions/fold."""
    validate(rows);folds=[];results=[]
    for held in sorted({r['subject_id'] for r in rows}):
        training=[r for r in rows if r['subject_id']!=held and r['status']=='available']
        testing=[r for r in rows if r['subject_id']==held]
        train_subjects=sorted({r['subject_id'] for r in training})
        models={};baseline=None
        if training:
            models={'ita_lab_ridge':_ridge(training,FEATURES),'ita_only_ridge':_ridge(training,FEATURES[:1])}
            scores={r['subject_id']:float(Decimal(r['source_mst_exact_decimal'])) for r in training}
            baseline=float(np.median(list(scores.values())))
        folds.append(dict(held_subject=held,training_subjects=train_subjects,training_cases=[r['case_id'] for r in training],
            evaluation_cases=[r['case_id'] for r in testing],models=models,median_baseline=baseline,
            status='available' if training else 'unavailable_no_training_measurements'))
        for r in testing:
            estimates={name:None for name in METHODS}
            if models and r['status']=='available':
                estimates.update({name:predict(model,r['features']) for name,model in models.items()})
                estimates['subject_median']=dict(raw=baseline,score=baseline)
            results.append(dict(case_id=r['case_id'],subject_id=held,condition=r['condition'],
                source_mst_exact_decimal=r['source_mst_exact_decimal'],status=r['status'],
                unavailable_reason=r.get('reason') if r['status']=='unavailable' else ('no_training_measurements' if not models else None),predictions=estimates))
    conditions=sorted({r['condition'] for r in results})
    # Descriptive intervals only, never integer MST categories.
    def interval(r):
        value=Decimal(r['source_mst_exact_decimal'])
        return '[1,3)' if value<3 else '[3,5)' if value<5 else '[5,7)' if value<7 else '[7,9)' if value<9 else '[9,10]'
    intervals=sorted({interval(r) for r in results})
    return dict(version=VERSION,folds=folds,records=results,metrics={m:_metrics(results,m) for m in METHODS},
        by_condition={c:{m:_metrics([r for r in results if r['condition']==c],m) for m in METHODS} for c in conditions},
        by_descriptive_score_interval={c:{m:_metrics([r for r in results if interval(r)==c],m) for m in METHODS} for c in intervals},
        mapping_ridge_fits=sum(2 for f in folds if f['models']),correction_tree_fits=0,
        integer_category_output=False,production_adopted=False,scientific_validation=False)
