"""Explicit fitting-control leaf protection; not a held-input safety guarantee."""
from copy import deepcopy
from src.model_training.portable_tree import PortableTree


def protect_identity_leaves(payload,training_features,identity_flags):
    """Keep splits fixed; emit identity in leaves containing fitting controls.

    Callers must supply fitting rows only. This does not identify an unseen
    clean image routed into a distortion-only leaf.
    """
    tree=PortableTree(payload)
    if not training_features or len(training_features)!=len(identity_flags):raise ValueError('Matching nonempty fitting rows and flags required')
    if any(type(flag) is not bool for flag in identity_flags):raise ValueError('Explicit boolean identity flags required')
    membership={}
    for index,(features,identity) in enumerate(zip(training_features,identity_flags)):
        leaf=tree.leaf_id(features)
        membership.setdefault(leaf,dict(training_indices=[],identity_indices=[]))['training_indices'].append(index)
        if identity:membership[leaf]['identity_indices'].append(index)
    modified=deepcopy(payload)
    protected=[]
    for leaf,members in membership.items():
        if members['identity_indices']:
            modified['nodes'][leaf]['values']=[1.,1.,1.];protected.append(leaf)
    modified.setdefault('provenance',{})['leaf_policy']='identity_if_any_fitting_control_v1'
    return modified,dict(protected_leaves=sorted(protected),membership=membership)
