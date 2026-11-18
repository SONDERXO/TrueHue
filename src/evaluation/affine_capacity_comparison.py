"""Matched reference-aware five-versus-saved-three capacity diagnostic."""
from pathlib import Path
import json
import hashlib
import math
import numpy as np
from src.model_training import affine_prepower_targets as target
from src.evaluation.directional_recoverability import ROLES, metrics, regions, write, array_hash


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def load_baseline(base, relative_run, hashes, source_ids, *, generated_fixture):
    base=Path(base).resolve();run=(base/relative_run).resolve()
    if not run.is_relative_to(base) or len(source_ids)!=11 or len(set(source_ids))!=11:
        raise ValueError('Fixed eleven-source cached run required')
    for name,digest in hashes.items():
        p=(base/name).resolve()
        if not p.is_relative_to(base) or sha(p)!=digest:
            raise ValueError('Baseline artifact hash mismatch')
    def bound(p):
        if str(p.relative_to(base)) not in hashes or sha(p)!=hashes[str(p.relative_to(base))]:
            raise ValueError('Every decoded baseline artifact must be bound')
        return p
    cases=[]
    for source_id in source_ids:
        folder=run/source_id
        with np.load(bound(folder/'support.npz'),allow_pickle=False) as pack:
            support={k:pack[k].copy() for k in ['reference','alpha','protected']}
        target.support(support['alpha'],support['protected'],support['reference'].shape[:2])
        for role in ROLES:
            old=read(bound(folder/(role+'.json')))
            if old['source_id']!=source_id or old['role']!=role or old['generated_fixture'] is not generated_fixture:
                raise ValueError('Baseline case/provenance mismatch')
            with np.load(bound(folder/(role+'.npz')),allow_pickle=False) as pack:
                image=pack['input'].copy();old_output=pack['output'].copy()
            case=dict(source_id=source_id,role=role,generated_fixture=generated_fixture,
                image=image,baseline_output=old_output,baseline=old,**support)
            # Check every witness/input before candidate fits begin.
            witness(case)
            cases.append(case)
    if len(cases)!=66:raise ValueError('Exactly66cached cases required')
    return cases


def witness(case):
    old=case['baseline'];p=old['target']['parameters']+[1.,0.]
    image,reference,alpha,protected=[case[k] for k in ['image','reference','alpha','protected']]
    output=target.render_rgb8(image,alpha,protected,p)
    if not np.array_equal(output,case['baseline_output']):raise ValueError('Nested baseline witness mismatch')
    float_output=target.render_float(image.astype(float)/255,alpha,protected,p)
    mse=float(np.mean((float_output[alpha>0]-reference[alpha>0]/255)**2))
    if not math.isclose(mse,old['target'].get('float_rmse',0.)**2,abs_tol=1e-12,rel_tol=1e-12):
        raise ValueError('Nested baseline objective mismatch')
    for name,mask in regions(alpha).items():
        saved=old['regions'][name]
        if saved['pixels']!=int(mask.sum()):raise ValueError('Baseline region mismatch')
        for label,im in [('input',image),('output',case['baseline_output'])]:
            actual=metrics(im,reference,mask)
            if actual is None:
                if saved[label] is not None:raise ValueError('Baseline empty region mismatch')
            else:
                for key in actual:
                    if not math.isclose(actual[key],saved[label][key],abs_tol=1e-10,rel_tol=1e-10):
                        raise ValueError('Baseline metric mismatch')
    return dict(controls=p,float_mse=mse,RGB8_exact=True)


