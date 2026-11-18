"""Read-only correction-learning diagnosis using saved JSON only; no refits."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
M=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1'
OUT=ROOT/'outputs/ffhq_learning_diagnosis_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')

def route(nodes,row):
    index=0;path=[]
    while nodes[index]['kind']=='split':
        n=nodes[index];left=row['input_vector_float32'][n['feature']]<=n['threshold'];path.append(dict(node=index,feature=n['feature'],threshold=n['threshold'],went_left=left));index=n['left'] if left else n['right']
    return index,path

def main():
    if OUT.exists():raise FileExistsError('Preserve diagnosis')
    receipt=read(M/'review_PRIVATE.json');assert all(sha(p)==h for p,h in receipt['input_sha256'].items())
    files=[P/'rows_PRIVATE.json',P/'folds_PRIVATE.json',M/'models_PRIVATE.json',M/'predictions_PRIVATE.json',M/'summary_PRIVATE.json',M/'verification_PRIVATE.json',ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json',Path(__file__),ROOT/'docs/table2-target-scaling-results.md',ROOT/'docs/clean-harm-diagnosis-and-repair-results-2026-11-06.md']
    bound={str(p):sha(p) for p in files};rows={r['case_id']:r for r in read(P/'rows_PRIVATE.json')};models=read(M/'models_PRIVATE.json');predictions=read(M/'predictions_PRIVATE.json');names=read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json')['feature_names']
    contexts=[];fitting=[];pairs=[];budgets=[];features=Counter();leaves=[]
    for model in models:
        f=model['definition'];nodes=model['tree']['nodes'];train=[rows[c] for c in f['fitting_cases']];members=defaultdict(list)
        for r in train:
            leaf,_=route(nodes,r);members[leaf].append(r)
        means=[sum(r['nominal_controls'][j] for r in train)/len(train) for j in range(3)]
        sse=[sum((r['nominal_controls'][j]-means[j])**2 for r in train) for j in range(3)]
        budgets.append(dict(held_group=f['held_publisher_group'],fitting_role_counts=dict(Counter(r['experimental_role'] for r in train)),target_root_SSE=sse,gamma_fraction=sse[0]/sum(sse)))
        for i,n in enumerate(nodes):
            if n['kind']=='split':features[names[n['feature']]]+=1
            else:
                group=members[i];expected=[sum(r['nominal_controls'][j] for r in group)/len(group) for j in range(3)]
                assert all(math.isclose(v,w,abs_tol=1e-12) for v,w in zip(expected,n['values']))
                leaves.append(dict(held_group=f['held_publisher_group'],leaf=i,members=[r['case_id'] for r in group],roles=dict(Counter(r['experimental_role'] for r in group)),controls=n['values']))
        for r in train:
            leaf,_=route(nodes,r);control=nodes[leaf]['values'];fitting.append(dict(held_group=f['held_publisher_group'],case_id=r['case_id'],role=r['experimental_role'],leaf=leaf,control=control,target=r['nominal_controls'],control_error=[a-b for a,b in zip(control,r['nominal_controls'])],nonidentity_control=any(abs(v-1)>1e-12 for v in control)))
        own=[p for p in predictions if p['held_publisher_group']==f['held_publisher_group']]
        for p in own:
            r=rows[p['case_id']];leaf,path=route(nodes,r);assert leaf==p['leaf_id'] and nodes[leaf]['values']==p['controls'];group=members[leaf]
            drift={role:[sum(v['nominal_controls'][j]-1 for v in group if v['experimental_role']==role)/len(group) for j in range(3)] for role in ['identity','exposure_under','exposure_over','colour_cool']}
            assert all(math.isclose(1+sum(v[j] for v in drift.values()),p['controls'][j],abs_tol=1e-12) for j in range(3))
            contexts.append(dict(case_id=p['case_id'],role=p['experimental_role'],held_group=f['held_publisher_group'],leaf=leaf,fitting_members=[v['case_id'] for v in group],fitting_roles=dict(Counter(v['experimental_role'] for v in group)),control=p['controls'],drift_from_identity_by_role=drift,path=path))
        normal=next(p for p in own if p['experimental_role']=='identity');cool=next(p for p in own if p['experimental_role']=='colour_cool')
        nr=rows[normal['case_id']];cr=rows[cool['case_id']];green=[n for n in names if n.startswith('input_green_')]
        pairs.append(dict(group=f['held_publisher_group'],identity_case=nr['case_id'],cool_case=cr['case_id'],same_leaf=normal['leaf_id']==cool['leaf_id'],unchanged_green_features=[n for n in green if nr['features'][n]==cr['features'][n]],green_feature_count=len(green)))
    duplicates=defaultdict(list)
    for r in rows.values():duplicates[tuple(r['input_vector_float32'])].append(r['case_id'])
    conflicts=[v for v in duplicates.values() if len({tuple(rows[c]['nominal_controls']) for c in v})>1]
    ids=[r for r in contexts if r['role']=='identity'];cool=[r for r in contexts if r['role']=='colour_cool'];fit_ids=[r for r in fitting if r['role']=='identity']
    only_exposure=lambda r:set(r['fitting_roles'])<=set(['exposure_under','exposure_over'])
    sse=[sum(r['target_root_SSE'][j] for r in budgets) for j in range(3)]
    summary=dict(held_contexts=len(contexts),fitting_row_appearances=len(fitting),unique_fitting_images=len(rows),fitting_identity_nonidentity_controls=sum(r['nonidentity_control'] for r in fit_ids),fitting_identity_appearances=len(fit_ids),held_identities_in_exposure_only_leaves=sum(only_exposure(r) for r in ids),held_cool_in_exposure_only_leaves=sum(only_exposure(r) for r in cool),identity_cool_same_leaf=sum(r['same_leaf'] for r in pairs),paired_photos=len(pairs),all_four_green_features_unchanged=all(len(r['unchanged_green_features'])==r['green_feature_count']==4 for r in pairs),target_root_SSE=sse,gamma_fraction_of_raw_target_root_SSE=sse[0]/sum(sse),conflicting_exact_feature_duplicate_groups=len(conflicts),split_feature_counts=dict(features),new_fits=0,new_inference_API_calls=0,image_bytes_read=0,holdout_reads=0)
    OUT.mkdir();write(OUT/'summary_PRIVATE.json',summary);write(OUT/'held_contexts_PRIVATE.json',contexts);write(OUT/'fitting_replays_PRIVATE.json',fitting);write(OUT/'leaves_PRIVATE.json',leaves);write(OUT/'paired_paths_PRIVATE.json',pairs);write(OUT/'target_budgets_PRIVATE.json',budgets);write(OUT/'conflicting_duplicates_PRIVATE.json',conflicts);write(OUT/'input_sha256_PRIVATE.json',bound)
    assert all(sha(p)==h for p,h in bound.items());print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
