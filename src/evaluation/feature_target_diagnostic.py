"""Descriptive neighbors using fitting-only scale; never a prediction rule."""
import numpy as np

def neighbor_diagnostic(fit_ids,features,targets,query,query_target,axes):
    x=np.asarray(features,float);y=np.asarray(targets,float);q=np.asarray(query,float);target=np.asarray(query_target,float)
    if x.ndim!=2 or not len(x) or len(fit_ids)!=len(x) or len(set(fit_ids))!=len(fit_ids):raise ValueError('Nonempty unique fitting rows required')
    if y.shape!=(len(x),3) or q.shape!=(x.shape[1],) or target.shape!=(3,):raise ValueError('Feature/target shape mismatch')
    if not all(np.isfinite(a).all() for a in [x,y,q,target]) or (y<=0).any() or (target<=0).any():raise ValueError('Finite measurements and positive targets required')
    if not axes or len(set(axes))!=len(axes) or any(isinstance(a,bool) or not isinstance(a,int) or not 0<=a<x.shape[1] for a in axes):raise ValueError('Valid distinct diagnostic axes required')
    selected=x[:,axes];center=selected.mean(axis=0);scale=selected.std(axis=0,ddof=0);active=scale>0
    distances=np.sqrt(np.square((selected[:,active]-q[np.array(axes)[active]])/scale[active]).sum(axis=1))
    matches=np.all(np.abs(y-target)<=1e-12,axis=1)
    ordered=sorted(range(len(x)),key=lambda i:(float(distances[i]),fit_ids[i]))
    ranking=[dict(pair_id=fit_ids[i],distance=float(distances[i]),target_matches=bool(matches[i])) for i in ordered]
    same=next((r for r in ranking if r['target_matches']),None);different=next((r for r in ranking if not r['target_matches']),None)
    return dict(axes=axes,fit_mean=center.tolist(),fit_population_std=scale.tolist(),active_axes=np.array(axes)[active].tolist(),
        constant_axes=np.array(axes)[~active].tolist(),query_differs_on_constant_axes=bool(np.any(q[np.array(axes)[~active]]!=center[~active])),
        ranking=ranking,top3=ranking[:3],nearest_matching_target=same,nearest_different_target=different,
        different_target_strictly_closer=bool(different['distance']<same['distance']) if same and different else None,
        limitation='Fitting-standardized descriptive distance; not a perceptual metric, confidence score or nearest-neighbor predictor')
