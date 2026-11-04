"""Generated-array supervision diagnostic; no photographs or model training."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.correction.seamless_blend import inward_alpha, apply_blended
from src.model_training.blended_recovery_targets import fit_target, render_rgb8

OUT = ROOT / 'outputs/blended_recovery_target_check_v1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    rng = np.random.default_rng(401)
    reference = rng.integers(20, 236, (48, 48, 3), dtype=np.uint8)
    mask = np.zeros((48, 48), np.uint8)
    mask[4:44, 4:44] = 255
    alpha, _ = inward_alpha(mask, face_width=80)
    scoring = alpha > 0
    parameters = [1.4, .85, 1.05]
    distorted = render_rgb8(reference, alpha, parameters)
    # Deliberately outside the three-control family, not a Table2 policy choice.
    x = reference.astype(float)/255
    composite_float = np.clip((x**.7-.5)*1.4+.5+.08, 0, 1)
    composite = np.rint(255*(x*(1-alpha[..., None])+
                             composite_float*alpha[..., None])).astype(np.uint8)
    cases = [('clean', reference.copy()), ('blended_three_control', distorted),
             ('composite_with_clipping', composite)]
    sources = ['src/model_training/blended_recovery_targets.py',
               'src/distortion_generation/paper_gamma.py',
               'src/correction/seamless_blend.py',
               'scripts/401_check_blended_recovery_targets.py']
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
    rows = []
    saved = reference.copy()
    for name, image in cases:
        before = image.copy()
        result = fit_target(image, reference, alpha, scoring)
        assert result['parameters'] is not None
        output = render_rgb8(image, alpha, result['parameters'])
        replay, _, _ = apply_blended(image[..., ::-1].copy(), mask,
                                    result['parameters'], face_width=80)
        assert np.array_equal(output, replay[..., ::-1])
        assert fit_target(image, reference, alpha, scoring) == result
        assert np.array_equal(output[~scoring], image[~scoring])
        assert np.array_equal(before, image)
        edge = (alpha > 0) & (alpha < 1)
        result.update(case=name, outside_support_exact=True,
                      fractional_edge_mae_codes=float(np.abs(
                          output[edge].astype(float)-reference[edge]).mean()))
        if name == 'blended_three_control':
            inverse = [1/parameters[0], parameters[1]**(-1/parameters[0]),
                       parameters[2]**(-1/parameters[0])]
            old = render_rgb8(image, alpha, inverse)
            result['unblended_inverse_mae_codes'] = float(np.abs(
                old[scoring].astype(float)-reference[scoring]).mean())
        rows.append(result)
    assert np.array_equal(saved, reference)
    assert rows[0]['parameters'] == [1., 1., 1.]
    OUT.mkdir()
    payload = dict(source_sha256=hashes, seed=401, shape=list(reference.shape),
        scope='three generated arrays; local supervised target fits, not decision-tree training',
        input_convention='RGB8, direct exponent, clipped transformed RGB, supplied inward alpha, nearest rounding',
        scoring='all positive-alpha pixels, including fractional edges',
        composite_probe='clip((x**0.7-0.5)*1.4+0.5+0.08); then alpha blend; illustrative only, not adopted Table2',
        fits=2, repeat_fit_checks=2, clean_shortcuts=1, renderer_replays=3,
        photos=0, model_training=0,
        runtime_changes=0, dataset_admissions=0, results=rows)
    (OUT/'results.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    for path, digest in hashes.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest
    (OUT/'sha256.json').write_text(json.dumps({'results.json': hashlib.sha256(
        (OUT/'results.json').read_bytes()).hexdigest()}, indent=2), encoding='utf-8')
    print(json.dumps([{'case': r['case'], 'input_mae': r['input_rgb8_mae_codes'],
                       'output_mae': r['rgb8_mae_codes']} for r in rows], indent=2))


if __name__ == '__main__':
    main()
