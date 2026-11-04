"""One fixed subject-balanced monotone mapping evaluation, no correction fitting."""
import csv
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.evaluation.mst_validation import evaluate_mst


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'outputs/mst_monotone_square256_v1'
    if out.exists():raise FileExistsError(out)
    source=ROOT/'outputs/mst_square256_measurement_v1/summary.json';plan_path=ROOT/'outputs/mst_evaluation_design_v1/fold_plan.json'
    meta_path=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    tracked=[source,plan_path,meta_path,Path(__file__),ROOT/'docs/mst-monotone-square256-protocol.md',ROOT/'src/evaluation/mst_validation.py']
    hashes={str(p):digest(p) for p in tracked}
    summary=json.loads(source.read_text());plan=json.loads(plan_path.read_text());by_id={r['image_id']:r for r in summary['records']}
    assert all(digest(Path(p))==h for p,h in summary['input_sha256'].items())
    with meta_path.open(encoding='utf-8-sig',newline='') as f:meta={r['image_id']:r for r in csv.DictReader(f)}
    attempts=[dict(image_id=r['image_id'],subject_id=r['subject_id'],mst=r['source_mst_label'],lighting=meta[r['image_id']]['source_lighting'],measured=r['status']=='success') for r in summary['records']]
    labels={r['subject_id']:r['source_mst_label'] for r in summary['records']};folds=[];predictions=[];models=[]
    out.mkdir();(out/'run_status.json').write_text('{"status":"running"}')
    for fold in plan['folds']:
        training=[by_id[i] for i in fold['fit_image_ids']];test=[by_id[i] for i in fold['held_success_ids']]
        assert all(r['subject_id']!=fold['held_subject'] and r['status']=='success' for r in training)
        assert all(r['subject_id']==fold['held_subject'] for r in test)
        fitlabels={s:labels[s] for s in fold['fit_subject_ids']}
        folds.append(dict(held_subject=fold['held_subject'],fit_subject_labels=fitlabels))
        x=[r['features']['input_ita_degrees'] for r in training];y=[r['source_mst_label'] for r in training]
        weights=[fold['fit_image_weight'][r['image_id']] for r in training]
        model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
        model.fit(x,y,sample_weight=weights)
        baseline=int(np.floor(np.median(list(fitlabels.values()))+.5))
        values=model.predict([r['features']['input_ita_degrees'] for r in test])
        for row,value in zip(test,values):
            # Independent interpolation check against fitted monotone knots.
            independent=float(np.interp(row['features']['input_ita_degrees'],model.X_thresholds_,model.y_thresholds_))
            assert abs(independent-float(value))<1e-12
            predictions.append(dict(image_id=row['image_id'],prediction=int(np.clip(np.floor(value+.5),1,10)),baseline=baseline,continuous_prediction=float(value)))
        models.append(dict(held_subject=fold['held_subject'],fit_subjects=sorted(fitlabels),
            fit_image_ids=fold['fit_image_ids'],x_knots=model.X_thresholds_.tolist(),y_knots=model.y_thresholds_.tolist()))
    metrics=evaluate_mst(attempts,predictions,folds);overall=metrics['overall']
    assert overall['available_predictions']==396 and overall['processing_failures']==22
    checks=dict(overall_equal_subject_mae_improves=overall['candidate']['equal_subject_mae']<overall['paired_baseline']['equal_subject_mae'],
        supported_equal_subject_mae_improves=overall['supported_candidate']['equal_subject_mae']<overall['supported_paired_baseline']['equal_subject_mae'])
    report=dict(status='development_gate_passed_not_final_validation' if all(checks.values()) else 'held_mapping_quality_failure',
        scope_approval='user_reports_adviser_confirmed_limited_evaluation_scope',metrics=metrics,checks=checks,
        predictions=predictions,fold_models=models,folds=folds,new_mapping_fits=15,correction_tree_fits=0,
        all_row_fit_performed=False,production_lookup_exported=False,input_sha256=hashes,
        measurement_contract_sha256=summary['measurement_contract_sha256'],
        limitations='Previously exposed development cohort;180measured images lack same-category fitting-subject support. No final independent or all-ten-category validation claim.')
    assert all(digest(Path(p))==h for p,h in hashes.items())
    (out/'summary.json').write_text(json.dumps(report,indent=2));(out/'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps(dict(status=report['status'],checks=checks,overall=overall),indent=2))


if __name__=='__main__':main()
