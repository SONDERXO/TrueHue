"""Generated-reference prior and standalone residual evaluator. No IO on import."""
from copy import deepcopy
import json,math
from pathlib import Path
SCHEMA='truehue_green_conditional_reference_prior_v1'

def pixels(values):
    if not isinstance(values,(list,tuple)):raise ValueError('Sequence of normalized RGB triples required')
    result=[]
    for row in values:
        if not isinstance(row,(list,tuple)) or len(row)!=3:raise ValueError('RGB triple required')
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in row):raise ValueError('Finite encoded values in[0,1] required')
        result.append(tuple(float(v) for v in row))
    return result

def rgb8(values):
    result=[]
    for row in values:
        if len(row)!=3 or any(type(v) is not int or not 0<=v<=255 for v in row):raise ValueError('RGB8 integer triples required')
        result.append([v/255 for v in row])
    return result

def bin_index(g):return min(7,math.floor(8*g))
def _ids(ids):
    if not isinstance(ids,(list,tuple)) or any(not isinstance(s,str) or not s for s in ids) or len(ids)!=len(set(ids)):raise ValueError('Unique nonempty source IDs required')
    return list(ids)

def build_generated_prior(records,fitting_ids,excluded_ids):
    fitting=_ids(fitting_ids);excluded=_ids(excluded_ids)
    if not fitting or set(fitting)&set(excluded):raise ValueError('Nonempty disjoint fitting/excluded IDs required')
    selected={}
    for r in records:
        source=r.get('source')
        if source not in fitting:continue # Do not inspect held roles/provenance/pixel payloads.
        if source in selected:raise ValueError('Duplicate fitting reference')
        if r.get('generated_fixture') is not True or r.get('role')!='reference':raise ValueError('Generated reference only')
        selected[source]=r
    if set(selected)!=set(fitting):raise ValueError('Missing fitting reference')
    bins=[[] for _ in range(8)];counts={}
    for source in sorted(fitting):
        values=pixels(selected[source]['pixels']);groups=[[] for _ in range(8)];eligible=0
        for r,g,b in values:
            if min(r,g,b)<=0:continue
            eligible+=1;groups[bin_index(g)].append((math.log(r/g),math.log(b/g)))
        if not eligible:raise ValueError('Fitting reference has no positive pixels')
        counts[source]=dict(total=len(values),positive=eligible,zero_channel=len(values)-eligible)
        for index,group in enumerate(groups):
            if group:bins[index].append(dict(source=source,pixels=len(group),mean=[math.fsum(p[j] for p in group)/len(group) for j in [0,1]]))
    table=[]
    for index,contributors in enumerate(bins):
        mean=[math.fsum(c['mean'][j] for c in contributors)/len(contributors) for j in [0,1]] if contributors else None
        table.append(dict(index=index,mean=mean,contributors=contributors))
    artifact=dict(schema_version=SCHEMA,green_bins=8,weighting='equal_source_bin_means',fitting_sources=sorted(fitting),excluded_sources=sorted(excluded),source_counts=counts,bins=table,generated_only=True)
    ConditionalReferencePrior(artifact)
    return artifact

class ConditionalReferencePrior:
    def __init__(self,artifact):
        a=deepcopy(artifact)
        if not isinstance(a,dict) or a.get('schema_version')!=SCHEMA or type(a.get('green_bins')) is not int or a['green_bins']!=8 or a.get('weighting')!='equal_source_bin_means' or a.get('generated_only') is not True:raise ValueError('Known generated prior schema required')
        fitting=_ids(a.get('fitting_sources'));excluded=_ids(a.get('excluded_sources'))
        if not fitting or fitting!=sorted(fitting) or set(fitting)&set(excluded):raise ValueError('Invalid table source split')
        counts=a.get('source_counts',{})
        if set(counts)!=set(fitting):raise ValueError('Source counts required')
        for s in fitting:
            c=counts[s]
            if any(type(c.get(k)) is not int or c[k]<0 for k in ['total','positive','zero_channel']) or c['positive']==0 or c['positive']+c['zero_channel']!=c['total']:raise ValueError('Invalid source pixel counts')
        table=a.get('bins');seen={s:0 for s in fitting}
        if not isinstance(table,list) or len(table)!=8:raise ValueError('Eight bins required')
        for index,entry in enumerate(table):
            if type(entry.get('index')) is not int or entry['index']!=index or not isinstance(entry.get('contributors'),list):raise ValueError('Indexed bin required')
            cs=entry['contributors'];ids=[c.get('source') for c in cs]
            if len(ids)!=len(set(ids)) or any(s not in fitting for s in ids) or ids!=sorted(ids):raise ValueError('Unique ordered fitting contributors required')
            for c in cs:
                if type(c.get('pixels')) is not int or c['pixels']<=0:raise ValueError('Positive bin count required')
                if not isinstance(c.get('mean'),list) or len(c['mean'])!=2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in c['mean']):raise ValueError('Finite log-chroma means required')
                seen[c['source']]+=c['pixels']
            if not cs:
                if entry.get('mean') is not None:raise ValueError('Missing bin must be null')
            else:
                mu=entry.get('mean')
                if not isinstance(mu,list) or len(mu)!=2:raise ValueError('Two bin means required')
                for j in [0,1]:
                    v=mu[j]
                    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not math.isclose(v,math.fsum(c['mean'][j] for c in cs)/len(cs),rel_tol=1e-12,abs_tol=1e-12):raise ValueError('Equal-source mean mismatch')
        if any(seen[s]!=counts[s]['positive'] for s in fitting):raise ValueError('Source bin accounting mismatch')
        self._artifact=a

    def artifact(self):return deepcopy(self._artifact)

    def describe(self,values):
        values=pixels(values);positive=supported=0;residuals=[];hist=[0]*8
        for r,g,b in values:
            if min(r,g,b)<=0:continue
            positive+=1;index=bin_index(g);hist[index]+=1;mu=self._artifact['bins'][index]['mean']
            if mu is None:continue
            supported+=1;residuals.append([math.log(r/g)-mu[0],math.log(b/g)-mu[1]])
        n=len(values)
        return dict(available=supported>0,positive_fraction=positive/n if n else 0.,supported_fraction=supported/n if n else 0.,
            mean_red_residual=math.fsum(r[0] for r in residuals)/supported if supported else None,mean_blue_residual=math.fsum(r[1] for r in residuals)/supported if supported else None,
            total_pixels=n,positive_pixels=positive,supported_pixels=supported,zero_channel_pixels=n-positive,unsupported_positive_pixels=positive-supported,positive_green_bin_counts=hist)

def build_once(out,records,fitting_ids,excluded_ids):
    out=Path(out);out.mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    try:
        artifact=build_generated_prior(records,fitting_ids,excluded_ids);write('table.json',artifact);write('status.json',dict(status='GENERATED_TABLE_COMPLETE',real_data_used=False));return artifact
    except BaseException as error:write('status.json',dict(status='FAILED_PRESERVED_NO_RETRY',error=repr(error),real_data_used=False));raise
