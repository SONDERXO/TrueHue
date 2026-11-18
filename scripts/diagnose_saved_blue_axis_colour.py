"""Saved JSON/scalar route diagnosis only. No trainer, arrays, rendering or new fit."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,math,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.joint_colour_verification import route

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    out=ROOT/'outputs/blue_axis_saved_colour_diagnosis_v1'
    if out.exists():raise FileExistsError('Preserve diagnosis')
    source=ROOT/'outputs/blue_axis_source_held_comparison_v1';records={r['case_id']:r for r in read(ROOT/'outputs/blue_axis_preparation_v1/rows_PRIVATE.json')}
    predictions=read(source/'predictions_PRIVATE.json');assessment=read(ROOT/'outputs/blue_axis_review_assessment_v1/assessment_PRIVATE.json');outcomes={r['case_id']:r for r in assessment['outcomes']}
    models=read(source/'models_PRIVATE.json');before={};fitchecks=heldchecks=leafchecks=0;leaves={}
    for m in models:
        folder=source/m['directory'];tree=read(folder/'candidate_PRIVATE.json');assert sha(folder/'candidate_PRIVATE.json')==m['candidate_sha256']
        replay=read(folder/'training_replay_PRIVATE.json');rows=read(folder/'fitting_inputs_PRIVATE.json');members=defaultdict(list)
        for i,r in enumerate(rows):
            leaf,value=route(tree,r['x']);assert leaf==replay['candidate_leaves'][i] and value==replay['candidate_predictions'][i];members[leaf].append(r);fitchecks+=1
        for leaf,rs in members.items():
            means=[math.fsum(r['y'][j] for r in rs)/len(rs) for j in range(3)]
            assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(means,tree['nodes'][leaf]['values']));leafchecks+=1
            leaves[(m['definition']['held_publisher_group'],leaf)]=dict(role_counts=dict(Counter(r['role'] for r in rs)),target_means=means)
        before[str((folder/'candidate_PRIVATE.json').relative_to(ROOT))]=sha(folder/'candidate_PRIVATE.json')
        for p in predictions:
            if p['source']!=m['definition']['held_publisher_group']:continue
            leaf,value=route(tree,records[p['case_id']]['x']);assert leaf==p['leaf'] and value==p['controls'];heldchecks+=1
    by={(p['source'],p['role']):p for p in predictions};old={p['case_id']:p for p in read(ROOT/'outputs/joint_colour_source_held_comparison_v1/predictions_PRIVATE.json')}
    diagnoses=[]
    for p in predictions:
        if p['role'] not in ['colour_cool','blue_decrease','blue_increase']:continue
        r=records[p['case_id']];target=r['y'];controls=p['controls'];composition=leaves[(p['source'],p['leaf'])]
        diagnoses.append(dict(case_id=p['case_id'],review_id=p['review_id'],role=p['role'],outcome=outcomes[p['case_id']]['outcome'],controls=controls,nominal=target,
            absolute_control_errors=[abs(a-b) for a,b in zip(controls,target)],leaf_composition=composition,
            same_leaf_as_identity=p['leaf']==by[(p['source'],'identity')]['leaf'],
            same_controls_as_other_colour=(controls==by[(p['source'],'blue_decrease' if p['role']=='colour_cool' else 'colour_cool')]['controls']) if p['role']!='blue_increase' else None,
            DE_benefit=p['primary']['input']['DE']-p['primary']['output']['DE'],RGB_benefit=p['primary']['input']['RGB']-p['primary']['output']['RGB'],
            clipping_whole_image=r.get('forward_report'),prior_saved_controls=old[p['case_id']]['controls'] if p['case_id'] in old else None))
    groups={role:[d for d in diagnoses if d['role']==role] for role in ['colour_cool','blue_decrease','blue_increase']}
    summary={}
    for role,items in groups.items():
        summary[role]=dict(outcomes=dict(Counter(d['outcome'] for d in items)),exact_nominal_controls=sum(all(abs(a-b)<=1e-12 for a,b in zip(d['controls'],d['nominal'])) for d in items),
            same_leaf_as_identity=sum(d['same_leaf_as_identity'] for d in items),DE_benefits=sum(d['DE_benefit']>0 for d in items),RGB_benefits=sum(d['RGB_benefit']>0 for d in items),
            leaf_roles=[d['leaf_composition']['role_counts'] for d in items])
    summary['red_blue_decrease_identical_control_pairs']=sum(by[(s,'colour_cool')]['controls']==by[(s,'blue_decrease')]['controls'] for s in {p['source'] for p in predictions})
    assert fitchecks==660 and heldchecks==66 and all(sha(ROOT/n)==h for n,h in before.items())
    out.mkdir();write(out/'diagnosis_PRIVATE.json',dict(passed=True,fitting_route_replays=fitchecks,held_route_replays=heldchecks,leaf_mean_replays=leafchecks,summary=summary,cases=diagnoses,input_sha256=before,new_fits=0,new_candidate_predictions=0,new_photo_arrays=0,model_adopted=False))
    write(out/'verification_PRIVATE.json',dict(passed=True,diagnosis_sha256=sha(out/'diagnosis_PRIVATE.json'),fitting_route_replays=fitchecks,held_route_replays=heldchecks,leaf_mean_replays=leafchecks,model_hashes_unchanged=True))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
