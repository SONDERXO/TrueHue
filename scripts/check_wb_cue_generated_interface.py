"""Generated interface verification; no model assets or portraits loaded."""
import ast
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
import numpy.matlib


def main():
    root = Path(__file__).resolve().parents[1]
    dest = root / 'outputs/wb_cue_generated_interface_v1'
    if dest.exists():
        raise RuntimeError('Refuse overwrite')
    source = root / 'outputs/wb_cue_feasibility_v1/WBsRGB.py.txt'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    # Keep official equations; never run constructor (which loads real assets).
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name in {'encode', 'rgb_uv_hist', 'correctImage'}]
    method = next(n for n in cls.body if n.name == 'correctImage')
    cut = next(i for i, n in enumerate(method.body)
               if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'I_corr' for t in n.targets))
    method.body = method.body[:cut] + [ast.Return(value=ast.Name(id='mf', ctx=ast.Load()))]
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'im2double')
    module = ast.fix_missing_locations(ast.Module(body=[cls, helper], type_ignores=[]))
    ns = {'np': np, 'cv2': cv2}
    exec(compile(module, str(source), 'exec'), ns)
    model = ns['WBsRGB'].__new__(ns['WBsRGB'])
    model.K, model.sigma, model.h = 25, .25, 60
    rng = np.random.default_rng(20261115)
    model.encoderBias = np.zeros((10800, 1))
    model.encoderWeights = rng.normal(0, .005, (10800, 4))
    model.features = rng.normal(0, .02, (30, 4))
    model.mappingFuncs = rng.normal(0, .1, (30, 33))
    def poison(*args):
        raise AssertionError('External image correction must never execute')
    model.colorCorrection = poison
    raster = rng.integers(15, 241, (24, 24, 3), dtype=np.uint8)
    raster[0, 0] = [0, 0, 0]
    raster[-1, -1] = [255, 255, 255]
    before = raster.copy()
    coefficients = model.correctImage(raster)
    repeated = model.correctImage(raster)
    assert coefficients.shape == (11, 3)
    assert np.isfinite(coefficients).all()
    assert np.array_equal(coefficients, repeated)
    assert np.array_equal(raster, before)
    normalized = ns['im2double'](raster[..., ::-1])
    scalar_norm = (raster[..., ::-1].astype(float) - float(raster.min())) / float(int(raster.max()) - int(raster.min()))
    assert np.max(np.abs(normalized - scalar_norm)) < 1e-14
    histogram = model.rgb_uv_hist(normalized)
    query = model.encode(histogram)
    # Independent scalar distance/selection/weighted coefficient reduction.
    distances = [sum((float(a) - float(b)) ** 2 for a, b in zip(row, query.reshape(-1)))
                 for row in model.features]
    selected = sorted(range(30), key=lambda i: (distances[i], i))[:25]
    weights = [math.exp(-distances[i] / (2 * .25 ** 2)) for i in selected]
    denom = sum(weights)
    expected = np.array([sum(w * float(model.mappingFuncs[i, j])
                            for w, i in zip(weights, selected)) / denom
                         for j in range(33)]).reshape(11, 3, order='F')
    error = float(np.max(np.abs(coefficients - expected)))
    assert error < 1e-10
    # Preserve source failure witness, then check the wrapper's fail-closed policy.
    with np.errstate(divide='ignore', invalid='ignore'):
        black_hist = model.rgb_uv_hist(np.zeros((24, 24, 3)))
    assert not np.isfinite(black_hist).all()
    def validate_histogram(hist):
        if not np.isfinite(hist).all():
            raise ValueError('UNAVAILABLE_NONFINITE_HISTOGRAM')
        return hist
    validate_histogram(histogram)
    try:
        validate_histogram(black_hist)
    except ValueError as exc:
        black_status = str(exc)
    else:
        raise AssertionError('Invalid histogram was accepted')
    dest.mkdir()
    record = {'status': 'GENERATED_INTERFACE_PASS', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'scalar_coefficient_max_error': error, 'repeat_exact': True, 'input_unchanged': True,
              'external_pixel_correction_calls': 0, 'black_status': black_status,
              'actual_model_asset_loads': 0, 'portrait_reads': 0, 'fits': 0,
              'limitations': 'Mock arrays; not real model or portrait inference; histogram/PCA use official source, not independent scalar verification.'}
    (dest / 'verification.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
