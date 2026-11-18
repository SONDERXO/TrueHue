"""Independent scalar281input checks; no trainer, portable runtime, NumPy or sklearn."""
from collections import Counter
import math,struct

def route(tree,row):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in row];i=0
    while tree['nodes'][i]['kind']=='split':
        n=tree['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    return i,list(tree['nodes'][i]['values'])

def validate(tree,names):
    assert tree['schema_version']=='truehue_regression_tree_v1' and tree['feature_names']==names
    assert tree['target_names']==['gamma','red_gain','blue_gain'] and tree['root']==0
    assert tree['input_dtype']=='float32' and tree['threshold_dtype']=='float64' and tree['comparison']=='<='
    assert 1<=len(tree['nodes'])<=31
    pending=[(0,0)];seen=set()
    while pending:
        index,depth=pending.pop();assert type(index) is int and 0<=index<len(tree['nodes']) and index not in seen and depth<=4
        seen.add(index);n=tree['nodes'][index]
        if n['kind']=='leaf':assert len(n['values'])==3 and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in n['values'])
        else:
            assert n['kind']=='split' and type(n['feature']) is int and 0<=n['feature']<len(names) and type(n['threshold']) in (int,float) and math.isfinite(n['threshold'])
            pending.extend([(n['left'],depth+1),(n['right'],depth+1)])
    assert len(seen)==len(tree['nodes'])

def metrics(tree,rows,width):
    predictions=[];leaves=[];members={}
    for i,row in enumerate(rows):
        leaf,value=route(tree,row['x'][:width]);predictions.append(value);leaves.append(leaf);members.setdefault(leaf,[]).append(i)
    errors=[[(p[j]-r['y'][j])**2 for j in range(3)] for p,r in zip(predictions,rows)]
    return dict(SSE=math.fsum(v for e in errors for v in e),per_control=[math.fsum(e[j] for e in errors) for j in range(3)],
        per_role={role:math.fsum(v for e,r in zip(errors,rows) if r['role']==role for v in e) for role in sorted({r['role'] for r in rows})},
        identity_max_abs_control_deviation=[max((abs(p[j]-1) for p,r in zip(predictions,rows) if r['role']=='identity'),default=0) for j in range(3)],
        predictions=predictions,leaves=leaves,members=members)

def verify(candidate,baseline,rows,replay,names):
    assert len(names)==281 and len(set(names))==281
    expected=['joint_colour_available','joint_colour_positive_fraction','joint_colour_clipped_fraction']+[f'joint_colour_u{i:02}_v{j:02}' for i in range(16) for j in range(16)]
    assert names[22:]==expected
    validate(candidate,names);validate(baseline,names[:22])
    assert rows and len({r['case_id'] for r in rows})==len(rows)
    for row in rows:
        assert len(row['x'])==281 and all(type(v) in (int,float) and math.isfinite(v) and struct.unpack('!f',struct.pack('!f',v))[0]==v for v in row['x'])
        assert len(row['y'])==3 and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in row['y'])
    settings=dict(criterion='squared_error',splitter='best',max_depth=4,random_state=42,min_samples_leaf=1,min_samples_split=2,
        min_weight_fraction_leaf=0.,max_features=None,max_leaf_nodes=None,min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
    assert replay['settings']==settings and replay['fit_calls']==1 and replay['held_predictions']==0
    current=metrics(candidate,rows,281);before=metrics(baseline,rows,22)
    assert current['predictions']==replay['candidate_predictions'] and current['leaves']==replay['candidate_leaves']
    assert before['predictions']==replay['baseline_predictions']
    composition=[]
    assert set(current['members'])=={i for i,n in enumerate(candidate['nodes']) if n['kind']=='leaf'}
    for leaf,indices in current['members'].items():
        means=[math.fsum(rows[i]['y'][j] for i in indices)/len(indices) for j in range(3)]
        assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(means,candidate['nodes'][leaf]['values']))
        composition.append(dict(leaf=leaf,target_means=means,case_ids=[rows[i]['case_id'] for i in indices],
            role_counts=dict(Counter(rows[i]['role'] for i in indices)),source_counts=dict(Counter(rows[i]['source'] for i in indices))))
    features=Counter(names[n['feature']] for n in candidate['nodes'] if n['kind']=='split')
    gain=before['SSE']-current['SSE'];tol=1e-12*max(1.,before['SSE'])
    return dict(passed=True,rows=len(rows),classification='STRICT_FITTING_IMPROVEMENT' if gain>tol else 'NO_STRICT_FITTING_GAIN',
        raw_SSE_gain=gain,candidate=current,baseline=before,leaf_composition=composition,split_features=dict(features),
        histogram_coordinates_used=any(n in names[25:] for n in features),availability_or_count_fields_used=any(n in names[22:25] for n in features),
        correction_quality_established=False,model_adopted=False,held_predictions=0,refits=0)
