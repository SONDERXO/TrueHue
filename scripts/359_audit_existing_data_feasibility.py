"""Audit local availability and saved eligibility; no image decoding or fits."""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/existing_data_feasibility_v2'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes = {}

    def read(path, table=False):
        raw = (ROOT / path).read_bytes()
        hashes[path] = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8-sig')
        return list(csv.DictReader(io.StringIO(text))) if table else json.loads(text)

    official = read('data/raw/mst-e_data/mst-e_image_details.csv', True)
    subjects = read('outputs/next_cycle_data_plan_v1/mst_subject_inventory.json')
    scin = read('outputs/independent_source_inventory_v1/scin_inventory.json')
    full_scin = read('outputs/mst_retention_checkpoint_v1/summary.json')
    selection = read('data/manifests/scin_candidate_selection.csv', True)
    downloads = read('data/manifests/scin_download_log.csv', True)
    reviews = read('outputs/reference_readiness_r1_import/decisions.json')
    manifest = read('outputs/reference_readiness_r1/manifest.json')
    continuity = read('outputs/continuous_correction_r2/verification.json')
    remaining = read('outputs/next_cycle_data_plan_v1/remaining_fairface_inventory.json')
    mst = []
    for subject in subjects:
        if subject['in_completed_cycle']:
            continue
        rows = {(r['subject_name'], r['image_ID']): r for r in official if r['subject_name'] == subject['subject_id']}
        available = [r for r in rows.values() if (ROOT / 'data/raw/mst-e_data' / r['subject_name'] / r['image_ID']).is_file()]
        mst.append(dict(subject, local_file_count=len(available),
            local_unique_lighting=dict(Counter(r['lighting'] for r in available)),
            local_unique_mask_metadata=dict(Counter(r['mask'] for r in available)),
            matching_measurement_admitted=False, final_test_untouched=False))
    local_scin = []
    for r in scin:
        existing = [p for p in r['existing_local_paths'] if Path(p).is_file()]
        local_scin.append(dict(r, confirmed_local_paths=existing,
            person_independence='not_verified', reference_colour_evidence='not_established',
            current_measurement_admitted=False))
    full_labels = {r['case_id']: r for r in full_scin['records']}
    roles = {r['image_id']: r['intended_use'] for r in selection}
    download_rows = []
    for r in downloads:
        label = full_labels.get(r['case_id'], {})
        download_rows.append(dict(image_id=r['image_id'], case_id=r['case_id'],
            local_file=bool(r['local_path']) and Path(r['local_path']).is_file(),
            intended_use=roles.get(r['image_id'], 'not_found'),
            label_status=label.get('status', 'missing'), india_label=label.get('india_label'),
            us_label=label.get('us_label'), india_gradable=label.get('india_gradable'),
            us_gradable=label.get('us_gradable'), historical_download_status=r['download_status']))
    local = [r for r in local_scin if r['confirmed_local_paths']]
    agreed = [r for r in local_scin if r['label_status'] == 'agree']
    assert len(mst) == 4 and len(local_scin) == 368 and len(reviews) == 16
    # Conservative planning flags supplement, never rewrite, actual reviewer fields.
    concerns = {
        '39083': 'measurement_facial_hair_contamination', '74882': 'measurement_glasses_contamination',
        '29321': 'source_rejected_shadow_and_mouth', '70911': 'dark_reference_note',
        '37251': 'blurry_reference_note', '71429': 'source_rejected_brightness',
        '37071': 'bright_reference_note', '77101': 'outer_forehead_gap',
        '35986': 'structured_measurement_rejection_conflicts_with_note',
    }
    reference_rows = [dict(r, planning_hold=concerns.get(Path(r['image_id']).stem),
        no_fit_admission=True, correction_repair_does_not_override_source_or_measurement=True) for r in reviews]
    summary = dict(status='not_ready_for_retained_method_training',
        additional_mst_subjects=4, additional_mst_unique_files=sum(r['unique_images'] for r in mst),
        additional_mst_local_files=sum(r['local_file_count'] for r in mst),
        additional_mst_official_categories=[r['official_mst'] for r in mst],
        full_mst_singleton_categories=[k for k, v in Counter(r['official_mst'] for r in subjects).items() if v == 1],
        scin_head_neck_records=len(local_scin), scin_confirmed_local_records=len(local),
        scin_local_roles=dict(Counter(r['role'] for r in local)),
        scin_local_label_status=dict(Counter(r['label_status'] for r in local)),
        scin_local_label_pairs=dict(Counter(str((r['india_label'], r['us_label'])) for r in local)),
        scin_all_agreed_category_counts=dict(Counter(r['india_label'] for r in agreed)),
        scin_download_records=len(download_rows),
        scin_download_confirmed_local_roles=dict(Counter(r['intended_use'] for r in download_rows if r['local_file'])),
        scin_download_local_label_status=dict(Counter(r['label_status'] for r in download_rows if r['local_file'])),
        scin_download_local_agreed_categories=dict(Counter(r['india_label'] for r in download_rows if r['local_file'] and r['label_status']=='agree')),
        scin_download_local_unique_cases=len({r['case_id'] for r in download_rows if r['local_file']}),
        scin_full_metadata_label_status=full_scin['annotator_status_counts'],
        remaining_fairface_sources=len(remaining),
        reviewed_sources=16, retained_technical_holds=manifest['holds'],
        structured_photographic_candidates=sum(r['photographic_candidate'] for r in reviews),
        independently_verified_lighting_references=0,
        current_reliable_mst_mapping=False, continuity=continuity,
        blockers=['No reliable matching MST mapping.',
            'Four outside-cycle MST-E subjects are exposed and lack matching current-mask admission; full MST-E still singleton7/10.',
            'SCIN annotator disagreement, subject independence, duplicate clearance and role/reference admission unresolved.',
            'Reference-quality and measurement-contamination concerns remain; photographs are not intrinsic-colour truth.'],
        scope_caveat='Singleton categories block supported ten-category validation, not all limited synthetic development.',
        raw_images_decoded=0, downloads=0, fits=0, reserved_pixels_accessed=0,
        decision='Stop this audit; do not refit existing subjects or silently remove difficult cases.')
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    OUT.mkdir()
    for name, value in [('mst_additional_subjects.json', mst), ('scin_readiness.json', local_scin),
                        ('scin_historical_downloads.json', download_rows), ('reference_dispositions.json', reference_rows),
                        ('summary.json', summary), ('input_sha256.json', hashes)]:
        (OUT / name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'continuity'}, indent=2))


if __name__ == '__main__':
    main()
