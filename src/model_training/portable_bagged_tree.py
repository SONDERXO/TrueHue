"""Standard-library-only mean of exactly 64 validated correction trees."""
from copy import deepcopy
import math
from .portable_tree import PortableTree

SCHEMA = 'truehue_source_bagged_tree_v1'
MEMBERS = 64


class PortableBaggedTree:
    def __init__(self, payload):
        if not isinstance(payload, dict) or payload.get('schema_version') != SCHEMA:
            raise ValueError('Unsupported ensemble schema')
        if payload.get('aggregation') != 'math.fsum_divide_64':
            raise ValueError('Fixed equal arithmetic mean required')
        members = payload.get('members')
        if not isinstance(members, list) or len(members) != MEMBERS:
            raise ValueError('Exactly 64 members required')
        self.feature_names = PortableTree._names(payload.get('feature_names'))
        self.target_names = PortableTree._names(payload.get('target_names'))
        if self.target_names != ('gamma', 'red_gain', 'blue_gain'):
            raise ValueError('Correction target schema required')
        trees = []
        for member in deepcopy(members):
            tree = PortableTree(member)
            if tree.feature_names != self.feature_names or tree.target_names != self.target_names:
                raise ValueError('All member schemas must match')
            stack = [(0, 0)]
            while stack:
                i, depth = stack.pop()
                if depth > 4:
                    raise ValueError('Member exceeds fixed depth')
                node = member['nodes'][i]
                if node['kind'] == 'split':
                    stack.extend([(node['left'], depth + 1), (node['right'], depth + 1)])
            trees.append(tree)
        self._trees = tuple(trees)

    def member_predictions(self, row):
        return [tree.predict_one(row) for tree in self._trees]

    def predict_one(self, row):
        values = self.member_predictions(row)
        return [math.fsum(v[c] for v in values) / MEMBERS for c in range(3)]

    def predict(self, rows):
        return [self.predict_one(row) for row in rows]
