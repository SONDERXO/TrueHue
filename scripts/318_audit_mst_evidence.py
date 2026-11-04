"""Audit saved MST evidence and replay saved-knot predictions; no image access/fits."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.evaluation.mst_validation import evaluate_mst
from src.ita_estimation.square_measurement import contract


def main():
    out=ROOT/'outputs/mst_evidence_audit_20261030_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[p.relative_to(ROOT).as_posix()]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/mst_monotone_square256_v1'
    report=read(folder/'summary.json');lookup=read(folder/'development_lookup.json');artifact=read(folder/'artifact_verification.json')
    strict=read(ROOT/'outputs/mst_square256_calibration_v1/summary.json')
    measured=read(ROOT/'outputs/mst_square256_measurement_v1/summary.json')
    assert digest(folder/'summary.json')==lookup['evaluation_summary_sha256']
    assert digest(folder/'development_lookup.json')==artifact['lookup_sha256']
    _,identity=contract(ROOT);assert identity==report['measurement_contract_sha256']==lookup['measurement_contract_sha256']
    dependency_checks=[]
    for path,expected in report['input_sha256'].items():
        p=Path(path);actual=digest(p) if p.is_file() else None
        dependency_checks.append(dict(path=str(p),matches=actual==expected,expected_sha256=expected,actual_sha256=actual))
    assert all(r['matches'] for r in dependency_checks)
    metadata=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    hashes[metadata.relative_to(ROOT).as_posix()]=digest(metadata)
    with metadata.open(encoding='utf-8-sig',newline='') as stream:meta={r['image_id']:r for r in csv.DictReader(stream)}
    attempts=[dict(image_id=r['image_id'],subject_id=r['subject_id'],mst=r['source_mst_label'],lighting=meta[r['image_id']]['source_lighting'],measured=r['status']=='success') for r in measured['records']]
    assert evaluate_mst(attempts,report['predictions'],report['folds'])==report['metrics']
    predictions={r['image_id']:r for r in report['predictions']};by_id={r['image_id']:r for r in measured['records']}
    checked=0
    for model in report['fold_models']:
        assert model['held_subject'] not in model['fit_subjects']
        assert all(by_id[p]['subject_id']!=model['held_subject'] for p in model['fit_image_ids'])
        for p,prediction in predictions.items():
            row=by_id[p]
            if row['subject_id']!=model['held_subject']:continue
            value=float(np.interp(row['features']['input_ita_degrees'],model['x_knots'],model['y_knots']))
            assert abs(value-prediction['continuous_prediction'])<1e-12
            assert int(np.clip(np.floor(value+.5),1,10))==prediction['prediction'];checked+=1
    assert checked==396
    subjects=defaultdict(set)
    for r in attempts:
        if r['measured']:subjects[r['mst']].add(r['subject_id'])
    result=dict(status='saved_evidence_verified_not_final_validation',
        scope_approval=report['scope_approval'],measurement_contract_sha256=identity,
        lookup_sha256=artifact['lookup_sha256'],strict_recipe_available_predictions=strict['available_heldout_predictions'],
        monotone_overall=report['metrics']['overall'],actual_lookup_output_range=artifact['fitted_label_range'],
        measured_subjects_by_category={str(label):len(subjects[label]) for label in range(1,11)},
        categories_without_two_measured_subjects=[label for label in range(1,11) if len(subjects[label])<2],
        saved_prediction_replays=checked,saved_dependency_checks=dependency_checks,
        missing_requirements=['Independent labeled subject validation with disclosed exposure and supported category scope.',
            'Adviser-agreed success criteria; development MAE improvement is not final scientific validation.',
            'Reference-region and lighting validity under the retained measurement contract.',
            'Separate documentation of experimental label range1–9 and unsupported categories; no fabricated MST10 endpoint.',
            'Any future mask change needs a matching measurement and calibration protocol.'],
        new_mapping_fits=0,correction_tree_fits=0,raw_image_decodes=0,reserved_pixel_access=0,lookup_changed=False,
        stale_document_notice='mst-limited-evaluation-implementation.md describes the earlier zero-prediction stage, not the later monotone lookup.',
        input_sha256=hashes)
    out.mkdir();(out/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','actual_lookup_output_range','measured_subjects_by_category','categories_without_two_measured_subjects','saved_prediction_replays']},indent=2))


if __name__=='__main__':main()
