"""Fixed input-only coefficient diagnostic; never renders portrait corrections."""
import json
import math
from pathlib import Path
import numpy as np
from wb_cue_adapter import ROOT, ASSETS, SOURCE, sha, load_model, extract

PROBES = np.array([[.2,.2,.2],[.5,.5,.5],[.8,.8,.8],[.2,.4,.6],[.4,.6,.2],[.6,.2,.4]])
ROLES = ('identity','colour_only','exposure_under','exposure_over','combined_under','combined_over')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')


def cue(coeff):
    r,g,b = PROBES.T
    basis = np.column_stack((r,g,b,r*g,r*b,g*b,r*r,g*g,b*b,r*g*b,np.ones(6)))
    out = np.clip(basis @ np.array(coeff).reshape(11,3,order='F'), 0, 1)
    if np.any(out.sum(axis=1) <= 0):
        raise ValueError('Unavailable zero probe output')
    return (out[:,[0,2]] / out.sum(axis=1)[:,None] - PROBES[:,[0,2]] / PROBES.sum(axis=1)[:,None]).reshape(-1)


def scalar_cue(coeff):
    result = []
    for r,g,b in PROBES.tolist():
        basis = (r,g,b,r*g,r*b,g*b,r*r,g*g,b*b,r*g*b,1)
        out = [max(0.,min(1.,math.fsum(basis[j]*coeff[11*k+j] for j in range(11)))) for k in range(3)]
        total = sum(out)
        if total <= 0:
            raise ValueError('Unavailable zero probe output')
        result.extend((out[0]/total-r/(r+g+b),out[2]/total-b/(r+g+b)))
    return result


def target():
    result=[]
    for p in PROBES.tolist():
        decoded=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in p]
        lin=[min(1.,v*f) for v,f in zip(decoded,(1/.85,1,1/1.15))]
        encoded=[12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in lin]
        result.extend((encoded[0]/sum(encoded)-p[0]/sum(p),encoded[2]/sum(encoded)-p[2]/sum(p)))
    return np.array(result)


