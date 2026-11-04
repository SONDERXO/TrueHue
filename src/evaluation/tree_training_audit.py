"""Read-only tree traces and explicit gamma-direction diagnostics."""
import numpy as np


def gamma_direction(value,tolerance=1e-8):
    if not np.isfinite(value) or value<=0 or not np.isfinite(tolerance) or tolerance<0:
        raise ValueError('Expected finite positive gamma and nonnegative tolerance')
    return 'brighten' if value>1+tolerance else 'darken' if value<1-tolerance else 'unchanged'


def trace_tree(model,features,feature_names):
    """Match sklearn's float32 input routing without training or editing a tree."""
    values=np.asarray(features,dtype=float)
    if values.shape!=(len(feature_names),) or not np.isfinite(values).all():
        raise ValueError('Invalid finite feature vector')
    values32=values.astype(np.float32)
    if not np.isfinite(values32).all():raise ValueError('Features overflow float32')
    tree=model.tree_;node=0;rules=[]
    while tree.children_left[node]!=tree.children_right[node]:
        index=int(tree.feature[node]);threshold=float(tree.threshold[node])
        left=bool(values32[index]<=threshold)
        rules.append(dict(node_id=int(node),feature=feature_names[index],
            input_value=float(values[index]),routing_float32_value=float(values32[index]),
            threshold=threshold,comparison='<=' if left else '>'))
        node=int(tree.children_left[node] if left else tree.children_right[node])
    expected=int(model.apply(values[None,:])[0])
    if node!=expected:raise RuntimeError('Manual trace differs from sklearn leaf')
    return dict(leaf_id=node,rules=rules)
