"""Source-held ordinary versus log multiplier targets; unchanged runtime curves."""
import argparse
from copy import deepcopy
import importlib
import json
import math
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.portable_tree import PortableTree, export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.evaluation.correction_prototype import image_errors
helpers = importlib.import_module('256_compare_clean_control_tree_depth')
OUT = ROOT / 'outputs/log_correction_targets_v1'
PARENT = ROOT / 'outputs/accepted_clean_control_comparison_v1'
METHODS = ('ordinary', 'log')
read, write, digest, vector, render = helpers.read, helpers.write, helpers.digest, helpers.vector, helpers.render


def summary(records):
    aggregates, gates = [], {}
    for method in METHODS:
        for scope in ('historical_all','historical_clean','historical_distorted','new_clean','combined'):
            values = helpers.selected(records, method, scope)
            aggregates.append(dict(method=method,scope=scope,pairs=len(values),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in values])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in values])),
                changed_pairs=sum(r['changed_input_pixels'] > 0 for r in values)))
        harms = [r['pair_id'] for r in helpers.selected(records,method,'combined') if r['variant']=='identity' and r['changed_input_pixels']]
        improves = aggregates[-1]['mean_ciede2000'] < aggregates[-1]['no_correction']
        gates[method] = dict(overall_improves=improves,clean_unchanged=not harms,harmed_clean_ids=harms,passed=improves and not harms)
    return dict(aggregates=aggregates,gates=gates,regression_fits=52,held_predictions=82,
                active_demo_changed=False,evidence_role='exposed source-held development, not final validation')


