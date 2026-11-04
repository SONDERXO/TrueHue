"""Refit saved clean-control comparisons and replay every held-source output."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree, export_tree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors


def main():
    out = ROOT / 'outputs/accepted_clean_control_comparison_v1'
    def read(p): return json.loads(p.read_text(encoding='utf-8'))
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    target = out / 'verification.json'
    if target.exists(): raise FileExistsError(target)
    plan, records, summary = [read(out / n) for n in ('plan.json', 'predictions.json', 'summary.json')]
    for path, digest in plan['input_sha256'].items(): assert sha(ROOT / path) == digest
    rows = {r['pair_id']: r for r in plan['rows']}
    new = [r for r in rows.values() if r['cohort'] == 'new_clean']
    assert {r['pair_id'].split('__')[0] for r in new} == set('85815 56839 75166 68073 75898 62105 20648 72400 34227 34458 29880'.split())
    reviews = read(ROOT / 'outputs/training_review36_import_v1/combined_original_mask_reviews60.json')
    for row in new:
        review = next(r for r in reviews if r['image_id'] == row['source_image_id'])
        assert review['decision'] == 'accept' and not review['notes'].strip()
        assert row['variant'] == 'identity' and row['paper_target'] == [1., 1., 1.]
        assert row['input_path'] == row['reference_path'] and row['input_mask_path'] == row['reference_mask_path']
    fits = 0
    for fold in plan['folds']:
        old = [r['pair_id'] for r in rows.values() if r['cohort'] == 'historical' and r['duplicate_group_id'] != fold['held_group']]
        extra = [r['pair_id'] for r in new if r['duplicate_group_id'] != fold['held_group']]
        controls = sorted([p for p in old if rows[p]['variant'] == 'identity'], key=lambda p: (hashlib.sha256(('clean_count_match_v1/' + p).encode()).hexdigest(), p))
        duplicates = [controls[i % len(controls)] for i in range(len(extra))]
        assert old == fold['historical_train_ids'] and extra == fold['new_control_train_ids'] and duplicates == fold['duplicate_control_ids']
        assert set(fold['held_pair_ids']) == {p for p, r in rows.items() if r['duplicate_group_id'] == fold['held_group']}
        for method in plan['methods']:
            ids = old + (extra if method == 'new_clean_sources' else duplicates if method == 'count_matched_controls' else [])
            training = [rows[p] for p in ids]
            assert not {r['source_image_id'] for r in training} & {rows[p]['source_image_id'] for p in fold['held_pair_ids']}
            x = [[r[k] for k in plan['features']] for r in training]
            model = DecisionTreeRegressor(**plan['settings']).fit(x, [r['paper_target'] for r in training])
            raw = export_tree(model, plan['features'], plan['target_names'], {})
            tree = PortableTree(raw)
            # Reconstruct protection independently from raw fitting membership.
            protected = {tree.leaf_id(v) for r, v in zip(training, x) if r['variant'] == 'identity'}
            for leaf in protected: raw['nodes'][leaf]['values'] = [1., 1., 1.]
            folder = out / f'fold_{fold["fold_id"]}'
            assert read(folder / (method + '.json'))['nodes'] == raw['nodes']
            assert read(folder / (method + '_membership.json'))['train_pair_ids'] == ids
            fits += 1
    for r in records:
        row = rows[r['pair_id']]
        folder = out / f'fold_{r["fold_id"]}'
        tree = PortableTree(read(folder / (r['method'] + '.json')))
        assert tree.predict_one([row[k] for k in plan['features']]) == r['parameters']
        image = cv2.cvtColor(cv2.imread(str(ROOT / row['input_path'])), cv2.COLOR_BGR2RGB)
        reference = cv2.cvtColor(cv2.imread(str(ROOT / row['reference_path'])), cv2.COLOR_BGR2RGB)
        mask = cv2.imread(str(ROOT / row['input_mask_path']), 0) > 0
        scoring = cv2.imread(str(ROOT / row['reference_mask_path']), 0) > 0
        result = image.copy()
        result[mask] = np.rint(transform_rgb(image.astype(float) / 255, *r['parameters'])[mask] * 255).astype(np.uint8)
        path = folder / (r['pair_id'] + '_' + r['method'] + '.png')
        assert sha(path) == r['output_sha256']
        np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB), result)
        np.testing.assert_array_equal(result[~mask], image[~mask])
        assert r['changed_input_pixels'] == np.count_nonzero(np.any(result != image, axis=2))
        for key, expected in [('metrics', image_errors(reference, result, scoring)), ('no_correction', image_errors(reference, image, scoring))]:
            for name, value in expected.items():
                if value is None: assert r[key][name] is None
                else: assert abs(value - r[key][name]) < 1e-12
    for a in summary['aggregates']:
        scope = a['scope']
        selected = [r for r in records if r['method'] == a['method'] and (scope == 'combined' or
                    scope == 'new_clean' and r['cohort'] == 'new_clean' or
                    r['cohort'] == 'historical' and (scope == 'historical_all' or
                    scope == 'historical_clean' and r['variant'] == 'identity' or
                    scope == 'historical_distorted' and r['variant'] != 'identity'))]
        assert len(selected) == a['pairs']
        assert abs(np.mean([r['metrics']['ciede2000_source_mask'] for r in selected]) - a['mean_ciede2000']) < 1e-12
        assert abs(np.mean([r['no_correction']['ciede2000_source_mask'] for r in selected]) - a['no_correction']) < 1e-12
        assert sum(r['changed_input_pixels'] > 0 for r in selected) == a['changed_pairs']
    for method, gate in summary['gates'].items():
        selected = [r for r in records if r['method'] == method]
        harms = [r['pair_id'] for r in selected if r['variant'] == 'identity' and r['changed_input_pixels']]
        assert harms == gate['harmed_clean_ids'] and gate['clean_unchanged'] == (not harms)
        improvement = np.mean([r['metrics']['ciede2000_source_mask'] - r['no_correction']['ciede2000_source_mask'] for r in selected]) < 0
        assert gate['overall_improves'] == improvement and gate['passed'] == (improvement and not harms)
    baseline = next(a for a in summary['aggregates'] if a['method'] == 'historical_only' and a['scope'] == 'historical_all')
    assert abs(baseline['mean_ciede2000'] - 7.131645878072771) < 1e-12
    assert fits == 78 and len(records) == 123 and len(plan['folds']) == 26
    target.write_text(json.dumps(dict(status='pass',independent_refits=fits,replayed_outputs_and_metrics=len(records),
        source_group_separation_verified=True,reference_review_admissions_verified=11,
        historical_baseline_reproduced=True,failed_candidates_not_promoted=True,
        evidence_sha256={p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS: 78 independent refits, 123 output/metric replays, 26 source-separated folds; no promotion.')


if __name__ == '__main__': main()
