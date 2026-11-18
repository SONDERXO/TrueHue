"""One bounded local split with saved costs and exact row constraints."""
import copy
import math
from src.model_training.portable_tree import float32


def refine_leaf(model, features, node_id):
    """Return a copy with at most one split, plus an explicit search receipt."""
    result = copy.deepcopy(model)
    nodes = result['tree']['nodes']
    assert nodes[node_id]['kind'] == 'leaf'
    trace = result['trace'][node_id]
    ids = sorted(trace['rows'])
    x = [[float32(v) for v in features[i]] for i in range(len(features))]
    costs = result['costs']

    def optimum(rows):
        feasible = [a for a in range(len(result['actions'])) if all(
            (not result['clean'][i] or costs[i][a] == 0) and
            (not result['nonharm'][i] or costs[i][a] <= costs[i][0]) for i in rows)]
        return min((math.fsum(costs[i][a] for i in rows), a) for a in feasible)

    parent, action = optimum(ids)
    assert nodes[node_id]['values'] == result['actions'][action]
    best = parent
    chosen = None
    count = 0
    tolerance = 1e-12 * max(1., abs(parent))
    for k in range(len(x[0])):
        values = sorted({x[i][k] for i in ids})
        for low, high in zip(values, values[1:]):
            threshold = (low + high) / 2.
            left = [i for i in ids if x[i][k] <= threshold]
            right = [i for i in ids if x[i][k] > threshold]
            lc, la = optimum(left)
            rc, ra = optimum(right)
            count += 1
            if lc + rc < best - tolerance:
                best = lc + rc
                chosen = (k, threshold, left, right, lc, la, rc, ra)
    receipt = dict(node=node_id, candidates=count, baseline_cost=parent,
                   split_added=chosen is not None, final_cost=best)
    if chosen is not None:
        k, threshold, left, right, lc, la, rc, ra = chosen
        li, ri = len(nodes), len(nodes) + 1
        nodes[node_id] = dict(kind='split', feature=k, threshold=threshold, left=li, right=ri)
        nodes.extend([dict(kind='leaf', values=result['actions'][la]),
                      dict(kind='leaf', values=result['actions'][ra])])
        trace.update(split_feature=k, split_threshold=threshold,
                     immediate_child_cost=best, local_refinement=True)
        for index, rows, cost, a in [(li, left, lc, la), (ri, right, rc, ra)]:
            result['trace'].append(dict(node=index, rows=rows, depth=trace['depth']+1,
                                       action=a, cost=cost))
        receipt.update(feature=k, threshold=threshold, left=li, right=ri,
                       left_action=la, right_action=ra)
    return result, receipt