def train():
    if OUT.exists(): raise FileExistsError(OUT)
    parent = read(PARENT/'plan.json')
    assert read(PARENT/'verification.json')['status']=='pass'
    hashes = dict(parent['input_sha256'])
    for path in (Path(__file__),Path(helpers.__file__),ROOT/'docs/log-target-tree-protocol.md',PARENT/'plan.json',PARENT/'verification.json'):
        hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    for path, sha in hashes.items(): assert digest(ROOT/path)==sha
    plan = dict(parent,input_sha256=hashes,methods=METHODS,status='frozen_before_training',target_coordinates={'ordinary':'direct multipliers','log':'natural log of direct multipliers; invert leaves before protection'})
    OUT.mkdir(); write(OUT/'plan.json',plan)
    rows = {r['pair_id']:r for r in plan['rows']}; records=[]
    for fold in plan['folds']:
        ids = fold['historical_train_ids']+fold['new_control_train_ids']
        fitting = [rows[p] for p in ids]
        assert not {r['source_image_id'] for r in fitting}&{rows[p]['source_image_id'] for p in fold['held_pair_ids']}
        x = [vector(r,plan) for r in fitting]; targets=np.array([r['paper_target'] for r in fitting])
        assert np.isfinite(targets).all() and (targets>0).all()
        folder=OUT/f'fold_{fold["fold_id"]}';folder.mkdir()
        for method in METHODS:
            y=np.log(targets) if method=='log' else targets
            model=DecisionTreeRegressor(**plan['settings']).fit(x,y)
            # Runtime export accepts positive multipliers only, never log values.
            if method=='log':model.tree_.value[:]=np.exp(model.tree_.value)
            raw=export_tree(model,plan['features'],plan['target_names'],dict(training_target_coordinates=method,inference_coordinates='direct multipliers',held_group=fold['held_group']))
            payload,audit=protect_identity_leaves(raw,x,[r['variant']=='identity' for r in fitting])
            write(folder/(method+'.json'),payload);write(folder/(method+'_membership.json'),dict(train_pair_ids=ids,**audit))
            tree=PortableTree(payload)
            for pair in fold['held_pair_ids']:
                row=rows[pair];params=tree.predict_one(vector(row,plan))
                image,reference,mask,score,output=render(row,params)
                assert np.array_equal(output[~mask],image[~mask])
                path=folder/(pair+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                records.append(dict(pair_id=pair,method=method,fold_id=fold['fold_id'],cohort=row['cohort'],variant=row['variant'],parameters=params,
                    changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),
                    metrics=image_errors(reference,output,score),no_correction=image_errors(reference,image,score),output_sha256=digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    write(OUT/'predictions.json',records);write(OUT/'summary.json',summary(records))
    print('Saved 52 fits and 82 predictions.')


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=read(OUT/'plan.json');records=read(OUT/'predictions.json');rows={r['pair_id']:r for r in plan['rows']}
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    parent=read(PARENT/'plan.json');assert plan['rows']==parent['rows'] and plan['folds']==parent['folds']
    assert len(records)==82 and len({(r['method'],r['pair_id']) for r in records})==82
    fits=0
    for fold in plan['folds']:
        ids=fold['historical_train_ids']+fold['new_control_train_ids']
        held={p for p,r in rows.items() if r['duplicate_group_id']==fold['held_group']}
        assert set(fold['held_pair_ids'])==held and set(ids)==set(rows)-held
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        x=[vector(rows[p],plan) for p in ids]
        for method in METHODS:
            y=[[math.log(v) if method=='log' else v for v in rows[p]['paper_target']] for p in ids]
            model=DecisionTreeRegressor(**plan['settings']).fit(x,y)
            if method=='log':
                for index in range(model.tree_.node_count):
                    for output in range(model.n_outputs_):
                        model.tree_.value[index,output,0]=math.exp(model.tree_.value[index,output,0])
            raw=export_tree(model,plan['features'],plan['target_names'],{})
            rawtree=PortableTree(raw);leaves=[rawtree.leaf_id(v) for v in x]
            protected={leaf for p,leaf in zip(ids,leaves) if rows[p]['variant']=='identity'}
            for index,node in enumerate(raw['nodes']):
                if node['kind']=='leaf':
                    if index in protected:node['values']=[1.,1.,1.]
            folder=OUT/f'fold_{fold["fold_id"]}';saved=read(folder/(method+'.json'))
            assert len(raw['nodes'])==len(saved['nodes'])
            for a,b in zip(raw['nodes'],saved['nodes']):
                if a['kind']=='split':assert a==b
                else:np.testing.assert_allclose(a['values'],b['values'],rtol=1e-14,atol=1e-14)
            audit=read(folder/(method+'_membership.json'))
            assert audit['train_pair_ids']==ids and audit['protected_leaves']==sorted(protected)
            for leaf in set(leaves):
                indices=[i for i,v in enumerate(leaves) if v==leaf]
                assert audit['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=[i for i in indices if rows[ids[i]]['variant']=='identity'])
            for r in [r for r in records if r['fold_id']==fold['fold_id'] and r['method']==method]:
                assert r['pair_id'] in held
                row=rows[r['pair_id']];assert PortableTree(saved).predict_one(vector(row,plan))==r['parameters']
                image,reference,mask,score,output=render(row,r['parameters'])
                path=folder/(r['pair_id']+'_'+method+'.png');assert digest(path)==r['output_sha256']
                np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
                np.testing.assert_array_equal(output[~mask],image[~mask])
                assert np.count_nonzero(np.any(output!=image,axis=2))==r['changed_input_pixels']
                assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,image,score)==r['no_correction']
            fits+=1
    assert summary(records)==read(OUT/'summary.json') and fits==52
    old={r['pair_id']:r for r in read(PARENT/'predictions.json') if r['method']=='new_clean_sources'}
    for r in records:
        if r['method']=='ordinary':assert r['parameters']==old[r['pair_id']]['parameters'] and r['metrics']==old[r['pair_id']]['metrics']
    write(target,dict(status='pass',independent_refits=52,replayed_outputs_and_metrics=82,
        source_separation_and_training_only_targets_verified=True,ordinary_parent_parity=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 52 refits, 82 output replays, fitting-only log targets and ordinary-parent parity.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else train()
