import json
import hashlib
import cv2
import numpy as np
import pytest
from src.evaluation import directional_recoverability as flow
from src.evaluation import directional_recoverability_scalar as scalar
from src.model_training import blended_recovery_targets as targets
from src.evaluation.directional_recoverability_loading import load_sources


def source(index=0):
    reference = np.random.default_rng(704 + index).integers(0, 256, (12, 12, 3), dtype=np.uint8)
    reference[3, 3] = [0, 0, 0]
    reference[4, 4] = [255, 255, 255]
    alpha = np.ones((12, 12), float)
    alpha[[0, -1], :] = 0
    alpha[:, [0, -1]] = 0
    alpha[1, 1:-1] = .25
    alpha[-2, 1:-1] = .75
    protected = np.zeros((12, 12), bool)
    protected[5, 5] = True
    alpha[protected] = 0
    return dict(source_id=f'generated_{index:02}', reference=reference, alpha=alpha,
                protected=protected, generated_fixture=True)


@pytest.mark.parametrize('role', list(flow.ROLES))
def test_actual_optimizer_and_independent_scalar_replay(role):
    s = source()
    before = {k: flow.array_hash(s[k]) for k in ('reference', 'alpha', 'protected')}
    record, image, output = flow.run_case(s, role)
    assert scalar.verify(s, record, image, output)
    assert before == {k: flow.array_hash(s[k]) for k in before}
    assert not record['training_admitted'] and not record['model_ready']


def test_identity_never_calls_fitter():
    def forbidden(*args):
        raise AssertionError('Identity must not optimize')
    s = source()
    record, image, output = flow.run_case(s, 'identity', fitter=forbidden)
    assert record['target']['evaluations'] == 0
    np.testing.assert_array_equal(output, s['reference'])


def test_optimizer_settings_remain_one_identity_start(monkeypatch):
    original = targets.least_squares
    calls = []
    def spy(fun, start, **kwargs):
        calls.append((start.copy(), kwargs))
        return original(fun, start, **kwargs)
    monkeypatch.setattr(targets, 'least_squares', spy)
    flow.run_case(source(), 'colour_only')
    assert len(calls) == 1
    start, options = calls[0]
    np.testing.assert_array_equal(start, [1, 1, 1])
    np.testing.assert_array_equal(options.pop('bounds'), [[.25] * 3, [4.] * 3])
    assert options == dict(method='trf', loss='linear', ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=500)


def test_direct_gamma_differs_from_reciprocal_and_rounding_ties():
    s = source()
    parameters = [.7, 1.1, .9]
    expected, _ = scalar.correction(s['reference'], s['alpha'], parameters, s['reference'])
    actual = targets.render_rgb8(s['reference'], s['alpha'], parameters)
    reciprocal = targets.render_rgb8(s['reference'], s['alpha'], [1/.7, 1.1, .9])
    np.testing.assert_array_equal(actual, expected)
    assert np.any(actual != reciprocal)
    image = np.array([[[1, 3, 5], [7, 9, 11]]], np.uint8)
    alpha = np.full((1, 2), .5)
    expected, _ = scalar.correction(image, alpha, [1, 2, 2], image)
    np.testing.assert_array_equal(targets.render_rgb8(image, alpha, [1, 2, 2]), expected)


@pytest.mark.parametrize('bad', ['nan', 'range', 'empty', 'protection', 'dtype', 'id', 'provenance'])
def test_invalid_support_rejected_before_fitting(bad):
    s = source()
    if bad == 'nan': s['alpha'][2, 2] = np.nan
    if bad == 'range': s['alpha'][2, 2] = 1.1
    if bad == 'empty': s['alpha'][:] = 0
    if bad == 'protection': s['alpha'][5, 5] = 1
    if bad == 'dtype': s['protected'] = s['protected'].astype(np.uint8)
    if bad == 'id': s['source_id'] = '../escape'
    if bad == 'provenance': s['generated_fixture'] = 'True'
    with pytest.raises(ValueError):
        flow.run_case(s, 'colour_only', fitter=lambda *a: pytest.fail('Must not fit'))


@pytest.mark.parametrize('bad', [[0, 1, 1], [5, 1, 1], [1, float('nan'), 1]])
def test_bad_controls_rejected_without_clamp_or_fallback(bad):
    with pytest.raises(ValueError):
        flow.run_case(source(), 'colour_only', fitter=lambda *a: dict(status='exact_neutral_target', parameters=bad))


def test_degenerate_input_unavailable_not_identity_substitution():
    s = source()
    s['reference'][:] = 100
    record, image, output = flow.run_case(s, 'colour_only')
    assert record['target']['status'] == 'unavailable_degenerate_input'
    assert output is None and record['regions']['primary']['output'] is None
    assert scalar.verify(s, record, image, output)


def test_explicit_unavailable_fit_preserved():
    result = {'status': 'unavailable_fit_or_identifiability', 'parameters': None}
    record, _, output = flow.run_case(source(), 'colour_only', fitter=lambda *a: result.copy())
    assert output is None and record['target'] == result


