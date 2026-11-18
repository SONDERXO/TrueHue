"""Generated adapter checks, then fixed132probe vectors; never fits a model."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
import sys, json, math, hashlib, argparse, platform, importlib.metadata
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.synthetic_exposure_probe import measure
from src.model_training.synthetic_exposure_ranking import SCHEMA, score
from src.model_training.reiqa_frozen_features import FrozenQualityEncoder, generated_inputs, sha
from synthetic_exposure_ranking_checks import scalar_score, close

QA = ROOT / 'outputs/synthetic_exposure_probe_engineering_v2'
OUT = ROOT / 'outputs/synthetic_exposure_probe_v2'
RANK = ROOT / 'outputs/synthetic_exposure_ranking_prediction_v1'
FILES = ['scripts/synthetic_exposure_probe_workflow.py',
         'src/model_training/synthetic_exposure_probe.py',
         'src/model_training/synthetic_exposure_ranking.py',
         'src/model_training/portrait_exposure_quality.py',
         'src/model_training/reiqa_frozen_features.py',
         'scripts/synthetic_exposure_ranking_checks.py',
         'docs/synthetic-probe-correction-protocol-2026-11-17.md']


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))


def write(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')


def lut(ev):
    values = []
    for code in range(256):
        x = code / 255
        linear = x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4
        linear = min(1., linear * 2 ** ev)
        encoded = linear * 12.92 if linear <= .0031308 else 1.055 * linear ** (1 / 2.4) - .055
        values.append(round(max(0., min(1., encoded)) * 255))
    return np.asarray(values, dtype=np.uint8)


def bindings(): return {p: sha(ROOT / p) for p in FILES}


def check(bound):
    for p, h in bound.items():
        path = (ROOT / p).resolve(); path.relative_to(ROOT)
        assert sha(path) == h, p


def generated():
    if QA.exists(): raise FileExistsError(QA)
    rng = np.random.default_rng(42)
    head = dict(schema=SCHEMA, generated_fixture=True, bias=0., weights=rng.normal(0, .01, 4096).tolist(),
                mean=[0.] * 4096, scale=[1.] * 4096)
    rgb = np.stack([np.tile(np.arange(256, dtype=np.uint8), (256, 1)),
                    np.tile(np.arange(256, dtype=np.uint8)[:, None], (1, 256)),
                    np.full((256, 256), 127, dtype=np.uint8)], axis=-1)
    class FakeEncoder:
        def __init__(self): self.calls = 0
        def encode(self, image):
            self.calls += 1
            return np.resize(image.mean(axis=(0, 1)) / 255, 4096).astype(np.float32)
    enc = FakeEncoder(); base = enc.encode(rgb); original = rgb.copy(); saved_base = base.copy()
    assert np.array_equal(base, base.reshape(1, 4096).reshape(-1))
    a = measure(head, enc, rgb, base); b = measure(head, enc, rgb, base)
    assert a['scores'] == b['scores'] and a['cues'] == b['cues']
    for name, ev in [('minus', -.5), ('plus', .5)]:
        assert np.array_equal(a['shifted'][name], lut(ev)[rgb])
        assert np.array_equal(a['vectors'][name], b['vectors'][name])
        close(a['scores'][name], scalar_score(head, a['vectors'][name]))
    close(a['scores']['base'], scalar_score(head, base))
    assert np.array_equal(rgb, original) and np.array_equal(base, saved_base)
    before = enc.calls
    for bad_rgb, bad_base, bad_head in [(rgb[:2], base, head), (rgb.astype(float), base, head),
             (rgb, base[:-1], head), (rgb, np.full(4096, np.nan, np.float32), head),
             (rgb, base, head | {'schema': 'PIQ_mock_not_this_schema'})]:
        try: measure(bad_head, enc, bad_rgb, bad_base)
        except ValueError: pass
        else: raise AssertionError('Invalid input accepted')
    assert enc.calls == before
    QA.mkdir()
    write(QA / 'verification.json', dict(passed=True, generated_fixture=True,
          generated_encoder_calls=enc.calls, real_encoder_calls=0, model_fits=0,
          scalar_lookup_codes=512, input_immutable=True, repeat='EXACT',
          invalid_before_encoder=True, mock_head_never_actual=True, code_sha256=bindings()))
    print('PASS generated probe adapter/scalar512codes/full4096score/repeat/invalid-before-call; zero fits.', flush=True)


def extract():
    if OUT.exists(): raise FileExistsError(OUT)
    qa = read(QA / 'verification.json'); assert qa['passed']; check(qa['code_sha256'])
    rank = read(RANK / 'verification.json'); independent = read(RANK / 'independent_assessment_verification.json')
    assert rank['passed'] and independent['passed'] and rank['real_head_fits'] == 11
    for p, h in rank['artifact_sha256'].items(): assert sha(RANK / p) == h
    heads = {s: read(RANK / s / 'head.json') for s in sorted(independent_sources())}
    for s, h in heads.items():
        assert h['generated_fixture'] is False and h['held_source'] == s and s not in h['training_sources']
    plan_path = ROOT / 'outputs/camera_halfstop_data_v1/plan_PRIVATE.json'
    plan = read(plan_path)
    records = [{k: r[k] for k in ('case_id', 'source_id', 'role', 'input_pack', 'input_pack_sha256')}
               for r in plan['rows']]
    assert len(records) == 66 and len({r['case_id'] for r in records}) == 66
    bound = dict(qa['code_sha256'])
    for p in [QA / 'verification.json', RANK / 'verification.json',
              RANK / 'independent_assessment_verification.json', RANK / 'held_scores_sealed.json',
              plan_path, ROOT / 'outputs/camera_halfstop_neural_v1/features.npz',
              ROOT / 'outputs/piq23_training_engineering_v1/verification.json',
              ROOT / 'outputs/reiqa_frozen_generated_v1/generated_features.npz',
              ROOT / 'outputs/reiqa_checkpoint_pilot_v1/quality_aware_r50.pth']:
        bound[p.relative_to(ROOT).as_posix()] = sha(p)
    for s in heads:
        p = RANK / s / 'head.json'; bound[p.relative_to(ROOT).as_posix()] = sha(p)
    for r in records:
        p = (ROOT / r['input_pack']).resolve()
        p.relative_to((ROOT / 'outputs/camera_halfstop_data_v1/cases').resolve())
        assert sha(p) == r['input_pack_sha256']
        bound[p.relative_to(ROOT).as_posix()] = r['input_pack_sha256']
    check(bound)  # All66container hashes BEFORE any actual array decode.
    actual_versions = dict(Python=platform.python_version(), **{p: importlib.metadata.version(p)
                           for p in ['numpy', 'Pillow', 'torch', 'torchvision']})
    assert actual_versions == read(ROOT / 'outputs/piq23_training_engineering_v1/verification.json')['versions']
    OUT.mkdir(); write(OUT / 'execution_bindings.json', dict(sha256=bound, versions=actual_versions,
                          actual_input_arrays_decoded=0, maximum_probe_encoder_calls=132))
    encoder = FrozenQualityEncoder(ROOT)
    # One generated contract replay, not a repeated integration campaign.
    with np.load(ROOT / 'outputs/reiqa_frozen_generated_v1/generated_features.npz', allow_pickle=False) as pack:
        assert np.array_equal(encoder.encode(generated_inputs()[0][1]), pack['identity'].reshape(-1))
    scalar_luts = {'minus': lut(-.5), 'plus': lut(.5)}
    base_path = ROOT / 'outputs/camera_halfstop_neural_v1/features.npz'
    prior_scores = {r['case_id']: r['score'] for r in read(RANK / 'held_scores_sealed.json')}
    vectors = {}; cues = []; access = []; calls = 0; identity_exact = 0; max_scalar_error = 0.
    try:
        with np.load(base_path, allow_pickle=False) as bases:
            for r in records:
                case = r['case_id']; head = heads[r['source_id']]
                assert r['source_id'] not in head['training_sources'] and case not in head['training_ids']
                with np.load(ROOT / r['input_pack'], allow_pickle=False) as pack:
                    rgb = pack['input'].copy()  # NO other key is decoded.
                access.append(dict(case_id=case, path=r['input_pack'], keys=['input']))
                original_sha = hashlib.sha256(rgb.tobytes()).hexdigest()
                base = bases[case]
                measured = measure(head, encoder, rgb, base); calls += 2
                assert hashlib.sha256(rgb.tobytes()).hexdigest() == original_sha
                close(measured['scores']['base'], prior_scores[case])
                for name in ('minus', 'plus'):
                    shifted = measured['shifted'][name]; vector = measured['vectors'][name]
                    assert np.array_equal(shifted, scalar_luts[name][rgb])
                    q_scalar = scalar_score(head, vector)
                    close(q_scalar, measured['scores'][name])
                    max_scalar_error = max(max_scalar_error, abs(q_scalar - measured['scores'][name]))
                    vectors[case + '__' + name] = vector
                    if r['role'] == 'identity':
                        role = 'exposure_under' if name == 'minus' else 'exposure_over'
                        other = next(a['case_id'] for a in records if a['source_id'] == r['source_id'] and a['role'] == role)
                        assert np.array_equal(vector, bases[other])
                        identity_exact += 1
                values = measured['scores']; best = max(values.values())
                expected = 'base' if r['role'] in ('identity', 'colour_only') else 'plus' if r['role'].endswith('under') else 'minus'
                cues.append({k: r[k] for k in ('case_id', 'source_id', 'role')} | dict(
                    scores=values, cues=measured['cues'], expected_option=expected,
                    preferred_options=[k for k, v in values.items() if v == best],
                    expected_strictly_best=all(values[expected] > v for k, v in values.items() if k != expected),
                    head_sha256=sha(RANK / r['source_id'] / 'head.json'), input_rgb_sha256=original_sha))
                if len(cues) % 11 == 0: print('Probe vectors verified ' + str(len(cues)) + '/66 cases.', flush=True)
        assert calls == 132 and identity_exact == 22
        encoder.verify_unchanged(); check(bound)
        np.savez_compressed(OUT / 'features.npz', **vectors)
        write(OUT / 'cues_sealed.json', cues)
        write(OUT / 'array_access.json', access)
        descriptive = {role: dict(cases=11, expected_option_strictly_best=sum(r['expected_strictly_best'] for r in cues if r['role'] == role),
                                 ties=sum(len(r['preferred_options']) > 1 for r in cues if r['role'] == role))
                       for role in sorted({r['role'] for r in cues})}
        write(OUT / 'verification.json', dict(passed=True, actual_inputs=66, new_probe_vectors=132,
              actual_probe_encoder_calls=132, generated_contract_encoder_calls=1, real_model_fits=0,
              scalar_probe_array_checks=132, scalar_lookup_codes=512, scalar_score_max_error=max_scalar_error,
              input_immutable=True, encoder_unchanged=True, identity_probe_vectors_exact_prior=22,
              head_source_exclusion=True, reference_or_support_decodes=0, correction_renders=0,
              features_sha256=sha(OUT / 'features.npz'), cues_sha256=sha(OUT / 'cues_sealed.json'),
              descriptive_by_role=descriptive, diagnostic_is_not_feature_usefulness_gate=True,
              versions=actual_versions, model_ready=False))
        print(json.dumps(descriptive, indent=2), flush=True)
    except Exception as exc:
        write(OUT / 'failure.json', dict(error=repr(exc), completed_cases=len(cues),
                                       completed_probe_encoder_calls=calls, fits=0))
        write(OUT / 'partial_access.json', access)
        raise


def independent_sources():
    return {r['source_id'] for r in read(ROOT / 'outputs/synthetic_exposure_ranking_admission_v1/roster.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=['generated', 'extract'])
    {'generated': generated, 'extract': extract}[parser.parse_args().stage]()
