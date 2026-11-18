"""Experimental zero-fit clean anchors and leaf-local support for split heads."""
import numpy as np
from src.model_training.portable_tree import PortableTree


def prepare_policy(model, features, clean):
    x = np.asarray(features, dtype=np.float32)
    clean = np.asarray(clean, dtype=bool)
    if (x.ndim != 2 or x.shape[1] != len(model['feature_names']) or not len(x)
            or clean.shape != (len(x),) or not np.isfinite(x).all()):
        raise ValueError('Finite fitting features and aligned clean flags required')
    heads = {}
    for name in ('gamma', 'gains'):
        tree = PortableTree(model['heads'][name]['tree'])
        if tuple(model['feature_names']) != tree.feature_names:
            raise ValueError('Head feature order mismatch')
        leaves = np.array([tree.leaf_id(row) for row in x])
        heads[name] = {str(int(leaf)): dict(
            minimum=x[leaves == leaf].min(axis=0).tolist(),
            maximum=x[leaves == leaf].max(axis=0).tolist(),
            rows=int((leaves == leaf).sum()),
            clean_rows=int(clean[leaves == leaf].sum())) for leaf in set(leaves)}
    return dict(schema_version='truehue_joint_neutral_support_v1', heads=heads)


def predict_policy(model, policy, features):
    if policy.get('schema_version') != 'truehue_joint_neutral_support_v1':
        raise ValueError('Unsupported policy')
    # PortableTree validates width, finite values and float32 routing.
    values = []; details = {}; supported = True
    for name in ('gamma', 'gains'):
        tree = PortableTree(model['heads'][name]['tree'])
        leaf = tree.leaf_id(features)
        member = policy['heads'][name][str(leaf)]
        x = np.asarray(features, dtype=np.float32)
        outside = np.flatnonzero((x < member['minimum']) | (x > member['maximum'])).tolist()
        supported = supported and not outside
        neutral = member['clean_rows'] > 0
        values.extend([1.] * len(tree.target_names) if neutral else tree.predict_one(features))
        details[name] = dict(leaf=leaf, outside_axes=outside, clean_anchored=neutral)
    return dict(parameters=values if supported else [1., 1., 1.],
                supported=bool(supported), heads=details)
