"""Descriptive saved-record assessment only; no images, training or inference."""
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/primary_training_evidence_feasibility_v1'
SOURCES = [
    'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',
    'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json',
    'outputs/bounded_search_transfer_diagnosis_v1/paired_paths_PRIVATE.json',
    'outputs/bounded_search_transfer_diagnosis_v1/held_contexts_PRIVATE.json',
    'docs/correction-training-target-audit-results-2026-11-11.md',
    'docs/training-exposure-colour-audit-2026-11-09.md',
    'outputs/proposal_scope_validation_20261103_v1/pages.json',
]


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def main():
    if OUT.exists():
        raise FileExistsError('Preserve prior assessment')
    bindings = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    rows = read(SOURCES[0])
    names = read(SOURCES[1])['feature_names']
    assert len(rows) == 44 and len(names) == 16
    assert all(r['status'] == 'available' and not r['generated_fixture'] for r in rows)
    byid = {r['case_id']: r for r in rows}
    groups = defaultdict(list)
    duplicates = defaultdict(list)
    for row in rows:
        groups[row['publisher_group']].append(row)
        duplicates[tuple(row['input_vector_float32'])].append(row)
    conflicts = [[r['case_id'] for r in v] for v in duplicates.values()
                 if len({tuple(r['nominal_controls']) for r in v}) > 1]
    pairs = []
    for saved in read(SOURCES[2]):
        a, b = byid[saved['identity_case']], byid[saved['cool_case']]
        changed = [n for j, n in enumerate(names)
                   if a['input_vector_float32'][j] != b['input_vector_float32'][j]]
        pairs.append(dict(group=saved['group'], same_leaf=saved['same_leaf'],
                          changed_features=changed, distinguishable=bool(changed)))
    contexts = read(SOURCES[3])
    collision_free_collapsed = []
    for g, rs in groups.items():
        assert Counter(r['experimental_role'] for r in rs) == dict(
            identity=1, exposure_under=1, exposure_over=1, colour_cool=1)
        cs = [c for c in contexts if c['held_group'] == g]
        if len({c['leaf'] for c in cs}) == 1:
            collision_free_collapsed.append(dict(group=g, distinct_vectors=len(
                {tuple(r['input_vector_float32']) for r in rs}),
                distinct_targets=len({tuple(r['nominal_controls']) for r in rs})))
    feature_summary = []
    roles = ['identity', 'exposure_under', 'exposure_over', 'colour_cool']
    for j, name in enumerate(names):
        intervals = {role: [min(r['input_vector_float32'][j] for r in rows if r['experimental_role'] == role),
                            max(r['input_vector_float32'][j] for r in rows if r['experimental_role'] == role)]
                     for role in roles}
        overlaps = {a + '__' + b: max(intervals[a][0], intervals[b][0]) <= min(intervals[a][1], intervals[b][1])
                    for a, b in combinations(roles, 2)}
        feature_summary.append(dict(name=name, distinct_values=len({r['input_vector_float32'][j] for r in rows}),
                                    role_intervals=intervals, interval_overlap=overlaps))
    mst = []
    for g, rs in groups.items():
        vals = {r['experimental_role']: r['features']['input_mst_score'] for r in rs}
        mst.append(dict(group=g, by_role=vals, within_source_span=max(vals.values())-min(vals.values())))
    role_targets = {role: sorted({tuple(r['nominal_controls']) for r in rows if r['experimental_role'] == role})
                    for role in roles}
    summary = dict(rows=44, photo_groups=len(groups), generated_fixtures=0,
                   distinct_full_vectors=len(duplicates), exact_conflicting_vector_groups=len(conflicts),
                   identity_cool_distinguishable=sum(p['distinguishable'] for p in pairs),
                   distinguishable_identity_cool_same_leaf=sum(p['distinguishable'] and p['same_leaf'] for p in pairs),
                   collapsed_groups=collision_free_collapsed,
                   target_values_by_axis=[sorted({r['nominal_controls'][j] for r in rows}) for j in range(3)],
                   role_targets=role_targets,
                   provided_mst_labels=sum(r['provided_mst_label'] is not None for r in rows),
                   mst_distinct_values=len({r['features']['input_mst_score'] for r in rows}),
                   mst_changes_with_recipe_groups=sum(v['within_source_span'] != 0 for v in mst),
                   target_independent_of_source_within_each_role=all(len(v) == 1 for v in role_targets.values()),
                   new_fits=0, new_predictions=0, photo_bytes_read=0, holdout_bytes_read=0,
                   decision='No distinct supported repair established; do not fit, acquire, or reopen closed trials.')
    OUT.mkdir()
    for name, data in [('summary', summary), ('feature_intervals', feature_summary),
                       ('identity_cool_distinguishability', pairs), ('mst_by_source', mst),
                       ('conflicts', conflicts), ('input_sha256', bindings)]:
        (OUT / (name + '_PRIVATE.json')).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in bindings.items())
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
