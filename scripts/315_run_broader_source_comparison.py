"""Execute the single frozen32-source comparison; reuse old predictions verbatim."""
import importlib
import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.evaluation.correction_prototype import image_errors
from src.ita_estimation.square_measurement import contract
h=importlib.import_module('256_compare_clean_control_tree_depth')
BASE=ROOT/'outputs';READY=BASE/'broader_source_comparison_readiness_v1'
OUT=BASE/'broader_source_comparison_v1'
METHODS=['A','B','C']


def aggregate(records,rows):
    old={r['pair_id'] for r in h.read(BASE/'reviewed_primary_comparison_v1/plan.json')['rows']}
    original47=set(h.read(BASE/'endpoint_feature_tree_v1/plan.json')['rows'][i]['pair_id'] for i in range(47))
    filters=dict(all=lambda p:True,clean=lambda p:rows[p]['stratum']=='original_control',
        primary_all=lambda p:rows[p]['stratum']=='primary',
        primary_old=lambda p:rows[p]['stratum']=='primary' and p in old,
        primary_new=lambda p:rows[p]['stratum']=='primary' and p not in old,
        stress_all=lambda p:rows[p]['stratum']=='clipped_stress',
        stress_old=lambda p:rows[p]['stratum']=='clipped_stress' and p in old,
        stress_new=lambda p:rows[p]['stratum']=='clipped_stress' and p not in old,
        original47=lambda p:p in original47,original105=lambda p:p in old)
    for variant in ['gamma_lighten','gamma_darken','color','exposure']:
        filters['primary_'+variant]=lambda p,v=variant:rows[p]['stratum']=='primary' and rows[p]['variant']==v
    result=[]
    for method in ['no_correction']+METHODS:
        for scope,include in filters.items():
            part=[r for r in records if r['method']==('C' if method=='no_correction' else method) and include(r['pair_id'])]
            grouped=defaultdict(list);values=[]
            for r in part:
                value=r['no_correction' if method=='no_correction' else 'metrics']['ciede2000_source_mask']
                values.append(value);grouped[r['source_image_id']].append(value)
            result.append(dict(method=method,scope=scope,cases=len(part),sources=len(grouped),
                case_weighted=None if not values else float(np.mean(values)),
                source_equal=None if not values else float(np.mean([np.mean(v) for v in grouped.values()]))))
    def metric(method,scope,weight):return next(r[weight] for r in result if r['method']==method and r['scope']==scope)
    harms={m:[r['pair_id'] for r in records if r['method']==m and rows[r['pair_id']]['stratum']=='original_control' and r['changed_input_pixels']>0] for m in METHODS}
    gates={'all_clean_originals_unchanged':not harms['C']}
    for weight in ['case_weighted','source_equal']:
        for scope in ['primary_new','primary_all','all']:
            gates[f'{weight}_{scope}_improves_no_correction']=metric('C',scope,weight) is not None and metric('C',scope,weight)<metric('no_correction',scope,weight)
        gates[weight+'_total_improves_A']=metric('C','all',weight)<metric('A','all',weight)
        gates[weight+'_new_primary_improves_B']=metric('C','primary_new',weight)<metric('B','primary_new',weight)
        for scope in ['primary_color','stress_all']:
            gates[f'{weight}_{scope}_no_worse_than_A']=metric('C',scope,weight) is not None and metric('C',scope,weight)<=metric('A',scope,weight)
    return dict(aggregates=result,gates=gates,passed=all(gates.values()),clean_failures=harms,
        new_tree_fits=34,reused_trees=52,reused_predictions=210,new_predictions=153,total_predictions=363,
        evaluation_cases=121,source_groups=32,active_demo_changed=False,exposed_development_only=True)


