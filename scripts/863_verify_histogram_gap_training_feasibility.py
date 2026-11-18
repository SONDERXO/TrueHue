"""Independent standard-library scalar replay; never imports trainer/sklearn."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,struct
ROOT=Path(__file__).resolve().parents[1]

def route(model,row):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in row];i=0
    while model['nodes'][i]['kind']=='split':
        n=model['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    return i,list(model['nodes'][i]['values'])

def validate(model,names):
    assert model['schema_version']=='truehue_regression_tree_v1' and model['feature_names']==names
    assert model['input_dtype']=='float32' and model['threshold_dtype']=='float64' and model['comparison']=='<=' and model['root']==0
    assert model['target_names']==['gamma','red_gain','blue_gain']
    nodes=model['nodes'];seen=set();pending=[(0,0)]
    assert 1<=len(nodes)<=31
    while pending:
        i,depth=pending.pop();assert type(i) is int and 0<=i<len(nodes) and i not in seen and depth<=4;seen.add(i);n=nodes[i]
        if n['kind']=='leaf':assert len(n['values'])==3 and all(math.isfinite(v) and v>0 for v in n['values'])
        else:
            assert n['kind']=='split' and type(n['feature']) is int and 0<=n['feature']<len(names) and math.isfinite(n['threshold'])
            pending.extend([(n['left'],depth+1),(n['right'],depth+1)])
    assert len(seen)==len(nodes)

def metrics(model,rows,width):
    errors=[];members={};predictions=[];leaves=[]
    for i,r in enumerate(rows):
        leaf,values=route(model,r['x'][:width]);members.setdefault(leaf,[]).append(i)
        errors.append([(a-b)**2 for a,b in zip(values,r['y'])]);predictions.append(values);leaves.append(leaf)
    return dict(SSE=math.fsum(v for row in errors for v in row),
        per_control=[math.fsum(row[j] for row in errors) for j in range(3)],
        per_role={role:math.fsum(v for i,row in enumerate(errors) if rows[i]['role']==role for v in row) for role in sorted({r['role'] for r in rows})},
        identity_max_abs_control_deviation=[max((abs(predictions[i][j]-1) for i,r in enumerate(rows) if r['role']=='identity'),default=0.) for j in range(3)],
        members=members,predictions=predictions,leaves=leaves)

def verify(candidate,baseline,rows,replay,names):
    validate(candidate,names);validate(baseline,names[:16])
    assert rows and len({r['case_id'] for r in rows})==len(rows)
    assert all(len(r['x'])==22 and len(r['y'])==3 and all(math.isfinite(v) for v in r['x']) and all(math.isfinite(v) and v>0 for v in r['y']) for r in rows)
    current=metrics(candidate,rows,22);before=metrics(baseline,rows,16)
    assert current['predictions']==replay['sklearn_predictions'] and current['leaves']==replay['sklearn_leaf_ids']
    assert before['predictions']==replay['saved_parent_predictions'] and replay['fit_calls']==1
    composition=[]
    for leaf,ids in current['members'].items():
        means=[math.fsum(rows[i]['y'][j] for i in ids)/len(ids) for j in range(3)]
        assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(means,candidate['nodes'][leaf]['values']))
        composition.append(dict(leaf=leaf,case_ids=[rows[i]['case_id'] for i in ids],
            role_counts=dict(Counter(rows[i]['role'] for i in ids)),source_counts=dict(Counter(rows[i]['source'] for i in ids)),target_means=means))
    features=Counter(names[n['feature']] for n in candidate['nodes'] if n['kind']=='split')
    gain=before['SSE']-current['SSE'];tol=1e-12*max(1.,before['SSE'])
    return dict(passed=True,rows=len(rows),classification='STRICT_FITTING_IMPROVEMENT' if gain>tol else ('FITTING_WORSE' if gain < -tol else 'NO_STRICT_FITTING_GAIN'),
        baseline=before,candidate=current,leaf_composition=composition,split_features=dict(features),
        added_features_used=any(n in features for n in names[16:]),raw_SSE_gain=gain,
        held_predictions=0,model_adopted=False,correction_quality_established=False,refits=0)

def main():
    out=ROOT/'outputs/histogram_gap_training_feasibility_v1';dest=out/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    read=lambda n:json.loads((out/n).read_text(encoding='utf-8'))
    receipt=read('execution_plan_PRIVATE.json')
    for table in ['input_sha256','code_sha256']:
        for name,digest in receipt[table].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    assert read('status_PRIVATE.json')['fit_calls']==1
    planpath=ROOT/'outputs/histogram_gap_training_feasibility_design_v1/plan_PRIVATE.json'
    assert hashlib.sha256(planpath.read_bytes()).hexdigest()==receipt['plan_sha256']
    plan=json.loads(planpath.read_text(encoding='utf-8'));snapshot=read('fitting_inputs_PRIVATE.json')
    wanted={r['case_id'] for r in plan['fitting_records']}
    audited=json.loads((ROOT/plan['audited_features_path']).read_text(encoding='utf-8'))
    gaps={r['case_id']:r for r in audited if r['case_id'] in wanted}
    assert len(gaps)==40 and [r['case_id'] for r in snapshot]==[r['case_id'] for r in plan['fitting_records']]
    for saved,binding in zip(snapshot,plan['fitting_records']):
        original=json.loads((ROOT/binding['record']).read_text(encoding='utf-8'));gap=gaps[binding['case_id']]
        expected=original['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gap['features'][n]))[0] for n in plan['new_feature_names']]
        assert saved['x']==expected and saved['y']==original['nominal_controls']
        assert saved['source']==original['publisher_group']==binding['source']!=plan['excluded_group']
        assert saved['role']==original['experimental_role']==binding['role']
    text=(ROOT/plan['baseline']['path']).read_text(encoding='utf-8').lstrip()
    first,_=json.JSONDecoder().raw_decode(text[1:].lstrip())
    assert first['tree']==read('baseline_SAVED_PRIVATE.json')
    replay=read('training_replay_PRIVATE.json')
    assert all(replay['settings'][k]==value for k,value in plan['settings'].items())
    result=verify(read('candidate_PRIVATE.json'),first['tree'],snapshot,replay,receipt['feature_names'])
    assert result['rows']==40
    result['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.json')}
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result['classification'])

if __name__=='__main__':main()
