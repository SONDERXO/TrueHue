"""Metadata-only inventory; no image reads, admission, generation or training."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_preparation.redesign_access import training_candidate

OUT = ROOT / 'outputs/independent_source_inventory_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes = {}

    def load(relative):
        path = ROOT / relative
        raw = path.read_bytes()
        hashes[relative] = hashlib.sha256(raw).hexdigest()
        return raw.decode('utf-8-sig')

    def read(relative):
        return json.loads(load(relative))

    def lines(relative):
        return [json.loads(s) for s in load(relative).splitlines() if s.strip()]

    frozen = 'outputs/correction_data_redesign_v1/'
    audit = 'outputs/correction_duplicate_audit_v1/'
    manifest = read(frozen + 'selection.json')
    policy = read(frozen + 'access_policy.json')
    dispositions = {r['image_id']: r for r in read(audit + 'candidate_dispositions.json')}
    assert read(audit + 'verification.json')['status'] == 'pass'
    queue = read(audit + 'verified_training_queue.json')
    queue_ids = {i for b in queue['batches'] for i in b['image_ids']}
    attempts = {r['image_id']: r for r in lines('outputs/correction_training_preparation_v1/attempts.jsonl')}
    core = {r['source_image_id'] for r in read('outputs/reviewed_primary_comparison_v1/plan.json')['rows']}
    assert len(core) == 26
    # Preserve exact scoped annotations as evidence, never collapse to global approval.
    reviews = {}
    review_paths = sorted(set(
        list((ROOT / 'outputs').glob('*review*import*/*reviews*.json'))
        + list((ROOT / 'outputs').glob('*review*import*/*decisions*.json'))))
    for path in review_paths:
        relative = path.relative_to(ROOT).as_posix()
        value = read(relative)
        if isinstance(value, list):
            for r in value:
                if isinstance(r, dict) and r.get('image_id'):
                    reviews.setdefault(r['image_id'], []).append(dict(evidence=relative, annotation=r))
    exposure = {}
    ledgers = sorted(set(list((ROOT / 'outputs').glob('*/access_ledger.jsonl'))
                         + [ROOT / 'data/manifests/development_exposure_additions.jsonl']))
    for path in ledgers:
        relative = path.relative_to(ROOT).as_posix()
        text = load(relative)
        for image_id in set(re.findall(r'fairface__train/\d+\.jpg', text)):
            exposure.setdefault(image_id, []).append(relative)
    rows = []
    for selected in manifest['selected']:
        if selected['role'] != 'train':
            continue
        image_id = selected['image_id']
        training_candidate(image_id, manifest, policy)
        d = dispositions[image_id]
        a = attempts.get(image_id, {})
        rows.append(dict(image_id=image_id, role='train', batch=selected['training_batch'],
            duplicate_group=d['duplicate_group'], duplicate_status=d['status'],
            person_independence='not_verified', in_current_26=image_id in core,
            additional_source_group=d['status']=='screen_clear_unreviewed' and image_id not in core,
            processing_status=a.get('status', 'not_prepared'),
            reference_status=a.get('reference_measurement', {}).get('status', 'unavailable'),
            experimental_severity=a.get('assigned_severity', 'unavailable'),
            experimental_reference_mst=a.get('reference_mst_estimate'),
            clipping_fraction=a.get('clipping_fraction'),
            exposure_evidence=exposure.get(image_id, []),
            scoped_review_evidence=reviews.get(image_id, []),
            reference_quality='not_established_by_mask_acceptance', training_admitted=False))
    assert len(rows) == 420 and len(queue_ids) == len(attempts) == 418
    assert queue_ids == set(attempts)
    assert queue_ids == {r['image_id'] for r in rows if r['duplicate_status']=='screen_clear_unreviewed'}
    # Bounded planning list: one source per duplicate group, not a review request.
    # No tone, clipping or model-performance ranking. Technical reference success
    # only makes existing saved material available; it is not a quality approval.
    eligible = [r for r in rows if r['additional_source_group'] and
                r['reference_status']=='success' and not r['scoped_review_evidence']]
    eligible.sort(key=lambda r: hashlib.sha256(
        ('truehue_inventory24_v1/' + r['image_id']).encode()).hexdigest())
    shortlist = []
    groups = set()
    for r in eligible:
        if r['duplicate_group'] not in groups:
            shortlist.append(r)
            groups.add(r['duplicate_group'])
        if len(shortlist) == 24:
            break
    assert len(shortlist) == 24
    scin_audit = read('outputs/mst_retention_checkpoint_v1/summary.json')
    selected_scin = list(csv.DictReader(load('data/manifests/scin_candidate_selection.csv').splitlines()))
    scin_ids = {r['case_id'] for r in selected_scin if r['intended_use']=='training_candidate'}
    scin = [dict(r, role='historical_training_candidate' if r['case_id'] in scin_ids else 'unallocated_metadata_only',
                 duplicate_screen='not_established_by_this_inventory',
                 exposure='previous_local_cases_not_claimed_unseen' if r['existing_local_paths'] else 'no_local_path_in_prior_audit',
                 training_admitted=False) for r in scin_audit['metadata_candidate_images']]
    def counts(items, key):
        return dict(Counter(r[key] for r in items))
    additional = [r for r in rows if r['additional_source_group']]
    summary = dict(status='metadata_inventory_only_no_admission', frozen_train=len(rows),
        quarantine=420-len(queue_ids), current_cohort_overlap=sum(r['in_current_26'] for r in rows),
        additional_screen_clear_sources=len(additional),
        additional_processing_status=counts(additional, 'processing_status'),
        additional_experimental_severity=counts(additional, 'experimental_severity'),
        additional_with_scoped_review_evidence=sum(bool(r['scoped_review_evidence']) for r in additional),
        additional_without_collected_review_evidence=sum(not r['scoped_review_evidence'] for r in additional),
        planning_candidates_before_bound=len(eligible), planning_list=len(shortlist),
        planning_experimental_severity=counts(shortlist, 'experimental_severity'),
        scin_metadata_images=len(scin), scin_roles=counts(scin, 'role'),
        scin_local_images_in_prior_audit=sum(bool(r['existing_local_paths']) for r in scin),
        locked_roles=['development_validation', 'final_test'], raw_images_opened=0,
        new_reviews_requested=0, new_masks_approved=0, model_fits=0,
        limitations=['Source groups do not prove distinct people.',
            'All 418 FairFace screen-clear sources already have development processing exposure.',
            'Collected scoped annotations are evidence, not a comprehensive never-reviewed certificate.',
            'Experimental severity/MST is not calibrated truth or independent illumination evidence.',
            'SCIN prior availability is not rechecked; unallocated cases cannot enter fitting.',
            'No clipping-based exclusion; existing technical failures and quarantines retained.'])
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    OUT.mkdir()
    def write(name, value):
        (OUT/name).write_text(json.dumps(value, indent=2), encoding='utf-8')
    write('fairface_inventory.json', rows)
    write('planning24.json', shortlist)
    write('scin_inventory.json', scin)
    write('summary.json', summary)
    write('verification.json', dict(status='pass', guarded_train_rows=420,
        queue_attempt_parity=418, unique_planning_groups=len(groups),
        planning_overlap_with_current26=0, reserved_pixel_access=0,
        inputs_unchanged=True, input_sha256=hashes,
        output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.json')}))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
