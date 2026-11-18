"""Fixed4377-feature isolated research adapter; old281 workflow unchanged."""
from pathlib import Path
import math
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from .portable_five_control_tree import FiveControlTree,export,controls,f32
from .reiqa_tree_verification import verify_fit
from .five_control_prediction_workflow import read,write,sha,score,summary,ROLES

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
