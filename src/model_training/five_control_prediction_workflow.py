"""Isolated eleven-fold research workflow; no file reads or fits on import."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from .blue_axis_preparation import features281
from .portable_five_control_tree import FiveControlTree,export,controls,f32
from .five_control_prediction_verification import verify_fit
from .affine_prepower_targets import render_rgb8
from src.evaluation.directional_recoverability import metrics,regions

ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare_features(cases,names,mapping,identities,*,extractor=features281):
    ids={c['source_id'] for c in cases}
    if len(cases)!=66 or len(ids)!=11 or set(identities)!=ids or len(names)!=281:
        raise ValueError('Exact66case/11identity/281feature preparation required')
    if len({c['case_id'] for c in cases})!=66 or {(c['source_id'],c['role']) for c in cases}!={(s,r) for s in ids for r in ROLES}:
        raise ValueError('Frozen source-role Cartesian roster required')
    vectors={};details={}
    def extract(c):
        vector,detail=extractor(c['image'],c['measurement'],mapping,names)
        if len(vector)!=281 or any(f32(v)!=v for v in vector):raise ValueError('Finite float32 features required')
        return vector,detail
    # Every identity verified before any nonidentity extraction or tree fitting.
    for c in cases:
        if c['role']!='identity':continue
        x,d=extract(c)
        if x!=identities[c['source_id']]:raise ValueError('Identity feature parity failure: '+c['source_id'])
        vectors[c['case_id']]=x;details[c['case_id']]=d
    for c in cases:
        if c['role']=='identity':continue
        vectors[c['case_id']],details[c['case_id']]=extract(c)
    rows=[]
    for c in cases:
        if type(c['generated_fixture']) is not bool:raise ValueError('Explicit unchanged provenance required')
        controls(c['y'])
        rows.append({k:c[k] for k in ['case_id','source_id','role','generated_fixture','y']} |
                    dict(x=vectors[c['case_id']],feature_details=details[c['case_id']]))
    return rows


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
        if len(x)!=281 or any(f32(v)!=v for v in x):raise ValueError('281finite float32 features required')
        controls(y)
        selected[case_id]=dict(case_id=case_id,source_id=row['source_id'],role=row['role'],
            generated_fixture=row['generated_fixture'],x=list(x),y=list(y))
    if set(selected)!=wanted:raise ValueError('Missing fitting cases')
    result=[selected[c] for c in fold['fitting_cases']]
    if len({r['source_id'] for r in result})!=10 or any(sum(r['role']==role for r in result)!=10 for role in ROLES):
        raise ValueError('Ten sources and ten fitting examples per role required')
    return result


def fit_all(plan,rows,out,*,factory=DecisionTreeRegressor):
    out=Path(out)
    if out.exists():raise FileExistsError('Preserve prior/partial models')
    if len(plan['folds'])!=11:raise ValueError('Exactly11folds required')
    fitting=[select_fitting(rows,f,generated_fixture=plan['generated_fixture']) for f in plan['folds']]
    out.mkdir();models=[]
    try:
        for fold,fit in zip(plan['folds'],fitting):
            folder=out/fold['held_source_id'];folder.mkdir()
            write(folder/'fitting_rows.json',fit)
            x=np.asarray([r['x'] for r in fit],np.float32);y=np.asarray([r['y'] for r in fit],float)
            model=factory(**plan['settings']);model.fit(x,y)
            tree=export(model,plan['feature_names'],dict(generated_fixture=plan['generated_fixture'],
                held_source_excluded=fold['held_source_id'],runtime_adopted=False))
            portable=FiveControlTree(tree)
            predictions=model.predict(x).tolist();leaves=model.apply(x).tolist()
            if portable.predict(x.tolist())!=predictions or [portable.leaf_id(v) for v in x.tolist()]!=leaves:
                raise AssertionError('Native/portable parity failure')
            constant=[math.fsum(r['y'][j] for r in fit)/60 for j in range(5)]
            replay=dict(settings=model.get_params(deep=False),fit_calls=1,held_predictions=0,
                predictions=predictions,leaves=leaves,constant_controls=constant)
            verified=verify_fit(tree,fit,replay,fold,plan['feature_names'],plan['settings'])
            write(folder/'tree.json',tree);write(folder/'replay.json',replay);write(folder/'verification.json',verified)
            models.append(dict(held_source_id=fold['held_source_id'],tree_path=str(folder/'tree.json'),
                tree_sha256=sha(folder/'tree.json'),fitting_rows_path=str(folder/'fitting_rows.json'),
                fitting_rows_sha256=sha(folder/'fitting_rows.json'),replay_path=str(folder/'replay.json'),
                replay_sha256=sha(folder/'replay.json'),verification_path=str(folder/'verification.json'),
                verification_sha256=sha(folder/'verification.json'),constant_controls=constant))
            print(f'Generated/research tree fit verified {len(models)}/11',flush=True)
        write(out/'all_fits_verified.json',dict(passed=True,fit_calls=11,fitting_routes=660,held_predictions=0,models=models))
    except Exception as error:
        write(out/'failure.json',dict(completed_verified_fits=len(models),error=str(error)));raise
    return models


def sealed_models(plan,models,out):
    certificate=read(Path(out)/'all_fits_verified.json')
    if not certificate['passed'] or certificate['fit_calls']!=11 or certificate['models']!=models:
        raise ValueError('All-eleven-fit verification barrier required')
    if {m['held_source_id'] for m in models}!={f['held_source_id'] for f in plan['folds']}:
        raise ValueError('Missing fold')
    for m in models:
        for stem in ['tree','fitting_rows','replay','verification']:
            if sha(m[stem+'_path'])!=m[stem+'_sha256']:raise ValueError('Verified model artifact changed')
    return {m['held_source_id']:m for m in models}


def predict_held(plan,rows,models,out):
    by_source=sealed_models(plan,models,out);by_case={r['case_id']:r for r in rows};predictions=[]
    for fold in plan['folds']:
        model=by_source[fold['held_source_id']];tree=FiveControlTree(read(model['tree_path']))
        for case_id in fold['evaluation_cases']:
            row=by_case[case_id]
            if row['source_id']!=fold['held_source_id']:raise ValueError('Held-source mismatch')
            p=tree.predict_one(row['x']);controls(p);controls(model['constant_controls'])
            predictions.append(dict(case_id=case_id,source_id=row['source_id'],role=row['role'],
                generated_fixture=row['generated_fixture'],controls=p,leaf=tree.leaf_id(row['x']),
                constant_controls=model['constant_controls']))
    if len(predictions)!=66 or len({p['case_id'] for p in predictions})!=66:raise ValueError('Incomplete held predictions')
    write(Path(out)/'held_controls_sealed.json',predictions)
    return predictions


def score(plan,cases,predictions,out):
    out=Path(out)
    if out.exists():raise FileExistsError('Preserve evaluation')
    by_case={c['case_id']:c for c in cases}
    if len(predictions)!=66 or {p['case_id'] for p in predictions}!=set(by_case):raise ValueError('Complete sealed predictions required')
    out.mkdir();records=[]
    for p in predictions:
        c=by_case[p['case_id']];image,reference,alpha,protected=[c[k] for k in ['image','reference','alpha','protected']]
        tree=render_rgb8(image,alpha,protected,p['controls'])
        constant=render_rgb8(image,alpha,protected,p['constant_controls'])
        for rendered in [tree,constant]:
            if not np.array_equal(rendered[alpha==0],image[alpha==0]) or not np.array_equal(rendered[protected],image[protected]):
                raise AssertionError('Outside/protected pixels changed')
        scored={name:dict(pixels=int(mask.sum()),**{label:metrics(im,reference,mask)
            for label,im in [('input',image),('tree',tree),('constant',constant)]}) for name,mask in regions(alpha).items()}
        record=dict(**p,regions=scored,oracle_controls=c['y'],
            control_squared_error=math.fsum((a-b)**2 for a,b in zip(p['controls'],c['y'])),
            identity_changed_pixels=int(np.any(tree!=image,axis=2).sum()) if c['role']=='identity' else None,
            identity_mean_RGB_change=float(np.abs(tree.astype(float)-image).mean()) if c['role']=='identity' else None)
        records.append(record)
        np.savez(out/(p['case_id']+'.npz'),input=image,reference=reference,alpha=alpha,protected=protected,tree=tree,constant=constant)
        write(out/(p['case_id']+'.json'),record)
    write(out/'summary.json',summary(records))
    return records


def summary(records):
    by_role={}
    for role in ROLES:
        own=[r for r in records if r['role']==role]
        means={label:{key:math.fsum(r['regions']['primary'][label][key] for r in own)/len(own) if own else None
            for key in ['RGB','DE']} for label in ['input','tree','constant']}
        by_role[role]=dict(cases=len(own),means=means,
            case_harms={key:[r['case_id'] for r in own if r['regions']['primary']['tree'][key]>r['regions']['primary']['input'][key]+1e-10] for key in ['RGB','DE']})
    complete=len(records)==66 and len({r['case_id'] for r in records})==66 and all(by_role[r]['cases']==11 for r in ROLES)
    checks={r:bool(complete and all(by_role[r]['means']['tree'][k]<by_role[r]['means'][b][k]-1e-10
                    for k in ['RGB','DE'] for b in ['input','constant'])) for r in ROLES if r!='identity'}
    return dict(complete=complete,by_role=by_role,numeric_role_checks=checks,
        status='NUMERIC_PREDICTION_ELIGIBLE_ONLY' if complete and all(checks.values()) else 'NOT_ADVANCED',
        human_identity_acceptability='not_assessed',model_ready=False,review_launched=False)


def execute(plan,cases,mapping,identities,out,*,extractor=features281,factory=DecisionTreeRegressor):
    out=Path(out)
    if out.exists():raise FileExistsError('Preserve completed/partial research run')
    out.mkdir(parents=True)
    try:
        write(out/'execution_plan.json',plan)
        rows=prepare_features(cases,plan['feature_names'],mapping,identities,extractor=extractor)
        write(out/'prepared_rows.json',rows)
        models=fit_all(plan,rows,out/'models',factory=factory)
        inference_rows=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x']} for r in rows]
        write(out/'inference_inputs.json',inference_rows)
        predictions=predict_held(plan,inference_rows,models,out/'models')
        records=score(plan,cases,predictions,out/'evaluation')
        write(out/'complete.json',dict(tree_fits=11,fitting_routes=660,held_predictions=66,constant_renders=66,model_ready=False))
        return rows,models,records
    except Exception as error:
        write(out/'failure.json',dict(status='failed_preserved',error=str(error)));raise
