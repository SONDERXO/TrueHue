"""Fixed capacity comparison using previously admitted source-held controls."""
import argparse
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
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors

OUT = ROOT / 'outputs/clean_control_tree_depth_v1'
PARENT = ROOT / 'outputs/accepted_clean_control_comparison_v1'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value): path.write_text(json.dumps(value, indent=2), encoding='utf-8')
def vector(row, plan): return [row[k] for k in plan['features']]


def render(row, params):
    image = cv2.cvtColor(cv2.imread(str(ROOT / row['input_path'])), cv2.COLOR_BGR2RGB)
    reference = cv2.cvtColor(cv2.imread(str(ROOT / row['reference_path'])), cv2.COLOR_BGR2RGB)
    mask = cv2.imread(str(ROOT / row['input_mask_path']), 0) > 0
    score = cv2.imread(str(ROOT / row['reference_mask_path']), 0) > 0
    output = image.copy()
    output[mask] = np.rint(transform_rgb(image.astype(float) / 255, *params)[mask] * 255).astype(np.uint8)
    return image, reference, mask, score, output


def selected(records, method, scope):
    return [r for r in records if r['method'] == method and (
        scope == 'combined' or scope == 'new_clean' and r['cohort'] == 'new_clean' or
        r['cohort'] == 'historical' and (scope == 'historical_all' or
        scope == 'historical_clean' and r['variant'] == 'identity' or
        scope == 'historical_distorted' and r['variant'] != 'identity'))]


def summarize(records):
    aggregates, gates = [], {}
    for method in ('depth3', 'depth5'):
        for scope in ('historical_all', 'historical_clean', 'historical_distorted', 'new_clean', 'combined'):
            values = selected(records, method, scope)
            aggregates.append(dict(method=method, scope=scope, pairs=len(values),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in values])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in values])),
                changed_pairs=sum(r['changed_input_pixels'] > 0 for r in values)))
        clean_harms = [r['pair_id'] for r in selected(records, method, 'combined') if r['variant'] == 'identity' and r['changed_input_pixels']]
        a = aggregates[-1]
        improvement = a['mean_ciede2000'] < a['no_correction']
        gates[method] = dict(overall_improves=improvement, clean_unchanged=not clean_harms,
                            harmed_clean_ids=clean_harms, passed=improvement and not clean_harms)
    return dict(aggregates=aggregates, gates=gates, active_demo_changed=False,
                evidence_role='exposed development; no final validation', fits=52, predictions=82)


