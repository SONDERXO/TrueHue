"""Scalar tree and selection verification. No model fitting or solver imports."""
import math
import struct
from collections import Counter
from pathlib import Path
import json
import hashlib

DEPTHS=[2,4,6,None]
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a,b):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12),(a,b)


def route(model,x):
    assert len(x)==model['dimensions']==4410
    i=0;seen=set();depth=0
    while model['nodes'][i]['kind']=='split':
        assert i not in seen;seen.add(i)
        node=model['nodes'][i]
        feature=node['feature'];assert 0<=feature<4410 and math.isfinite(node['threshold'])
        value=struct.unpack('!f',struct.pack('!f',x[feature]))[0]
        i=node['left'] if value<=node['threshold'] else node['right'];depth+=1
        if model['settings']['max_depth'] is not None:assert depth<=model['settings']['max_depth']
        assert depth<len(model['nodes'])
    return i,model['nodes'][i]['values']


def verify_fit(model,rows,wanted,forbidden,settings):
    assert [r['case_id'] for r in rows]==wanted and len(rows) in [48,60]
    assert len(set(wanted))==len(wanted)
    assert not set(r['source_id'] for r in rows)&set(forbidden)
    assert model['settings']==settings and model['dimensions']==4410
    assert model['schema']=='truehue_camera_control_cart_research_v1'
    assert model['comparison']=='<=' and model['settings']['max_depth'] in DEPTHS
    assert model['target_names']==['gamma','exposure_gain','red_balance','blue_balance','chroma_scale']
    assert Counter(r['role'] for r in rows)==Counter({role:len(rows)//6 for role in ROLES})
    assert len({r['source_id'] for r in rows})==len(rows)//6
    leaves={}
    for row in rows:
        leaf,p=route(model,row['x']);leaves.setdefault(leaf,[]).append(row)
    assert set(leaves)=={i for i,node in enumerate(model['nodes']) if node['kind']=='leaf'}
    for leaf,members in leaves.items():
        for k in range(5):close(model['nodes'][leaf]['values'][k],math.fsum(r['y'][k] for r in members)/len(members))
    return len(rows)


def verify_selection(root,rows,allocation):
    root=Path(root);byid={r['case_id']:r for r in rows}
    entries=read(root/'all_inner_fits_verified.json')['models'];assert len(entries)==220
    predictions=read(root/'inner_predictions.json');assert len(predictions)==2640
    config=read(root/'selection_config.json');assert config['depths']==DEPTHS and config['tie_tolerance']==1e-12
    selections=read(root/'selections.json');assert len(selections)==11
    models={}
    for e in entries:
        assert sha(root/e['path'])==e['sha256']
        models[e['key']]=read(root/e['path'])
    fit_routes=0;validation_routes=0;expected_selections=[]
    for oi,outer in enumerate(allocation['outer_folds']):
        allowed={c:byid[c] for c in outer['outer_fitting_cases']}
        assert all(r['source_id']!=outer['held_source_id'] for r in allowed.values())
        scores=[];details=[]
        for di,depth in enumerate(DEPTHS):
            own=[]
            for inner in outer['inner_folds']:
                key=f'{oi}_{di}_{inner["index"]}'
                model=models[key];fit=[allowed[c] for c in inner['fitting_cases']]
                forbidden={outer['held_source_id']}|{allowed[c]['source_id'] for c in inner['validation_cases']}
                settings=dict(config['settings'],max_depth=depth)
                fit_routes+=verify_fit(model,fit,inner['fitting_cases'],forbidden,settings)
                actual=[p for p in predictions if p['key']==key]
                assert [p['case_id'] for p in actual]==inner['validation_cases']
                for p in actual:
                    row=allowed[p['case_id']];leaf,controls=route(model,row['x']);validation_routes+=1
                    assert p['source_id']==row['source_id'] and p['role']==row['role']
                    assert p['leaf']==leaf and p['controls']==controls
                    errors=[abs(a-b) for a,b in zip(controls,row['y'])]
                    for a,b in zip(errors,p['absolute_errors']):close(a,b)
                    own.append(p)
            assert len(own)==60 and len({p['case_id'] for p in own})==60
            value=math.fsum(v for p in own for v in p['absolute_errors'])/300
            scores.append(value)
            details.append({'depth':depth,'MAE':value,
                'per_control':[math.fsum(p['absolute_errors'][k] for p in own)/60 for k in range(5)],
                'per_role':{role:math.fsum(v for p in own if p['role']==role for v in p['absolute_errors'])/50 for role in ROLES}})
        chosen=next(i for i,value in enumerate(scores) if value<=min(scores)+1e-12)
        s=selections[oi]
        assert s['held_source_id']==outer['held_source_id'] and s['depth']==DEPTHS[chosen]
        assert len(s['candidates'])==4
        for a,b in zip(details,s['candidates']):
            assert a['depth']==b['depth'];close(a['MAE'],b['MAE'])
            for u,v in zip(a['per_control'],b['per_control']):close(u,v)
            for role in ROLES:close(a['per_role'][role],b['per_role'][role])
        expected_selections.append(s['depth'])
    assert fit_routes==10560 and validation_routes==2640
    return dict(inner_fitting_routes=fit_routes,inner_validation_routes=validation_routes,selected_depths=expected_selections)


def verify_outer(root,rows,allocation):
    root=Path(root);byid={r['case_id']:r for r in rows}
    config=read(root/'selection_config.json')
    choices=read(root/'selections.json');cert=read(root/'all_outer_fits_verified.json')
    assert cert['verified_outer_fits']==11 and cert['total_real_or_generated_fits']==231
    assert read(root/'fit_accounting.json')['started']==231
    models={};fitting_routes=0
    for outer,choice,e in zip(allocation['outer_folds'],choices,cert['models']):
        assert e['source']==choice['held_source_id']==outer['held_source_id']
        assert e['selected_depth']==choice['depth'] and sha(root/e['path'])==e['sha256']
        model=read(root/e['path'])
        fit=[byid[c] for c in outer['outer_fitting_cases']]
        fitting_routes+=verify_fit(model,fit,outer['outer_fitting_cases'],{outer['held_source_id']},dict(config['settings'],max_depth=choice['depth']))
        models[e['source']]=(model,[math.fsum(r['y'][k] for r in fit)/60 for k in range(5)])
    inference=read(root/'inference.json');sealed=read(root/'held_controls_sealed.json')
    assert len(sealed)==len(inference)==66
    assert sha(root/'held_controls_sealed.json')==read(root/'prediction_seal.json')['sha256']
    for q,p in zip(inference,sealed):
        assert set(q)=={'case_id','source_id','role','generated_fixture','x'}
        assert q['x']==byid[q['case_id']]['x']
        model,constant=models[q['source_id']];leaf,controls=route(model,q['x'])
        assert p['controls']==controls and p['leaf']==leaf and p['selected_depth']==model['settings']['max_depth']
        assert all(p[k]==q[k] for k in ['case_id','source_id','role','generated_fixture'])
        for a,b in zip(p['constant'],constant):close(a,b)
    assert fitting_routes==660
    return dict(outer_fitting_routes=660,outer_held_routes=66,maximum_fit_budget_verified=231)
