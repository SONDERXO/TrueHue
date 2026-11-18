"""Independent scalar fitting audit; no NumPy, solver or portable runtime import."""
from collections import Counter,defaultdict
import math,struct
from .linear_leaf_scalar_check import coefficients,predict

def close(a,b):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12)
def verify(plan,rows,scaffold,baseline,candidate,replay):
    assert len(rows)==60 and [r['case_id'] for r in rows]==plan['fitting_cases'] and len({r['case_id'] for r in rows})==60
    assert len({r['source'] for r in rows})==10 and plan['excluded_source'] not in {r['source'] for r in rows}
    assert Counter(r['role'] for r in rows)=={r:10 for r in ['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']}
    for r in rows:
        assert r['generated_fixture'] is False and r['status']=='available' and len(r['x'])==281
        assert all(type(v) in [float,int] and math.isfinite(v) and struct.unpack('!f',struct.pack('!f',v))[0]==v for v in r['x'])
        assert len(r['y'])==3 and all(type(v) in [float,int] and math.isfinite(v) and v>0 for v in r['y'])
    assert candidate['schema_version']=='truehue_linear_leaf_tree_v1' and candidate['input_dtype']=='float32' and candidate['coefficient_dtype']=='float64' and candidate['comparison']=='<='
    assert candidate['target_names']==['gamma','red_gain','blue_gain'] and candidate['feature_names']==plan['feature_names']==scaffold['feature_names'] and candidate['leaf_feature_indices']==[5,6]
    nodes=candidate['nodes'];assert len(nodes)==len(scaffold['nodes'])==len(plan['topology'])==11 and candidate['root']==0
    pending=[(0,0)];seen=set()
    while pending:
        i,depth=pending.pop();assert type(i) is int and 0<=i<len(nodes) and i not in seen and depth<=4;seen.add(i);n=nodes[i];old=scaffold['nodes'][i]
        if old['kind']=='split':
            assert n==old==plan['topology'][i];pending.extend([(n['left'],depth+1),(n['right'],depth+1)])
        else:
            assert n['kind']=='linear_leaf' and len(n['coefficients'])==3
            assert all(len(c)==3 and all(type(v) in [float,int] and math.isfinite(v) for v in c) for c in n['coefficients'])
    assert len(seen)==11 and replay['solver_calls']==6 and replay['branch_fits']==replay['held_predictions']==0 and replay['lambda_fixed']==plan['lambda_fixed']==.01 and replay['leaf_coordinates']==[5,6]
    members=defaultdict(list);predictions=[];leaves=[]
    for i,r in enumerate(rows):
        leaf,value=predict(candidate,r['x']);assert leaf==baseline['candidate_leaves'][i] and baseline['candidate_predictions'][i]==scaffold['nodes'][leaf]['values']
        assert leaf==replay['leaves'][i];members[leaf].append(r);leaves.append(leaf)
        for a,b in zip(value,replay['predictions'][i]):close(a,b)
        predictions.append(value)
    assert len(members)==6;compositions=[]
    for leaf,rs in members.items():
        expected=coefficients(rs)
        for a,b in zip(nodes[leaf]['coefficients'],expected):
            for c,d in zip(a,b):close(c,d)
        assert replay['leaf_statistics'][str(leaf)]['n']==len(rs)
        compositions.append(dict(leaf=leaf,records=len(rs),roles=dict(Counter(r['role'] for r in rs)),sources=dict(Counter(r['source'] for r in rs))))
    def losses(values):
        e=[[(a-b)**2 for a,b in zip(v,r['y'])] for v,r in zip(values,rows)]
        return dict(total=math.fsum(x for row in e for x in row),per_control=[math.fsum(row[j] for row in e) for j in range(3)],per_role={role:math.fsum(x for row,r in zip(e,rows) if r['role']==role for x in row) for role in sorted({r['role'] for r in rows})})
    after=losses(predictions);before=losses(baseline['candidate_predictions']);b=before['per_control'];a=after['per_control'];tol=lambda v:1e-12*max(1.,v)
    exposure=all(all(abs(p[j]-r['y'][j])<=1e-12 for j in range(3)) for p,r in zip(predictions,rows) if r['role'] in ['exposure_under','exposure_over'])
    checks=dict(red_nonworse=a[1]<=b[1]+tol(b[1]),blue_nonworse=a[2]<=b[2]+tol(b[2]),strict_colour_gain=sum(b[1:])-sum(a[1:])>tol(sum(b[1:])),exposure_nominal=exposure)
    return dict(passed=True,classification='FITTING_LEAF_RESPONSE_PASS' if all(checks.values()) else 'FITTING_LEAF_RESPONSE_STOP',checks=checks,candidate=after,baseline_saved=before,
        identity_max_deviation=[max(abs(p[j]-1) for p,r in zip(predictions,rows) if r['role']=='identity') for j in range(3)],control_ranges=[[min(p[j] for p in predictions),max(p[j] for p in predictions)] for j in range(3)],
        max_abs_coefficient=max(abs(v) for n in nodes if n['kind']=='linear_leaf' for row in n['coefficients'] for v in row),leaf_composition=compositions,coefficients_checked=54,predictions_checked=60,branch_fits=0,held_predictions=0,correction_quality_established=False,model_adopted=False)
