"""Subject-held MST reporting with explicit unsupported/unavailable denominators."""
import math
from collections import defaultdict


def _label(value):
    if isinstance(value,bool) or not isinstance(value,int) or not 1<=value<=10:
        raise ValueError('Official/predicted MST must be integer1–10')
    return value


def evaluate_mst(attempts, predictions, folds):
    """Missing measured predictions must be explicit None, never silently dropped.

    Attempts require image_id/subject_id/mst/lighting/measured. Predictions
    require image_id/prediction/baseline for every measured attempt. Folds bind
    each held subject to fitting subjects and their official labels. No fitting.
    """
    by_id={};subjects={}
    for row in attempts:
        key=row['image_id'];subject=row['subject_id'];mst=_label(row['mst'])
        if not isinstance(key,str) or not key or key in by_id or not isinstance(subject,str) or not subject:
            raise ValueError('Unique image IDs and nonempty subject IDs required')
        if type(row['measured']) is not bool or not isinstance(row['lighting'],str):
            raise ValueError('Explicit measurement status and lighting required')
        if subject in subjects and subjects[subject]!=mst:raise ValueError('Inconsistent official subject label')
        subjects[subject]=mst;by_id[key]=dict(row)
    if not attempts:raise ValueError('Nonempty attempts required')
    plans={}
    for fold in folds:
        subject=fold['held_subject'];fitting=fold['fit_subject_labels']
        if subject in plans or subject not in subjects or not isinstance(fitting,dict) or not fitting:
            raise ValueError('Unique held-subject plans with fitting support required')
        if subject in fitting:raise ValueError('Held subject leaks into calibration')
        for name,label in fitting.items():
            if not isinstance(name,str) or not name:raise ValueError('Nonempty fitting subject ID required')
            _label(label)
            if name in subjects and subjects[name]!=label:raise ValueError('Fitting subject label mismatch')
        plans[subject]=dict(fitting)
    if set(plans)!=set(subjects):raise ValueError('Exact held-subject fold coverage required')
    supplied={}
    for prediction in predictions:
        key=prediction['image_id']
        if key in supplied or key not in by_id or not by_id[key]['measured']:
            raise ValueError('Unique measured-attempt predictions only')
        value=prediction['prediction']
        if value is not None:_label(value)
        baseline=_label(prediction['baseline'])
        fitting=sorted(plans[by_id[key]['subject_id']].values());n=len(fitting)
        median=fitting[n//2] if n%2 else (fitting[n//2-1]+fitting[n//2])/2
        if baseline!=math.floor(median+.5):raise ValueError('Baseline must use fitting subjects only')
        supplied[key]=dict(prediction)
    if set(supplied)!={r['image_id'] for r in attempts if r['measured']}:
        raise ValueError('Every measured attempt needs explicit prediction or None')
    records=[]
    for row in attempts:
        p=supplied.get(row['image_id']);support=row['mst'] in plans[row['subject_id']].values()
        records.append(dict(**row,prediction=None if p is None else p['prediction'],
                            baseline=None if p is None else p['baseline'],held_category_supported=support))
    def metrics(rows,key):
        if not rows:return None
        errors=[abs(r[key]-r['mst']) for r in rows];groups=defaultdict(list)
        for r,error in zip(rows,errors):groups[r['subject_id']].append(error)
        return dict(images=len(rows),subjects=len(groups),exact_accuracy=sum(e==0 for e in errors)/len(errors),
            within_one_accuracy=sum(e<=1 for e in errors)/len(errors),ordinal_mae=sum(errors)/len(errors),
            equal_subject_mae=sum(sum(v)/len(v) for v in groups.values())/len(groups))
    def group(rows):
        measured=[r for r in rows if r['measured']];available=[r for r in measured if r['prediction'] is not None]
        supported=[r for r in available if r['held_category_supported']]
        return dict(attempts=len(rows),subjects=len({r['subject_id'] for r in rows}),measured=len(measured),
            processing_failures=len(rows)-len(measured),available_predictions=len(available),
            unavailable_predictions=len(measured)-len(available),
            measured_without_held_category_support=sum(not r['held_category_supported'] for r in measured),
            candidate=metrics(available,'prediction'),paired_baseline=metrics(available,'baseline'),
            supported_candidate=metrics(supported,'prediction'),supported_paired_baseline=metrics(supported,'baseline'),
            all_measured_baseline=metrics(measured,'baseline'))
    return dict(overall=group(records),by_mst={str(i):group([r for r in records if r['mst']==i]) for i in range(1,11)},
                by_lighting={name:group([r for r in records if r['lighting']==name]) for name in sorted({r['lighting'] for r in records})},
                by_subject={name:group([r for r in records if r['subject_id']==name]) for name in sorted(subjects)},
                limitation='Descriptive subject-held development metrics; support and accuracy do not establish fresh final validation.')
