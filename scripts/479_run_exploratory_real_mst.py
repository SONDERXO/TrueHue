"""User-authorized one bounded real-data diagnostic, preserving false admissions."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.ita_estimation.exploratory_real_mst import evaluate
from src.ita_estimation.contextual_mst_experiment import predict
PARENT=ROOT/'outputs/exploratory_real_mst_preparation_v1'
OUT=ROOT/'outputs/exploratory_real_mst_results_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings={str(PARENT/p):h for p,h in json.loads((PARENT/'sha256.json').read_text()).items()}
    bindings.update(json.loads((PARENT/'input_sha256_PRIVATE.json').read_text()))
    for rel in ['src/ita_estimation/exploratory_real_mst.py','src/ita_estimation/contextual_mst_experiment.py',
        'scripts/479_run_exploratory_real_mst.py','docs/exploratory-real-mst-protocol-2026-11-06.md']:
        bindings[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    rows=json.loads((PARENT/'rows_PRIVATE.json').read_text());result=evaluate(rows)
    indexed={r['case_id']:r for r in rows};replays=0;normal_checks=0
    for fold in result['folds']:
        assert fold['held_subject'] not in fold['training_subjects']
        train=[indexed[k] for k in fold['training_cases']]
        for method,model in fold['models'].items():
            names=model['features'];counts=model['training_subject_row_counts']
            weights=np.array([1/counts[r['subject_id']] for r in train]);x=np.array([[r['features'][f] for f in names] for r in train])
            y=np.array([float(r['source_mst_exact_decimal']) for r in train])
            mu=np.average(x,axis=0,weights=weights);mu=np.where(np.ptp(x,axis=0)==0,x[0],mu)
            scale=np.sqrt(np.average((x-mu)**2,axis=0,weights=weights));scale=np.where(scale==0,1.,scale)
            np.testing.assert_allclose(model['mean'],mu,atol=1e-12,rtol=0)
            np.testing.assert_allclose(model['scale'],scale,atol=1e-12,rtol=0)
            z=(x-mu)/scale;coef=np.array(model['coefficient']);intercept=np.average(y,weights=weights)
            np.testing.assert_allclose((z.T@(weights[:,None]*z)+np.eye(len(names)))@coef,z.T@(weights*(y-intercept)),atol=1e-10,rtol=0)
            normal_checks+=1
            for key in fold['evaluation_cases']:
                r=indexed[key]
                if r['status']=='available':
                    saved=next(v for v in result['records'] if v['case_id']==key)['predictions'][method]
                    assert predict(model,r['features'])==saved;replays+=1
    summary=dict(fits=result['mapping_ridge_fits'],folds=len(result['folds']),prediction_replays=replays,
        independent_weighted_scaling_and_normal_equations=normal_checks,real_correction_tree_fits=0,
        admissions=0,scientific_validation=False,original_rows_unchanged=True)
    assert all(sha(Path(p))==h for p,h in bindings.items())
    OUT.mkdir(parents=True)
    for name,v in [('results_PRIVATE.json',result),('verification.json',summary),('input_sha256_PRIVATE.json',bindings)]:
        (OUT/name).write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(dict(verification=summary,metrics=result['metrics']),indent=2))


if __name__=='__main__':main()
