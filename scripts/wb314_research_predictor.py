"""Frozen research inference on normalized RGB plus explicit measurement/application masks.

No training, photo loading, resizing, mask inference, default app integration or
external RGB correction. The development MST feature remains unvalidated.
"""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.model_training.blue_axis_preparation import features281
from src.model_training.luminance_chroma_operator import parameters, render_rgb8
from wb_cue_equivalent_ties import load_model, extract

MODEL_SHA256 = '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'
MAPPING_SHA256 = '6863575e284a6495e71e7445c88445d4215300db95f2b9111a43cd2191fe6be3'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def validate_inputs(rgb, measurement, alpha, protected):
    if not isinstance(rgb, np.ndarray) or rgb.dtype != np.uint8 or rgb.shape != (256, 256, 3):
        raise ValueError('Normalized256 RGB8 required; no implicit resizing or channel conversion')
    if (not isinstance(measurement, np.ndarray) or measurement.dtype != np.uint8
            or measurement.shape != (256, 256) or not np.isin(measurement, [0, 255]).all()
            or np.count_nonzero(measurement) < 1000):
        raise ValueError('Separate binary measurement mask with at least1000 pixels required')
    if (not isinstance(alpha, np.ndarray) or alpha.shape != (256, 256)
            or not np.issubdtype(alpha.dtype, np.floating) or not np.isfinite(alpha).all()
            or (alpha < 0).any() or (alpha > 1).any() or not (alpha > 0).any()):
        raise ValueError('Finite nonempty application alpha in[0,1] required')
    if (not isinstance(protected, np.ndarray) or protected.dtype != bool
            or protected.shape != (256, 256) or np.any(alpha[protected] != 0)):
        raise ValueError('Explicit boolean protection with zero application alpha required')


class FrozenWB314:
    """One reviewed tree; caller must supply compatible, separately qualified masks."""

    def __init__(self):
        folder = ROOT / 'outputs/wb314_final_training_v1'
        if sha(folder / 'model.json') != MODEL_SHA256:
            raise ValueError('Frozen predictor hash mismatch')
        self.model = read(folder / 'model.json')
        if (self.model['generated_fixture'] is not False or self.model['dimensions'] != 314
                or self.model['comparison'] != '<='):
            raise ValueError('Actual frozen314 predictor required')
        plan = read(folder / 'plan.json')
        self.names = plan['feature_names']
        parent = read(folder / 'bindings.json')
        schema = ROOT / 'outputs/wb_feature_direct_prediction_v1/feature_schema.json'
        if sha(schema) != parent[schema.relative_to(ROOT).as_posix()]:
            raise ValueError('Frozen feature schema hash mismatch')
        if self.names != read(schema)['314'] or len(self.names) != 314:
            raise ValueError('Frozen314 feature ordering required')
        mapping = ROOT / 'outputs/shared_core_mst_features_v1/mapping_PRIVATE.json'
        if sha(mapping) != MAPPING_SHA256:
            raise ValueError('Frozen development mapping hash mismatch')
        self.mapping = read(mapping)
        # Original pinned adapter validates source and every local WB asset hash.
        self.wb, self.normalize, _ = load_model()

    def predict_features(self, features):
        x = np.asarray(features)
        if x.shape != (314,) or x.dtype.kind not in 'fiu' or not np.isfinite(x).all():
            raise ValueError('Finite314 feature vector required')
        x = x.astype(np.float32)
        if not np.isfinite(x).all():
            raise ValueError('Float32 feature overflow')
        index, depth = 0, 0
        while True:
            node = self.model['nodes'][index]
            if node['kind'] == 'leaf':
                return parameters(node['values']).tolist(), index
            if node['kind'] != 'split' or depth >= 4:
                raise ValueError('Invalid frozen tree structure')
            # Python float preserves the binary64 threshold under NumPy2 promotion.
            index = node['left'] if float(x[node['feature']]) <= node['threshold'] else node['right']
            depth += 1

    def correct(self, rgb, measurement, alpha, protected):
        validate_inputs(rgb, measurement, alpha, protected)  # Before WB or rendering.
        first, details = features281(rgb, measurement, self.mapping, self.names[:281])
        coefficients, _, _, _ = extract(self.wb, self.normalize, rgb)
        features = np.asarray(first + coefficients.tolist(), np.float32).astype(float).tolist()
        controls, leaf = self.predict_features(features)
        output = render_rgb8(rgb, alpha, protected, controls)
        if (not np.array_equal(output[protected], rgb[protected])
                or not np.array_equal(output[alpha == 0], rgb[alpha == 0])):
            raise RuntimeError('Application preservation failed')
        return dict(output=output, features=features, controls=controls, leaf=leaf,
                    feature_details=details, model_sha256=MODEL_SHA256,
                    qualification_complete=False, masking_supplied_by_caller=True,
                    mst_mapping_validated=False)
