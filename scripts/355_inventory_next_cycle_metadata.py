"""Read saved metadata only; no image access, allocation changes or fitting."""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/next_cycle_data_plan_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes = {}

    def read(path, csv_file=False, encoding='utf-8-sig'):
        raw = (ROOT / path).read_bytes()
        hashes[path] = hashlib.sha256(raw).hexdigest()
        value = raw.decode(encoding)
        return list(csv.DictReader(io.StringIO(value))) if csv_file else json.loads(value)

    official = read('data/raw/mst-e_data/mst-e_image_details.csv', True)
    reviewed = read('data/manifests/mst_mapping_feasibility_v1/review_source_original.csv', True, 'cp1252')
    measured = read('outputs/nostril_mst_measurement_v4/summary.json')['records']
    fair = read('outputs/independent_source_inventory_v1/fairface_inventory.json')
    scin = read('outputs/independent_source_inventory_v1/scin_inventory.json')
    old = read('outputs/reviewed_source_evidence32_v1/registry.json')['rows']
    preferred = read('outputs/preferred_support_cohort_v1/plan.json')
    records = read('outputs/preferred_support_cohort_v1/records.json')
    allocation = read('outputs/correction_data_redesign_v1/selection.json')
    duplicate = read('outputs/correction_duplicate_audit_v1/candidate_dispositions.json')
    exposure_path = 'data/manifests/development_exposure_additions.jsonl'
    exposure_raw = (ROOT / exposure_path).read_bytes()
    hashes[exposure_path] = hashlib.sha256(exposure_raw).hexdigest()
    exposure = [json.loads(line) for line in exposure_raw.decode('utf-8-sig').splitlines() if line.strip()]
    used = {r['subject_id'] for r in measured}
    subjects = defaultdict(list)
    for r in official:
        subjects[r['subject_name']].append(r)
    subject_rows = []
    for subject, rows in sorted(subjects.items()):
        review_rows = [r for r in reviewed if r['image_id'].startswith('mst_e__' + subject + '/')]
        labels = sorted({int(r['MST']) for r in rows})
        assert len(labels) == 1
        subject_rows.append(dict(subject_id=subject, official_mst=labels[0],
            metadata_rows=len(rows), unique_images=len({r['image_ID'] for r in rows}),
            lighting=dict(Counter(r['lighting'] for r in rows)),
            in_completed_cycle=subject in used, historical_review_rows=len(review_rows),
            historical_review_status=dict(Counter(r['quality_review'].strip() for r in review_rows)),
            independent_new_subject=False, admission='not_admitted'))
    prior_ids = {r['source_image_id'] for r in old}
    preferred_ids = set(preferred['anchors']) | {r['image_id'] for r in preferred['selected']}
    remaining = [r for r in fair if r['additional_source_group'] and r['image_id'] not in prior_ids | preferred_ids]
    assert len(fair) == 420 and len(used) == 15 and len(subjects) == 19
    summary = dict(status='metadata_only_no_processing_or_fitting',
        official_subjects=len(subjects), completed_cycle_subjects=len(used),
        subjects_outside_cycle=[r for r in subject_rows if not r['in_completed_cycle']],
        official_subject_support=dict(Counter(r['official_mst'] for r in subject_rows)),
        cycle_subject_support=dict(Counter(r['official_mst'] for r in subject_rows if r['in_completed_cycle'])),
        fairface_frozen_train=len(fair), duplicate_dispositions=dict(Counter(r['status'] for r in duplicate)),
        frozen_roles=dict(Counter(r['role'] for r in allocation['selected'])),
        remaining_fairface_sources_outside_old32_and_preferred18=len(remaining),
        remaining_processing=dict(Counter(r['processing_status'] for r in remaining)),
        remaining_historical_estimated_severity=dict(Counter(r['experimental_severity'] for r in remaining)),
        preferred_record_status=dict(Counter(r.get('status', 'unspecified') for r in records)),
        scin_images=len(scin), scin_cases=len({r['case_id'] for r in scin}),
        scin_roles=dict(Counter(r['role'] for r in scin)),
        scin_label_status=dict(Counter(r['label_status'] for r in scin)),
        scin_local_paths_in_prior_audit=sum(bool(r['existing_local_paths']) for r in scin),
        exposure_additions_records=len(exposure), verified_additional_independent_labelled_subjects=0,
        new_reference_approvals=0, raw_images_opened=0, fits=0)
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    OUT.mkdir()
    for name, value in [('summary.json', summary), ('mst_subject_inventory.json', subject_rows),
                        ('remaining_fairface_inventory.json', remaining), ('input_hashes.json', hashes)]:
        (OUT / name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
