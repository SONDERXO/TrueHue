"""Joint correction/identity tree using rendered loss and clean feasibility."""
import numpy as np
from src.model_training.portable_tree import PortableTree

def action_costs(image_pixels, reference_pixels, actions):
    a=np.asarray(image_pixels);b=np.asarray(reference_pixels);p=np.asarray(actions,float)
    if (a.dtype!=np.uint8 or b.dtype!=np.uint8 or a.ndim!=2 or a.shape[1]!=3
            or not len(a) or a.shape!=b.shape or p.ndim!=2 or p.shape[1]!=3
            or not len(p) or not np.isfinite(p).all() or (p<=0).any()):
        raise ValueError('Matching nonempty RGB8 pixels and positive finite actions required')
    unit=a.astype(float)/255.;target=b.astype(float);loss=[]
    for gamma,red,blue in p:
        output=np.rint(np.clip(unit**gamma*[red,1.,blue],0.,1.)*255.)
        loss.append(float(np.abs(output-target).mean()))
    return loss

def fit_action_tree(features, costs, clean, actions, names, max_depth=3, *, nonharm):
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
    safe=np.asarray(nonharm)
    if safe.shape!=flags.shape or safe.dtype!=bool:raise ValueError("Matching boolean nonharm flags required")
    forbidden=(flags[:,None] & (loss>0)) | (safe[:,None] & (loss>loss[:,0,None]))
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
        provenance=dict(experimental=True,objective='rgb8_mae_clean_and_colour_nonharm_feasibility',max_depth=max_depth))
    tree=PortableTree(payload)
    for i in np.flatnonzero(flags):
        node=tree.leaf_id(x[i]);leaf=next(t for t in trace if t['node']==node)
        assert loss[i,leaf['action']]==0
    for i in np.flatnonzero(safe):
        node=tree.leaf_id(x[i]);leaf=next(t for t in trace if t['node']==node)
        assert loss[i,leaf['action']]<=loss[i,0]
    return dict(tree=payload,actions=controls.tolist(),trace=trace)
