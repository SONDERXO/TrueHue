"""Read-only replay of saved oblique routing; no optimizer or pixel reads."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.portable_oblique_tree import PortableObliqueTree
OUT=ROOT/'outputs/oblique_identity_route_diagnosis_v1'

def trace(model,values):
    x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in values]
    nodes=model['nodes'];i=0;path=[]
    while nodes[i]['kind']=='split':
        n=nodes[i];terms=[w*v for w,v in zip(n['weights'],x)]
        score=math.fsum([n['intercept']]+terms);right=score>0
        path.append(dict(node=i,score=score,direction='right' if right else 'left',
            intercept=n['intercept'],active_terms=[dict(feature=model['feature_names'][j],
                input=x[j],weight=n['weights'][j],product=t) for j,t in enumerate(terms) if n['weights'][j]!=0]))
        i=n['right'] if right else n['left']
    return i,path

def main():
    if OUT.exists():raise FileExistsError('Preserve completed route diagnosis')
    hashes={}
    def read(name):
        path=ROOT/name;assert path.suffix=='.json'
        hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_text(encoding='utf-8'))
    base='outputs/oblique_source_held_comparison_v1/'
    rows={r['case_id']:r for r in read('outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')}
    models={m['definition']['held_publisher_group']:m for m in read(base+'models_PRIVATE.json')}
    preds={r['case_id']:r for r in read(base+'predictions_PRIVATE.json')}
    assessment=read(base+'assessment_45516d2751fd453580dae63f41d809bd.json')
    cases=[r['case_id'] for r in assessment['outcomes'] if r['outcome']=='noticeable_change']
    assert len(cases)==9
    results=[];verified=0
    for case in cases:
        row=rows[case];saved=models[row['publisher_group']];model=saved['tree'];portable=PortableObliqueTree(model)
        assert case in saved['definition']['evaluation_cases'] and case not in saved['definition']['fitting_cases']
        leaf,path=trace(model,row['input_vector_float32']);value=model['nodes'][leaf]['values']
        assert leaf==portable.leaf_id(row['input_vector_float32']) and value==preds[case]['controls'];verified+=1
        members={};fit=[]
        for name in saved['definition']['fitting_cases']:
            r=rows[name];dest,route=trace(model,r['input_vector_float32'])
            assert dest==portable.leaf_id(r['input_vector_float32']);verified+=1
            item=dict(case_id=name,source=r['publisher_group'],role=r['experimental_role'],target=r['nominal_controls'],leaf=dest,route=route)
            members.setdefault(dest,[]).append(item);fit.append(item)
        chosen=members.get(leaf,[]);assert chosen
        mean=[math.fsum(r['target'][j] for r in chosen)/len(chosen) for j in range(3)]
        assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(mean,value))
        split_context=[]
        for step in path:
            node=step['node'];arriving=[]
            for item in fit:
                at=next((s for s in item['route'] if s['node']==node),None)
                if at:arriving.append((item,at))
            split_context.append(dict(node=node,held_direction=step['direction'],held_score=step['score'],
                fitting_role_counts_by_direction={direction:dict(Counter(item['role'] for item,at in arriving if at['direction']==direction)) for direction in ['left','right']},
                fitting_identity_routes=[dict(case_id=item['case_id'],score=at['score'],direction=at['direction']) for item,at in arriving if item['role']=='identity']))
        targets={tuple(r['target']) for r in chosen}
        results.append(dict(case_id=case,source=row['publisher_group'],leaf=leaf,controls=value,
            path=path,split_context=split_context,leaf_fitting_cases=[{k:v for k,v in r.items() if k!='route'} for r in chosen],
            leaf_role_counts=dict(Counter(r['role'] for r in chosen)),leaf_target_means=mean,
            leaf_target_vectors_identical=len(targets)==1,
            diagnosis='PURE_NONIDENTITY_TARGET_DESTINATION' if len(targets)==1 and next(iter(targets))!=(1.,1.,1.) else 'MIXED_TARGET_DESTINATION'))
    totals=dict(noticeable_cases=9,route_replays=verified,
        pure_nonidentity_destinations=sum(r['diagnosis']=='PURE_NONIDENTITY_TARGET_DESTINATION' for r in results),
        mixed_target_destinations=sum(r['diagnosis']=='MIXED_TARGET_DESTINATION' for r in results),
        leaves_containing_fitting_identity=sum('identity' in r['leaf_role_counts'] for r in results),
        interpretation='Saved control means are correct for fitting destinations; held role routing does not transfer.',
        scope='9 failed held identities and their corresponding 40-row fitting folds; not new predictions/validation',
        new_fits=0,new_candidate_predictions=0,route_replays_are_saved_result_checks=True,pixel_reads=0)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    OUT.mkdir()
    for name,value in [('routes_PRIVATE.json',results),('summary_PRIVATE.json',totals),('verification_PRIVATE.json',dict(passed=True,independent_scalar_vs_portable_routes=verified,leaf_means_checked=9,input_sha256=hashes,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_hashes_unchanged=True))]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(totals,indent=2))
    for r in results:print(r['case_id'],'leaf',r['leaf'],r['leaf_role_counts'],r['controls'])

if __name__=='__main__':main()
