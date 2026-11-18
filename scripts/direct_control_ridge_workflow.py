"""One eleven-fold regressor comparison. No execution on import."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.direct_control_ridge import fit,predict
from src.model_training.luminance_chroma_operator import parameters
from direct_control_ridge_verify import scalar_predict,verify_fit,close


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select(rows,fold):
    wanted=set(fold['fitting_cases']);found={}
    for r in rows:
        if r['case_id'] not in wanted:continue
        if r['case_id'] in found or r['source_id']==fold['held_source_id']:raise ValueError('Held/duplicate fit row')
        x=r['x314'];y=r['y']
        if len(x)!=314 or np.asarray(x,np.float32).astype(float).tolist()!=x:raise ValueError('Float32 features required')
        if not np.isfinite(x).all():raise ValueError('Nonfinite feature')
        parameters(y);found[r['case_id']]=r
    if set(found)!=wanted or len(found)!=60:raise ValueError('Incomplete fitting roster')
    result=[found[c] for c in fold['fitting_cases']]
    if len({r['source_id'] for r in result})!=10:raise ValueError('Incomplete sources')
    if sorted(set(r['role'] for r in result))!=sorted(set(r['role'] for r in rows)):raise ValueError('Incomplete roles')
    if any(sum(r['role']==v for r in result)!=10 for v in set(r['role'] for r in result)):raise ValueError('Unequal roles')
    return result


def fit_and_seal(plan,rows,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    assert len(rows)==66 and len(plan['folds'])==11
    assert len({r['case_id'] for r in rows})==66 and len({r['source_id'] for r in rows})==11
    assert all(r['generated_fixture'] is plan['generated_fixture'] for r in rows)
    payloads=[]
    for fold in plan['folds']:
        assert [r['case_id'] for r in rows if r['source_id']==fold['held_source_id']]==fold['evaluation_cases']
        payloads.append((fold,select(rows,fold)))
    out.mkdir();(out/'models').mkdir();write(out/'plan.json',plan)
    fits=[];started=0
    try:
        for fold,fitting in payloads:
            started+=1;assert started<=11
            write(out/'fit_accounting.json',dict(started=started,maximum=11))
            model=fit(fitting);proof=verify_fit(model,fitting,fold)
            for r in fitting:
                a=predict(model,r['x314']);b=scalar_predict(model,r['x314'])
                for u,v in zip(a,b):close(u,v,1e-10)
            path='models/'+fold['held_source_id']+'.json';write(out/path,model)
            fits.append(dict(source=fold['held_source_id'],path=path,sha256=sha(out/path),proof=proof))
            print('Ridge model verified '+str(started)+'/11',flush=True)
        write(out/'all_fits_verified.json',dict(verified_fits=11,fitting_predictions=660,models=fits))
        # Held inference gets features/IDs only; no targets or paired references.
        inference=[{k:r[k] for k in ['case_id','source_id','role','generated_fixture','x314']} for r in rows]
        write(out/'inference.json',inference)
        models={entry['source']:read(out/entry['path']) for entry in fits}
        for e in fits:assert sha(out/e['path'])==e['sha256']
        sealed=[]
        for r in inference:
            model=models[r['source_id']];p=predict(model,r['x314']);s=scalar_predict(model,r['x314'])
            for u,v in zip(p,s):close(u,v,1e-10)
            parameters(p)
            sealed.append({k:r[k] for k in ['case_id','source_id','role','generated_fixture']}|dict(controls=p))
        write(out/'held_controls_sealed.json',sealed)
        write(out/'prediction_seal.json',dict(predictions=66,sha256=sha(out/'held_controls_sealed.json')))
        return sealed
    except Exception as exc:
        write(out/'failure.json',dict(error=str(exc),actual_fit_calls=started));raise
