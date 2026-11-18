"""Fixed linear exposure-quality head. No image loading or external I/O."""
from collections import Counter
import hashlib
import json
import math
import numpy as np
from .portrait_exposure_quality import ranking_pairs, fit_scaler, rank_objective

SETTINGS=dict(width=4096,epochs=50,batch_size=512,seed=42,learning_rate=.01,
              beta1=.9,beta2=.999,epsilon=1e-8,regularization=.001)


def prepare(training,features,*,generated_fixture):
    x=np.asarray(features,dtype=np.float64)
    if not isinstance(generated_fixture,bool):raise ValueError('Explicit provenance boolean required')
    if x.shape!=(len(training),4096) or not np.isfinite(x).all() or not len(training):
        raise ValueError('Finite aligned training Nx4096 features required')
    if any(r['partition']!='Train' or r['generated_fixture'] is not generated_fixture for r in training):
        raise ValueError('Training partition/provenance only')
    if len({r['id'] for r in training})!=len(training):raise ValueError('Duplicate training ID')
    order=sorted(range(len(training)),key=lambda i:training[i]['id'])
    records=[dict(training[i]) for i in order];x=x[order].copy()
    for r in records:
        for k in ['low','score','high']:r[k]=float(r[k])
    pairs=ranking_pairs(records)
    pairs.sort(key=lambda p:(records[p[0]]['id'],records[p[1]]['id']))
    counts=Counter(records[i]['scene'] for i,j in pairs)
    scenes={r['scene'] for r in records}
    if not pairs or set(counts)!=scenes:raise ValueError('Every training scene needs eligible ranking pairs')
    weights=np.array([1/(len(scenes)*counts[records[i]['scene']]) for i,j in pairs],dtype=np.float64)
    mean,scale=fit_scaler(x,range(len(records)))
    z=(x-mean)/scale
    return dict(records=records,x=x,z=z,mean=mean,scale=scale,pairs=np.asarray(pairs,dtype=np.int64),pair_weights=weights,
                scene_pair_counts=dict(counts),generated_fixture=generated_fixture)


def batch_objective(w,z,pairs,pair_weights,indices):
    indices=np.asarray(indices,dtype=np.int64)
    if indices.ndim!=1 or not len(indices) or np.any(indices<0) or np.any(indices>=len(pairs)):
        raise ValueError('Nonempty valid batch indices required')
    pair=pairs[indices];a=pair_weights[indices]
    differences=z[pair[:,0]]-z[pair[:,1]]
    # rank_objective normalizes its weights. Restore global scene weighting here.
    normalized_loss,normalized_grad=rank_objective(w,differences,a,regularization=0.)
    multiplier=len(pairs)/len(indices)*float(a.sum())
    lam=SETTINGS['regularization']
    return (multiplier*normalized_loss+lam/2*float(w@w),
            multiplier*normalized_grad+lam*w)


def adam_update(w,m,v,g,step):
    if step<1 or any(a.shape!=w.shape for a in [m,v,g]) or not all(np.isfinite(a).all() for a in [w,m,v,g]):
        raise ValueError('Finite aligned optimizer arrays and positive step required')
    b1,b2=SETTINGS['beta1'],SETTINGS['beta2']
    m=b1*m+(1-b1)*g;v=b2*v+(1-b2)*g*g
    update=SETTINGS['learning_rate']*(m/(1-b1**step))/(np.sqrt(v/(1-b2**step))+SETTINGS['epsilon'])
    result=w-update
    if not np.isfinite(result).all():raise ValueError('Nonfinite optimizer result')
    return result,m,v


def fit_head(training,features,*,generated_fixture,observer=None):
    data=prepare(training,features,generated_fixture=generated_fixture)
    rng=np.random.default_rng(SETTINGS['seed']);w=np.zeros(4096);m=w.copy();v=w.copy();step=0
    batches=[];trace=[]
    for epoch in range(SETTINGS['epochs']):
        order=rng.permutation(len(data['pairs']))
        for start in range(0,len(order),SETTINGS['batch_size']):
            indices=order[start:start+SETTINGS['batch_size']]
            loss,gradient=batch_objective(w,data['z'],data['pairs'],data['pair_weights'],indices)
            step+=1;w,m,v=adam_update(w,m,v,gradient,step)
            if observer is not None:observer(step,w.copy(),m.copy(),v.copy())
            batches.append(hashlib.sha256(indices.tobytes()).hexdigest())
            trace.append(dict(step=step,epoch=epoch,batch_size=len(indices),loss=loss))
    expected=SETTINGS['epochs']*math.ceil(len(data['pairs'])/SETTINGS['batch_size'])
    assert step==expected
    pair_ids=[(data['records'][i]['id'],data['records'][j]['id']) for i,j in data['pairs']]
    head=dict(schema='truehue_exposure_quality_linear_research_v1',settings=dict(SETTINGS),
        generated_fixture=generated_fixture,weights=w.tolist(),mean=data['mean'].tolist(),scale=data['scale'].tolist(),bias=0.,
        training_ids=[r['id'] for r in data['records']],scene_pair_counts=data['scene_pair_counts'],
        eligible_pairs=len(data['pairs']),optimizer_updates=step,
        pair_ids_sha256=hashlib.sha256(json.dumps(pair_ids,separators=(',',':')).encode()).hexdigest(),
        epoch_batch_index_sha256=batches)
    return head,trace


def score(head,features):
    x=np.asarray(features,dtype=np.float64)
    if x.shape!=(4096,) or not np.isfinite(x).all():raise ValueError('Finite4096feature vector required')
    w=np.asarray(head['weights']);mean=np.asarray(head['mean']);scale=np.asarray(head['scale'])
    if any(a.shape!=(4096,) or not np.isfinite(a).all() for a in [w,mean,scale]) or np.any(scale<=0) or head['bias']!=0:
        raise ValueError('Invalid head state')
    return float(w@((x-mean)/scale))
