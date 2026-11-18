"""Fixed facial-root hierarchy for the existing joint image-loss objective."""
import numpy as np
from src.model_training.portable_tree import PortableTree
ROOT_FEATURES=('input_mean_l_star','input_mean_a_star','input_mean_b_star','input_ita_degrees','input_mst_score')

def fit_face_first_tree(features, costs, clean, actions, names, max_depth=3):
    x=np.asarray(features,dtype=np.float32);loss=np.asarray(costs,float)
    flags=np.asarray(clean);controls=np.asarray(actions,float);names=list(names)
    if (x.ndim!=2 or not len(x) or x.shape[1]!=len(names) or len(set(names))!=len(names)
            or flags.shape!=(len(x),) or flags.dtype!=bool or loss.ndim!=2
            or loss.shape!=(len(x),len(controls)) or controls.ndim!=2 or controls.shape[1]!=3
            or not np.isfinite(x).all() or not np.isfinite(loss).all() or (loss<0).any()
            or not np.isfinite(controls).all() or (controls<=0).any()
            or len(controls)==0 or controls[0].tolist()!=[1.,1.,1.]
            or not np.all(loss[flags,0]==0) or type(max_depth)!=int or max_depth<0):
        raise ValueError('Aligned finite features, costs, bool clean flags and identity-first actions required')
    forbidden=flags[:,None] & (loss>0)
    nodes=[];trace=[]
    def optimum(sums,bad):
        feasible=np.where(bad==0,sums,np.inf);action=int(np.argmin(feasible))
        return action,float(feasible[action])
    def build(ids,depth):
        total=loss[ids].sum(axis=0);bad=forbidden[ids].sum(axis=0)
        action,parent=optimum(total,bad);index=len(nodes)
        nodes.append(dict(kind='leaf',values=controls[action].tolist()))
        entry=dict(node=index,rows=ids.tolist(),depth=depth,action=action,cost=parent)
        trace.append(entry);best=parent;split=None
        if depth<max_depth and len(ids)>1:
            for feature in range(x.shape[1]):
                if depth==0 and names[feature] not in ROOT_FEATURES:continue
                order=ids[np.argsort(x[ids,feature],kind='stable')]
                values=x[order,feature];sums=np.cumsum(loss[order],axis=0)
                bads=np.cumsum(forbidden[order],axis=0)
                for k in np.flatnonzero(values[:-1]<values[1:]):
                    la,lc=optimum(sums[k],bads[k]);ra,rc=optimum(sums[-1]-sums[k],bads[-1]-bads[k])
                    candidate=lc+rc
                    if candidate<best-1e-12*max(1.,abs(parent)):
                        best=candidate;split=(feature,(float(values[k])+float(values[k+1]))/2.,order[:k+1],order[k+1:])
        if split is not None:
            feature,threshold,left,right=split
            entry.update(split_feature=feature,split_threshold=threshold,immediate_child_cost=best)
            li=build(left,depth+1);ri=build(right,depth+1)
            nodes[index]=dict(kind='split',feature=feature,threshold=threshold,left=li,right=ri)
        return index
    build(np.arange(len(x)),0)
    payload=dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',
        threshold_dtype='float64',comparison='<=',root=0,feature_names=names,
        target_names=['target_gamma','target_red_gain','target_blue_gain'],nodes=nodes,
        provenance=dict(experimental=True,objective='rgb8_mae_with_exact_fitting_clean_feasibility',max_depth=max_depth,root_feature_names=list(ROOT_FEATURES)))
    tree=PortableTree(payload)
    for i in np.flatnonzero(flags):
        node=tree.leaf_id(x[i]);leaf=next(t for t in trace if t['node']==node)
        assert loss[i,leaf['action']]==0
    return dict(tree=payload,actions=controls.tolist(),trace=trace)
