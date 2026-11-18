"""Isolated two-arm camera-control tree workflow. No fits or IO at import."""
from pathlib import Path
import sys
import json
import math
import hashlib
import numpy as np
from sklearn.tree import DecisionTreeRegressor
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.luminance_chroma_operator import parameters,render_rgb8
from src.evaluation.directional_recoverability import metrics,regions
from wb_feature_direct_verify import verify_fit,route

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']
SETTINGS=dict(criterion='squared_error',splitter='best',max_depth=4,min_samples_split=2,min_samples_leaf=1,
              min_weight_fraction_leaf=0.,max_features=None,random_state=42,max_leaf_nodes=None,
              min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def select(rows,fold,arm):
    wanted=set(fold['fitting_cases']);found={}
    for r in rows:
        case=r['case_id']
        if case not in wanted:continue
        if case in found or r['source_id']==fold['held_source_id']:raise ValueError('Held/duplicate fit payload')
        x=r['x'+arm];y=r['y']
        if len(x)!=int(arm) or not np.isfinite(x).all() or np.asarray(x,np.float32).astype(float).tolist()!=x:raise ValueError('Float32 width/finite failure')
        parameters(y)
        found[case]={k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(x=x,y=y)
    if set(found)!=wanted or len(found)!=60:raise ValueError('Incomplete fit roster')
    result=[found[c] for c in fold['fitting_cases']]
    if len({r['source_id'] for r in result})!=10 or any(sum(r['role']==role for r in result)!=10 for role in ROLES):raise ValueError('Incomplete fitting sources/roles')
    return result

def validate(plan,rows):
    assert len(rows)==66 and len(plan['folds'])==11
    assert len({r['case_id'] for r in rows})==66
    assert len({r['source_id'] for r in rows})==11
    assert len({(r['source_id'],r['role']) for r in rows})==66
    assert set(r['role'] for r in rows)==set(ROLES)
    assert all(r['generated_fixture'] is plan['generated_fixture'] for r in rows)
    for f in plan['folds']:
        held=[r for r in rows if r['source_id']==f['held_source_id']]
        assert [r['case_id'] for r in held]==f['evaluation_cases'] and len(held)==6
    return [(arm,fold,select(rows,fold,arm)) for arm in ['281','314'] for fold in plan['folds']]

def fit_and_seal(plan,rows,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    payloads=validate(plan,rows) # Global validation BEFORE output and any fit.
    out.mkdir();(out/'models').mkdir();write(out/'plan.json',plan);write(out/'rows.json',rows)
    entries=[];models={};constants={};fit_calls=0
    try:
        for arm,fold,fit in payloads:
            assert fit_calls<22;fit_calls+=1
            write(out/'fit_accounting.json',dict(started=fit_calls,maximum=22))
            x=np.asarray([r['x'] for r in fit],np.float32);y=np.asarray([r['y'] for r in fit],float)
            model=DecisionTreeRegressor(**SETTINGS);model.fit(x,y)
            nodes=[];t=model.tree_
            for i in range(t.node_count):
                if t.children_left[i]==-1:nodes.append(dict(kind='leaf',values=t.value[i,:,0].tolist()))
                else:nodes.append(dict(kind='split',feature=int(t.feature[i]),threshold=float(t.threshold[i]),left=int(t.children_left[i]),right=int(t.children_right[i])))
            exported=dict(schema='truehue_camera_control_cart_research_v1',dimensions=int(arm),target_names=['gamma','exposure_gain','red_balance','blue_balance','chroma_scale'],
                          settings=model.get_params(deep=False),comparison='<=',nodes=nodes)
            assert exported['settings']==SETTINGS
            replay=[route(exported,r['x']) for r in fit]
            assert [p for _,p in replay]==model.predict(x).tolist() and [i for i,_ in replay]==model.apply(x).tolist()
            constant=verify_fit(exported,fit,fold,SETTINGS)
            sid=fold['held_source_id']
            if sid in constants:assert constant==constants[sid]
            constants[sid]=constant;models[(arm,sid)]=exported
            path='models/'+arm+'_'+sid+'.json';write(out/path,exported)
            entries.append(dict(arm=arm,source_id=sid,path=path,sha256=sha(out/path)))
            print(f'Trees verified {fit_calls}/22',flush=True)
        write(out/'all_fits_verified.json',dict(verified_fits=22,fitting_routes=1320,models=entries))
        infer=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x281','x314']} for r in rows]
        write(out/'inference.json',infer)
        return predict(plan,infer,out,constants)
    except Exception as exc:
        write(out/'failure.json',dict(error=str(exc),actual_fit_calls=fit_calls));raise

def predict(plan,inference,out,constants):
    out=Path(out);cert=read(out/'all_fits_verified.json');assert cert['verified_fits']==22 and len(cert['models'])==22
    models={}
    for entry in cert['models']:
        assert sha(out/entry['path'])==entry['sha256']
        models[(entry['arm'],entry['source_id'])]=read(out/entry['path'])
    assert len(models)==22 and len(inference)==66
    sealed=[]
    for r in inference:
        sid=r['source_id'];pred={k:r[k] for k in ['case_id','source_id','role','generated_fixture']}
        for arm in ['281','314']:
            _,p=route(models[(arm,sid)],r['x'+arm]);parameters(p);pred['controls'+arm]=p
        pred['constant']=constants[sid];sealed.append(pred)
    write(out/'held_controls_sealed.json',sealed)
    write(out/'prediction_seal.json',dict(held_predictions=132,sha256=sha(out/'held_controls_sealed.json')))
    return sealed

def score(plan,rows,out,loader):
    out=Path(out);seal=read(out/'prediction_seal.json')
    assert seal['held_predictions']==132 and sha(out/'held_controls_sealed.json')==seal['sha256']
    sealed=read(out/'held_controls_sealed.json');by_id={r['case_id']:r for r in rows}
    (out/'evaluation').mkdir();records=[]
    for i,p in enumerate(sealed):
        row=by_id[p['case_id']];c=loader(row);image,ref,alpha,protected=[c[k] for k in ['image','reference','alpha','protected']]
        outputs={'constant':render_rgb8(image,alpha,protected,p['constant'])}
        for arm in ['281','314']:outputs[arm]=render_rgb8(image,alpha,protected,p['controls'+arm])
        for output in outputs.values():assert np.array_equal(output[alpha==0],image[alpha==0]) and np.array_equal(output[protected],image[protected])
        scored={name:{label:metrics(output,ref,mask) for label,output in dict(input=image,**outputs).items()} for name,mask in regions(alpha).items()}
        rec={k:p[k] for k in ['case_id','source_id','role']}|dict(regions=scored)
        rec['parameter_MAE']={arm:[abs(a-b) for a,b in zip(p['controls'+arm],row['y'])] for arm in ['281','314']}
        rec['identity_changed_pixels']={arm:int(np.any(outputs[arm]!=image,axis=2).sum()) for arm in ['281','314']} if p['role']=='identity' else None
        records.append(rec)
        np.savez(out/'evaluation'/(p['case_id']+'.npz'),input=image,reference=ref,alpha=alpha,protected=protected,**outputs)
        if (i+1)%11==0:print(f'Three outputs scored {i+1}/66',flush=True)
    write(out/'records.json',records)
    means={role:{label:{m:math.fsum(r['regions']['primary'][label][m] for r in records if r['role']==role)/11 for m in ['RGB','DE']} for label in ['input','constant','281','314']} for role in ROLES}
    gates={arm:{role:all(means[role][arm][m]<means[role][b][m]-1e-10 for m in ['RGB','DE'] for b in ['input','constant']) for role in ROLES[1:]} for arm in ['281','314']}
    added=all(means['colour_only']['314'][m]<means['colour_only']['281'][m]-1e-10 for m in ['RGB','DE'])
    harms={arm:{role:{m:[r['case_id'] for r in records if r['role']==role and r['regions']['primary'][arm][m]>r['regions']['primary']['input'][m]+1e-10] for m in ['RGB','DE']} for role in ROLES} for arm in ['281','314']}
    result=dict(by_role=means,role_gates=gates,added_colour_benefit=added,candidate_numeric_eligible=all(gates['314'].values()) and added,
                baseline_numeric_eligible=all(gates['281'].values()),case_harms=harms,model_ready=False,human_review=False)
    write(out/'summary.json',result);return result
