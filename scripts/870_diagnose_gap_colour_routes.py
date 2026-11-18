"""Saved JSON routing diagnosis only: 11 cool cases and 5 noticeable identities."""
from pathlib import Path
from collections import Counter
import json,math,hashlib,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_tree import PortableTree
OUT=ROOT/'outputs/gap_colour_route_diagnosis_v1'

def trace(model,x):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in x];i=0;steps=[]
    while model['nodes'][i]['kind']=='split':
        n=model['nodes'][i];left=x[n['feature']]<=n['threshold']
        steps.append(dict(node=i,feature=model['feature_names'][n['feature']],value=x[n['feature']],threshold=n['threshold'],direction='left' if left else 'right'))
        i=n['left'] if left else n['right']
    return i,steps

def main():
    if OUT.exists():raise FileExistsError('Preserve diagnosis')
    bindings={}
    def read(name):
        p=ROOT/name;assert p.suffix=='.json';bindings[name]=hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text(encoding='utf-8'))
    base='outputs/histogram_gap_source_held_comparison_v1/'
    rows={r['case_id']:r for r in read('outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    gaps={r['case_id']:r for r in read('outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json')}
    models=read(base+'models_PRIVATE.json');preds={p['case_id']:p for p in read(base+'predictions_PRIVATE.json')}
    assessment=read(base+'assessment_d88b0567e26e4f28beecbfb9a53062e4.json')
    checked_cases={r['case_id'] for r in assessment['outcomes'] if r['outcome']=='noticeable_change'}
    checked_cases|={case for case,r in rows.items() if r['experimental_role']=='colour_cool'}
    assert len(checked_cases)==16
    results=[];replays=0
    for model in models:
        tree=model['tree'];portable=PortableTree(tree);membership={};paths={}
        for case in model['definition']['fitting_cases']:
            r=rows[case];x=r['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gaps[case]['features'][n]))[0] for n in tree['feature_names'][16:]]
            leaf,path=trace(tree,x);assert leaf==portable.leaf_id(x);replays+=1
            membership.setdefault(leaf,[]).append(dict(case_id=case,source=r['publisher_group'],role=r['experimental_role'],target=r['nominal_controls']))
            paths[case]=path
        for case in model['definition']['evaluation_cases']:
            if case not in checked_cases:continue
            r=rows[case];x=r['input_vector_float32']+[struct.unpack('!f',struct.pack('!f',gaps[case]['features'][n]))[0] for n in tree['feature_names'][16:]]
            leaf,path=trace(tree,x);assert leaf==portable.leaf_id(x)==preds[case]['leaf'];replays+=1
            value=tree['nodes'][leaf]['values'];assert value==preds[case]['controls']
            fit=membership[leaf];means=[math.fsum(t['target'][j] for t in fit)/len(fit) for j in range(3)]
            assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(value,means))
            rolecounts=dict(Counter(t['role'] for t in fit))
            if abs(value[0]-1)>1e-12:kind='WRONG_EXPOSURE_LEAF'
            elif len({tuple(t['target']) for t in fit})>1:kind='MIXED_IDENTITY_COLOUR_LEAF'
            elif rolecounts=={'identity':len(fit)}:kind='IDENTITY_ONLY_LEAF'
            else:kind='PURE_COLOUR_LEAF'
            excluded=None
            if kind=='WRONG_EXPOSURE_LEAF':
                for step in path:
                    relevant=[p for name,p in paths.items() if rows[name]['experimental_role'] in ['identity','colour_cool']]
                    matched=[s for p in relevant for s in p if s['node']==step['node']]
                    if matched and not any(s['direction']==step['direction'] for s in matched):excluded=step;break
            results.append(dict(case_id=case,role=r['experimental_role'],kind=kind,leaf=leaf,controls=value,nominal_target=r['nominal_controls'],
                path=path,first_nonexposure_free_branch=excluded,leaf_role_counts=rolecounts,fitting_cases=fit,target_means=means))
    assert replays==456 and len(results)==16
    summary=dict(status='SAVED_ROUTE_DIAGNOSIS_COMPLETE_NO_REPAIR_SELECTED',route_replays=456,
        cool_destinations=dict(Counter(r['kind'] for r in results if r['role']=='colour_cool')),
        noticeable_identity_destinations=dict(Counter(r['kind'] for r in results if r['role']=='identity')),
        wrong_exposure_cases=[r['case_id'] for r in results if r['kind']=='WRONG_EXPOSURE_LEAF'],
        new_fits=0,new_candidate_predictions=0,pixel_reads=0,old_results_unchanged=True)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in bindings.items())
    OUT.mkdir()
    for name,value in [('routes_PRIVATE.json',results),('summary_PRIVATE.json',summary),('verification_PRIVATE.json',dict(passed=True,route_replays=456,leaf_means_checked=16,input_sha256=bindings))]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    for r in results:print(r['case_id'],r['kind'],r['leaf_role_counts'],r['controls'])

if __name__=='__main__':main()
