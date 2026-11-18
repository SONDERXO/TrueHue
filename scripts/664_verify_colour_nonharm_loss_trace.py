"""Independent scalar routes, blocker sets and cost sums for six fixed losses."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/colour_nonharm_loss_trace_v1'
f32=lambda v:struct.unpack('f',struct.pack('f',v))[0]
def main():
    read=lambda p:json.loads(Path(p).read_text());d=read(OUT/'trace_PRIVATE.json');old=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json');new=read(ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    fits=[{f['held_key']:f for f in m['folds']+[m['full']]} for m in (old,new)];pred={p['case_id']:p for p in new['predictions']}
    for r in d['records']:
        leaves=[]
        for ff,path in zip(fits,(r['old_route'],r['new_route'])):
            f=ff[r['fit_key']];tree=f['model']['tree'];x=list(map(f32,pred[r['case_id']]['features']));node=0
            for s in path:
                n=tree['nodes'][node];left=x[n['feature']]<=n['threshold'];assert s['node']==node and s['left']==left and s['threshold']==n['threshold'];assert s['training_rows']==f['pre_veto_model']['trace'][node]['rows'];node=n['left'] if left else n['right']
            leaves.append(node)
        assert leaves==[r['old_leaf'],r['new_leaf']]
        f=fits[1][r['fit_key']];m=f['pre_veto_model'];ix=m['trace'][r['new_leaf']]['rows'];a=m['actions'].index(r['old_controls'])
        clean=[f['training_cases'][i] for i in ix if m['clean'][i] and m['costs'][i][a]>0]
        colour=[f['training_cases'][i] for i in ix if m['nonharm'][i] and m['costs'][i][a]>m['costs'][i][0]]
        assert clean==r['prior_action_clean_blockers'] and colour==r['prior_action_colour_blockers']
        assert abs(sum(m['costs'][i][a] for i in ix)-r['new_leaf_prior_action_cost'])<1e-8
        assert r['new_pre_veto_controls']==r['new_controls']==[1.,1.,1.] and not r['new_leaf_vetoed']
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,lost_conditions=6,route_replays=12,new_fits=0,new_predictions=0,holdout_image_reads=0)
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
