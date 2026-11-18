"""Check source-label/exposure eligibility without opening photos or locked allocations."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/wb314_mste_evaluation_metadata_v1'
CATALOG = ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv'
MAPPING = ROOT / 'outputs/mst_square256_measurement_v1/summary.json'
CLOSED = ROOT / 'outputs/additional_mst_eligibility_v1/summary.json'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, value):
    with p.open('x', encoding='utf-8') as f: json.dump(value, f, indent=2, allow_nan=False)


def main():
    if OUT.exists(): raise FileExistsError('Preserve the original assessment')
    # These are a public source catalogue and two exposed-study results, not
    # locked allocation manifests. No dependency paths inside them are traversed.
    paths = [CATALOG, MAPPING, CLOSED, ROOT / 'docs/mst-calibration-evaluation-design.md',
             ROOT / 'docs/additional-mst-eligibility-results-2026-11-01.md',
             ROOT / 'docs/wb314-mst-evaluation-requirement-2026-11-18.md', Path(__file__),
             ROOT / 'outputs/wb314_final_training_v1/model.json']
    bindings = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    with CATALOG.open(encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
    grouped = defaultdict(list)
    for r in rows:
        label = int(r['MST'])
        if not 1 <= label <= 10: raise ValueError('Invalid publisher category')
        grouped[r['subject_name'], r['image_ID']].append(r)
    subjects = defaultdict(set)
    for (subject, _), own in grouped.items():
        labels = {int(r['MST']) for r in own}
        if len(labels) != 1: raise ValueError('Conflicting publisher labels')
        subjects[subject].update(labels)
    assert all(len(v) == 1 for v in subjects.values())
    mapping_rows = read(MAPPING)['records']; closed_rows = read(CLOSED)['records']
    exposed = {r['subject_id'] for r in mapping_rows}
    closed_subjects = {r['subject_id'] for r in closed_rows}
    assert len(mapping_rows) == 418 and len(closed_rows) == 25
    assert not exposed & closed_subjects
    assert set(subjects) == exposed | closed_subjects and len(subjects) == 19
    for r in mapping_rows:
        assert {int(r['source_mst_label'])} == subjects[r['subject_id']]
    for r in closed_rows:
        assert {int(r['official_mst'])} == subjects[r['subject_id']]
    remaining = {key: own for key, own in grouped.items() if key[0] not in closed_subjects}
    old_image_ids = {r['image_id'] for r in mapping_rows}
    assert len(old_image_ids) == 418
    for key in remaining:
        assert 'mst_e__' + key[0] + '/' + key[1] in old_image_ids or key[0] in exposed
    unseen_images = [key for key in remaining if 'mst_e__' + key[0] + '/' + key[1] not in old_image_ids]
    universe_category_subjects = Counter(next(iter(v)) for v in subjects.values())
    remaining_category_subjects = Counter(next(iter(subjects[s])) for s in exposed)
    # Second aggregation from raw rows independently checks the key/label joins.
    raw_subjects = {r['subject_name'] for r in rows}
    assert len(raw_subjects) == 19 and raw_subjects - exposed - closed_subjects == set()
    for label in range(1, 11):
        assert len({r['subject_name'] for r in rows if int(r['MST']) == label}) == universe_category_subjects[label]
    status = dict(
        authorization='Okay lets d that',
        scope='Separate MST-E evaluation-cohort eligibility assessment; no fitting, Form edits or locked access',
        decision='SEPARATE_UNRESERVED_INDEPENDENT_COHORT_NOT_ESTABLISHED',
        official_label_coverage=list(range(1, 11)), catalog_rows=len(rows),
        unique_subject_image_keys=len(grouped), duplicate_catalog_rows=len(rows) - len(grouped),
        publisher_subjects=len(subjects), prior_mapping_development_subjects=len(exposed),
        closed_screen_subjects=len(closed_subjects), closed_screen_attempts=len(closed_rows),
        closed_subject_catalog_keys=len(grouped) - len(remaining),
        catalog_keys_outside_closed_subjects=len(remaining),
        previously_mapping_measured_keys=418,
        other_catalog_keys_for_same_exposed_subjects=len(unseen_images),
        previously_unused_subjects=0,
        all_category_subject_counts={str(k): universe_category_subjects[k] for k in range(1, 11)},
        outside_closed_category_subject_counts={str(k): remaining_category_subjects[k] for k in range(1, 11)},
        positive_new_unreserved_evaluation_admissions=0,
        allocation_clearance='No locked manifest opened; no new independent evaluation role positively established',
        interpretation=[
            'Official labels exist; this is not a missing-label or universally unusable-dataset result.',
            'Outside the four closed-screen subjects, all15remaining subjects are already exposed mapping-development subjects.',
            'Unmeasured photographs of those same people do not create new independent subjects.',
            'Prior exposure alone does not forbid every disclosed development analysis; none is newly selected or presented as final evaluation here.',
            'The Form has20photo slots, not proof of20independent people; repeated photos must retain subject grouping.',
            'Unknown role clearance is not silently treated as unreserved or cured by opening a locked manifest.',
            'No image quality, compatible current support or photographic-reference eligibility is inferred from label metadata.'
        ],
        model_sha256=bindings['outputs/wb314_final_training_v1/model.json'],
        fits=0, source_image_decodes=0, image_path_stats=0, features=0, predictions=0,
        correction_renders=0, image_downloads=0, model_downloads=0,
        locked_content_or_manifest_reads=0, Form_edits=0, expert_responses=0)
    assert status['model_sha256'] == '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'
    for p, digest in bindings.items(): assert sha(ROOT / p) == digest
    OUT.mkdir()
    write(OUT / 'bindings.json', bindings)
    write(OUT / 'summary.json', status)
    write(OUT / 'subject_role_reconciliation_PRIVATE.json', [dict(
        subject_id=s, official_MST=next(iter(subjects[s])),
        known_history='closed_additional_eligibility_subject' if s in closed_subjects else 'exposed_mapping_development',
        newly_admitted=False) for s in sorted(subjects)])
    write(OUT / 'verification.json', dict(passed=True, catalog_subjects_reconciled=19,
          historical_rows_label_checked=443, independent_category_counts=10,
          all_input_bindings_unchanged=True, fits=0, image_reads=0, locked_reads=0,
          artifacts={p.name: sha(p) for p in OUT.iterdir() if p.is_file()}))
    print(json.dumps(status, indent=2))


if __name__ == '__main__': main()
