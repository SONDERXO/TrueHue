"""Independent arithmetic/ranking/routing replay and readable diagnostic tables."""
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.train_model import load_model

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=ROOT/'outputs/core_feature_conflict_v1';data=json.loads((out/'summary.json').read_text());parent=ROOT/'outputs/core_control_comparison_v1'
    prior=json.loads((parent/'summary.json').read_text());lookup={p['pair_id']:p for p in prior['predictions'] if p['method']=='no_correction'}
    audits={(a['fold_id'],a['method']):a for a in prior['fit_audits']};models={};rankings_checked=0;leaf_checks=0;csv_rows=[];neighbors=[]
    for r in data['records']:
        key=(r['fold_id'],r['method']);audit=audits[key];ids=audit['fit_pair_ids'];assert r['fitting_pair_ids']==ids
        assert not set(ids)&set(prior['held_ids']) and r['source_image_id'] not in {lookup[p]['source_image_id'] for p in ids}
        if key not in models:models[key]=load_model(str(parent/'fold_models'/f'fold{key[0]}_{key[1]}.joblib'))
        model=models[key];query=r['features'];target=r['target_parameters'];x=[lookup[p]['features'] for p in ids];y=[lookup[p]['target_parameters'] for p in ids]
        node=0;route=[]
        while model.tree_.children_left[node]!=model.tree_.children_right[node]:
            feature=int(model.tree_.feature[node]);threshold=float(model.tree_.threshold[node]);left=float(np.float32(query[feature]))<=threshold
            route.append((node,feature,threshold,left));node=int(model.tree_.children_left[node] if left else model.tree_.children_right[node])
        assert node==r['routing']['leaf_id'] and len(route)==len(r['routing']['rules'])
        for expected,saved in zip(route,r['routing']['rules']):
            assert expected[0]==saved['node_id'] and expected[2]==saved['threshold'] and expected[3]==(saved['comparison']=='<=')
            assert saved['feature']==audit['feature_columns'][expected[1]] and saved['input_value']==query[expected[1]]
            assert saved['routing_float32_value']==float(np.float32(query[expected[1]]))
        training_leaves=model.apply(np.asarray(x));members=[i for i,l in enumerate(training_leaves) if l==node]
        assert [ids[i] for i in members]==[m['pair_id'] for m in r['members']]
        target_match=[all(abs(a-b)<=1e-12 for a,b in zip(t,target)) for t in y]
        assert r['leaf_matching_members']==sum(target_match[i] for i in members)
        assert r['leaf_only_different_targets']==(not any(target_match[i] for i in members))
        assert r['leaf_mixed_targets']==(len({tuple(round(v,12) for v in y[i]) for i in members})>1)
        mean=[math.fsum(y[i][j] for i in members)/len(members) for j in range(3)]
        np.testing.assert_allclose(mean,r['predicted_parameters'],rtol=0,atol=1e-12);leaf_checks+=1
        for name,n in r['neighborhoods'].items():
            axes=n['axes'];centers=[math.fsum(row[j] for row in x)/len(x) for j in axes]
            scales=[math.sqrt(math.fsum((row[j]-c)**2 for row in x)/len(x)) for j,c in zip(axes,centers)]
            np.testing.assert_allclose(n['fit_population_std'],scales,rtol=0,atol=1e-12)
            np.testing.assert_allclose(n['fit_mean'],centers,rtol=0,atol=1e-12)
            distances=[math.sqrt(math.fsum(((row[j]-query[j])/scale)**2 for j,scale in zip(axes,scales) if scale>0)) for row in x]
            order=sorted(range(len(ids)),key=lambda i:(distances[i],ids[i]));assert [ids[i] for i in order]==[a['pair_id'] for a in n['ranking']]
            for i,saved in zip(order,n['ranking']):
                np.testing.assert_allclose(saved['distance'],distances[i],rtol=0,atol=1e-12);assert saved['target_matches']==target_match[i]
            same=next((i for i in order if target_match[i]),None);different=next((i for i in order if not target_match[i]),None)
            assert (n['nearest_matching_target']['pair_id'] if same is not None else None)==(ids[same] if same is not None else None)
            assert (n['nearest_different_target']['pair_id'] if different is not None else None)==(ids[different] if different is not None else None)
            expected_closer=distances[different]<distances[same] if same is not None and different is not None else None
            assert n['different_target_strictly_closer']==expected_closer
            assert n['nearest_matching_target_in_leaf']==(bool(training_leaves[same]==node) if same is not None else None)
            csv_rows.append(dict(pair_id=r['pair_id'],method=r['method'],reference_status=r['reference_status'],variant=r['variant'],distance=name,
                worsened=r['worsened_vs_no_correction'],leaf_id=node,leaf_matching_members=r['leaf_matching_members'],leaf_members=r['leaf_members'],
                leaf_only_different_targets=r['leaf_only_different_targets'],leaf_mixed_targets=r['leaf_mixed_targets'],
                nearest=n['ranking'][0]['pair_id'],nearest_distance=n['ranking'][0]['distance'],nearest_target_matches=n['ranking'][0]['target_matches'],
                nearest_same_target=ids[same] if same is not None else '',same_target_distance=distances[same] if same is not None else '',
                nearest_different_target=ids[different] if different is not None else '',different_target_distance=distances[different] if different is not None else '',
                different_target_closer=expected_closer))
            for rank,i in enumerate(order[:3],1):neighbors.append(dict(probe=r['pair_id'],method=r['method'],distance=name,rank=rank,neighbor=ids[i],
                standardized_distance=distances[i],target_matches=target_match[i],same_leaf=bool(training_leaves[i]==node),neighbor_variant=lookup[ids[i]]['variant'],neighbor_features=x[i],neighbor_targets=y[i]))
            rankings_checked+=1
    for count in data['counts']:
        part=[]
        for r in data['records']:
            if r['method']!=count['method']:continue
            primary=r['reference_status']=='primary_eligible_ID';control=r['variant'] in ['identity_control','mild_bright_exposure'];subset=count['subset']
            if (subset=='held_diagnostics' and not primary) or (primary and (subset=='all_primary' or control and (subset=='primary_controls' or subset=='harmful_primary_controls' and r['worsened_vs_no_correction']))):part.append(r)
        assert count['probes']==len(part)
        assert count['matching_target_available']==sum(r['neighborhoods'][count['distance']]['nearest_matching_target'] is not None for r in part)
        assert count['different_target_closer']==sum(r['neighborhoods'][count['distance']]['different_target_strictly_closer'] is True for r in part)
        assert count['matching_nearest_target_but_leaf_excludes_it']==sum(r['neighborhoods'][count['distance']]['ranking'][0]['target_matches'] and r['neighborhoods'][count['distance']]['nearest_matching_target_in_leaf'] is False for r in part)
        assert count['leaves_only_different_targets']==sum(r['leaf_only_different_targets'] for r in part)
        assert count['mixed_target_leaves']==sum(r['leaf_mixed_targets'] for r in part)
    # Check the actual rounded and float32 collision claims without assigning a proximity cutoff.
    eligible=[lookup[p] for p in sorted(prior['eligible_ids'])];collisions=[]
    for i,a in enumerate(eligible):
        for b in eligible[i+1:]:
            if a['source_image_id']==b['source_image_id']:continue
            for label,dtype in [('rounded_features',float),('float32_features',np.float32)]:
                if np.array_equal(np.asarray(a['features'],dtype),np.asarray(b['features'],dtype)):
                    collisions.append((a['pair_id'],b['pair_id'],label))
    assert len(collisions)==len(data['exact_feature_collisions'])==0
    assert max(abs(r['features'][3]-round(math.degrees(math.atan((r['features'][0]-50)/r['features'][2])),4)) for r in lookup.values())==data['ita_max_recomputed_error']==0
    for name,rows in [('neighbor_summary.csv',csv_rows),('top3_neighbors.csv',neighbors),('counts.csv',data['counts'])]:
        with (out/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    primary_controls=[r for r in data['records'] if r['method']=='with_controls' and r['reference_status']=='primary_eligible_ID' and r['variant'] in ['identity_control','mild_bright_exposure']]
    page=['<!doctype html><meta charset="utf-8"><title>Core feature/target diagnostic</title><style>body{font:16px system-ui;max-width:1200px;margin:24px auto;background:#182028;color:#eee}a{color:#9cd9ff}img{max-width:100%}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #627080;padding:6px;text-align:left}details{margin:18px 0}</style><h1>Why controls still overcorrect</h1><p>Saved folds only: no fit, threshold or new prediction rule.12primary controls,22primary probes and8held diagnostic probes remain separate. Distances use each fitting pool only and are descriptive, not perceptual similarity/confidence.</p><p>11/12primary controls have a different-target nearest example in standardized3D Lab. One failed control has a matching nearest example excluded by its tree leaf. No exact cross-source feature collisions. ITA is derived from L* and b*, not an independent color measurement.</p><p><a href="neighbor_summary.csv">All neighbor summaries</a> · <a href="top3_neighbors.csv">Top3neighbors</a> · <a href="counts.csv">Denominators</a> · <a href="summary.json">Full routes/leaf members</a> · <a href="verification.json">Replay</a></p><img src="feature_projection.png"><p>The2D figure omits a*; it cannot establish separation/overlap in the full measured space.</p>']
    for r in primary_controls:
        n=r['neighborhoods']['Lab3'];page.append('<details><summary>'+html.escape(r['pair_id'])+' — '+('worsened' if r['worsened_vs_no_correction'] else 'not worsened')+'</summary>')
        page.append('<p>Predicted gamma/red/blue: '+html.escape(str(r['predicted_parameters']))+'; target: '+html.escape(str(r['target_parameters']))+'. Leaf matching members: '+str(r['leaf_matching_members'])+'/'+str(r['leaf_members'])+'.</p><table><tr><th>Nearest training example</th><th>Distance</th><th>Matching target</th><th>Same leaf</th></tr>')
        for neighbor in n['top3']:page.append('<tr><td>'+html.escape(neighbor['pair_id'])+'</td><td>'+format(neighbor['distance'],'.4f')+'</td><td>'+str(neighbor['target_matches'])+'</td><td>'+str(neighbor['same_leaf'])+'</td></tr>')
        page.append('</table></details>')
    (out/'review.html').write_text('\n'.join(page),encoding='utf-8')
    assert all(digest(ROOT/p)==h for p,h in data['input_sha256'].items())
    result=dict(status='pass',routing_leaf_means_checked=leaf_checks,rankings_recomputed=rankings_checked,neighbor_summary_rows=len(csv_rows),top3_neighbor_rows=len(neighbors),
        count_rows_checked=len(data['counts']),exact_feature_collision_claim_verified=True,ita_relation_verified=True,original_hashes_unchanged=True,new_model_fits=0,
        summary_sha256=digest(out/'summary.json'),verifier_sha256=digest(Path(__file__)),
        artifact_sha256={str(p.relative_to(ROOT)):digest(p) for p in list(out.glob('*.csv'))+list(out.glob('*.png'))+list(out.glob('*.pdf'))+list(out.glob('*.html'))})
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'}))
if __name__=='__main__':main()
