"""One fit-only clean-reference projection/prototype predictor, research only."""
from pathlib import Path
import copy,math
import numpy as np
from .portable_five_control_tree import f32
from .luminance_chroma_operator import parameters
from .camera_halfstop_neighbour import read,write,sha,score,summary,ROLES
from .paired_reference_prototype_scalar import verify_index
def controls(p):return parameters(p).tolist()

def block_energy(matrix):
    energies=[]
    for lo,hi in [(0,281),(281,4377)]:
        a=matrix[:,lo:hi];energy=float(np.square(a-a.mean(axis=0)).sum()/len(a))
        if not math.isfinite(energy) or energy<=0:raise ValueError('Zero/nonfinite block energy; no fallback')
        energies.append(energy)
    return energies

def project(index,x):
    x=np.asarray(x,dtype=np.float64).copy()
    for (lo,hi),e in zip([(0,281),(281,4377)],index['block_energy']):x[lo:hi]/=math.sqrt(e)
    x-=np.asarray(index['clean_mean'])
    if index['nuisance_rank']:
        basis=np.asarray(index['nuisance_basis']);x=x-(x@basis.T)@basis
    return x

def build_index(rows):
    rows=sorted(copy.deepcopy(rows),key=lambda r:r['case_id'])
    if len(rows)!=60 or len({r['source_id'] for r in rows})!=10:raise ValueError('Exact60/10fitting rows required')
    for r in rows:
        if len(r['x'])!=4377 or any(f32(v)!=v for v in r['x']):raise ValueError('4377finitefloat32 required')
        controls(r['y'])
    if set(r['role'] for r in rows)!=set(ROLES):raise ValueError('Six roles required')
    matrix=np.asarray([r['x'] for r in rows],dtype=np.float64)
    energy=block_energy(matrix)
    for (lo,hi),e in zip([(0,281),(281,4377)],energy):matrix[:,lo:hi]/=math.sqrt(e)
    clean_rows=[i for i,r in enumerate(rows) if r['role']=='identity']
    if len(clean_rows)!=10:raise ValueError('Ten fitting clean references required')
    mean=matrix[clean_rows].mean(axis=0);clean=matrix[clean_rows]-mean
    left,singular,right=np.linalg.svd(clean,full_matrices=False)
    rank_tol=max(clean.shape)*np.finfo(float).eps*float(singular[0])
    rank=int((singular>rank_tol).sum());basis=right[:rank]
    coefficients=(left[:,:rank]/singular[:rank]).T if rank else np.empty((0,10))
    centred=matrix-mean;projected=centred-(centred@basis.T)@basis
    tolerance=np.finfo(float).eps*4377*max(1.,float(np.linalg.norm(centred)))
    centres=[]
    for role in sorted(ROLES):
        ix=[i for i,r in enumerate(rows) if r['role']==role]
        if len(ix)!=10:raise ValueError('Source-equal ten rows per role required')
        centres.append(dict(role=role,projected_mean=projected[ix].mean(axis=0).tolist(),
            controls=[math.fsum(rows[i]['y'][j] for i in ix)/10 for j in range(5)],
            fitting_cases=[rows[i]['case_id'] for i in ix]))
    for i,a in enumerate(centres):
        for b in centres[i+1:]:
            if np.linalg.norm(np.asarray(a['projected_mean'])-b['projected_mean'])<=tolerance:
                raise ValueError('Effective prototype contrast unavailable at machine precision; no fallback')
    return dict(schema='truehue_paired_reference_prototype_research_v1',rows=rows,block_energy=energy,
        clean_case_ids=[rows[i]['case_id'] for i in clean_rows],clean_mean=mean.tolist(),nuisance_rank=rank,
        nuisance_basis=basis.tolist(),basis_combinations=coefficients.tolist(),singular_values=singular.tolist(),
        rank_tolerance=rank_tol,coincident_threshold=tolerance,centres=centres,dimensions=4377,
        query_clean_reference_required=False,model_ready=False)

def search(index,x):
    if len(x)!=4377 or any(f32(v)!=v for v in x):raise ValueError('4377float32query required')
    z=project(index,x);choices=[]
    for c in index['centres']:
        distance=float(np.square(z-np.asarray(c['projected_mean'])).sum())
        if not math.isfinite(distance):raise ValueError('Nonfinite prototype distance')
        choices.append((distance,c['role'],c['controls']))
    distance,role,p=min(choices,key=lambda c:(c[0],c[1]))
    return dict(prototype_role=role,squared_distance=distance,controls=list(p))


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

def select_fitting(rows,fold,*,generated_fixture):
    wanted=set(fold['fitting_cases']);selected={}
    if len(wanted)!=60:raise ValueError('Exactly60 fitting cases required')
    for row in rows:
        case_id=row['case_id']
        if case_id not in wanted:continue # No excluded feature or target payload access.
        if case_id in selected or row['source_id']==fold['held_source_id']:
            raise ValueError('Duplicate or held fitting source')
        if row['generated_fixture'] is not generated_fixture:raise ValueError('Provenance mismatch')
        x=row['x'];y=row['y']
        if len(x)!=4377 or any(f32(v)!=v for v in x):raise ValueError('4377finite float32 features required')
        controls(y)
        selected[case_id]=dict(case_id=case_id,source_id=row['source_id'],role=row['role'],
            generated_fixture=row['generated_fixture'],x=list(x),y=list(y))
    if set(selected)!=wanted:raise ValueError('Missing fitting cases')
    result=[selected[c] for c in fold['fitting_cases']]
    if len({r['source_id'] for r in result})!=10 or any(sum(r['role']==role for r in result)!=10 for role in ROLES):
        raise ValueError('Ten sources and ten fitting examples per role required')
    return result
