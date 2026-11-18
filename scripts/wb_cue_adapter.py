"""Research-only mapping features. Derived from Afifi et al. CVPR2019.

CC BY-NC-SA4; original copyright/license retained under wb_cue_feasibility_v1.
Own guard/interface changes; never applies the external colour mapping.
"""
import ast
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
import numpy.matlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'outputs/wb_cue_feasibility_v1/WBsRGB.py.txt'
ASSETS = ROOT / 'outputs/wb_cue_base_assets_v2'
SOURCE_HASH = 'b4f9c12bc3f8e2e55725c2f5e6952421dd78962ab69e1da32b5d4920307b5bf1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model():
    assert sha(SOURCE) == SOURCE_HASH
    receipt = json.loads((ASSETS / 'receipt.json').read_text(encoding='utf-8'))
    for record in receipt['assets']:
        assert sha(ASSETS / record['name']) == record['sha256']
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                and n.name in {'encode', 'rgb_uv_hist', 'correctImage'}]
    method = next(n for n in cls.body if n.name == 'correctImage')
    cut = next(i for i, n in enumerate(method.body) if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'I_corr' for t in n.targets))
    method.body = method.body[:cut] + [ast.Return(ast.Name(id='mf', ctx=ast.Load()))]
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'im2double')
    module = ast.fix_missing_locations(ast.Module(body=[cls, helper], type_ignores=[]))
    ns = {'np': np, 'cv2': cv2}
    exec(compile(module, str(SOURCE), 'exec'), ns)
    model = ns['WBsRGB'].__new__(ns['WBsRGB'])
    for field, file in [('features', 'features.npy'), ('mappingFuncs', 'mappingFuncs.npy'),
                        ('encoderWeights', 'encoderWeights.npy'), ('encoderBias', 'encoderBias.npy')]:
        array = np.load(ASSETS / file, allow_pickle=False)
        assert np.isfinite(array).all()
        array.flags.writeable = False
        setattr(model, field, array)
    model.K, model.sigma, model.h = 25, .25, 60
    def poison(*args):
        raise AssertionError('Forbidden external pixel correction')
    model.colorCorrection = poison
    return model, ns['im2double'], receipt


def extract(model, normalize, rgb):
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError('INVALID_RGB8')
    image = normalize(rgb)
    with np.errstate(divide='ignore', invalid='ignore'):
        hist = model.rgb_uv_hist(image)
    if not np.isfinite(hist).all():
        raise ValueError('UNAVAILABLE_NONFINITE_HISTOGRAM')
    query = model.encode(hist)
    if not np.isfinite(query).all():
        raise ValueError('UNAVAILABLE_QUERY')
    distance = np.einsum('ij,ij->i', model.features, model.features)[:, None] + np.einsum('ij,ij->i', query, query) - 2 * model.features.dot(query.T)
    if not np.isfinite(distance).all() or (distance < 0).any():
        raise ValueError('UNAVAILABLE_DISTANCE')
    sorted_distance = np.sort(distance[:, 0])
    if sorted_distance[model.K - 1] == sorted_distance[model.K]:
        raise ValueError('UNAVAILABLE_BOUNDARY_TIE')
    indices = distance.argpartition(model.K, axis=0)[:model.K]
    selected = np.sqrt(np.take_along_axis(distance, indices, axis=0))
    weights = np.exp(-np.power(selected, 2) / (2 * model.sigma ** 2))
    if not np.isfinite(weights).all() or float(sum(weights)[0]) <= 0:
        raise ValueError('UNAVAILABLE_WEIGHTS')
    weights = weights / sum(weights)
    coefficients = sum(np.matlib.repmat(weights, 1, 33) * np.squeeze(model.mappingFuncs[indices, :]), 0)
    if not np.isfinite(coefficients).all():
        raise ValueError('UNAVAILABLE_COEFFICIENTS')
    return coefficients, query, distance, indices
