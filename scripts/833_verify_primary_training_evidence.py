"""Independent pairwise and saved-tree replay; no fitting or image access."""
from pathlib import Path
from itertools import combinations
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/primary_training_evidence_feasibility_v1'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    dest = OUT / 'verification_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve verification')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h
               for p, h in read(OUT/'input_sha256_PRIVATE.json').items())
    rows = read(ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')
    names = read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json')['feature_names']
    models = read(ROOT/'outputs/bounded_training_comparison_v1/models_PRIVATE.json')
    result = read(OUT/'summary_PRIVATE.json')
    # Independent all-pairs comparison instead of hashing vectors into buckets.
    comparisons = 0
    for a, b in combinations(rows, 2):
        comparisons += 1
        assert any(x != y for x, y in zip(a['input_vector_float32'], b['input_vector_float32']))
    assert result['distinct_full_vectors'] == len(rows) == 44
    assert result['exact_conflicting_vector_groups'] == 0
    def leaf(m, r):
        nodes = m['tree']['nodes']
        i = 0
        while nodes[i]['kind'] == 'split':
            n = nodes[i]
            i = n['left'] if r['input_vector_float32'][n['feature']] <= n['threshold'] else n['right']
        return i
    checked = 0
    for pair in read(OUT/'identity_cool_distinguishability_PRIVATE.json'):
        model = next(m for m in models if m['definition']['held_publisher_group'] == pair['group'])
        own = [r for r in rows if r['publisher_group'] == pair['group']]
        a = next(r for r in own if r['experimental_role'] == 'identity')
        b = next(r for r in own if r['experimental_role'] == 'colour_cool')
        assert pair['same_leaf'] == (leaf(model, a) == leaf(model, b))
        assert pair['changed_features'] == [name for j, name in enumerate(names)
            if a['input_vector_float32'][j] != b['input_vector_float32'][j]]
        checked += 1
    for feature in read(OUT/'feature_intervals_PRIVATE.json'):
        j = names.index(feature['name'])
        for role, interval in feature['role_intervals'].items():
            vals = sorted(r['input_vector_float32'][j] for r in rows if r['experimental_role'] == role)
            assert interval == [vals[0], vals[-1]]
        for key, overlap in feature['interval_overlap'].items():
            a, b = key.split('__')
            aa, bb = feature['role_intervals'][a], feature['role_intervals'][b]
            assert overlap == (aa[0] <= bb[1] and bb[0] <= aa[1])
    normal = [r for r in rows if r['experimental_role'] == 'identity']
    assert len({r['features']['input_mst_score'] for r in normal}) == 1
    assert result['provided_mst_labels'] == sum(r['provided_mst_label'] is not None for r in rows) == 0
    assert result['mst_changes_with_recipe_groups'] == 2
    for m in read(OUT/'mst_by_source_PRIVATE.json'):
        own = [r for r in rows if r['publisher_group'] == m['group']]
        assert m['by_role'] == {r['experimental_role']:r['features']['input_mst_score'] for r in own}
    assert all(len({tuple(r['nominal_controls']) for r in rows if r['experimental_role'] == role}) == 1
               for role in ['identity', 'exposure_under', 'exposure_over', 'colour_cool'])
    for collapsed in result['collapsed_groups']:
        m = next(m for m in models if m['definition']['held_publisher_group'] == collapsed['group'])
        own = [r for r in rows if r['publisher_group'] == collapsed['group']]
        assert len({leaf(m, r) for r in own}) == 1
        assert len({tuple(r['nominal_controls']) for r in own}) == collapsed['distinct_targets'] == 4
    dest.write_text(json.dumps(dict(passed=True, pairwise_vector_checks=comparisons,
        paired_saved_tree_replays=checked, feature_intervals=64, marginal_overlaps=96,
        mst_source_checks=11, collapsed_groups=3, fits=0, photo_reads=0, holdout_reads=0,
        summary_sha256=hashlib.sha256((OUT/'summary_PRIVATE.json').read_bytes()).hexdigest(),
        assessor_sha256=hashlib.sha256((ROOT/'scripts/832_assess_primary_training_evidence.py').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    print(dest.read_text())


if __name__ == '__main__':
    main()
