"""Saved trace diagnosis; no predictive fitting, forward passes or rendering."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree

OUT=ROOT/'outputs/joint_policy_trace_audit_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    if OUT.exists():raise FileExistsError(OUT)
    P=ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json'
    F=ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json'
    S=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json'
    G=ROOT/'outputs/benefit_aware_gate_v1/results_PRIVATE.json'
    T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    C=ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json'
    source=read(P);full=read(F);split=read(S);gates=read(G);table={r['case_id']:r for r in read(T)}
    contexts={(r['suite'],r['case_id']):r for r in read(C)['records']}
    bound={str(p):sha(p) for p in [P,F,S,G,T,C,Path(__file__),ROOT/'src/model_training/portable_tree.py',ROOT/'docs/joint-policy-trace-audit-protocol-2026-11-07.md']}
    rows=[r for r in source['records'] if r['suite'] in ('fold_working256','fallback_native224')]
    foldgates={f['held_key']:f['model'] for f in gates['folds']};foldsplit={f['held_key']:f for f in split['folds']}
    summaries={};classified=[];gate_checks=0
    for r in rows:
        if r['features'] is not None:
            g=foldgates[r['subject_id']] if r['suite']=='fold_working256' else full['gate']
            assert r['subject_id'] not in g['training_keys']
            z=[(v-m)/s for v,m,s in zip(r['features'],g['mean'],g['scale'])]
            terms=[v*c for v,c in zip(z,g['coefficient'])]
            logit=math.fsum(terms+[g['intercept']])
            assert abs(logit-r['gate']['logit'])<1e-10
            assert (logit>0)==r['gate']['apply_correction'];gate_checks+=1
        if not r['reference_available']:continue
        p=r['paths'];inp=r['input_reference_metrics']['rgb8_mae_codes']
        gain=lambda method:inp-p[method]['reference_metrics']['rgb8_mae_codes']
        useful= gain('policy_ungated')>0
        rejected=useful and p['policy_gated']['changed_channels']==0
        lost=gain('retained')>0 and p['policy_gated']['changed_channels']==0
        reason=None
        if lost:
            assert r['gate']['apply_correction']
            assert p['policy_ungated']['changed_channels']==0
            reason='outside_leaf_ranges' if r['policy'] is not None and not r['policy']['supported'] else 'neutral_leaf_controls'
        classified.append(dict(suite=r['suite'],case_id=r['case_id'],subject_id=r['subject_id'],layer=r['layer'],recipe=r['recipe'],
            input_mae=inp,retained_gain=gain('retained'),policy_ungated_gain=gain('policy_ungated'),policy_gated_gain=gain('policy_gated'),
            modified_benefit_rejected_by_gate=rejected,retained_benefit_lost=lost,lost_reason=reason))
    def stats(rr):
        return dict(rows=len(rr),original_photos=len({r['case_id'].split('__')[0] for r in rr}),publisher_keys=len({r['subject_id'] for r in rr}),
            recipes=dict(Counter(r['recipe'] for r in rr)),lost_reasons=dict(Counter(r['lost_reason'] for r in rr if r['lost_reason'])),
            mean_retained_gain=float(np.mean([r['retained_gain'] for r in rr])) if rr else None,
            mean_modified_gain=float(np.mean([r['policy_ungated_gain'] for r in rr])) if rr else None)
    selected=[('ungated_clean_failure','fallback_native224','eval_02__clean')]
    for suite in ('fold_working256','fallback_native224'):
        summaries[suite]={}
        for layer in ('clean','core','composite_stress_design'):
            rr=[r for r in classified if r['suite']==suite and r['layer']==layer]
            rejected=[r for r in rr if r['modified_benefit_rejected_by_gate']]
            lost=[r for r in rr if r['retained_benefit_lost']]
            summaries[suite][layer]=dict(scored=len(rr),modified_benefit_rejected=stats(rejected),retained_benefit_lost=stats(lost))
            old=source['summary'][suite][layer]
            assert len(lost)==old['retained_beneficial_actions_now_unchanged']
            if layer!='clean':
                for category,candidates,metric in [('gate_rejected_benefit',rejected,'policy_ungated_gain'),('policy_lost_benefit',lost,'retained_gain')]:
                    if candidates:
                        chosen=sorted(candidates,key=lambda r:(-r[metric],r['case_id']))[0]
                        selected.append((category,suite,chosen['case_id']))
    query=next(r for r in rows if r['suite']=='fallback_native224' and r['case_id']=='eval_02__clean')
    assert query['subject_id'] not in full['training_keys'] and query['policy']['supported']
    tree=full['split']['heads']['gamma']['tree'];x=np.asarray(query['features'],np.float32);node=0;route=[]
    while tree['nodes'][node]['kind']=='split':
        n=tree['nodes'][node];left=x[n['feature']]<=n['threshold']
        route.append(dict(node=node,feature=tree['feature_names'][n['feature']],value=float(x[n['feature']]),threshold=n['threshold'],branch='left' if left else 'right'))
        node=n['left'] if left else n['right']
    predictor=PortableTree(tree);assert predictor.leaf_id(query['features'])==node
    members=[(c,v) for c,v in zip(full['training_cases'],full['training_features']) if predictor.leaf_id(v)==node]
    targets=[table[c]['target'][0] for c,_ in members]
    assert abs(float(np.mean(targets))-tree['nodes'][node]['values'][0])<1e-12
    counterparts=[]
    for origin in sorted({table[c]['source_case'] for c,_ in members}):
        cid=origin+'__clean';i=full['training_cases'].index(cid);v=full['training_features'][i]
        assert table[cid]['target']==[1.,1.,1.]
        counterparts.append(dict(case_id=cid,gamma_leaf=predictor.leaf_id(v),gamma=predictor.predict_one(v)[0]))
    focal=dict(case_id=query['case_id'],route=route,leaf=node,raw_gamma=tree['nodes'][node]['values'][0],
        members=[c for c,_ in members],fitting_rows=len(members),publisher_keys=len({table[c]['subject_id'] for c,_ in members}),
        source_photos=len(counterparts),recipes=dict(Counter(table[c]['case']['id'] for c,_ in members)),target_min=min(targets),target_max=max(targets),target_mean=float(np.mean(targets)),
        clean_counterparts=counterparts,policy=query['policy'],gate=query['gate'],paths=query['paths'])
    OUT.mkdir();boards=[]
    byid={(r['suite'],r['case_id']):r for r in rows}
    for index,(reason,suite,cid) in enumerate(selected):
        r=byid[suite,cid];c=contexts[suite,cid]
        paths=[r['reference_path'],r['image_path'],c['old_output_paths']['old_gated'],r['output_paths']['policy_ungated'],r['output_paths']['policy_gated']]
        for p in paths:bound[p]=sha(p)
        panels=[rgb(p) for p in paths];title=np.full((30,panels[0].shape[1]*5,3),255,np.uint8)
        cv2.putText(title,f'{reason} {suite} {cid}: ref | input | retained | policy ungated | gated',(2,19),cv2.FONT_HERSHEY_SIMPLEX,.34,(0,0,0),1)
        path=OUT/f'{index:02d}_{reason}.png';assert cv2.imwrite(str(path),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR))
        boards.append(dict(reason=reason,suite=suite,case_id=cid,path=str(path)))
    result=dict(summary=summaries,classifications=classified,focal=focal,gate_checks=gate_checks,attempts=len(rows),selected_boards=boards,
        selection='Outcome-selected largest saved benefits, not independent evaluation',new_research_fits=0,new_image_forwards=0,new_correction_renders=0,production_adopted=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    print(json.dumps(dict(summary=summaries,focal={k:focal[k] for k in ('route','leaf','raw_gamma','fitting_rows','publisher_keys','source_photos','recipes')},gate_checks=gate_checks,boards=len(boards)),indent=2))

if __name__=='__main__':main()
