"""Independent scalar verification; imports neither optimizer nor portable runtime."""
from collections import Counter
import hashlib
import math
import struct


def verify(candidate, rows, replay, names, excluded):
    assert candidate['schema_version'] == 'truehue_source_bagged_tree_v1'
    assert candidate['aggregation'] == 'math.fsum_divide_64'
    assert candidate['feature_names'] == names and candidate['target_names'] == ['gamma', 'red_gain', 'blue_gain']
    assert len(candidate['members']) == len(replay['members']) == replay['fit_calls'] == 64
    assert rows and len({r['case_id'] for r in rows}) == len(rows)
    sources = []
    for row in rows:
        assert len(row['x']) == 22 and len(row['y']) == 3
        assert all(type(v) in (int, float) and math.isfinite(v) and struct.unpack('!f', struct.pack('!f', v))[0] == v for v in row['x'])
        assert all(type(v) in (int, float) and math.isfinite(v) and v > 0 for v in row['y'])
        if row['source'] not in sources:
            sources.append(row['source'])
    assert excluded not in sources and replay['canonical_sources'] == sources
    for s in sources:
        assert [r['role'] for r in rows if r['source'] == s] == ['identity', 'exposure_under', 'exposure_over', 'colour_cool']
    all_predictions, mean_checks = [], 0
    split_features = Counter()
    for member, (tree, rec) in enumerate(zip(candidate['members'], replay['members'])):
        assert rec['member'] == member
        expected_settings = dict(criterion='squared_error', splitter='best', max_depth=4, random_state=42+member,
            min_samples_leaf=1, min_samples_split=2, min_weight_fraction_leaf=0., max_features=None,
            max_leaf_nodes=None, min_impurity_decrease=0., ccp_alpha=0., monotonic_cst=None)
        assert rec['settings'] == expected_settings
        n = len(sources)
        draws = []
        for draw in range(n):
            attempt = 0
            while True:
                digest = hashlib.sha256(('%d:%d:%d:%d' % (42, member, draw, attempt)).encode()).hexdigest()
                number = int(digest[:8], 16)
                if number < 4294967296 - (4294967296 % n):
                    draws.append(number % n)
                    break
                attempt += 1
        assert draws == rec['source_indices']
        occurrences = []
        for d in draws:
            occurrences.extend(r for r in rows if r['source'] == sources[d])
        assert rec['occurrence_cases'] == [r['case_id'] for r in occurrences]
        validate_tree(tree, names)
        predictions, leaves = [], []
        for row in rows:
            leaf, value = route(tree, row['x'])
            predictions.append(value)
            leaves.append(leaf)
        assert predictions == rec['predictions'] and leaves == rec['leaves']
        by_leaf = {}
        for row in occurrences:
            leaf, _ = route(tree, row['x'])
            by_leaf.setdefault(leaf, []).append(row['y'])
        assert set(by_leaf) == {i for i, v in enumerate(tree['nodes']) if v['kind'] == 'leaf'}
        for leaf, targets in by_leaf.items():
            expected = [math.fsum(t[c] for t in targets) / len(targets) for c in range(3)]
            assert all(math.isclose(a, b, abs_tol=1e-12, rel_tol=1e-12) for a, b in zip(expected, tree['nodes'][leaf]['values']))
            mean_checks += 1
        split_features.update(names[node['feature']] for node in tree['nodes'] if node['kind'] == 'split')
        all_predictions.append(predictions)
    means = [[math.fsum(p[i][c] for p in all_predictions) / 64 for c in range(3)] for i in range(len(rows))]
    assert means == replay['mean_predictions']
    return dict(passed=True, members=64, member_original_fit_routes=64*len(rows),
        bootstrap_routes=64*4*len(sources), leaf_mean_checks=mean_checks,
        fitting_SSE=math.fsum((pred[c]-row['y'][c])**2 for pred, row in zip(means, rows) for c in range(3)),
        per_role_SSE={role: math.fsum((pred[c]-row['y'][c])**2 for pred, row in zip(means, rows) if row['role']==role for c in range(3)) for role in ['identity','exposure_under','exposure_over','colour_cool']},
        split_features=dict(split_features), held_predictions=0, refits=0, model_adopted=False)


def validate_tree(tree, names):
    assert tree['schema_version'] == 'truehue_regression_tree_v1'
    assert tree['feature_names'] == names and tree['target_names'] == ['gamma', 'red_gain', 'blue_gain']
    assert tree['input_dtype'] == 'float32' and tree['threshold_dtype'] == 'float64' and tree['comparison'] == '<=' and tree['root'] == 0
    assert 1 <= len(tree['nodes']) <= 31
    todo, seen = [(0, 0)], set()
    while todo:
        index, depth = todo.pop()
        assert type(index) is int and 0 <= index < len(tree['nodes']) and index not in seen and depth <= 4
        seen.add(index)
        node = tree['nodes'][index]
        if node['kind'] == 'leaf':
            assert len(node['values']) == 3 and all(type(v) in (int,float) and math.isfinite(v) and v > 0 for v in node['values'])
        else:
            assert node['kind'] == 'split' and type(node['feature']) is int and 0 <= node['feature'] < 22
            assert type(node['threshold']) in (int,float) and math.isfinite(node['threshold'])
            todo.extend([(node['left'], depth+1), (node['right'], depth+1)])
    assert len(seen) == len(tree['nodes'])


def route(tree, values):
    x = [struct.unpack('!f', struct.pack('!f', v))[0] for v in values]
    index = 0
    while tree['nodes'][index]['kind'] == 'split':
        node = tree['nodes'][index]
        index = node['left'] if x[node['feature']] <= node['threshold'] else node['right']
    return index, list(tree['nodes'][index]['values'])


def mean_predict(candidate, values):
    predictions = [route(tree, values)[1] for tree in candidate['members']]
    return [math.fsum(p[c] for p in predictions)/64 for c in range(3)]
