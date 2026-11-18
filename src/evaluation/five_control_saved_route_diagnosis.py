"""Pure stdlib descriptive saved-route helpers. No fitter, runtime or pixel imports."""
from collections import Counter
import math
import struct

NEUTRAL={'identity','colour_only'}


def trace(tree,features):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in features]
    node=0;visited=[];path=[]
    while True:
        if node in visited:raise ValueError('Cyclic saved tree')
        visited.append(node);item=tree['nodes'][node]
        if item['kind']=='leaf':return dict(leaf=node,controls=list(item['values']),visited=visited,path=path)
        j=item['feature'];value=x[j];left=value<=item['threshold']
        child=item['left'] if left else item['right']
        path.append(dict(node=node,feature_index=j,feature_name=tree['feature_names'][j],
            threshold=item['threshold'],held_value=value,direction='left' if left else 'right',child=child))
        node=child


def composition(rows):
    return dict(rows=len(rows),roles=dict(Counter(r['role'] for r in rows)),
        sources=dict(Counter(r['source_id'] for r in rows)),
        neutral=sum(r['role'] in NEUTRAL for r in rows),exposure=sum(r['role'] not in NEUTRAL for r in rows))


def value_range(rows,index,value):
    if not rows:return dict(count=0,min=None,max=None,held_inside=None)
    values=[r['x'][index] for r in rows];lo,hi=min(values),max(values)
    return dict(count=len(values),min=lo,max=hi,held_inside=lo<=value<=hi)


def detailed_path(tree,features,rows,routes):
    result=trace(tree,features);details=[];first=None
    for split in result['path']:
        n=tree['nodes'][split['node']]
        parent=[r for r,route in zip(rows,routes) if split['node'] in route['visited']]
        left=[r for r,route in zip(rows,routes) if n['left'] in route['visited']]
        right=[r for r,route in zip(rows,routes) if n['right'] in route['visited']]
        chosen=left if split['direction']=='left' else right
        neutral=[r for r in parent if r['role'] in NEUTRAL]
        exposure=[r for r in parent if r['role'] not in NEUTRAL]
        j,v=split['feature_index'],split['held_value']
        nr,er=value_range(neutral,j,v),value_range(exposure,j,v)
        overlap=bool(neutral and exposure and max(nr['min'],er['min'])<=min(nr['max'],er['max']))
        entry=dict(**split,parent=composition(parent),left=composition(left),right=composition(right),
            chosen=composition(chosen),node_feature_range=value_range(parent,j,v),
            chosen_feature_range=value_range(chosen,j,v),node_neutral_feature_range=nr,
            node_exposure_feature_range=er,node_family_feature_ranges_overlap=overlap,
            full_fitting_neutral_feature_range=value_range([r for r in rows if r['role'] in NEUTRAL],j,v),
            full_fitting_exposure_feature_range=value_range([r for r in rows if r['role'] not in NEUTRAL],j,v))
        details.append(entry)
        if first is None and entry['parent']['neutral']>0 and entry['chosen']['neutral']==0 and entry['chosen']['exposure']>0:
            first=entry
    members=[r for r,route in zip(rows,routes) if route['leaf']==result['leaf']]
    return dict(leaf=result['leaf'],controls=result['controls'],path=details,
        reached_leaf=composition(members),first_neutral_exclusion=first,
        reached_fitting_cases=[r['case_id'] for r in members])


def errors(p,y):return [(a-b)**2 for a,b in zip(p,y)]


def summarize_errors(records):
    if not records:return None
    per=[math.fsum(r[j] for r in records)/len(records) for j in range(5)]
    return dict(occurrences=len(records),mean_per_control_squared_error=per,mean_total_control_SSE=math.fsum(per))
