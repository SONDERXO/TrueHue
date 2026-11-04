"""Reconcile existing source evidence without processing images or fitting."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / 'outputs/core_source_readiness_v1'
    if out.exists():
        raise FileExistsError(out)
    paths = {}

    def read(name):
        p = ROOT / name
        paths[name] = hashlib.sha256(p.read_bytes()).hexdigest()
        if p.suffix == '.csv':
            with p.open(encoding='utf-8-sig', newline='') as f:
                return list(csv.DictReader(f))
        return json.loads(p.read_text(encoding='utf-8-sig'))

    inventory = read('data/manifests/paint_protection_validation_v1/draft_manifest.json')['inventory']
    master = {r['image_id']: r for r in read('data/manifests/controlled_development_v1/source_audit.csv')}
    screens = {}
    for folder, name in [('training_coverage_audit_v1', 'candidate_disposition.json'),
                         ('source_screening_followup_v1', 'candidate_disposition.json'),
                         ('brightness_color_source_screen_v1', 'candidate_disposition.json'),
                         ('training_source60_screen_v1', 'source_dispositions.json')]:
        name = f'data/manifests/{folder}/{name}'
        data = read(name)
        for row in data.get('observations', data.get('new_sources', [])):
            screens.setdefault(row['image_id'], []).append({'path': name, 'record': row})
    pairs = read('data/manifests/source60_user_review_v1/reconciled_pairs.json')['pairs']
    remaining = read('data/manifests/non_skin_regenerated_remaining28_v1/recheck_dispositions.json')['pairs']
    two = read('data/manifests/non_skin_regenerated_two_v1/recheck_dispositions.json')['pairs']
    coverage = read('data/manifests/non_skin_regenerated_remaining28_v1/user_coverage_review.json')
    plan = read('data/manifests/non_skin_regenerated_remaining28_v1/proposed_nine_source_plan.json')
    policy = read('data/manifests/non_skin_regenerated_remaining28_v1/policy.json')
    for name in ['docs/core-source-readiness-protocol.md', 'scripts/125_audit_core_source_readiness.py',
                 'data/manifests/development_exposure_additions.jsonl',
                 'models/correction_prototype_v1/decision_tree.joblib']:
        paths[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(inventory) == len({r['image_id'] for r in inventory}) == 114
    assert len(pairs) == len({r['pair_id'] for r in pairs}) == 75
    by_pair = {r['pair_id']: r for r in pairs}
    candidates = {r['pair_id'] for r in remaining} | {
        r['pair_id'] for r in two if r['new_status'] == 'regenerated_candidate_pending_changed_mask_review'}
    assert len(candidates) == 32
    assert set(coverage['pair_ids']) == {r['pair_id'] for r in remaining}
    assert all(by_pair[p]['human_decision'] == 'accept' for p in candidates)
    folds = plan['folds']
    held = [p for f in folds for p in f['held_pair_ids']]
    assert len(held) == len(set(held)) == len(candidates) and set(held) == candidates
    for fold in folds:
        train, test = set(fold['train_pair_ids']), set(fold['held_pair_ids'])
        assert train == candidates - test and not train & test
        source = fold['held_source']
        assert all(by_pair[p]['image_id'] == source for p in test)
        held_group = master[source]['duplicate_group_id']
        assert all(master[by_pair[p]['image_id']]['duplicate_group_id'] != held_group for p in train)
    records = []
    for item in inventory:
        ident = item['image_id']
        assert master[ident]['partition'] == item['partition'] == 'train'
        selected = [r for r in pairs if r['image_id'] == ident]
        accepted = [r for r in selected if r['human_decision'] == 'accept']
        records.append(dict(image_id=ident, partition='train',
            duplicate_group_id=master[ident]['duplicate_group_id'],
            prior_screens=screens.get(ident, []),
            original_pair_decisions=[dict(pair_id=r['pair_id'], variant=r['variant'],
                decision=r['human_decision'], notes=r['human_notes'],
                historical_status=r['status'], clipped_pixels=r['clipped_pixels']) for r in selected],
            accepted_variants=sorted(r['variant'] for r in accepted),
            proposed_regenerated_pair_ids=sorted(r['pair_id'] for r in selected if r['pair_id'] in candidates),
            complete_five_original_acceptances=len(accepted) == 5,
            ready_for_core_training=False,
            readiness_reason=('changed_mask_coverage_unresolved_and_processing_policy_differs'
                              if any(r['pair_id'] in candidates for r in selected)
                              else 'no_current_core_cohort_admission_established')))
    assert all(r['image_id'] in {i['image_id'] for i in inventory} for r in pairs)
    counts = dict(inventoried_sources=len(records), original_attempts=len(pairs),
        human_decisions=dict(Counter(r['human_decision'] for r in pairs)),
        original_accepted_sources=len({r['image_id'] for r in pairs if r['human_decision'] == 'accept'}),
        original_complete_five_sources=sum(r['complete_five_original_acceptances'] for r in records),
        proposed_changed_mask_pairs=len(candidates), proposed_sources=len(folds),
        proposed_variant_counts=dict(Counter(by_pair[p]['variant'] for p in candidates)),
        newly_ready_core_pairs=0, new_model_fits=0, new_image_exposures=0)
    summary = dict(status='complete_no_new_cohort_admission', counts=counts, sources=records,
        proposed_fold_checks='all_ids_exact_train_and_source_duplicate_group_separated',
        coverage_review=coverage,
        processing_mismatch=dict(existing_candidate=policy,
            current_core='native224; HSV/YCrCb complete-mouth; legacy estimation correction support; four Lab/ITA features'),
        reference_limitation='Photographic reconstruction references, not calibrated neutral exposure/color or independent MST labels.',
        input_sha256=paths)
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in paths.items())
    out.mkdir(parents=True)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with (out / 'sources.csv').open('w', encoding='utf-8', newline='') as f:
        keys = ['image_id', 'partition', 'duplicate_group_id', 'accepted_variants',
                'proposed_regenerated_pair_ids', 'complete_five_original_acceptances',
                'ready_for_core_training', 'readiness_reason']
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows({k: r[k] for k in keys} for r in records)
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
