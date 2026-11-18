"""One frozen nested tree-selection study. No fitting or file access on import."""
import hashlib
import math
from pathlib import Path
import sys
import numpy as np
from sklearn.tree import DecisionTreeRegressor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from wb_feature_direct_workflow import SETTINGS,read,write,sha
from fivefold_tree_verify import route,verify_fit,verify_selection
from src.model_training.luminance_chroma_operator import parameters
DEPTHS=[2,4,6,None]
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def take(rows,wanted,forbidden):
    found={};wanted_set=set(wanted)
    for r in rows:
        if r['case_id'] not in wanted_set:continue
        if r['case_id'] in found or r['source_id'] in forbidden:raise ValueError('Duplicate/forbidden fitting payload')
        x=r['x'];y=r['y']
        if len(x)!=4410 or not np.isfinite(x).all() or np.asarray(x,np.float32).astype(float).tolist()!=x:raise ValueError('Finite float32 width4410 required')
        parameters(y);found[r['case_id']]=r
    if set(found)!=wanted_set or len(found)!=len(wanted):raise ValueError('Incomplete fitting roster')
    return [found[c] for c in wanted]


def validate(allocation,rows):
    assert allocation['depths']==DEPTHS and len(allocation['outer_folds'])==11 and len(rows)==66
    assert len({r['case_id'] for r in rows})==66 and len({(r['source_id'],r['role']) for r in rows})==66
    assert len({r['source_id'] for r in rows})==11 and set(r['role'] for r in rows)==set(ROLES)
    prepared=[]
    for outer in allocation['outer_folds']:
        excluded={outer['held_source_id']}
        allowed=take(rows,outer['outer_fitting_cases'],excluded)
        assert len(allowed)==60 and len({r['source_id'] for r in allowed})==10
        assert [r['case_id'] for r in rows if r['source_id'] in excluded]==outer['outer_evaluation_cases']
        sources=sorted({r['source_id'] for r in allowed},key=lambda s:(hashlib.sha256(('truehue-tree-cv-v1|'+s).encode()).hexdigest(),s))
        inners=[]
        for i,inner in enumerate(outer['inner_folds']):
            assert inner['index']==i
            val=set(sources[2*i:2*i+2])
            assert [r['case_id'] for r in allowed if r['source_id'] in val]==inner['validation_cases']
            assert [r['case_id'] for r in allowed if r['source_id'] not in val]==inner['fitting_cases']
            fitting=take(allowed,inner['fitting_cases'],excluded|val)
            assert len(fitting)==48 and len(inner['validation_cases'])==12
            assert len({r['source_id'] for r in fitting})==8
            inners.append((inner,fitting))
        assert len(inners)==5
        assert sorted(c for x in outer['inner_folds'] for c in x['validation_cases'])==sorted(outer['outer_fitting_cases'])
        prepared.append((outer,allowed,inners))
    return prepared


def choose_depth(scores):
    if len(scores)!=4 or not all(math.isfinite(s) for s in scores):raise ValueError('Four finite scores required')
    return next(i for i,value in enumerate(scores) if value<=min(scores)+1e-12)


def train_one(rows,depth,wanted,forbidden,factory):
    settings=dict(SETTINGS,max_depth=depth)
    x=np.asarray([r['x'] for r in rows],np.float32);y=np.asarray([r['y'] for r in rows],float)
    native=factory(**settings);native.fit(x,y);t=native.tree_;nodes=[]
    for i in range(t.node_count):
        if t.children_left[i]==-1:nodes.append(dict(kind='leaf',values=t.value[i,:,0].tolist()))
        else:nodes.append(dict(kind='split',feature=int(t.feature[i]),threshold=float(t.threshold[i]),left=int(t.children_left[i]),right=int(t.children_right[i])))
    model=dict(schema='truehue_camera_control_cart_research_v1',dimensions=4410,
               target_names=['gamma','exposure_gain','red_balance','blue_balance','chroma_scale'],
               settings=native.get_params(deep=False),comparison='<=',nodes=nodes)
    assert model['settings']==settings
    scalar=[route(model,r['x']) for r in rows]
    assert [p for leaf,p in scalar]==native.predict(x).tolist()
    assert [leaf for leaf,p in scalar]==native.apply(x).tolist()
    verify_fit(model,rows,wanted,forbidden,settings)
    return model