def run(resume=False):
    if OUT.exists() and not resume:raise FileExistsError(OUT)
    if resume and ((OUT/'predictions.json').exists() or not (OUT/'plan.json').exists()):raise RuntimeError('No incomplete run to resume')
    plan=h.read(READY/'plan.json');verify=h.read(READY/'verification.json')
    assert verify['status']=='pass'
    for p,sha in verify['evidence_sha256'].items():assert h.digest(READY/p)==sha
    for p,sha in verify['input_sha256'].items():assert h.digest(ROOT/p)==sha
    _,identity=contract(ROOT);assert identity==plan['measurement_contract_sha256']
    lookup=BASE/'mst_monotone_square256_v1/development_lookup.json';assert h.digest(lookup)==plan['lookup_sha256']
    old=h.read(BASE/'reviewed_primary_comparison_v1/plan.json');oldrows={r['pair_id']:r for r in old['rows']}
    controls={r['source_image_id']:r for r in plan['rows'] if r['stratum']=='original_control'}
    for r in plan['rows']:
        if r['pair_id'] in oldrows:
            original=oldrows[r['pair_id']]
            r.update({k:original[k] for k in ['variant','reference_path','reference_mask_path']})
        else:
            c=controls[r['source_image_id']]
            r['reference_path']=c['input_path'];r['reference_mask_path']=c['input_mask_path']
            r.setdefault('variant','identity' if r['stratum']=='original_control' else 'saved_composite_stress')
        for path,key in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256')]:assert h.digest(ROOT/r[path])==r[key]
    rows={r['pair_id']:r for r in plan['rows']};vectors={p:r['features'] for p,r in rows.items()}
    assert len(rows)==121 and len(plan['C_ordered_fit_candidates'])==94
    aliases={}
    for r in rows.values():
        assert r['input_sha256'] not in aliases,('image alias',r['pair_id'])
        aliases[r['input_sha256']]=r['pair_id']
    plan.update(status='authorized_single_frozen_comparison',execution_started=True,target_names=old['target_names'],methods=METHODS,
        runner_sha256=h.digest(Path(__file__)),readiness_plan_sha256=h.digest(READY/'plan.json'),
        protocol_sha256=h.digest(ROOT/plan['protocol']),implementation_dependencies_sha256={p:h.digest(ROOT/p) for p in
        ['src/model_training/portable_tree.py','src/model_training/training_identity_leaf_policy.py',
         'src/distortion_generation/paper_gamma.py','src/evaluation/correction_prototype.py','scripts/256_compare_clean_control_tree_depth.py']})
    if resume:
        prior=h.read(OUT/'plan.json')
        if not (OUT/'initial_interrupted_plan.json').exists():h.write(OUT/'initial_interrupted_plan.json',prior)
        plan['resume_reason']='Missing added-source variant metadata interrupted reporting; preserve and reuse every saved fit.'
        plan['initial_interrupted_plan_sha256']=h.digest(OUT/'initial_interrupted_plan.json')
    else:OUT.mkdir()
    h.write(OUT/'plan.json',plan)
    records=[];trees={};new_fit_count=0
    def fit(method,ids,folder,held_group):
        nonlocal new_fit_count
        folder.mkdir(parents=True,exist_ok=True)
        if (folder/(method+'.json')).exists():
            assert resume
            membership=h.read(folder/(method+'_membership.json'))
            assert membership['train_pair_ids']==ids
            new_fit_count+=1
            return PortableTree(h.read(folder/(method+'.json')))
        x=[vectors[p] for p in ids];y=[rows[p]['target_direct_gamma_red_blue'] for p in ids]
        model=DecisionTreeRegressor(**plan['settings']).fit(x,y)
        raw=export_tree(model,plan['features'],plan['target_names'],dict(gamma_convention='direct_exponent',held_group=held_group,method=method))
        payload,audit=protect_identity_leaves(raw,x,[rows[p]['stratum']=='original_control' for p in ids])
        tree=PortableTree(payload)
        # Check exported unprotected predictions against the trained estimator.
        np.testing.assert_allclose([PortableTree(raw).predict_one(v) for v in x],model.predict(x),rtol=0,atol=1e-12)
        h.write(folder/(method+'.json'),payload);h.write(folder/(method+'_membership.json'),dict(train_pair_ids=ids,**audit))
        new_fit_count+=1
        return tree
    for method in ['A','B']:
        trees[(method,'shared')]=fit(method,plan[method+'_ordered_fit_candidates'],OUT/'shared','six_new_sources_absent_from_historical_training')
    reusable={(r['method'],r['held_group']):r for r in plan['historical_reusable_trees']}
    historical={(('A' if r['method']=='frozen_endpoint_baseline' else 'B'),r['pair_id']):r for r in h.read(BASE/'reviewed_primary_comparison_v1/predictions.json')}
    for f in plan['folds']:
        fid=f['fold_id'];group=f['held_group'];folder=OUT/f'fold_{fid}'
        ids=f['C_ordered_training_pair_ids'];held=f['evaluation_pair_ids']
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        trees[('C',group)]=fit('C',ids,folder,group)
        for method in ['A','B']:
            if (method,group) in reusable:
                r=reusable[(method,group)];assert h.digest(ROOT/r['tree_path'])==r['tree_sha256']
                trees[(method,group)]=PortableTree(h.read(ROOT/r['tree_path']))
            else:trees[(method,group)]=trees[(method,'shared')]
        h.write(folder/'membership.json',f)
        for pair in held:
            row=rows[pair]
            for method in METHODS:
                tree=trees[(method,group)]
                if (method,pair) in historical:
                    prior=historical[(method,pair)]
                    assert tree.predict_one(vectors[pair])==prior['parameters']
                    path=BASE/'reviewed_primary_comparison_v1'/f'fold_{prior["fold_id"]}'/(pair+'_'+prior['method']+'.png')
                    assert h.digest(path)==prior['output_sha256']
                    records.append(dict(prior,method=method,fold_id=fid,reused=True,original_record=prior,
                        output_path=path.relative_to(ROOT).as_posix()))
                    continue
                with (OUT/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                    stream.write(json.dumps(dict(pair_id=pair,source_image_id=row['source_image_id'],phase='fixed_comparison_render',method=method,historical_or_train_role=True))+'\n')
                params=tree.predict_one(vectors[pair]);image,reference,mask,score,output=h.render(row,params)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(pair+'_'+method+'.png')
                if path.exists():
                    assert resume
                    np.testing.assert_array_equal(output,cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB))
                else:assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records.append(dict(pair_id=pair,source_image_id=row['source_image_id'],method=method,fold_id=fid,
                    variant=row['variant'],parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                    metrics=image_errors(reference,output,score),no_correction=image_errors(reference,image,score),
                    output_path=path.relative_to(ROOT).as_posix(),output_sha256=h.digest(path),reused=False))
        print('Fold',fid,'complete',flush=True)
        h.write(folder/'predictions.json',[r for r in records if r['fold_id']==fid])
    assert new_fit_count==34 and len(records)==363 and sum(r['reused'] for r in records)==210
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',aggregate(records,rows))
    print('Done:34 new fits,210 predictions reused,153 new predictions.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true')
    run(resume=parser.parse_args().resume)
