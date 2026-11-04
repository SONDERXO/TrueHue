"""Independent record/count replay of the existing-source readiness audit."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'outputs/core_source_readiness_v1'
    load = lambda name: json.loads((ROOT / name).read_text(encoding='utf-8'))
    report = load('outputs/core_source_readiness_v1/summary.json')
    for name, expected in report['input_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    original = load('data/manifests/source60_user_review_v1/reconciled_pairs.json')['pairs']
    records = report['sources']
    assert len(records) == len({r['image_id'] for r in records}) == 114
    flattened = [p for s in records for p in s['original_pair_decisions']]
    assert {p['pair_id'] for p in flattened} == {p['pair_id'] for p in original}
    for old in original:
        new = next(p for p in flattened if p['pair_id'] == old['pair_id'])
        assert new['decision'] == old['human_decision']
        assert new['notes'] == old['human_notes']
        assert new['historical_status'] == old['status']
        assert new['clipped_pixels'] == old['clipped_pixels']
    assert dict(Counter(p['human_decision'] for p in original)) == report['counts']['human_decisions']
    with (folder / 'sources.csv').open(encoding='utf-8', newline='') as f:
        table = list(csv.DictReader(f))
    assert {r['image_id'] for r in table} == {r['image_id'] for r in records}
    assert all(r['ready_for_core_training'] == 'False' for r in table)
    assert not any(r['ready_for_core_training'] for r in records)
    plan = load('data/manifests/non_skin_regenerated_remaining28_v1/proposed_nine_source_plan.json')
    expected_ids = {p for f in plan['folds'] for p in f['held_pair_ids']}
    actual_ids = {p for s in records for p in s['proposed_regenerated_pair_ids']}
    assert expected_ids == actual_ids and len(actual_ids) == 32
    by_id = {p['pair_id']: p for p in original}
    for fold in plan['folds']:
        assert set(fold['train_pair_ids']) == expected_ids - set(fold['held_pair_ids'])
        assert all(by_id[p]['image_id'] != fold['held_source'] for p in fold['train_pair_ids'])
    # Recalculate variant denominators independently from the original decisions.
    assert dict(Counter(by_id[p]['variant'] for p in actual_ids)) == report['counts']['proposed_variant_counts']
    summary = dict(status='pass', original_decisions_and_notes_checked=len(original),
        source_rows_checked=len(table), proposed_pair_ids_checked=len(actual_ids),
        source_folds_checked=len(plan['folds']), original_hashes_unchanged=True,
        new_model_fits=0, new_admissions=0,
        summary_sha256=hashlib.sha256((folder / 'summary.json').read_bytes()).hexdigest(),
        source_table_sha256=hashlib.sha256((folder / 'sources.csv').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (folder / 'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
