"""One declared subject-balanced, monotone empirical lookup recipe."""
import math
import numpy as np
from sklearn.isotonic import IsotonicRegression


def fit_thresholds(rows):
    subjects={}
    for row in rows:
        subject=row['subject_id']; label=row['source_mst_label']; ita=row['ita_degrees']
        if not isinstance(subject,str) or not subject or isinstance(label,bool) or not isinstance(label,int) or not 1<=label<=10 or not math.isfinite(float(ita)):
            raise ValueError('Subject, official integer MST and finite ITA required')
        if subject in subjects and subjects[subject]['label']!=label:raise ValueError('Inconsistent subject label')
        subjects.setdefault(subject,dict(label=label,values=[]))['values'].append(float(ita))
    support={label:sum(s['label']==label for s in subjects.values()) for label in range(1,11)}
    if not all(support.values()):
        return dict(status='blocked_missing_categories',subject_support=support,thresholds=None)
    centers=[float(np.median([np.median(s['values']) for s in subjects.values() if s['label']==label])) for label in range(1,11)]
    monotone=IsotonicRegression(increasing=False).fit_transform(np.arange(1,11),centers,sample_weight=list(support.values()))
    if any(a<=b for a,b in zip(monotone,monotone[1:])):
        return dict(status='blocked_pooled_category_centers',subject_support=support,
                    raw_centers=centers,monotone_centers=monotone.tolist(),thresholds=None)
    thresholds=[float((a+b)/2) for a,b in zip(monotone,monotone[1:])][::-1]
    return dict(status='diagnostic_thresholds_fitted',subject_support=support,raw_centers=centers,
                monotone_centers=monotone.tolist(),thresholds=thresholds)
