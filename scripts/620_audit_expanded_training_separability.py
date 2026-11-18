"""Fixed clean-range audit of saved affected training leaves, not a model search."""
from pathlib import Path
from collections import Counter
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/expanded_training_separability_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve completed audit')
    bound={}
    def read(name):
        p=ROOT/name;b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
    m=read('outputs/expanded_correction_models_v1/models_PRIVATE.json')
    d=read('outputs/expanded_lost_benefit_diagnosis_v1/diagnosis_PRIVATE.json')
    assert read('outputs/expanded_lost_benefit_diagnosis_v1/verification_PRIVATE.json')['passed']
    preds={p['case_id']:p for p in m['predictions']}
    fits={f['held_key']:f for f in m['folds']+[m['full']]}
    # Existing affected leaf IDs only; no evaluation features/outcomes choose boundaries.
    selected=set()
    for r in d['records']:
        p=preds[r['case_id']];selected.add((p['subject_id'] if p['cohort']=='development' else 'full',r['leaf']))
    records=[]
    for key,leaf in sorted(selected):
        f=fits[key];m0=f['model'];t=next(t for t in m0['trace'] if t['node']==leaf)
        ids=np.asarray(t['rows']);x=np.asarray(f['training_features'],np.float32)[ids]
        costs=np.asarray(m0['costs'])[ids];clean=np.asarray(m0['clean'])[ids]
        names=[f['training_cases'][i] for i in ids];assert clean.any()
        lo=x[clean].min(axis=0);hi=x[clean].max(axis=0)
        outside=(x<lo)|(x>hi);useful=(costs.min(axis=1)<costs[:,0])&~clean
        recipes=[c.split('__',1)[1] for c in names]
        over=np.array([r in ('exposure_over','combined_warm_over','combined_cool_over') for r in recipes])
        target=useful&over;assert not outside[clean].any()
        cleanvectors={tuple(v) for v in x[clean]}
        collision=[names[i] for i in np.flatnonzero(target) if tuple(x[i]) in cleanvectors]
        axes=[]
        for j,name in enumerate(m['feature_names']):
            axes.append(dict(feature=name,clean_min=float(lo[j]),clean_max=float(hi[j]),
                useful_overexposure_outside=int((target&outside[:,j]).sum()),
                useful_any_recipe_outside=int((useful&outside[:,j]).sum())))
        rows=[dict(case_id=names[i],useful=bool(useful[i]),useful_overexposure=bool(target[i]),
            outside_clean_axes=[m['feature_names'][j] for j in np.flatnonzero(outside[i])]) for i in range(len(ids))]
        records.append(dict(fit_key=key,leaf=leaf,training_rows=len(ids),clean_rows=int(clean.sum()),
            useful_rows=int(useful.sum()),useful_overexposure_rows=int(target.sum()),
            useful_overexposure_outside_any=int((target&outside.any(axis=1)).sum()),
            useful_overexposure_inside_all=int((target&~outside.any(axis=1)).sum()),
            useful_overexposure_exact_clean_feature_collisions=collision,axes=axes,rows=rows))
    summary={}
    for scope in ('full','folds'):
        rr=[r for r in records if (r['fit_key']=='full')==(scope=='full')]
        summary[scope]={k:sum(r[k] for r in rr) for k in ('training_rows','clean_rows','useful_rows','useful_overexposure_rows','useful_overexposure_outside_any','useful_overexposure_inside_all')}
        summary[scope]['leaves']=len(rr)
        summary[scope]['exact_collisions']=sum(len(r['useful_overexposure_exact_clean_feature_collisions']) for r in rr)
    for p,h in bound.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    bound[str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    OUT.mkdir();result=dict(summary=summary,records=records,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0,
        method='Strict float32 per-axis range of fitting clean rows within each frozen affected leaf. No threshold optimisation, splits, new model or evaluation routing.',
        limitations='Outcome-selected leaves; repeated fold rows are not independent. Outside-range coverage is training-only; inside ranges does not prove multivariate inseparability; no exact collision does not prove safe separation.')
    (OUT/'audit_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
