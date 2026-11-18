"""Independent scalar route and action-cost checks on frozen sixteen-case trace."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/remaining_correction_decision_trace_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'trace_PRIVATE.json');m=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    fits={f['held_key']:f for f in m['folds']+[m['full']]};pred={p['case_id']:p for p in m['predictions']}
    for r in d['records']:
        f=fits[r['fit_key']];model=f['model'];tree=model['tree'];x=list(map(f32,pred[r['case_id']]['features']));node=0
        for s in r['route']:
            n=tree['nodes'][node];left=x[n['feature']]<=n['threshold'];assert s['node']==node and s['left']==left and s['value']==x[n['feature']]
            node=n['left'] if left else n['right']
        assert node==r['leaf'] and tree['nodes'][node]['values']==r['parameters']
        ids=model['trace'][node]['rows'];costs=[sum(model['costs'][i][a] for i in ids) for a in range(14)];clean=[i for i in ids if model['clean'][i]]
        feasible=[a for a in range(14) if all(model['costs'][i][a]==0 for i in clean)]
        assert feasible==r['feasible_actions'] and len(clean)==r['leaf_training_clean']
        assert min(range(14),key=lambda a:costs[a])==r['unconstrained_best']
        assert abs(costs[r['selected_action']]-r['selected_total_cost'])<1e-8
        assert r['selected_action']==min(feasible,key=lambda a:costs[a])
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,saved_case_routes=16,scalar_action_totals=224,new_fits=0,new_inference=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
