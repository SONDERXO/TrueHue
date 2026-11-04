"""Fixed subject-held-out calibration diagnostic; never export production lookup."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.ita_estimation.threshold_calibration import fit_thresholds


def main():
    out=ROOT/'outputs/mst_square256_calibration_v1'
    if out.exists():raise FileExistsError(out)
    source=ROOT/'outputs/mst_square256_measurement_v1/summary.json'
    summary=json.loads(source.read_text());assert summary['status']=='complete_development_measurement_no_lookup'
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in summary['input_sha256'].items())
    rows=[dict(subject_id=r['subject_id'],source_mst_label=r['source_mst_label'],ita_degrees=r['features']['input_ita_degrees'],image_id=r['image_id']) for r in summary['records'] if r['status']=='success']
    subjects=sorted({r['subject_id'] for r in rows});full=fit_thresholds(rows);folds=[];predictions=[]
    for subject in subjects:
        fitting=[r for r in rows if r['subject_id']!=subject];testing=[r for r in rows if r['subject_id']==subject]
        assert not {r['subject_id'] for r in fitting}&{subject}
        fitted=fit_thresholds(fitting)
        by_subject={r['subject_id']:r['source_mst_label'] for r in fitting}
        baseline=int(np.floor(np.median(list(by_subject.values()))+.5))
        folds.append(dict(held_subject=subject,fit_subjects=sorted(by_subject),held_images=len(testing),calibration=fitted))
        for row in testing:
            guess=None if fitted['thresholds'] is None else 10-int(np.searchsorted(fitted['thresholds'],row['ita_degrees'],side='right'))
            predictions.append(dict(**row,prediction=guess,baseline=baseline,fold_status=fitted['status']))
    available=[r for r in predictions if r['prediction'] is not None]
    def metrics(selected,key):
        if not selected:return None
        errors=[abs(r[key]-r['source_mst_label']) for r in selected]
        return dict(images=len(selected),subjects=len({r['subject_id'] for r in selected}),
            exact_accuracy=float(np.mean(np.array(errors)==0)),within_one=float(np.mean(np.array(errors)<=1)),
            ordinal_mae=float(np.mean(errors)),equal_subject_mae=float(np.mean([np.mean([abs(r[key]-r['source_mst_label']) for r in selected if r['subject_id']==s]) for s in {r['subject_id'] for r in selected}])))
    candidate=metrics(available,'prediction');baseline=metrics(available,'baseline')
    checks=dict(at_least_two_subjects_each_category=all(v>=2 for v in full['subject_support'].values()),
        full_thresholds_available=full['thresholds'] is not None,
        all_held_subject_folds_supported=len(available)==len(rows) and bool(rows),
        paired_mae_improves=bool(candidate and candidate['equal_subject_mae']<baseline['equal_subject_mae']))
    result=dict(status='diagnostic_complete_no_production_lookup',measurement_contract_sha256=summary['measurement_contract_sha256'],
        attempted_images=summary['attempts'],measured_images=len(rows),measured_subjects=len(subjects),
        full_calibration_diagnostic=full,folds=folds,predictions=predictions,
        available_heldout_predictions=len(available),unavailable_heldout_predictions=len(rows)-len(available),
        candidate_available_fold_metrics=candidate,paired_baseline_metrics=baseline,
        all_measured_baseline_metrics=metrics(predictions,'baseline'),checks=checks,
        production_lookup_exported=False,correction_tree_fits=0,
        input_sha256={str(source):hashlib.sha256(source.read_bytes()).hexdigest(),str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        limitation='Exposed development cohort; unsupported category folds are retained, never imputed. New masks lack fresh human approval. Not final evaluation or a deployed lookup.')
    out.mkdir();(out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ['folds','predictions','input_sha256']},indent=2))


if __name__=='__main__':main()
