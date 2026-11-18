"""Independent scalar audit replay, with no image/evaluation accesses."""
from pathlib import Path
import hashlib
import json
import struct

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/conflicting_leaf_separability_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]

def main():
    target=OUT/'verification_PRIVATE.json'
    assert not target.exists()
    d=read(OUT/'audit_PRIVATE.json')
    old=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    new=read(ROOT/'outputs/fixed_structure_nonharm_models_v1/models_PRIVATE.json')
    expected=[]; axes=0; pair_checks=0; routed=0; unique_blockers=set(); unique_exposure=set()
    for a,b in zip(old['folds']+[old['full']],new['folds']+[new['full']],strict=True):
        prior=a['pre_veto_model']; current=b['pre_veto_model']
        nodes=prior['tree']['nodes']; x=[[f32(v) for v in row] for row in a['training_features']]
        for n,(p,q) in enumerate(zip(nodes,current['tree']['nodes'],strict=True)):
            if p['kind']!='leaf' or p['values']==q['values']:continue
            expected.append((a['held_key'],n))
            r=next(r for r in d['records'] if r['configuration']==a['held_key'] and r['leaf']==n)
            members=[]
            for i,row in enumerate(x):
                node=0
                while nodes[node]['kind']=='split':
                    t=nodes[node];node=t['left'] if row[t['feature']]<=t['threshold'] else t['right']
                if node==n:members.append(i)
                routed+=1
            assert set(r['leaf_rows'])==set(members)==set(prior['trace'][n]['rows'])
            old_action=prior['actions'].index(p['values']); new_action=current['actions'].index(q['values'])
            assert r['old_action']==old_action and r['reassigned_action']==new_action
            blocker=[];exposure=[];clean=[]
            for i in members:
                recipe=a['training_cases'][i].split('__',1)[1];cost=prior['costs'][i]
                if recipe in ['colour_cool','colour_warm','stress_color_none'] and cost[old_action]>cost[0]:blocker.append(i)
                if ('under' in recipe or 'over' in recipe) and cost[old_action]<cost[0]:exposure.append(i)
                if prior['clean'][i] and cost[old_action]>0:clean.append(i)
            assert blocker==sorted(r['colour_blockers']) and exposure==sorted(r['exposure_beneficiaries']) and clean==sorted(r['clean_blockers'])
            unique_blockers.update(a['training_cases'][i] for i in blocker)
            unique_exposure.update(a['training_cases'][i] for i in exposure)
            for k,name in enumerate(new['feature_names']):
                vals=sorted(x[i][k] for i in blocker);others=sorted(x[i][k] for i in exposure)
                rr=r['ranges'][k];assert rr['feature']==name
                assert rr['colour_blocker_range']==[vals[0],vals[-1]]
                assert rr['exposure_beneficiary_range']==[others[0],others[-1]]
                assert rr['strictly_disjoint']==(vals[0]>others[-1] or others[0]>vals[-1]);axes+=1
            pairs=[]
            for i in blocker:
                for j in exposure:
                    if all(v==w for v,w in zip(x[i],x[j],strict=True)):pairs.append([i,j])
                    pair_checks+=1
            assert pairs==sorted(r['identical_float32_vector_conflicts'])
            outside=[]
            for i in blocker:
                if any(not min(x[j][k] for j in exposure)<=x[i][k]<=max(x[j][k] for j in exposure) for k in range(len(new['feature_names']))):outside.append(i)
            assert outside==sorted(r['blockers_outside_exposure_bounding_box'])
            for row in r['rows']:
                i=row['index'];assert i in members and row['case_id']==a['training_cases'][i] and row['features']==x[i]
                assert row['old_action_cost']==prior['costs'][i][old_action] and row['identity_cost']==prior['costs'][i][0]
                assert row['new_action_cost']==prior['costs'][i][new_action]
            assert len(r['rows'])==len(members)
    assert expected==[(r['configuration'],r['leaf']) for r in d['records']]
    expected_summary=dict(changed_leaves=len(expected),configurations=len({a for a,b in expected}),
        repeated_colour_blockers=sum(len(r['colour_blockers']) for r in d['records']),
        repeated_exposure_beneficiaries=sum(len(r['exposure_beneficiaries']) for r in d['records']),
        clean_blockers=sum(len(r['clean_blockers']) for r in d['records']),
        leaves_with_disjoint_axis=sum(any(t['strictly_disjoint'] for t in r['ranges']) for r in d['records']),
        exact_vector_conflicts=sum(len(r['identical_float32_vector_conflicts']) for r in d['records']))
    assert d['summary']==expected_summary
    for p,h in d['input_sha256'].items():assert sha(Path(p))==h
    result=dict(passed=True,changed_leaves=len(expected),feature_range_checks=axes,vector_pair_checks=pair_checks,
        fitting_routes_checked=routed,unique_blocking_conditions=sorted(unique_blockers),
        unique_exposure_beneficiary_conditions=len(unique_exposure),
        audit_sha256=sha(OUT/'audit_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        new_fits=0,new_evaluation_predictions=0,image_reads=0,holdout_image_reads=0)
    target.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