def run_case(case,*,fitter=target.fit_rgb8_target):
    baseline_witness=witness(case)
    keys=['image','reference','alpha','protected','baseline_output']
    before={k:array_hash(case[k]) for k in keys}
    image,reference,alpha,protected=[case[k] for k in ['image','reference','alpha','protected']]
    result=fitter(image,reference,alpha,protected,generated_fixture=case['generated_fixture'])
    output=None
    if result['parameters'] is not None:
        output=target.render_rgb8(image,alpha,protected,result['parameters'])
        if not np.array_equal(output[alpha==0],image[alpha==0]) or not np.array_equal(output[protected],image[protected]):
            raise AssertionError('Preservation failed')
        if case['role']=='identity' and not np.array_equal(output,reference):
            raise AssertionError('Identity changed')
    record=dict(source_id=case['source_id'],role=case['role'],generated_fixture=case['generated_fixture'],
        baseline_target=case['baseline']['target'],baseline_regions=case['baseline']['regions'],
        baseline_witness=baseline_witness,target=result,regions={},model_ready=False)
    for name,mask in regions(alpha).items():
        old=case['baseline']['regions'][name]['output']
        new=metrics(output,reference,mask) if output is not None else None
        record['regions'][name]=dict(pixels=int(mask.sum()),output=new,
            improvement_over_baseline={k:old[k]-new[k] for k in old} if old is not None and new is not None else None)
    record['float_mse_delta_to_baseline']=result.get('float_mse')-baseline_witness['float_mse'] if result['parameters'] is not None else None
    if before!={k:array_hash(case[k]) for k in keys}:raise AssertionError('Cached source mutated')
    return record,output


def summarize(records):
    summary={}
    for role in ROLES:
        own=[r for r in records if r['role']==role]
        paired=[r for r in own if r['target']['parameters'] is not None]
        primary={}
        for key in ['RGB','DE']:
            primary[key]={name:math.fsum(r[block]['primary'][field][key] for r in paired)/len(paired) if paired else None
                for name,block,field in [('baseline','baseline_regions','output'),('candidate','regions','output'),('improvement','regions','improvement_over_baseline')]}
        summary[role]=dict(attempted=len(own),available=len(paired),primary=primary,
            unavailable_sources=[r['source_id'] for r in own if r['target']['parameters'] is None],
            RGB_regressions=[r['source_id'] for r in paired if r['regions']['primary']['improvement_over_baseline']['RGB'] < -1e-10],
            DE_regressions=[r['source_id'] for r in paired if r['regions']['primary']['improvement_over_baseline']['DE'] < -1e-10],
            worse_float_objectives=[r['source_id'] for r in paired if r['float_mse_delta_to_baseline']>1e-12])
    coverage=len(records)==66 and all(summary[r]['attempted']==summary[r]['available']==11 for r in ROLES)
    identity=coverage and all(r['target']['parameters']==[1.,1.,1.,1.,0.] and r['regions']['primary']['output']=={'RGB':0.,'DE':0.}
        for r in records if r['role']=='identity')
    nonworse=coverage and all(summary[role]['primary'][key]['improvement']>=-1e-10
        for role in ROLES if role!='identity' for key in ['RGB','DE'])
    exposure=coverage and any(all(summary[role]['primary'][key]['improvement']>1e-10 for key in ['RGB','DE'])
        for role in ['exposure_under','exposure_over','combined_under','combined_over'])
    return dict(by_role=summary,checks=dict(coverage=coverage,identity=identity,
        each_role_RGB_and_DE_nonworse=nonworse,one_exposure_role_strictly_better=exposure),
        status='NUMERIC_CAPACITY_ELIGIBLE_ONLY' if coverage and identity and nonworse and exposure else 'NOT_ADVANCED',
        model_ready=False,automatic_training_authorized=False)


def execute(cases,destination,*,fitter=target.fit_rgb8_target):
    destination=Path(destination)
    if destination.exists():raise FileExistsError('Preserve completed or partial comparison')
    if len(cases)!=66 or len({(c['source_id'],c['role']) for c in cases})!=66:
        raise ValueError('Frozen66case roster required')
    for case in cases:witness(case)
    destination.mkdir(parents=True)
    records=[]
    try:
        for case in cases:
            record,output=run_case(case,fitter=fitter)
            folder=destination/case['source_id'];folder.mkdir(exist_ok=True)
            arrays={}
            if output is not None:arrays['output']=output
            np.savez(folder/(case['role']+'.npz'),**arrays)
            write(folder/(case['role']+'.json'),record)
            records.append(record)
        write(destination/'summary.json',summarize(records))
        write(destination/'status.json',dict(status='complete',records=66,new_baseline_fits=0,tree_fits=0))
    except Exception as error:
        write(destination/'failure.json',dict(status='failed_preserved',completed=len(records),error=str(error)))
        raise
    return records