def main():
    dest=ROOT/'outputs/wb_cue_portrait_assessment_v1'
    if dest.exists():
        raise RuntimeError('Refuse overwrite')
    # Generated metric checks BEFORE any portrait-array access.
    ident=np.zeros((11,3));ident[:3]=np.eye(3)
    flat=ident.reshape(-1,order='F')
    assert np.max(np.abs(cue(flat)))<1e-14
    for matrix in (ident,ident*1.1,ident*np.array([.8,1,1.2])):
        v=matrix.reshape(-1,order='F')
        assert np.max(np.abs(cue(v)-scalar_cue(v)))<1e-14
    try:cue(np.zeros(33))
    except ValueError:pass
    else:raise AssertionError('zero output accepted')
    qa=ROOT/'outputs/wb_cue_actual_generated_v1/verification.json'
    assert read(qa)['status']=='ACTUAL_ASSET_GENERATED_PASS'
    data=ROOT/'outputs/camera_halfstop_data_v1'
    completion=read(data/'completion_PRIVATE.json')
    plan_path=data/'plan_PRIVATE.json'
    assert completion['passed'] and sha(plan_path)==completion['plan_sha256']
    plan=read(plan_path);rows=plan['rows']
    assert len(rows)==66 and len({r['source_id'] for r in rows})==11
    actual_roles=set(r['role'] for r in rows)
    # Exact role names are the frozen camera task's public schema.
    assert actual_roles=={'identity','colour_only','exposure_under','exposure_over','combined_under','combined_over'},actual_roles
    assert len({(r['source_id'],r['role']) for r in rows})==66
    paths=[plan_path,data/'completion_PRIVATE.json',qa,SOURCE,Path(__file__).resolve(),
           ROOT/'scripts/wb_cue_adapter.py',ROOT/'docs/wb-cue-portrait-assessment-protocol-2026-11-15.md']
    bindings={str(p.relative_to(ROOT)):sha(p) for p in paths}
    for row in rows:
        assert row['input_pack'].replace('\\','/').startswith('outputs/camera_halfstop_data_v1/cases/')
        assert (ROOT/row['input_pack']).resolve().parent == (data/'cases').resolve()
        bindings[row['input_pack']]=row['input_pack_sha256']
    receipt=read(ASSETS/'receipt.json')
    for a in receipt['assets']:bindings[str((ASSETS/a['name']).relative_to(ROOT))]=a['sha256']
    for path,h in bindings.items():assert sha(ROOT/path)==h,path
    dest.mkdir();write(dest/'bindings.json',bindings)
    features=[];access=[]
    try:
        model,normalize,_=load_model()
        for i,row in enumerate(rows):
            with np.load(ROOT/row['input_pack'],allow_pickle=False) as pack:
                image=pack['input'].copy()
            access.append({'case_id':row['case_id'],'path':row['input_pack'],'keys':['input']})
            coeff,query,distances,indices=extract(model,normalize,image)
            features.append({'case_id':row['case_id'],'source_id':row['source_id'],'role':row['role'],
                             'coefficients':coeff.tolist(),'query':query.reshape(-1).tolist(),'selected_rows':indices.reshape(-1).tolist()})
            np.save(dest/(row['case_id']+'_distances.npy'),distances,allow_pickle=False)
            if (i+1)%11==0:print(f'Input-only WB cues {i+1}/66',flush=True)
        feature_path=dest/'sealed_features.json';write(feature_path,features)
        sealed_hash=sha(feature_path)
        write(dest/'feature_seal.json',{'sha256':sealed_hash,'cases':66,'scoring_started':False})
        # No target/probe scoring before ALL features sealed.
        expected=target();by_source={};scored=[];maximum=0.
        for row in read(feature_path):
            v=cue(row['coefficients']);ind=scalar_cue(row['coefficients'])
            maximum=max(maximum,float(np.max(np.abs(v-ind))))
            assert np.max(np.abs(v-ind))<1e-10
            cast=row['role'] in {'colour_only','combined_under','combined_over'}
            y=expected if cast else np.zeros(12)
            error=float(np.linalg.norm(v-y));inderror=math.sqrt(math.fsum((float(a)-float(b))**2 for a,b in zip(ind,y)))
            assert abs(error-inderror)<1e-10
            entry={'case_id':row['case_id'],'source_id':row['source_id'],'role':row['role'],
                   'cue':v.tolist(),'error':error,'baseline_error':float(np.linalg.norm(y))}
            scored.append(entry);by_source.setdefault(row['source_id'],{})[row['role']]=entry
        pairs=[('identity','colour_only'),('exposure_under','combined_under'),('exposure_over','combined_over')]
        paired=[]
        for neutral,cast in pairs:
            vals=[]
            for sid,group in by_source.items():
                diff=np.array(group[cast]['cue'])-group[neutral]['cue']
                projection=float(diff@expected/(expected@expected))
                check=math.fsum(float(a)*float(b) for a,b in zip(diff,expected))/math.fsum(float(a)**2 for a in expected)
                assert abs(projection-check)<1e-10
                vals.append({'source_id':sid,'projection':projection})
            paired.append({'pair':[neutral,cast],'mean_projection':math.fsum(v['projection'] for v in vals)/11,'cases':vals})
        means={role:math.fsum(v['error'] for v in scored if v['role']==role)/11 for role in actual_roles}
        error=math.fsum(v['error'] for v in scored)/66
        baseline=math.fsum(v['baseline_error'] for v in scored)/66
        passed=all(p['mean_projection']>1e-10 for p in paired) and error<baseline-1e-10
        for path,h in bindings.items():assert sha(ROOT/path)==h
        assert sha(feature_path)==sealed_hash
        write(dest/'scored_cues.json',scored)
        result={'status':'CUE_ASSESSMENT_SUPPORTED' if passed else 'NOT_ADVANCED_CUE_PROXY_FAILURE',
                'cases':66,'role_mean_cue_error':means,'mean_cue_error':error,'zero_cue_baseline':baseline,
                'pairs':paired,'independent_scalar_max_error':maximum,'feature_sha256':sealed_hash,
                'implementation_verified':True,'portrait_correction_renders':0,'predictor_fits':0,
                'note':'Synthetic-probe proxy, not image restoration error, human harm, or fairness.'}
        write(dest/'verification.json',result);print(json.dumps(result,indent=2))
    except Exception as exc:
        write(dest/'failure.json',{'error':str(exc),'extracted_cases':len(features)})
        raise
    finally:write(dest/'array_access.json',access)


if __name__=='__main__':main()