def train():
    if OUT.exists(): raise FileExistsError(OUT)
    parent = read(PARENT / 'plan.json')
    assert read(PARENT / 'verification.json')['status'] == 'pass'
    hashes = dict(parent['input_sha256'])
    for p in (PARENT / 'plan.json', PARENT / 'verification.json', Path(__file__), ROOT / 'docs/clean-control-tree-depth-protocol.md'):
        hashes[p.relative_to(ROOT).as_posix()] = digest(p)
    for path, sha in hashes.items(): assert digest(ROOT / path) == sha
    plan = dict(parent, input_sha256=hashes, methods=['depth3', 'depth5'], depths={'depth3':3, 'depth5':5},
                status='frozen_before_training', parent_experiment=str(PARENT.relative_to(ROOT)))
    OUT.mkdir(); write(OUT / 'plan.json', plan)
    rows = {r['pair_id']:r for r in plan['rows']}; records = []
    for fold in plan['folds']:
        ids = fold['historical_train_ids'] + fold['new_control_train_ids']
        fitting = [rows[p] for p in ids]
        assert not {r['source_image_id'] for r in fitting} & {rows[p]['source_image_id'] for p in fold['held_pair_ids']}
        folder = OUT / f'fold_{fold["fold_id"]}'; folder.mkdir()
        x = [vector(r, plan) for r in fitting]
        for method, depth in plan['depths'].items():
            settings = dict(plan['settings'], max_depth=depth)
            model = DecisionTreeRegressor(**settings).fit(x, [r['paper_target'] for r in fitting])
            raw = export_tree(model, plan['features'], plan['target_names'], dict(gamma_convention='direct_exponent', held_group=fold['held_group']))
            payload, audit = protect_identity_leaves(raw, x, [r['variant'] == 'identity' for r in fitting])
            tree = PortableTree(payload)
            write(folder / (method + '.json'), payload)
            write(folder / (method + '_membership.json'), dict(train_pair_ids=ids, **audit))
            for pair in fold['held_pair_ids']:
                row = rows[pair]; features = vector(row, plan); params = tree.predict_one(features)
                image, reference, mask, score, output = render(row, params)
                assert np.array_equal(image[~mask], output[~mask])
                path = folder / (pair + '_' + method + '.png')
                assert cv2.imwrite(str(path), cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
                leaf = tree.leaf_id(features)
                members = [p for p, v in zip(ids, x) if tree.leaf_id(v) == leaf]
                records.append(dict(pair_id=pair, method=method, fold_id=fold['fold_id'],
                    cohort=row['cohort'], variant=row['variant'], parameters=params, leaf_id=leaf,
                    fitting_leaf_pair_ids=members, fitting_leaf_control_count=sum(rows[p]['variant'] == 'identity' for p in members),
                    changed_input_pixels=int(np.count_nonzero(np.any(output != image, axis=2))),
                    metrics=image_errors(reference, output, score), no_correction=image_errors(reference, image, score),
                    output_sha256=digest(path)))
        print('Fold', fold['fold_id'], 'complete', flush=True)
    write(OUT / 'predictions.json', records); write(OUT / 'summary.json', summarize(records))
    print('Saved 52 fits and 82 held predictions.')


def verify():
    target = OUT / 'verification.json'
    if target.exists(): raise FileExistsError(target)
    plan, records = read(OUT / 'plan.json'), read(OUT / 'predictions.json')
    rows = {r['pair_id']:r for r in plan['rows']}; fits = 0
    for path, sha in plan['input_sha256'].items(): assert digest(ROOT / path) == sha
    parent = read(PARENT / 'plan.json')
    assert plan['rows'] == parent['rows'] and plan['folds'] == parent['folds']
    assert len(plan['folds']) == 26 and len(records) == 82
    for fold in plan['folds']:
        ids = fold['historical_train_ids'] + fold['new_control_train_ids']
        held = {p for p, r in rows.items() if r['duplicate_group_id'] == fold['held_group']}
        assert held == set(fold['held_pair_ids'])
        assert set(ids) == {p for p in rows if p not in held}
        assert not {rows[p]['source_image_id'] for p in ids} & {rows[p]['source_image_id'] for p in held}
        x = [vector(rows[p], plan) for p in ids]
        for method, depth in plan['depths'].items():
            raw = export_tree(DecisionTreeRegressor(**dict(plan['settings'], max_depth=depth)).fit(x, [rows[p]['paper_target'] for p in ids]), plan['features'], plan['target_names'], {})
            rawtree = PortableTree(raw)
            leaf_ids = [rawtree.leaf_id(v) for v in x]
            protected = {leaf for p, leaf in zip(ids, leaf_ids) if rows[p]['variant'] == 'identity'}
            for leaf in protected: raw['nodes'][leaf]['values'] = [1.,1.,1.]
            folder = OUT / f'fold_{fold["fold_id"]}'
            saved = read(folder / (method + '.json'))
            assert raw['nodes'] == saved['nodes']
            membership = read(folder / (method + '_membership.json'))
            assert membership['train_pair_ids'] == ids and membership['protected_leaves'] == sorted(protected)
            for leaf in set(leaf_ids):
                expected_indices = [i for i, value in enumerate(leaf_ids) if value == leaf]
                assert membership['membership'][str(leaf)] == dict(training_indices=expected_indices,
                    identity_indices=[i for i in expected_indices if rows[ids[i]]['variant'] == 'identity'])
            for r in [r for r in records if r['fold_id'] == fold['fold_id'] and r['method'] == method]:
                assert r['pair_id'] in held
                row = rows[r['pair_id']]; tree = PortableTree(saved)
                assert tree.predict_one(vector(row, plan)) == r['parameters']
                leaf = tree.leaf_id(vector(row, plan))
                members = [p for p, value in zip(ids, leaf_ids) if value == leaf]
                assert leaf == r['leaf_id'] and members == r['fitting_leaf_pair_ids']
                assert sum(rows[p]['variant'] == 'identity' for p in members) == r['fitting_leaf_control_count']
                image, reference, mask, score, output = render(row, r['parameters'])
                path = folder / (r['pair_id'] + '_' + method + '.png')
                assert digest(path) == r['output_sha256']
                np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB), output)
                np.testing.assert_array_equal(output[~mask], image[~mask])
                assert np.count_nonzero(np.any(image != output, axis=2)) == r['changed_input_pixels']
                assert image_errors(reference, output, score) == r['metrics']
                assert image_errors(reference, image, score) == r['no_correction']
            fits += 1
    assert summarize(records) == read(OUT / 'summary.json')
    previous = {r['pair_id']:r for r in read(PARENT / 'predictions.json') if r['method'] == 'new_clean_sources'}
    for r in records:
        if r['method'] == 'depth3':
            assert r['parameters'] == previous[r['pair_id']]['parameters']
            assert r['metrics'] == previous[r['pair_id']]['metrics']
    assert fits == 52
    write(target, dict(status='pass', independent_refits=52, verified_output_replays=82,
        depth3_parent_reproduced=True, source_separation_and_fitting_membership_verified=True,
        active_demo_changed=False, evidence_sha256={p.relative_to(OUT).as_posix():digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 52 refits, 82 pixel/metric replays, exact depth-3 parent parity.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    verify() if args.verify else train()
