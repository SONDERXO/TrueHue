"""One frozen subject-held mapping evaluation; no all-row lookup or tree fit."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.evaluation.mst_validation import evaluate_mst
from src.ita_estimation.nostril_measurement import contract


def main():
    source=ROOT/'outputs/nostril_mst_measurement_v4/summary.json';out=ROOT/'outputs/nostril_mst_calibration_v4'
    if out.exists():raise FileExistsError(out)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'));digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    measured=read(source);rows=measured['records'];identity=contract(ROOT)[1]
    oldpath=ROOT/'outputs/semantic_mst_calibration_v1/summary.json';old=read(oldpath)
    assert measured['measurement_contract_sha256']==identity and len(rows)==418
    hashes={str(p):digest(p) for p in [source,oldpath,Path(__file__),ROOT/'src/evaluation/mst_validation.py',ROOT/'docs/nostril-mst-single-cycle-protocol-2026-11-01.md']}
    assert all(digest(Path(p))==h for p,h in measured['input_sha256'].items())
    subjects=sorted({r['subject_id'] for r in rows});folds=[];models=[];predictions=[]
    attempts=[dict(image_id=r['image_id'],subject_id=r['subject_id'],mst=r['source_mst_label'],lighting=r['lighting'],measured=r['status']=='success') for r in rows]
    out.mkdir();(out/'plan.json').write_text(json.dumps(dict(held_subjects=subjects,input_sha256=hashes,
        recipe='unchanged_decreasing_equal_subject_isotonic',measurement_contract_sha256=identity,
        all_row_lookup_export=False,correction_tree_fits=0),indent=2))
    for subject in subjects:
        train=[r for r in rows if r['status']=='success' and r['subject_id']!=subject]
        held=[r for r in rows if r['status']=='success' and r['subject_id']==subject]
        counts=Counter(r['subject_id'] for r in train);labels={r['subject_id']:r['source_mst_label'] for r in train}
        assert subject not in labels
        weights=[1/counts[r['subject_id']] for r in train]
        model=IsotonicRegression(increasing=False,out_of_bounds='clip',y_min=1,y_max=10)
        model.fit([r['features']['input_ita_degrees'] for r in train],[r['source_mst_label'] for r in train],sample_weight=weights)
        baseline=int(np.floor(np.median(list(labels.values()))+.5))
        for row in held:
            value=float(model.predict([row['features']['input_ita_degrees']])[0])
            replay=float(np.interp(row['features']['input_ita_degrees'],model.X_thresholds_,model.y_thresholds_))
            assert abs(value-replay)<1e-12
            predictions.append(dict(image_id=row['image_id'],prediction=int(np.floor(value+.5)),baseline=baseline,continuous_prediction=value))
        folds.append(dict(held_subject=subject,fit_subject_labels=labels))
        models.append(dict(held_subject=subject,fit_image_ids=[r['image_id'] for r in train],
            held_image_ids=[r['image_id'] for r in held],fit_weights=weights,
            x_knots=model.X_thresholds_.tolist(),y_knots=model.y_thresholds_.tolist()))
    metrics=evaluate_mst(attempts,predictions,folds)
    common={r['image_id'] for r in predictions}&{r['image_id'] for r in old['predictions']}
    commonsubjects={r['subject_id'] for r in attempts if r['image_id'] in common}
    score=lambda pp,ff:evaluate_mst([r for r in attempts if r['image_id'] in common],
        [r for r in pp if r['image_id'] in common],[r for r in ff if r['held_subject'] in commonsubjects])['overall']
    comparison=dict(common_rows=len(common),old_semantic=score(old['predictions'],old['folds']),nostril_excluded=score(predictions,folds),
        limitation='Same scoring rows; measurement-specific technical-success fit memberships may differ.')
    overall=metrics['overall']
    report=dict(status='single_development_cycle_complete_not_reliable_or_adopted',
        measurement_contract_sha256=identity,metrics=metrics,predictions=predictions,folds=folds,fold_models=models,
        shared_row_comparison=comparison,new_mapping_fits=len(models),all_row_fit=False,production_lookup_exported=False,
        correction_tree_fits=0,new_mask_approvals=0,input_sha256=hashes,
        reliability_limitations=['Exposed development subjects, not fresh final validation.',
            'Unreviewed masks and approximate nostril geometry; predicted exclusions are not ground truth.',
            'Same-category independent subject support and lighting sensitivity remain limitations.',
            'No success threshold fabricated or recipe tuned after this outcome.'])
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],overall=overall,shared_row_comparison=comparison),indent=2))


if __name__=='__main__':main()
