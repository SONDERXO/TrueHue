"""Exploratory subject-separated ITA-to-MST tests, not production calibration."""
import numpy as np
from sklearn.isotonic import IsotonicRegression


def fit_predict(train_x, train_y, train_subjects, test_x):
    """Fit only training subjects. Higher ITA implies nonincreasing MST label."""
    x=np.asarray(train_x,float);y=np.asarray(train_y,int)
    subjects=np.asarray(train_subjects);test=np.asarray(test_x,float)
    if not len(x) or not np.isfinite(x).all() or not np.isfinite(test).all():
        raise ValueError('Finite nonempty training measurements required')
    per_subject=[]
    weights=np.zeros(len(x))
    for subject in np.unique(subjects):
        mask=subjects==subject
        labels=np.unique(y[mask])
        if len(labels)!=1:
            raise ValueError('A metadata subject has inconsistent official labels')
        weights[mask]=1/mask.sum()
        per_subject.append((int(labels[0]),float(np.median(x[mask]))))
    median_label=int(np.floor(np.median([p[0] for p in per_subject])+.5))
    baseline=np.full(len(test),median_label,int)
    iso=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
    iso.fit(x,y,sample_weight=weights)
    # Predict separately: test values must never participate in fitting.
    predicted=iso.predict(test)
    rounded=np.clip(np.floor(predicted+.5),1,10).astype(int)
    labels=sorted({p[0] for p in per_subject})
    centers=np.array([np.median([p[1] for p in per_subject if p[0]==label]) for label in labels])
    nearest=np.asarray(labels)[np.abs(test[:,None]-centers).argmin(axis=1)]
    return {'training_subject_median':baseline,'monotone_ita_lookup':rounded,
            'nearest_class_median_ita':nearest},predicted


def leave_subject_out(rows):
    """Exactly one held-out subject per fold; no image-random split or tuning."""
    subjects=sorted({r['subject_id'] for r in rows})
    if len(subjects)<2:
        raise ValueError('At least two distinct subjects required')
    output=[]
    for subject in subjects:
        train=[r for r in rows if r['subject_id']!=subject]
        test=[r for r in rows if r['subject_id']==subject]
        predictions,continuous=fit_predict([r['ita_degrees'] for r in train],
            [r['source_mst_label'] for r in train],[r['subject_id'] for r in train],
            [r['ita_degrees'] for r in test])
        supported={r['source_mst_label'] for r in train}
        for method,values in predictions.items():
            for i,(record,prediction) in enumerate(zip(test,values)):
                output.append(dict(record,method=method,predicted_mst=int(prediction),
                    continuous_prediction=float(continuous[i]) if method=='monotone_ita_lookup' else '',
                    held_out_subject=subject,training_subject_count=len(subjects)-1,
                    true_label_present_in_training=record['source_mst_label'] in supported))
    return output


def paired_cohorts(comparisons, versions=('historical','regenerated_v2','complete_mouth')):
    """Use identical successful source IDs for every version's paired test.

    Failure rates remain separate from this conditional common-cohort result.
    A current mask's numerical success does not inherit historical visual QA.
    """
    common=[]
    for row in comparisons:
        if all(row.get(version+'_status')=='success' for version in versions):
            if not all(np.isfinite(float(row[version+'_ita'])) for version in versions):
                raise ValueError('Successful comparison has nonfinite ITA')
            common.append(row)
    cohorts={}
    for version in versions:
        cohorts[version]=[dict(image_id=r['image_id'],subject_id=r['subject_id'],
            source_mst_label=int(r['source_mst_label']),source_lighting=r['source_lighting'],
            ita_degrees=float(r[version+'_ita'])) for r in common]
    return cohorts
