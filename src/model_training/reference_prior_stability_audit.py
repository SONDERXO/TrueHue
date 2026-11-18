"""Diagnostic sufficient statistics; no correction fitting or generated flag reuse."""
import numpy as np

def summarize(rgb):
    if rgb.dtype!=np.uint8 or rgb.shape!=(256,256,3):raise ValueError('Declared256RGB8 required')
    x=rgb.reshape(-1,3).astype(float)/255;positive=np.all(x>0,axis=1);x=x[positive]
    bins=np.minimum(7,np.floor(8*x[:,1])).astype(int);uv=np.log(x[:,[0,2]]/x[:,1,None]);result=[]
    for k in range(8):
        selected=uv[bins==k];result.append(dict(count=len(selected),mean=selected.mean(axis=0).tolist() if len(selected) else None))
    return dict(total=65536,positive=len(x),bins=result)

def table_for_fold(summaries,fitting_ids,held):
    if not fitting_ids or len(fitting_ids)!=len(set(fitting_ids)) or held in fitting_ids or set(fitting_ids)!=set(summaries)-{held}:raise ValueError('Exact disjoint source-held fitting roster required')
    table=[]
    for k in range(8):
        contributing=[s for s in sorted(fitting_ids) if summaries[s]['bins'][k]['count']>0]
        means=[summaries[s]['bins'][k]['mean'] for s in contributing]
        table.append(dict(index=k,contributors=contributing,mean=np.mean(means,axis=0).tolist() if means else None))
    return table

def residual(summary,table):
    supported=sum(b['count'] for b,t in zip(summary['bins'],table) if t['mean'] is not None)
    delta=[sum(b['count']*(b['mean'][j]-t['mean'][j]) for b,t in zip(summary['bins'],table) if b['count'] and t['mean'] is not None)/supported for j in [0,1]] if supported else [None,None]
    return dict(available=supported>0,positive_fraction=summary['positive']/summary['total'],supported_fraction=supported/summary['total'],positive_pixels=summary['positive'],supported_pixels=supported,red_residual=delta[0],blue_residual=delta[1])