def test_corrupted_record_detected():
    s = source()
    record, image, output = flow.run_case(s, 'combined_under')
    record['clipping']['primary']['channels'] += 1
    with pytest.raises(AssertionError): scalar.verify(s, record, image, output)


def test_zero_core_or_feather_regions_are_null():
    s = source()
    s['alpha'][s['alpha'] > 0] = .5
    record, image, output = flow.run_case(s, 'exposure_over')
    assert record['regions']['core']['input'] is None
    assert scalar.verify(s, record, image, output)


def test_persistence_failure_preserved_and_overwrite_refused(tmp_path):
    dest = tmp_path / 'failed'
    def fail(*args): raise RuntimeError('injected failure')
    with pytest.raises(RuntimeError): flow.execute_sources([source()], dest, fitter=fail)
    assert json.loads((dest/'status.json').read_text())['completed_cases'] == 1
    assert json.loads((dest/'status.json').read_text())['status'] == 'failed_preserved'
    assert (dest/'generated_00/identity.npz').exists()
    with pytest.raises(FileExistsError): flow.execute_sources([source()], dest)


def test_all_supports_checked_before_output_or_fits(tmp_path):
    a, b = source(), source(1)
    b['alpha'][5, 5] = 1
    with pytest.raises(ValueError): flow.execute_sources([a, b], tmp_path/'invalid')
    assert not (tmp_path/'invalid').exists()


def test_non_generated_provenance_never_forged():
    s = source()
    s['generated_fixture'] = False
    record, _, _ = flow.run_case(s, 'identity')
    assert record['generated_fixture'] is False


def test_duplicate_sources_rejected(tmp_path):
    with pytest.raises(ValueError): flow.execute_sources([source(), source()], tmp_path/'duplicate')


def test_unavailable_counts_not_removed_from_attempt_denominator():
    s = source()
    records = []
    for role in flow.ROLES:
        records.append(flow.run_case(s, role, fitter=lambda *a: dict(status='unavailable_probe', parameters=None))[0])
    summary = flow.summarize(records)
    assert summary['colour_only']['attempted'] == 1
    assert summary['colour_only']['available'] == 0
    assert summary['colour_only']['primary']['output']['RGB'] is None


def bound_generated_plan(root):
    refs, supports = [], []
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    for index in range(11):
        s = source(index)
        folder = root/'outputs'/s['source_id']
        folder.mkdir(parents=True)
        np.savez(folder/'identity.npz', input_rgb8=s['reference'], forbidden=np.array([object()], dtype=object))
        np.save(folder/'alpha.npy', s['alpha'])
        assert cv2.imwrite(str(folder/'protected_mask.png'), s['protected'].astype(np.uint8)*255)
        (folder/'receipt.json').write_text('{}')
        refs.append(dict(source_id=s['source_id'], identity_container=str(folder/'identity.npz'),
            identity_sha256=sha(folder/'identity.npz'), allowed_key='input_rgb8', official_tone_label=None))
        supports.append(dict(source_id=s['source_id'], selected=dict(directory=str(folder),
            receipt='receipt.json', receipt_sha256=sha(folder/'receipt.json'), alpha_filename='alpha.npy',
            files={n:sha(folder/n) for n in ['alpha.npy','protected_mask.png']})))
    return dict(source_references=refs, support_sources=supports)


def test_bound_loader_only_allowed_key_and_provenance(tmp_path):
    plan = bound_generated_plan(tmp_path)
    loaded = load_sources(tmp_path, plan, generated_fixture=True)
    assert len(loaded) == 11 and all(s['generated_fixture'] is True for s in loaded)
    np.testing.assert_array_equal(loaded[0]['reference'], source()['reference'])


@pytest.mark.parametrize('corrupt', ['last_container','last_support','receipt','key','tone','escape'])
def test_loading_barrier_before_any_array_decode(tmp_path, monkeypatch, corrupt):
    plan = bound_generated_plan(tmp_path)
    if corrupt == 'last_container': plan['source_references'][-1]['identity_sha256'] = '0'*64
    if corrupt == 'last_support': plan['support_sources'][-1]['selected']['files']['alpha.npy'] = '0'*64
    if corrupt == 'receipt': plan['support_sources'][-1]['selected']['receipt_sha256'] = '0'*64
    if corrupt == 'key': plan['source_references'][-1]['allowed_key'] = 'forbidden'
    if corrupt == 'tone': plan['source_references'][-1]['official_tone_label'] = 8
    if corrupt == 'escape': plan['source_references'][-1]['identity_container'] = str(tmp_path.parent/'escape.npz')
    monkeypatch.setattr(np, 'load', lambda *a, **k: pytest.fail('Hash/schema barrier must precede decoding'))
    with pytest.raises(ValueError): load_sources(tmp_path, plan, generated_fixture=True)


def test_loader_requires_exact_joined_roster(tmp_path):
    plan = bound_generated_plan(tmp_path)
    plan['support_sources'].pop()
    with pytest.raises(ValueError): load_sources(tmp_path, plan, generated_fixture=True)
