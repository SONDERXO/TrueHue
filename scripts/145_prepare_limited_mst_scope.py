"""Prepare factual support tables for an adviser-review scope; no fit or admission."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/mst_limited_scope_proposal_v1'
    if out.exists():raise FileExistsError(out)
    coverage=ROOT/'data/manifests/mst_mapping_feasibility_v1/subject_label_coverage.csv'
    audit=ROOT/'data/manifests/mst_mapping_feasibility_v1/measurement_metadata_audit.csv'
    source=ROOT/'outputs/mst_square256_measurement_v1/summary.json'
    def read(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    attempts=json.loads(source.read_text())['records'];history=read(audit);historical={}
    for r in history:historical.setdefault(r['subject_id'],Counter())[r['historical_quality_review']]+=1
    categories=[]
    for row in read(coverage):
        label=int(row['source_mst_label']);official=row['official_subjects'].split(';')
        selected=[r for r in attempts if r['source_mst_label']==label]
        measured=[r for r in selected if r['status']=='success']
        subjects=sorted({r['subject_id'] for r in measured})
        categories.append(dict(mst=label,official_subjects=official,measured_subjects=subjects,
            attempted_images=len(selected),measured_images=len(measured),failed_images=len(selected)-len(measured),
            independent_category_comparison_structurally_supported=len(subjects)>=2,
            unrepresented_official_subjects=[dict(subject_id=s,historical_quality_counts=dict(historical.get(s,{})),
                admitted=False) for s in official if s not in subjects]))
    supported=[r['mst'] for r in categories if r['independent_category_comparison_structurally_supported']]
    assert supported==[1,2,3,6,8]
    report=dict(status='proposal_for_adviser_review_not_approved',user_direction='Prepare a limited evaluation scope for adviser review',
        categories=categories,structurally_supported_categories=supported,
        limited_support_categories=[r['mst'] for r in categories if r['mst'] not in supported],
        no_validated_mapping_available=True,ten_label_mapping_still_required=True,
        category_support_does_not_establish_mapping_accuracy=True,
        no_new_fits=True,no_new_admissions=True,no_new_images_opened=True,
        data_role='Exposed mapping development; not fresh final evaluation or correction-tree training',
        input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [coverage,audit,source,Path(__file__)]})
    out.mkdir();(out/'support.json').write_text(json.dumps(report,indent=2))
    with (out/'category_support.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['mst','measured_subjects','attempted','available','failed','independent_category_comparison_structurally_supported'])
        for r in categories:w.writerow([r['mst'],';'.join(r['measured_subjects']),r['attempted_images'],r['measured_images'],r['failed_images'],r['independent_category_comparison_structurally_supported']])
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in report['input_sha256'].items())
    print(json.dumps(dict(status=report['status'],supported_categories=supported,limited_support_categories=report['limited_support_categories'],mapping_available=False),indent=2))


if __name__=='__main__':main()
