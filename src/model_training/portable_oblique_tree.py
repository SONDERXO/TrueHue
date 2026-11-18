"""Separate, standard-library-only oblique control tree; not wired into the app."""
from copy import deepcopy
import math
from numbers import Real
import struct

SCHEMA = 'truehue_oblique_regression_tree_v1'
TARGETS = ['gamma', 'red_gain', 'blue_gain']


def finite(value):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError('Finite real numeric value required')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Nonfinite numeric value')
    return value


def float32(value):
    try:
        value = struct.unpack('!f', struct.pack('!f', finite(value)))[0]
    except (OverflowError, struct.error) as exc:
        raise ValueError('float32 overflow') from exc
    return finite(value)


def score(node, values):
    try:
        result = math.fsum([node['intercept']] +
                           [w*x for w, x in zip(node['weights'], values)])
    except (OverflowError, ValueError) as exc:
        raise ValueError('Nonfinite dot product') from exc
    return finite(result)


def payload(feature_names, nodes, provenance=None):
    return dict(schema_version=SCHEMA, input_dtype='float32',
        coefficient_dtype='float64', comparison='score>0:right;else:left',
        accumulation='math.fsum([intercept]+indexed_products)', root=0,
        feature_names=list(feature_names), target_names=TARGETS.copy(),
        nodes=deepcopy(nodes), provenance=deepcopy(provenance or {}))


class PortableObliqueTree:
    def __init__(self, model):
        expected = dict(schema_version=SCHEMA, input_dtype='float32',
            coefficient_dtype='float64', comparison='score>0:right;else:left',
            accumulation='math.fsum([intercept]+indexed_products)', root=0)
        if (not isinstance(model, dict) or type(model.get('root')) is not int or
            any(model.get(k) != v for k, v in expected.items())):
            raise ValueError('Unsupported oblique tree contract')
        names = model.get('feature_names')
        if (not isinstance(names, list) or not 1 <= len(names) <= 16 or
            any(not isinstance(n, str) or not n.strip() for n in names) or len(set(names)) != len(names)):
            raise ValueError('Unique nonempty feature names required')
        if model.get('target_names') != TARGETS:
            raise ValueError('Three positive control outputs required')
        nodes = deepcopy(model.get('nodes'))
        if not isinstance(nodes, list) or not 1 <= len(nodes) <= 31:
            raise ValueError('Invalid node count')
        pending, seen = [(0, 0)], set()
        while pending:
            i, depth = pending.pop()
            if type(i) is not int or not 0 <= i < len(nodes) or i in seen or depth > 4:
                raise ValueError('Invalid, shared, cyclic or too-deep node')
            seen.add(i);n = nodes[i]
            if not isinstance(n, dict):
                raise ValueError('Invalid node')
            if n.get('kind') == 'leaf':
                values = n.get('values')
                if not isinstance(values, list) or len(values) != 3:
                    raise ValueError('Control width mismatch')
                n['values'] = [finite(v) for v in values]
                if min(n['values']) <= 0:
                    raise ValueError('Positive controls required')
            elif n.get('kind') == 'split':
                weights = n.get('weights')
                if not isinstance(weights, list) or len(weights) != len(names):
                    raise ValueError('Weight width mismatch')
                n['weights'] = [finite(v) for v in weights]
                n['intercept'] = finite(n.get('intercept'))
                pending.extend([(n.get('left'), depth+1), (n.get('right'), depth+1)])
            else:
                raise ValueError('Unknown node kind')
        if len(seen) != len(nodes):
            raise ValueError('Unreachable nodes')
        self.feature_names = tuple(names)
        self._model = deepcopy(model);self._model['nodes'] = nodes

    def to_dict(self):
        return deepcopy(self._model)

    def leaf_id(self, features, start=0):
        if isinstance(features, dict):
            if set(features) != set(self.feature_names):
                raise ValueError('Named feature schema mismatch')
            features = [features[n] for n in self.feature_names]
        try:
            if len(features) != len(self.feature_names):
                raise ValueError('Feature width mismatch')
            x = [float32(v) for v in features]
        except TypeError as exc:
            raise ValueError('Feature vector required') from exc
        nodes = self._model['nodes']
        if type(start) is not int or not 0 <= start < len(nodes):
            raise ValueError('Invalid subtree root')
        i = start
        while nodes[i]['kind'] == 'split':
            n = nodes[i]
            i = n['right'] if score(n, x) > 0 else n['left']
        return i

    def predict_one(self, features, start=0):
        return list(self._model['nodes'][self.leaf_id(features, start)]['values'])

    def predict(self, rows):
        return [self.predict_one(row) for row in rows]


def from_axis_tree(axis):
    from src.model_training.portable_tree import PortableTree
    PortableTree(axis)  # Validate legacy topology before conversion; no refitting.
    if (axis.get('schema_version') != 'truehue_regression_tree_v1' or
        axis.get('input_dtype') != 'float32' or axis.get('comparison') != '<=' or
        axis.get('threshold_dtype') != 'float64' or axis.get('root') != 0 or
        axis.get('target_names') != TARGETS):
        raise ValueError('Compatible legacy axis schema required')
    nodes = []
    for n in axis['nodes']:
        if n['kind'] == 'leaf':
            nodes.append(dict(kind='leaf', values=list(n['values'])))
        else:
            j = n['feature']
            if type(j) is not int or not 0 <= j < len(axis['feature_names']):
                raise ValueError('Invalid axis feature')
            weights = [0.]*len(axis['feature_names']);weights[j] = 1.
            nodes.append(dict(kind='split', weights=weights, intercept=-finite(n['threshold']),
                              left=n['left'], right=n['right']))
    result = payload(axis['feature_names'], nodes, dict(converted_axis_schema=axis['schema_version']))
    PortableObliqueTree(result)
    return result
