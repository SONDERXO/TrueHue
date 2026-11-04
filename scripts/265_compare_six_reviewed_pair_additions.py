"""Source-held paired training after exact human acceptance of six new masks."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
OUT=ROOT/'outputs/six_reviewed_pair_comparison_v1'
PARENT=ROOT/'outputs/accepted_clean_control_comparison_v1'
IMPORTED=ROOT/'outputs/distorted_mask_review11_import_v1'
METHODS=('clean_augmented_baseline','six_pairs_added')


def summarize(records):
    filters={'historical_all':lambda r:r['cohort']=='historical',
        'historical_distorted':lambda r:r['cohort']=='historical' and r['variant']!='identity',
        'all_clean':lambda r:r['variant']=='identity','new_distorted':lambda r:r['cohort']=='new_distorted',
        'original_41':lambda r:r['cohort']!='new_distorted','combined_47':lambda r:True}
    aggregates=[];gates={}
    for method in METHODS:
        for scope,include in filters.items():
            part=[r for r in records if r['method']==method and include(r)]
            aggregates.append(dict(method=method,scope=scope,pairs=len(part),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in part])),
                changed_pairs=sum(r['changed_input_pixels']>0 for r in part)))
        harms=[r['pair_id'] for r in records if r['method']==method and r['variant']=='identity' and r['changed_input_pixels']]
        improves=aggregates[-1]['mean_ciede2000']<aggregates[-1]['no_correction']
        gates[method]=dict(overall_improves=improves,clean_unchanged=not harms,harmed_clean_ids=harms,passed=improves and not harms)
    return dict(aggregates=aggregates,gates=gates,regression_fits=52,held_predictions=94,source_groups=26,
        active_demo_changed=False,evidence_role='exposed source-held development; not final validation')


def fitting_ids(plan,fold,method):
    ids=fold['historical_train_ids']+fold['new_control_train_ids']
    if method=='six_pairs_added':ids+=[r['pair_id'] for r in plan['rows'] if r['cohort']=='new_distorted' and r['duplicate_group_id']!=fold['held_group']]
    return ids


def train():
    if OUT.exists():raise FileExistsError(OUT)
    parent=h.read(PARENT/'plan.json');added=h.read(IMPORTED/'accepted_pairs.json');verification=h.read(IMPORTED/'verification.json')
    assert verification['status']=='pass' and len(added)==6
    for path,sha in verification['evidence_sha256'].items():assert h.digest(IMPORTED/path)==sha
    rows=parent['rows']+added;assert len(rows)==47 and len({r['pair_id'] for r in rows})==47
    folds=[]
    for old in parent['folds']:
        folds.append(dict(old,held_pair_ids=[r['pair_id'] for r in rows if r['duplicate_group_id']==old['held_group']]))
    hashes=dict(parent['input_sha256'])
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/reviewed-six-pair-training-protocol.md',IMPORTED/'accepted_pairs.json',IMPORTED/'verification.json',IMPORTED/'reconciled_reviews.json',IMPORTED/'original_user_export.json',PARENT/'plan.json',PARENT/'verification.json']
    for row in added:paths.extend(ROOT/row[k] for k in ('input_path','input_mask_path','reference_path','reference_mask_path'))
    hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    plan=dict(parent,rows=rows,folds=folds,input_sha256=hashes,methods=METHODS,status='frozen_before_training',
        new_distorted_pairs_admitted=6,accepted_with_notes=verification['accepted_with_notes'])
    OUT.mkdir();h.write(OUT/'plan.json',plan)
    by_id={r['pair_id']:r for r in rows};records=[]
    for fold in folds:
        folder=OUT/f'fold_{fold["fold_id"]}';folder.mkdir()
        for method in METHODS:
            ids=fitting_ids(plan,fold,method);fitting=[by_id[p] for p in ids]
            assert not {r['source_image_id'] for r in fitting}&{by_id[p]['source_image_id'] for p in fold['held_pair_ids']}
            x=[h.vector(r,plan) for r in fitting]
            raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[r['paper_target'] for r in fitting]),plan['features'],plan['target_names'],dict(method=method,held_group=fold['held_group'],gamma_convention='direct_exponent'))
            payload,audit=protect_identity_leaves(raw,x,[r['variant']=='identity' for r in fitting]);tree=PortableTree(payload)
            h.write(folder/(method+'.json'),payload);h.write(folder/(method+'_membership.json'),dict(train_pair_ids=ids,**audit))
            for pair in fold['held_pair_ids']:
                row=by_id[pair];params=tree.predict_one(h.vector(row,plan))
                image,reference,mask,score,output=h.render(row,params)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(pair+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records.append(dict(pair_id=pair,source_image_id=row['source_image_id'],method=method,fold_id=fold['fold_id'],
                    cohort=row['cohort'],variant=row['variant'],parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                    metrics=image_errors(reference,output,score),no_correction=image_errors(reference,image,score),output_sha256=h.digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');records=h.read(OUT/'predictions.json');rows={r['pair_id']:r for r in plan['rows']}
    parent=h.read(PARENT/'plan.json');added=h.read(IMPORTED/'accepted_pairs.json')
    assert plan['rows']==parent['rows']+added
    assert {r['source_image_id'] for r in added}=={r['image_id'] for r in h.read(IMPORTED/'reconciled_reviews.json') if r['decision']=='accept'}
    assert len(records)==94 and len({(r['pair_id'],r['method']) for r in records})==94
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    fits=0
    for fold in plan['folds']:
        held={p for p,r in rows.items() if r['duplicate_group_id']==fold['held_group']}
        assert held==set(fold['held_pair_ids'])
        for method in METHODS:
            # Independent cohort-based reconstruction, not fitting_ids().
            expected=[r['pair_id'] for r in plan['rows'] if r['duplicate_group_id']!=fold['held_group'] and (method=='six_pairs_added' or r['cohort']!='new_distorted')]
            ids=fitting_ids(plan,fold,method);assert ids==expected
            assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
            x=[h.vector(rows[p],plan) for p in ids]
            raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),plan['features'],plan['target_names'],{})
            rawtree=PortableTree(raw);leaves=[rawtree.leaf_id(v) for v in x]
            protected={leaf for p,leaf in zip(ids,leaves) if rows[p]['variant']=='identity'}
            for leaf in protected:raw['nodes'][leaf]['values']=[1.,1.,1.]
            folder=OUT/f'fold_{fold["fold_id"]}';saved=h.read(folder/(method+'.json'));assert saved['nodes']==raw['nodes']
            audit=h.read(folder/(method+'_membership.json'));assert audit['train_pair_ids']==ids and audit['protected_leaves']==sorted(protected)
            for leaf in set(leaves):
                indices=[i for i,v in enumerate(leaves) if v==leaf]
                assert audit['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=[i for i in indices if rows[ids[i]]['variant']=='identity'])
            for record in [r for r in records if r['fold_id']==fold['fold_id'] and r['method']==method]:
                assert record['pair_id'] in held;row=rows[record['pair_id']]
                assert PortableTree(saved).predict_one(h.vector(row,plan))==record['parameters']
                image,reference,mask,score,output=h.render(row,record['parameters']);path=folder/(record['pair_id']+'_'+method+'.png')
                assert h.digest(path)==record['output_sha256'];np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
                np.testing.assert_array_equal(output[~mask],image[~mask]);assert np.count_nonzero(np.any(output!=image,axis=2))==record['changed_input_pixels']
                assert image_errors(reference,output,score)==record['metrics'] and image_errors(reference,image,score)==record['no_correction']
            fits+=1
    assert fits==52 and summarize(records)==h.read(OUT/'summary.json')
    old={r['pair_id']:r for r in h.read(PARENT/'predictions.json') if r['method']=='new_clean_sources'}
    for r in records:
        if r['method']=='clean_augmented_baseline' and r['pair_id'] in old:
            assert r['parameters']==old[r['pair_id']]['parameters'] and r['metrics']==old[r['pair_id']]['metrics']
    h.write(target,dict(status='pass',independent_refits=52,output_and_metric_replays=94,original_41_baseline_parity=True,
        source_separation_and_exact_accepted_admissions_verified=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 52 refits, 94 output/metric replays, exact six accepted additions and original baseline parity.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else train()
