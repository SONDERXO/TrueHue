"""Generated integration fixtures only: no trained assets or photo studies."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_wb314_photo as runner


def fixture(tmp_path, monkeypatch):
    # Asymmetric colours expose BGR/RGB mistakes; non-square size exposes resize drift.
    image = np.zeros((300, 420, 3), np.uint8)
    image[:, :, 0] = 30; image[:, :, 1] = 70; image[:, :, 2] = 120
    image[::3, ::2, :] = [45, 85, 135]
    source = tmp_path / 'input.png'; runner.save_png(source, image)
    rgb = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)[:, :, ::-1].copy()
    measurement = np.zeros((256, 256), np.uint8); measurement[40:120, 40:120] = 255
    alpha = np.zeros((256, 256), float); alpha[30:180, 30:180] = 1
    protected = np.zeros((256, 256), bool); protected[70:80, 70:80] = True; alpha[protected] = 0
    seen = dict(constructs=0, calls=0)
    def masks(normalized, folder, glasses):
        np.testing.assert_array_equal(normalized, rgb[:, :, ::-1])
        seen['glasses'] = glasses
        return measurement, alpha, protected, dict(geometry_origin='generated_fixture')
    monkeypatch.setattr(runner, 'prepare_masks', masks)
    class Predictor:
        def __init__(self): seen['constructs'] += 1
        def correct(self, actual, m, a, p):
            seen['calls'] += 1
            np.testing.assert_array_equal(actual, rgb)
            assert m is measurement and a is alpha and p is protected
            primary = actual.copy(); primary[a > 0] += 5
            alternate = actual.copy(); alternate[a > 0] += 2
            result = dict(output=primary, headroom_candidate=alternate, controls=[1., 1.1, 1., 1., 1.],
                features=[0.] * 314, leaf=4, model_sha256=runner.MODEL_SHA256,
                headroom_candidate_controls=[1., 1.05, 1., 1., 1.],
                headroom_advisory=dict(available=True, applied_to_primary=False),
                headroom_applied_to_primary=False)
            seen['result'] = result
            return result
    monkeypatch.setattr(runner, 'WB314WithHeadroomAdvisory', Predictor)
    return source, rgb, measurement, alpha, protected, seen


def test_generated_file_to_masks_to_primary_export_preserves_channels_and_policy(tmp_path, monkeypatch):
    source, rgb, m, a, p, seen = fixture(tmp_path, monkeypatch)
    output = tmp_path / 'result'
    report = runner.run_photo(source, output, glasses='opaque')
    actual = cv2.imread(str(output / 'primary_correction.png'))[:, :, ::-1]
    candidate = cv2.imread(str(output / 'separate_headroom_candidate.png'))[:, :, ::-1]
    np.testing.assert_array_equal(actual, seen['result']['output'])
    np.testing.assert_array_equal(candidate, seen['result']['headroom_candidate'])
    assert not np.array_equal(actual, candidate)
    np.testing.assert_array_equal(actual[p | (a == 0)], rgb[p | (a == 0)])
    assert seen['constructs'] == seen['calls'] == 1 and seen['glasses'] == 'opaque'
    assert report['headroom_applied_to_primary'] is report['qualification_complete'] is False
    assert report['fallback_to_legacy'] is False and report['status'] == 'research_output_ready'
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    assert all(runner.sha(output / name) == digest for name, digest in manifest['artifacts'].items())
    with pytest.raises(FileExistsError):
        runner.run_photo(source, output, glasses='opaque')
    assert seen['calls'] == 1


@pytest.mark.parametrize('failure', ['service', 'measurement', 'alpha', 'protection'])
def test_failed_masks_never_construct_predictor_or_export_correction(tmp_path, monkeypatch, failure):
    source, rgb, m, a, p, seen = fixture(tmp_path, monkeypatch)
    original = runner.prepare_masks
    def bad_masks(*args):
        if failure == 'service': raise ValueError('Mask service failed')
        if failure == 'measurement': m[:] = 0
        if failure == 'alpha': a[0, 0] = np.nan
        if failure == 'protection': a[p] = 1
        return original(*args)
    monkeypatch.setattr(runner, 'prepare_masks', bad_masks)
    output = tmp_path / 'result'
    with pytest.raises(ValueError): runner.run_photo(source, output, glasses='opaque')
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    assert report['status'] == 'failed' and report['failed_stage'] == 'masking'
    assert seen['constructs'] == seen['calls'] == report['correction_calls_attempted'] == 0
    assert not (output / 'primary_correction.png').exists()


def test_corrupt_photo_and_unknown_glasses_fail_without_model(tmp_path, monkeypatch):
    source, rgb, m, a, p, seen = fixture(tmp_path, monkeypatch)
    source.write_bytes(b'not a photo')
    with pytest.raises(ValueError): runner.run_photo(source, tmp_path / 'bad_photo', glasses='clear')
    with pytest.raises(ValueError): runner.run_photo(source, tmp_path / 'bad_choice', glasses='automatic')
    assert seen['constructs'] == 0 and not (tmp_path / 'bad_choice').exists()


def test_unavailable_advisory_keeps_primary_without_alternative_file(tmp_path, monkeypatch):
    source, rgb, m, a, p, seen = fixture(tmp_path, monkeypatch)
    original = runner.WB314WithHeadroomAdvisory
    class NoCandidate(original):
        def correct(self, *args):
            result = super().correct(*args)
            result.update(headroom_candidate=None, headroom_candidate_controls=None,
                          headroom_advisory=dict(available=False, not_a_safety_pass=True))
            return result
    monkeypatch.setattr(runner, 'WB314WithHeadroomAdvisory', NoCandidate)
    output = tmp_path / 'result'
    report = runner.run_photo(source, output, glasses='uncertain')
    assert report['separate_candidate_output'] is None and (output / 'primary_correction.png').exists()
    assert not (output / 'separate_headroom_candidate.png').exists()


@pytest.mark.parametrize('fault', ['pixels', 'mutation', 'policy', 'inference'])
def test_bad_prediction_cannot_export_valid_result(tmp_path, monkeypatch, fault):
    source, rgb, m, a, p, seen = fixture(tmp_path, monkeypatch)
    original = runner.WB314WithHeadroomAdvisory
    class BadPrediction(original):
        def correct(self, *args):
            if fault == 'inference': raise RuntimeError('Model unavailable')
            result = super().correct(*args)
            if fault == 'pixels': result['output'][p] = 0
            if fault == 'mutation': args[0][0, 0] = 0
            if fault == 'policy': result['headroom_applied_to_primary'] = True
            return result
    monkeypatch.setattr(runner, 'WB314WithHeadroomAdvisory', BadPrediction)
    output = tmp_path / 'result'
    with pytest.raises((ValueError, RuntimeError)):
        runner.run_photo(source, output, glasses='opaque')
    assert not (output / 'primary_correction.png').exists()
    assert json.loads((output / 'report.json').read_text(encoding='utf-8'))['status'] == 'failed'


@pytest.mark.parametrize('fault', ['none', 'uncertain', 'changed_pixels', 'failed_measurement'])
def test_native_mask_bridge_checks_preparation_before_correction(tmp_path, monkeypatch, fault):
    folder = tmp_path / 'masks'; folder.mkdir()
    image = np.full((256, 256, 3), 90, np.uint8)
    runner.save_png(folder / 'normalized_input.png', image)
    runner.save_png(folder / 'candidate_measurement_mask.png', np.full((256, 256), 255, np.uint8))
    preview = SimpleNamespace(alpha=np.ones((256, 256)), protected=np.zeros((256, 256), bool),
        report=dict(requires_glasses_choice=fault == 'uncertain'))
    prepared = image.copy()
    if fault == 'changed_pixels': prepared[0, 0] = 91
    helper = SimpleNamespace(dependencies=lambda: ({}, 'generated_contract'),
        prepare_photo=lambda *args: (prepared, None, None, None, None, {}),
        read=lambda path: dict(status='failed' if fault == 'failed_measurement' else 'success'))
    monkeypatch.setattr(runner, 'import_module', lambda name: helper)
    monkeypatch.setattr(runner, 'render_preview', lambda *args, **kwargs: preview)
    if fault == 'none':
        measurement, alpha, protected, metadata = runner.prepare_masks(image, folder, 'opaque')
        np.testing.assert_array_equal(measurement, np.full((256, 256), 255, np.uint8))
        assert alpha is preview.alpha and protected is preview.protected
        assert metadata['mask_contract_sha256'] == 'generated_contract'
        assert metadata['geometry_origin'] == 'computed_on_this_normalized_input'
    else:
        with pytest.raises(ValueError): runner.prepare_masks(image, folder, 'uncertain')
