"""Freeze exact subject folds, support and lighting denominators without fitting."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/mst_evaluation_design_v1'
    if out.exists():raise FileExistsError(out)
    source=ROOT/'outputs/mst_square256_measurement_v1/summary.json'
    metadata=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    protocol=ROOT/'docs/mst-calibration-evaluation-design.md'
    summary=json.loads(source.read_text())
    with metadata.open(encoding='utf-8-sig',newline='') as f:original={r['image_id']:r for r in csv.DictReader(f)}
    rows=summary['records'];assert len(rows)==len(original)==418
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in summary['input_sha256'].items())
    folds=[]
    for index,subject in enumerate(sorted({r['subject_id'] for r in rows}),1):
        training=[r for r in rows if r['subject_id']!=subject and r['status']=='success']
        held=[r for r in rows if r['subject_id']==subject]
        subjects={r['subject_id']:r['source_mst_label'] for r in training}
        support={k:sum(v==k for v in subjects.values()) for k in range(1,11)}
        label_set={r['source_mst_label'] for r in held};assert len(label_set)==1
        label=next(iter(label_set))
        fit_ids=sorted(r['image_id'] for r in training);held_ids=sorted(r['image_id'] for r in held)
        assert not set(fit_ids)&set(held_ids)
        assert subject not in subjects
        folds.append(dict(fold=index,held_subject=subject,held_official_mst=label,
            fit_subject_ids=sorted(subjects),fit_image_ids=fit_ids,held_attempt_ids=held_ids,
            held_success_ids=sorted(r['image_id'] for r in held if r['status']=='success'),
            held_failure_ids=sorted(r['image_id'] for r in held if r['status']!='success'),
            fitting_category_subject_support=support,held_category_supported=support[label]>0,
            held_lighting_attempts=dict(Counter(original[r['image_id']]['source_lighting'] for r in held)),
            held_lighting_successes=dict(Counter(original[r['image_id']]['source_lighting'] for r in held if r['status']=='success')),
            fit_image_weight={r['image_id']:1/sum(x['subject_id']==r['subject_id'] for x in training) for r in training}))
    held=[p for f in folds for p in f['held_attempt_ids']]
    assert len(held)==len(set(held))==418
    assert sum(len(f['held_success_ids']) for f in folds)==396
    assert sum(len(f['held_failure_ids']) for f in folds)==22
    for fold in folds:
        for subject in fold['fit_subject_ids']:
            total=sum(w for p,w in fold['fit_image_weight'].items() if original[p]['subject_id']==subject)
            assert abs(total-1)<1e-12
    report=dict(status='frozen_subject_evaluation_design_no_fit',folds=folds,attempts=418,measured=396,
        failures=22,subjects=15,folds_missing_held_category=sum(not f['held_category_supported'] for f in folds),
        measurement_contract_sha256=summary['measurement_contract_sha256'],
        data_role='previously_exposed_MST-E_mapping_development_only_not_correction_training_or_untouched_test',
        new_fits=0,lookup_exported=False,final_ten_category_validation_feasible=False,
        input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,metadata,protocol,Path(__file__)]})
    out.mkdir();(out/'fold_plan.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['folds','input_sha256']},indent=2))


if __name__=='__main__':main()
