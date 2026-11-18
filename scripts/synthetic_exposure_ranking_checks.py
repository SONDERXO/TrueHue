"""Independent scalar scaler, pair, gradient/Adam and score replay."""
import math
import numpy as np

PAIRS = [('identity', 'exposure_under'), ('identity', 'exposure_over'),
         ('colour_only', 'combined_under'), ('colour_only', 'combined_over')]


def close(a, b, tol=1e-10):
    if not math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol):
        raise AssertionError((a, b, tol))


def scalar_score(head, x):
    return math.fsum(w * ((float(a) - mean) / scale)
                     for w, a, mean, scale in zip(head['weights'], x, head['mean'], head['scale']))


def verify_model(head, trace, states, records, provider, held_source):
    # No trainer prepare/scaler/pair/loss/optimizer call in this replay.
    ordered = sorted(records, key=lambda r: r['case_id'])
    assert all(r['source_id'] != held_source and r['partition'] == 'Train' for r in ordered)
    ids = [r['case_id'] for r in ordered]
    assert head['training_ids'] == ids and head['held_source'] == held_source
    by_source = {}
    for r in ordered:
        by_source.setdefault(r['source_id'], {})[r['role']] = r['case_id']
    expected_pairs = sorted((g[a], g[b]) for g in by_source.values() for a, b in PAIRS)
    assert [list(p) for p in expected_pairs] == [list(p) for p in head['explicit_pair_ids']]
    assert head['training_sources'] == sorted(by_source)
    assert head['source_pair_counts'] == {s: 4 for s in by_source}
    x = [np.asarray(provider(k), dtype=np.float64).tolist() for k in ids]
    n = len(x)
    means = [math.fsum(row[j] for row in x) / n for j in range(4096)]
    scales = [math.sqrt(math.fsum((row[j] - means[j]) ** 2 for row in x) / n)
              for j in range(4096)]
    scales = [s if s != 0 else 1. for s in scales]
    for actual, expected in zip(head['mean'] + head['scale'], means + scales):
        close(actual, expected)
    # Use the declared independently checked scaler to isolate optimizer replay.
    z = [[(value - mean) / scale for value, mean, scale
          in zip(row, head['mean'], head['scale'])] for row in x]
    pos = {k: i for i, k in enumerate(ids)}
    d = [[a - b for a, b in zip(z[pos[p]], z[pos[q]])] for p, q in expected_pairs]
    # Sparse generated fixtures can omit provably inactive coordinates.
    active = [j for j in range(4096) if any(row[j] != 0 for row in d)]
    inactive = sorted(set(range(4096)) - set(active))
    dd = [[row[j] for j in active] for row in d]
    w = [0.] * len(active); m = w.copy(); v = w.copy()
    max_state_error = 0.; max_loss_error = 0.
    assert len(trace) == head['optimizer_updates'] == 50
    assert all(a.shape == (50, 4096) for a in states.values())
    rng = np.random.default_rng(42)
    for step, entry in enumerate(trace, 1):
        # Replay each update independently from its recorded prior state.
        # A separate end-to-end rounded trajectory can diverge near a perfectly
        # stationary coordinate because Adam divides tiny gradients by epsilon.
        # Native gradients/loss/update functions are never used here.
        if step > 1:
            w = states['weights'][step - 2, active].tolist()
            m = states['first_moment'][step - 2, active].tolist()
            v = states['second_moment'][step - 2, active].tolist()
        order = entry['batch_indices']
        assert order == rng.permutation(len(expected_pairs)).tolist()
        assert sorted(order) == list(range(len(expected_pairs)))
        assert entry['step'] == step and entry['epoch'] == step - 1
        margins = [math.fsum(a * b for a, b in zip(w, dd[i])) for i in order]
        loss = math.fsum(max(0., -a) + math.log1p(math.exp(-abs(a)))
                         for a in margins) / len(order) + .0005 * math.fsum(a * a for a in w)
        max_loss_error = max(max_loss_error, abs(loss - entry['loss']))
        close(loss, entry['loss'])
        coeffs = [-(math.exp(-a) / (1 + math.exp(-a)) if a >= 0
                    else 1 / (1 + math.exp(a))) / len(order) for a in margins]
        gradients = [math.fsum(c * dd[i][j] for c, i in zip(coeffs, order)) + .001 * w[j]
                     for j in range(len(active))]
        for j, g in enumerate(gradients):
            m[j] = .9 * m[j] + .1 * g
            v[j] = .999 * v[j] + .001 * g * g
            w[j] -= .01 * (m[j] / (1 - .9 ** step)) / (math.sqrt(v[j] / (1 - .999 ** step)) + 1e-8)
        for field, expected in [('weights', w), ('first_moment', m), ('second_moment', v)]:
            actual = states[field][step - 1]
            if inactive:
                assert np.count_nonzero(actual[inactive]) == 0
            for k, value in zip(active, expected):
                max_state_error = max(max_state_error, abs(float(actual[k]) - value))
                close(actual[k], value, 1e-8)
    expected_full = [0.] * 4096
    for k, value in zip(active, w):
        expected_full[k] = value
    for a, b in zip(head['weights'], expected_full):
        close(a, b, 1e-8)
    assert np.array_equal(states['weights'][-1], np.asarray(head['weights']))
    return dict(passed=True, source_exclusion=True, independently_replayed_updates=50,
                replay_from_each_saved_prior_state=True,
                scaler_values=8192, explicit_preferences=len(expected_pairs),
                active_coordinates=len(active), scalar_state_max_error=max_state_error,
                scalar_loss_max_error=max_loss_error, verifier_candidate_fits=0)
