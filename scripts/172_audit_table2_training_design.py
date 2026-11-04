"""Audit fixed ten-source design, saved routing and matched-cohort changes; no fits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import joblib
import numpy as np
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.data_preparation.controlled_training_table import TARGETS
from src.model_training.portable_tree import float32

OUT=ROOT/'outputs/table2_training_design_audit_v1'
PARENT=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    plan=read(PARENT/'fit_plan.json');data=read(PARENT/'summary.json');verification=read(PARENT/'verification.json')
    assert digest(PARENT/'fit_plan.json')==verification['fit_plan_sha256']
    assert digest(PARENT/'summary.json')==verification['summary_sha256']
    old=ROOT/'outputs/table2_reviewed_expansion_evaluation_v1'
    old_data=read(old/'summary.json');old_verify=read(old/'verification.json')
    assert digest(old/'summary.json')==old_verify['summary_sha256']
    paths=[Path(__file__),PARENT/'fit_plan.json',PARENT/'summary.json',PARENT/'verification.json',
        old/'summary.json',old/'verification.json',ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json']
    paths+=list(PARENT.glob('fold_*/*'))
    hashes={str(p.relative_to(ROOT)):digest(p) for p in paths}
    rows={r['pair_id']:r for r in plan['rows']}
    assert len(rows)==20
    OUT.mkdir()
    write(OUT/'protocol.json',dict(scope='No fitting, source selection, new features, thresholds or runtime changes',
        routes='All20 saved predictions; leaf means and float32 routing verified',
        proximity='Lab3 primary, all5 sensitivity; fitting-only population standardization; nearest identity vs nonidentity descriptive comparison',
        matched_cohort='Compare old16 pair IDs on identical saved inputs under old and new folds; training pools differ',
        representation='Check input ITA/MST deterministic relationship and exact conflicting clean/distorted feature collisions',
        limitation='Distances and ranges are not confidence; no impossibility claim or causal claim from leaf membership'))
    records=[];split_counts={k:0 for k in MST_FEATURES}
    for fold in plan['folds']:
        training=[rows[p] for p in fold['train_pair_ids']]
        model=joblib.load(PARENT/f"fold_{fold['fold_id']}/decision_tree.joblib")
        for i,k in enumerate(MST_FEATURES):split_counts[k]+=int(np.sum(model.tree_.feature==i))
        xfit=np.asarray([[r[k] for k in MST_FEATURES] for r in training],float)
        leaves=model.apply(xfit)
        for prediction in [r for r in data['records'] if r['fold_id']==fold['fold_id']]:
            row=rows[prediction['pair_id']]
            assert all(r['source_image_id']!=row['source_image_id'] and r['duplicate_group_id']!=row['duplicate_group_id'] for r in training)
            x=np.asarray([row[k] for k in MST_FEATURES],float);leaf=int(model.apply([x])[0]);node=0;route=[]
            while model.tree_.children_left[node]!=-1:
                axis=int(model.tree_.feature[node]);value=float32(x[axis]);threshold=float(model.tree_.threshold[node])
                left=value<=threshold
                route.append(dict(feature=MST_FEATURES[axis],value_float32=value,threshold=threshold,branch='left' if left else 'right'))
                node=int(model.tree_.children_left[node] if left else model.tree_.children_right[node])
            assert node==leaf
            members=[r for r,l in zip(training,leaves) if l==leaf]
            mean=np.mean([[r[k] for k in TARGETS] for r in members],axis=0)
            np.testing.assert_allclose(mean,prediction['parameters'],rtol=0,atol=1e-12)
            identity_count=sum(r['variant']=='identity' for r in members)
            neighbors={}
            for method,axes in [('Lab3',[0,1,2]),('all5',[0,1,2,3,4])]:
                scales=xfit[:,axes].std(axis=0,ddof=0)
                distances=[]
                for fit_index,r in enumerate(training):
                    distance=sum(((float(xfit[fit_index,a])-float(x[a]))/float(s))**2 for a,s in zip(axes,scales) if s>0)**.5
                    distances.append(dict(pair_id=r['pair_id'],identity=r['variant']=='identity',distance=distance))
                distances.sort(key=lambda r:(r['distance'],r['pair_id']))
                nearest_identity=next(r for r in distances if r['identity']);nearest_distorted=next(r for r in distances if not r['identity'])
                # Independent vector arithmetic checks all fitting distances.
                active=scales>0
                vector=np.linalg.norm((xfit[:,np.asarray(axes)[active]]-x[np.asarray(axes)[active]])/scales[active],axis=1)
                byid={r['pair_id']:r['distance'] for r in distances}
                np.testing.assert_allclose(vector,[byid[r['pair_id']] for r in training],atol=1e-12,rtol=0)
                neighbors[method]=dict(nearest_identity=nearest_identity,nearest_distorted=nearest_distorted,
                    distorted_strictly_nearer=nearest_distorted['distance']<nearest_identity['distance'],top3=distances[:3])
            records.append(dict(pair_id=row['pair_id'],identity=row['variant']=='identity',fold_id=fold['fold_id'],
                error=prediction['learned']['ciede2000_source_mask'],parameters=prediction['parameters'],route=route,leaf=leaf,
                leaf_kind='identity_only' if identity_count==len(members) else 'distortion_only' if identity_count==0 else 'mixed',
                leaf_members=[r['pair_id'] for r in members],neighbors=neighbors))
    previous={r['pair_id']:r for r in old_data['records']};current={r['pair_id']:r for r in data['records']}
    old_plan=read(old/'fit_plan.json');old_rows={r['pair_id']:r for r in old_plan['rows']}
    matched=[]
    for pair,r in previous.items():
        for key in ['input_sha256','input_mask_sha256','reference_mask_sha256',*MST_FEATURES,*TARGETS]:assert rows[pair][key]==old_rows[pair][key]
        matched.append(dict(pair_id=pair,identity=r['variant']=='identity',old_error=r['learned']['ciede2000_source_mask'],
            new_error=current[pair]['learned']['ciede2000_source_mask'],delta=current[pair]['learned']['ciede2000_source_mask']-r['learned']['ciede2000_source_mask']))
    matched_aggregate={kind:dict(pairs=len(subset),old_mean=float(np.mean([r['old_error'] for r in subset])),new_mean=float(np.mean([r['new_error'] for r in subset])),
        improved=sum(r['delta']<0 for r in subset),worsened=sum(r['delta']>0 for r in subset),unchanged=sum(r['delta']==0 for r in subset))
        for kind,subset in [('all',matched),('identity',[r for r in matched if r['identity']]),('distorted',[r for r in matched if not r['identity']])]}
    clean=[r for r in records if r['identity']];harmful=[r for r in clean if r['error']>0]
    summary_counts=dict(harmed_clean=len(harmful),harmful_leaf_kinds={k:sum(r['leaf_kind']==k for r in harmful) for k in ['identity_only','mixed','distortion_only']},
        harmful_clean_distorted_nearer={m:sum(r['neighbors'][m]['distorted_strictly_nearer'] for r in harmful) for m in ['Lab3','all5']},
        uncorrected_distorted=[r['pair_id'] for r in records if not r['identity'] and np.all(np.abs(np.array(r['parameters'])-1)<=1e-12)])
    collisions=[]
    for i,a in enumerate(rows.values()):
        for b in list(rows.values())[i+1:]:
            if (a['variant']=='identity')==(b['variant']=='identity'):continue
            if all(float32(a[k])==float32(b[k]) for k in MST_FEATURES):collisions.append([a['pair_id'],b['pair_id']])
    ranges={kind:{k:dict(min=min(r[k] for r in subset),max=max(r[k] for r in subset)) for k in MST_FEATURES}
        for kind,subset in [('identity',[r for r in rows.values() if r['variant']=='identity']),('distorted',[r for r in rows.values() if r['variant']!='identity'])]}
    assert hashes=={p:digest(ROOT/p) for p in hashes}
    write(OUT/'summary.json',dict(status='complete_no_fit',records=records,counts=summary_counts,matched_pairs=matched,
        matched_aggregate=matched_aggregate,split_counts=split_counts,feature_ranges=ranges,
        float32_identity_distortion_collisions=collisions,input_sha256=hashes))
    write(OUT/'verification.json',dict(status='pass',verified_routes_and_leaf_means=20,independent_neighbor_distance_sets=40,
        identical_old_pair_contracts=16,source_duplicate_separation=True,original_hashes_unchanged=True,summary_sha256=digest(OUT/'summary.json')))
    lines=['# Ten-source design audit','','Saved models only; no new fit.','', '| Input | Error | Leaf type | Fitting leaf members |','| --- | ---: | --- | --- |']
    lines += [f"| {r['pair_id']} | {r['error']:.3f} | {r['leaf_kind']} | {', '.join(r['leaf_members'])} |" for r in records]
    (OUT/'review-index.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(counts=summary_counts,matched=matched_aggregate,split_counts=split_counts,collisions=collisions),indent=2))


if __name__=='__main__':main()