def run_nested(allocation,rows,out,factory=DecisionTreeRegressor):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    prepared=validate(allocation,rows) # All row/width/fold guards before output/fitting.
    assert len({r['generated_fixture'] for r in rows})==1
    out.mkdir();(out/'models').mkdir();write(out/'allocation.json',allocation);write(out/'rows.json',rows)
    write(out/'selection_config.json',dict(settings=SETTINGS,depths=DEPTHS,tie_tolerance=1e-12,score='source_role_equal_native_control_MAE'))
    entries=[];started=0
    try:
        for oi,(outer,allowed,inners) in enumerate(prepared):
            for di,depth in enumerate(DEPTHS):
                for inner,fitting in inners:
                    started+=1;assert started<=220
                    write(out/'fit_accounting.json',dict(started=started,maximum=231,phase='inner'))
                    val_sources={r['source_id'] for r in allowed if r['case_id'] in set(inner['validation_cases'])}
                    model=train_one(fitting,depth,inner['fitting_cases'],{outer['held_source_id']}|val_sources,factory)
                    key=f'{oi}_{di}_{inner["index"]}';path='models/inner_'+key+'.json';write(out/path,model)
                    entries.append(dict(key=key,path=path,sha256=sha(out/path)))
            print('Inner models verified '+str(started)+'/220',flush=True)
        write(out/'all_inner_fits_verified.json',dict(verified_fits=220,fitting_routes=10560,models=entries))
        models={e['key']:read(out/e['path']) for e in entries}
        for e in entries:assert sha(out/e['path'])==e['sha256']
        inner_predictions=[];selections=[]
        for oi,(outer,allowed,inners) in enumerate(prepared):
            # The selector only receives this outer fitting projection, never outer targets.
            byid={r['case_id']:r for r in allowed};candidates=[]
            for di,depth in enumerate(DEPTHS):
                own=[]
                for inner,_ in inners:
                    key=f'{oi}_{di}_{inner["index"]}';model=models[key]
                    queries=[{k:byid[c][k] for k in ['case_id','source_id','role','x']} for c in inner['validation_cases']]
                    for q in queries:
                        leaf,p=route(model,q['x']);parameters(p)
                        errors=[abs(a-b) for a,b in zip(p,byid[q['case_id']]['y'])]
                        record={k:q[k] for k in ['case_id','source_id','role']}|dict(key=key,leaf=leaf,controls=p,absolute_errors=errors)
                        own.append(record);inner_predictions.append(record)
                assert len(own)==60
                candidates.append(dict(depth=depth,MAE=math.fsum(v for p in own for v in p['absolute_errors'])/300,
                    per_control=[math.fsum(p['absolute_errors'][k] for p in own)/60 for k in range(5)],
                    per_role={role:math.fsum(v for p in own if p['role']==role for v in p['absolute_errors'])/50 for role in ROLES}))
            chosen=choose_depth([c['MAE'] for c in candidates])
            selections.append(dict(held_source_id=outer['held_source_id'],depth=DEPTHS[chosen],candidates=candidates))
        write(out/'inner_predictions.json',inner_predictions);write(out/'selections.json',selections)
        selection_proof=verify_selection(out,rows,allocation);write(out/'selection_verified.json',selection_proof)
        outer_entries=[];outer_models={};constants={}
        for oi,((outer,allowed,_),selection) in enumerate(zip(prepared,selections)):
            started+=1;assert started<=231
            write(out/'fit_accounting.json',dict(started=started,maximum=231,phase='selected_outer'))
            model=train_one(allowed,selection['depth'],outer['outer_fitting_cases'],{outer['held_source_id']},factory)
            path=f'models/outer_{oi}.json';write(out/path,model)
            outer_entries.append(dict(source=outer['held_source_id'],path=path,sha256=sha(out/path),selected_depth=selection['depth']))
            outer_models[outer['held_source_id']]=model
            constants[outer['held_source_id']]=[math.fsum(r['y'][k] for r in allowed)/60 for k in range(5)]
        assert started==231
        write(out/'all_outer_fits_verified.json',dict(verified_outer_fits=11,total_real_or_generated_fits=231,fitting_routes=660,models=outer_entries))
        for e in outer_entries:assert sha(out/e['path'])==e['sha256']
        inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
        write(out/'inference.json',inference);sealed=[]
        for r in inference:
            model=outer_models[r['source_id']];leaf,p=route(model,r['x']);parameters(p)
            sealed.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(leaf=leaf,controls=p,constant=constants[r['source_id']],selected_depth=model['settings']['max_depth']))
        write(out/'held_controls_sealed.json',sealed)
        write(out/'prediction_seal.json',dict(predictions=66,sha256=sha(out/'held_controls_sealed.json')))
        return selections
    except Exception as exc:
        write(out/'failure.json',dict(error=str(exc),started_fits=started,maximum=231));raise
