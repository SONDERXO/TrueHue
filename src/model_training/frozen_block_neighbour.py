"""One fixed block-balanced nearest-neighbour research predictor."""
from pathlib import Path
import math
import copy
import numpy as np
from .portable_five_control_tree import controls,f32
from .reiqa_tree_workflow import select_fitting
from .five_control_prediction_workflow import read,write,sha,score,summary,ROLES
from .frozen_block_neighbour_scalar import verify_index

def build_index(rows):
    if len(rows)<2 or len({r['case_id'] for r in rows})!=len(rows):raise ValueError('Distinct stored rows required')
    rows=sorted(copy.deepcopy(rows),key=lambda r:r['case_id'])
    for r in rows:
        if len(r['x'])!=4377 or any(f32(v)!=v for v in r['x']):raise ValueError('4377float32 required')
        controls(r['y'])
    matrix=np.asarray([r['x'] for r in rows],dtype=np.float64)
    energies=[]
    for lo,hi in [(0,281),(281,4377)]:
        block=matrix[:,lo:hi]
        energy=float(np.square(block-block.mean(axis=0)).sum()/len(rows))
        if not math.isfinite(energy) or energy<=0:raise ValueError('Zero/nonfinite block dispersion; stop no fallback')
        energies.append(energy)
    return dict(schema='truehue_two_block_1nn_research_v1',rows=rows,block_energy=energies,
                dimensions=4377,k=1,blocks=[[0,281],[281,4377]],tie='lexical_case_id',weights='equal_blocks')

def search(index,x):
    if len(x)!=4377 or any(f32(v)!=v for v in x):raise ValueError('4377float32 query required')
    matrix=np.asarray([r['x'] for r in index['rows']],dtype=np.float64)
    query=np.asarray(x,dtype=np.float64)
    distances=np.zeros(len(matrix),dtype=np.float64)
    for (lo,hi),energy in zip(index['blocks'],index['block_energy']):
        distances+=np.square(matrix[:,lo:hi]-query[lo:hi]).sum(axis=1)/energy
    if not np.isfinite(distances).all():raise ValueError('Nonfinite distances')
    i=int(np.argmin(distances));chosen=index['rows'][i]
    return dict(neighbour_case_id=chosen['case_id'],neighbour_source_id=chosen['source_id'],
                squared_distance=float(distances[i]),controls=list(chosen['y']))

def fit_all(plan,rows,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    if len(plan['folds'])!=11 or len(plan['feature_names'])!=4377:raise ValueError('Frozen11fold4377plan required')
    # Complete all fitting projections before any index construction.
    fitting=[select_fitting(rows,f,generated_fixture=plan['generated_fixture']) for f in plan['folds']]
    out.mkdir();models=[]
    try:
        for fold,fit in zip(plan['folds'],fitting):
            folder=out/fold['held_source_id'];folder.mkdir()
            write(out/'index_accounting.json',dict(started=len(models)+1,maximum=11))
            index=build_index(fit)
            replay=[dict(case_id=r['case_id'],**search(index,r['x'])) for r in fit]
            proof=verify_index(index,fit,replay,fold)
            constant=[math.fsum(r['y'][j] for r in fit)/60 for j in range(5)]
            for name,value in [('index',index),('fitting_rows',fit),('replay',replay),('verification',proof)]:write(folder/(name+'.json'),value)
            models.append(dict(held_source_id=fold['held_source_id'],constant_controls=constant,
                **{name+'_path':str(folder/(name+'.json')) for name in ['index','fitting_rows','replay','verification']},
                **{name+'_sha256':sha(folder/(name+'.json')) for name in ['index','fitting_rows','replay','verification']}))
            print(f'Index and scalar proof {len(models)}/11',flush=True)
        write(out/'all_indices_verified.json',dict(passed=True,index_constructions=11,fitting_routes=660,held_predictions=0,models=models))
    except Exception as e:
        write(out/'failure.json',dict(verified_indices=len(models),error=str(e)));raise
    return models

def predict_held(plan,inference,models,out):
    out=Path(out);cert=read(out/'all_indices_verified.json')
    if not cert['passed'] or cert['index_constructions']!=11 or cert['models']!=models:raise ValueError('All11indices barrier required')
    by_source={m['held_source_id']:m for m in models};by_case={r['case_id']:r for r in inference}
    if set(by_source)!={f['held_source_id'] for f in plan['folds']}:raise ValueError('Incomplete index set')
    for m in models:
        for key in ['index','fitting_rows','replay','verification']:
            if sha(m[key+'_path'])!=m[key+'_sha256']:raise ValueError('Index proof changed')
    predictions=[]
    for fold in plan['folds']:
        m=by_source[fold['held_source_id']];index=read(m['index_path'])
        for case_id in fold['evaluation_cases']:
            r=by_case[case_id]
            if r['source_id']!=fold['held_source_id']:raise ValueError('Held source mismatch')
            p=search(index,r['x'])
            predictions.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|
                p|dict(constant_controls=m['constant_controls']))
    if len(predictions)!=66:raise ValueError('Complete66required')
    write(out/'held_controls_sealed.json',predictions)
    return predictions
