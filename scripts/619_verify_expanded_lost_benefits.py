"""Independent scalar replay of saved loss diagnosis; no fits or image reads."""
from pathlib import Path
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'outputs/expanded_lost_benefit_diagnosis_v1'
    d=json.loads((out/'diagnosis_PRIVATE.json').read_text())
    m=json.loads((ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json').read_text())
    pred={r['case_id']:r for r in m['predictions']};fits={f['held_key']:f for f in m['folds']+[m['full']]}
    for r in d['records']:
        p=pred[r['case_id']];f=fits[p['subject_id'] if p['cohort']=='development' else 'full'];model=f['model'];tree=model['tree'];i=tree['root'];x=np.asarray(p['features'],np.float32)
        while tree['nodes'][i]['kind']=='split':
            n=tree['nodes'][i];i=n['left'] if float(x[n['feature']])<=n['threshold'] else n['right']
        assert i==r['leaf'] and tree['nodes'][i]['values']==[1.,1.,1.]
        t=next(t for t in model['trace'] if t['node']==i);ids=t['rows']
        totals=[sum(model['costs'][j][a] for j in ids) for a in range(14)]
        assert min(range(14),key=lambda a:totals[a])==r['unconstrained_best_action']==0
        assert totals[r['parent_action']]>=totals[0]
        blockers=[f['training_cases'][j] for j in ids if model['clean'][j] and model['costs'][j][r['parent_action']]>0]
        assert blockers==r['parent_action_clean_blockers'] and any(b.startswith('diversity_') for b in blockers)
        feasible=[a for a in range(14) if all(not model['clean'][j] or model['costs'][j][a]==0 for j in ids)]
        assert feasible==r['feasible_actions']==[0]
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,independent_routes_and_scalar_leaf_cost_checks=len(d['records']),new_fits=0,holdout_image_reads=0,
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
