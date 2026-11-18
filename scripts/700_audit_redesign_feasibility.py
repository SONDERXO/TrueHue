"""Metadata-only fitting audit; never follow image paths or fit a model."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/correction_redesign_feasibility_v1'
FEATURES = 'outputs/fitting_green_features_v1/features_PRIVATE.json'
RECEIPT = 'outputs/fitting_green_features_v1/verification_with_metadata_PRIVATE.json'
DOCS = [
    'brightness-feature-comparison.md', 'brightness-feature-audit.md',
    'chromatic-feature-tree-results.md', 'endpoint-feature-tree-results.md',
    'chroma-feature-correction-results-2026-11-06.md',
    'face-local-action-results-2026-11-08.md',
    'training-exposure-colour-audit-2026-11-09.md',
    'green-feature-correction-results-2026-11-09.md',
    'correction-redesign-decision-brief-2026-11-09.md',
]


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing feasibility artifacts')
    bound = {}

    def read(rel):
        data = (ROOT / rel).read_bytes()
        bound[rel] = hashlib.sha256(data).hexdigest()
        return data

    data = json.loads(read(FEATURES))
    receipt = json.loads(read(RECEIPT))
    assert receipt['passed'] and receipt['features_sha256'] == bound[FEATURES]
    for name in DOCS:
        read('docs/' + name)
    read('scripts/700_audit_redesign_feasibility.py')
    rows = [r for r in data['records'] if r['role'] == 'fitting']
    assert len(rows) == 890 and len({r['case_id'] for r in rows}) == 890
    assert len({r['source_case'] for r in rows}) == 82
    vectors = {r['case_id']: dict(r['raw_features'], **r['features']) for r in rows}
    names = list(vectors[rows[0]['case_id']])
    assert len(names) == 8
    assert all(set(v) == set(names) and all(math.isfinite(x) for x in v.values())
               for v in vectors.values())
    by_recipe = {recipe: [r for r in rows if r['recipe'] == recipe]
                 for recipe in sorted({r['recipe'] for r in rows})}

    def ranges(group):
        return {n: [min(vectors[r['case_id']][n] for r in group),
                    max(vectors[r['case_id']][n] for r in group)] for n in names}

    # Fixed descriptive comparisons, no threshold fitting or outcome selection.
    comparisons = []
    for reference, query in [('clean', 'exposure_over'),
                             ('clean', 'exposure_under'),
                             ('exposure_under', 'colour_cool'),
                             ('exposure_under', 'colour_warm'),
                             ('exposure_under', 'stress_color_none')]:
        bounds = ranges(by_recipe[reference])
        inside = []
        for r in by_recipe[query]:
            v = vectors[r['case_id']]
            inside.append(all(bounds[n][0] <= v[n] <= bounds[n][1] for n in names))
        # Independent scalar replay of membership, not a learned predictor.
        replay = []
        for r in by_recipe[query]:
            ok = True
            for n in names:
                values = sorted(vectors[a['case_id']][n] for a in by_recipe[reference])
                x = vectors[r['case_id']][n]
                if x < values[0] or x > values[-1]:
                    ok = False
            replay.append(ok)
        assert replay == inside
        comparisons.append(dict(reference_recipe=reference, query_recipe=query,
            query_rows=len(inside), inside_all_eight_marginal_ranges=sum(inside),
            reference_ranges=bounds,
            limitation='Marginal-range overlap is not multivariate inseparability or a deployable rule.'))
    result = dict(
        passed=True, scope='Saved fitting metadata and named historical reports only',
        fitting_rows=len(rows), originals=len({r['source_case'] for r in rows}),
        recipe_counts=dict(sorted(Counter(r['recipe'] for r in rows).items())),
        feature_names=names, comparisons=comparisons,
        limitation='Only four raw Lab/ITA plus four green summaries; not all model inputs. No target-cost or predictive separability claim.',
        independent_membership_replay=True,
        disposition='No substantive new intervention qualified by this audit; no new model comparison selected.',
        image_reads=0, new_features_extracted=0, new_fits=0, predictions=0,
        evaluation_rows_used=0, holdout_reads=0, source_sha256=bound)
    for rel, expected in bound.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected
    OUT.mkdir()
    (OUT / 'audit_PRIVATE.json').write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['fitting_rows', 'originals', 'recipe_counts']}))
    for c in comparisons:
        print(c['query_recipe'], 'inside', c['reference_recipe'], c['inside_all_eight_marginal_ranges'], '/', c['query_rows'])
    print('Source hashes unchanged; scalar membership replay PASS; zero image/model/holdout access.')


if __name__ == '__main__':
    main()
