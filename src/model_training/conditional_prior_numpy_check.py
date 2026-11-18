"""Independent vectorized reconstruction; no production prior imports."""
import numpy as np
def table(records,fitting_ids):
    groups=[[] for _ in range(8)];counts={}
    for source in sorted(fitting_ids):
        r=next(r for r in records if r['source']==source);x=np.asarray(r['pixels'],float);positive=np.all(x>0,axis=1);x=x[positive]
        counts[source]=dict(total=len(r['pixels']),positive=int(positive.sum()),zero_channel=int((~positive).sum()))
        bins=np.minimum(7,np.floor(x[:,1]*8)).astype(int);uv=np.log(x[:,[0,2]]/x[:,1,None])
        for k in range(8):
            selected=uv[bins==k]
            if len(selected):groups[k].append(dict(source=source,pixels=len(selected),mean=selected.mean(axis=0).tolist()))
    return dict(source_counts=counts,bins=[dict(index=k,contributors=cs,mean=np.mean([c['mean'] for c in cs],axis=0).tolist() if cs else None) for k,cs in enumerate(groups)])
def describe(artifact,values):
    x=np.asarray(values,float).reshape(-1,3);n=len(x);positive=np.all(x>0,axis=1);xp=x[positive];bins=np.minimum(7,np.floor(xp[:,1]*8)).astype(int)
    hist=np.bincount(bins,minlength=8).tolist();support=np.array([artifact['bins'][k]['mean'] is not None for k in bins],bool)
    if support.any():
        chosen=xp[support];means=np.asarray([artifact['bins'][k]['mean'] for k in bins[support]]);delta=np.log(chosen[:,[0,2]]/chosen[:,1,None])-means;mu=delta.mean(axis=0).tolist()
    else:mu=[None,None]
    count=int(support.sum());p=int(positive.sum())
    return dict(available=count>0,positive_fraction=p/n if n else 0.,supported_fraction=count/n if n else 0.,mean_red_residual=mu[0],mean_blue_residual=mu[1],total_pixels=n,positive_pixels=p,supported_pixels=count,zero_channel_pixels=n-p,unsupported_positive_pixels=p-count,positive_green_bin_counts=hist)
