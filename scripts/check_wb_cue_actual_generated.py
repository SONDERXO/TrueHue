"""Actual frozen model; exclusively generated rasters; no correction rendering."""
import json
import math
import numpy as np
from wb_cue_adapter import ROOT, ASSETS, SOURCE, sha, load_model, extract


def main():
    dest = ROOT / 'outputs/wb_cue_actual_generated_v1'
    if dest.exists():
        raise RuntimeError('Refuse overwrite')
    dest.mkdir()
    records = []
    try:
        model, normalize, receipt = load_model()
        yy, xx = np.indices((256, 256))
        base = np.stack(((xx + 2 * yy) % 256, (3 * xx + yy) % 256, (xx + 5 * yy) % 256), axis=2).astype(np.uint8)
        s = base.astype(float) / 255
        linear = np.where(s <= .04045, s / 12.92, ((s + .055) / 1.055) ** 2.4)
        roles = [('identity', 0, False), ('colour', 0, True), ('under', -.5, False),
                 ('over', .5, False), ('combined_under', -.5, True), ('combined_over', .5, True)]
        first = None
        for role, ev, cast in roles:
            z = np.clip(linear * 2 ** ev * (np.array([.85, 1, 1.15]) if cast else 1), 0, 1)
            encoded = np.where(z <= .0031308, 12.92 * z, 1.055 * z ** (1 / 2.4) - .055)
            rgb = np.rint(encoded * 255).astype(np.uint8)
            before = rgb.copy()
            coeff, query, distances, indices = extract(model, normalize, rgb)
            official = model.correctImage(rgb[..., ::-1]).reshape(-1, order='F')
            assert np.array_equal(coeff, official), role
            assert np.array_equal(rgb, before)
            if role == 'identity':
                first = coeff.copy()
                assert np.array_equal(first, extract(model, normalize, rgb)[0])
            direct = np.sum((model.features.astype(float) - query) ** 2, axis=1)
            u = np.finfo(np.float32).eps / 2
            bound = (110 * u / (1 - 110 * u)) * np.sum(model.features.astype(float) ** 2, axis=1) + 1e-10
            assert np.all(np.abs(distances[:, 0] - direct) <= bound)
            selected = indices[:, 0].tolist()
            w = [math.exp(-float(distances[i, 0]) / (2 * .25 ** 2)) for i in selected]
            expected = [math.fsum(weight * float(model.mappingFuncs[i, j]) for weight, i in zip(w, selected)) / math.fsum(w) for j in range(33)]
            error = float(np.max(np.abs(coeff - expected)))
            assert error < 1e-10, (role, error)
            records.append({'role': role, 'status': 'PASS', 'scalar_coefficient_error': error,
                            'direct_double_top25_equal': set(selected) == set(np.argsort(direct)[:25].tolist()),
                            'max_distance_error': float(np.max(np.abs(distances[:, 0] - direct)))})
            np.savez(dest / (role + '.npz'), coefficients=coeff, query=query, distances=distances, input_rgb8=rgb)
        for name, image in [('black', np.zeros_like(base)), ('constant', np.full_like(base, 100)),
                            ('red_only', np.stack((base[:, :, 0], np.zeros((256, 256), dtype=np.uint8), np.zeros((256, 256), dtype=np.uint8)), axis=2))]:
            try:
                extract(model, normalize, image)
            except ValueError as exc:
                assert str(exc) == 'UNAVAILABLE_NONFINITE_HISTOGRAM'
                records.append({'role': name, 'status': str(exc)})
            else:
                raise AssertionError(name + ' was accepted')
        for asset in receipt['assets']:
            assert sha(ASSETS / asset['name']) == asset['sha256']
        result = {'status': 'ACTUAL_ASSET_GENERATED_PASS', 'records': records,
                  'source_sha256': sha(SOURCE), 'portrait_reads': 0, 'fits': 0, 'external_correction_renders': 0}
        (dest / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    except Exception as exc:
        (dest / 'failure.json').write_text(json.dumps({'error': str(exc), 'records': records}, indent=2), encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
