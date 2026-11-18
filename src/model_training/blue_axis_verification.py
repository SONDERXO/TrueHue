"""Independent scalar60row routes/leafmeans/bluegate; no optimizer or runtime."""
from collections import Counter
import math,struct
from .joint_colour_verification import validate,route

def verify(tree,rows,replay,names,excluded):
    assert len(names)==281 and len(rows)==60 and len({r['case_id'] for r in rows})==60
    assert len({r['source'] for r in rows})==10 and excluded not in {r['source'] for r in rows}
    roles=['identity','exposure_under','exposure_over','colour_cool','blue_decrease','blue_increase']
    assert Counter(r['role'] for r in rows)=={r:10 for r in roles}
    for r in rows:
        assert len(r['x'])==281 and all(type(v) in (float,int) and math.isfinite(v) and struct.unpack('!f',struct.pack('!f',v))[0]==v for v in r['x'])
        assert len(r['y'])==3 and all(type(v) in (float,int) and math.isfinite(v) and v>0 for v in r['y'])
    validate(tree,names)
    expected=dict(criterion='squared_error',splitter='best',max_depth=4,random_state=42,min_samples_leaf=1,min_samples_split=2,min_weight_fraction_leaf=0.,max_features=None,max_leaf_nodes=None,min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
    assert replay['settings']==expected and replay['fit_calls']==1 and replay['held_predictions']==0
    predictions=[];leaves=[];members={}
    for i,r in enumerate(rows):
        leaf,value=route(tree,r['x']);predictions.append(value);leaves.append(leaf);members.setdefault(leaf,[]).append(i)
    assert predictions==replay['candidate_predictions'] and leaves==replay['candidate_leaves']
    assert set(members)=={i for i,n in enumerate(tree['nodes']) if n['kind']=='leaf'}
    composition=[]
    for leaf,indices in members.items():
        mean=[math.fsum(rows[i]['y'][j] for i in indices)/len(indices) for j in range(3)]
        assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(mean,tree['nodes'][leaf]['values']))
        composition.append(dict(leaf=leaf,target_means=mean,role_counts=dict(Counter(rows[i]['role'] for i in indices)),source_counts=dict(Counter(rows[i]['source'] for i in indices))))
    errors=[[(p[j]-r['y'][j])**2 for j in range(3)] for p,r in zip(predictions,rows)]
    best=math.fsum(r['y'][2] for r in rows)/60
    constant_sse=math.fsum((r['y'][2]-best)**2 for r in rows);blue_sse=math.fsum(e[2] for e in errors)
    bluevalues=[n['values'][2] for n in tree['nodes'] if n['kind']=='leaf']
    means={role:math.fsum(p[2] for p,r in zip(predictions,rows) if r['role']==role)/10 for role in ['blue_decrease','blue_increase']}
    checks=dict(nonconstant_blue=max(bluevalues)-min(bluevalues)>1e-12,
        strict_gain_vs_best_constant=constant_sse-blue_sse>1e-12*max(1.,constant_sse),
        both_directions=means['blue_decrease']>1+1e-12 and means['blue_increase']<1-1e-12)
    used=Counter(names[n['feature']] for n in tree['nodes'] if n['kind']=='split')
    return dict(passed=True,classification='BLUE_FITTING_FEASIBILITY_PASS' if all(checks.values()) else 'BLUE_FITTING_FEASIBILITY_STOP',blue_checks=checks,
        SSE=math.fsum(v for e in errors for v in e),per_control=[math.fsum(e[j] for e in errors) for j in range(3)],
        per_role={role:math.fsum(v for e,r in zip(errors,rows) if r['role']==role for v in e) for role in roles},
        old40_subset_SSE=math.fsum(v for e,r in zip(errors,rows) if r['role'] in roles[:4] for v in e),
        best_constant_blue=best,best_constant_blue_SSE=constant_sse,blue_leaf_range=[min(bluevalues),max(bluevalues)],blue_role_mean_predictions=means,
        identity_max_control_deviation=[max(abs(p[j]-1) for p,r in zip(predictions,rows) if r['role']=='identity') for j in range(3)],
        split_features=dict(used),histogram_coordinates_used=any(n in names[25:] for n in used),leaf_composition=composition,
        held_predictions=0,refits=0,model_adopted=False,correction_quality_established=False)
