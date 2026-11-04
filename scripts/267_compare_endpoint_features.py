"""One endpoint-feature candidate against two verified saved baselines."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.facial_endpoint_features import facial_endpoint_features,ADDITIONS
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
prior=importlib.import_module('265_compare_six_reviewed_pair_additions')
PARENT=ROOT/'outputs/six_reviewed_pair_comparison_v1'
OUT=ROOT/'outputs/endpoint_feature_tree_v1'
CANDIDATE='paired_endpoint11'
METHODS=(*prior.METHODS,CANDIDATE)


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
    return dict(aggregates=aggregates,gates=gates,new_fits=26,new_predictions=47,imported_baseline_predictions=94,
        active_demo_changed=False,evidence_role='exposed development; synthetic endpoint shortcut risk')


def train():
    if OUT.exists():raise FileExistsError(OUT)
    parent=h.read(PARENT/'plan.json');verification=h.read(PARENT/'verification.json')
    assert verification['status']=='pass'
    for path,sha in verification['evidence_sha256'].items():assert h.digest(PARENT/path)==sha
    hashes=dict(parent['input_sha256'])
    paths=[Path(__file__),Path(h.__file__),Path(prior.__file__),ROOT/'src/model_training/facial_endpoint_features.py',ROOT/'docs/endpoint-feature-tree-protocol.md']
    paths.extend(PARENT/path for path in verification['evidence_sha256']);paths.append(PARENT/'verification.json')
    hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    plan=dict(parent,input_sha256=hashes,features=parent['features']+list(ADDITIONS),baseline_features=parent['features'],methods=METHODS,status='frozen_before_training')
    OUT.mkdir();h.write(OUT/'plan.json',plan)
    rows={r['pair_id']:r for r in plan['rows']};extra={}
    for pair,row in rows.items():
        result=facial_endpoint_features(cv2.imread(str(ROOT/row['input_path'])),cv2.imread(str(ROOT/row['input_mask_path']),0)>0)
        assert result['valid'];extra[pair]=result['features']
    h.write(OUT/'features.json',extra)
    records=h.read(PARENT/'predictions.json')
    for fold in plan['folds']:
        ids=prior.fitting_ids(plan,fold,'six_pairs_added')
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in fold['held_pair_ids']}
        def vector(p):return [{**rows[p],**extra[p]}[k] for k in plan['features']]
        x=[vector(p) for p in ids]
        raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),plan['features'],plan['target_names'],dict(held_group=fold['held_group'],gamma_convention='direct_exponent'))
        payload,audit=protect_identity_leaves(raw,x,[rows[p]['variant']=='identity' for p in ids]);tree=PortableTree(payload)
        folder=OUT/f'fold_{fold["fold_id"]}';folder.mkdir()
        h.write(folder/'candidate.json',payload);h.write(folder/'membership.json',dict(train_pair_ids=ids,**audit))
        for pair in fold['held_pair_ids']:
            row=rows[pair];params=tree.predict_one(vector(pair));image,reference,mask,score,output=h.render(row,params)
            assert np.array_equal(output[~mask],image[~mask])
            path=folder/(pair+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
            records.append(dict(pair_id=pair,source_image_id=row['source_image_id'],method=CANDIDATE,fold_id=fold['fold_id'],
                cohort=row['cohort'],variant=row['variant'],parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(image!=output,axis=2))),
                metrics=image_errors(reference,output,score),no_correction=image_errors(reference,image,score),output_sha256=h.digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');rows={r['pair_id']:r for r in plan['rows']};extra=h.read(OUT/'features.json')
    parent=h.read(PARENT/'plan.json');assert plan['rows']==parent['rows'] and plan['folds']==parent['folds']
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    for pair,row in rows.items():
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        count=int(mask.sum());values=[]
        for channel in (2,1,0):
            counts=np.bincount(image[:,:,channel][mask],minlength=256)
            values.extend([float(counts[0]/count),float(counts[255]/count)])
        assert dict(zip(ADDITIONS,values))==extra[pair]
    records=h.read(OUT/'predictions.json');assert len(records)==141 and len({(r['method'],r['pair_id']) for r in records})==141
    assert [r for r in records if r['method']!=CANDIDATE]==h.read(PARENT/'predictions.json')
    fits=0
    for fold in plan['folds']:
        held={p for p,r in rows.items() if r['duplicate_group_id']==fold['held_group']}
        assert held==set(fold['held_pair_ids'])
        ids=[r['pair_id'] for r in plan['rows'] if r['duplicate_group_id']!=fold['held_group']]
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        def vector(p):return [{**rows[p],**extra[p]}[k] for k in plan['features']]
        x=[vector(p) for p in ids]
        raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),plan['features'],plan['target_names'],{})
        rawtree=PortableTree(raw);leaves=[rawtree.leaf_id(v) for v in x]
        protected={leaf for p,leaf in zip(ids,leaves) if rows[p]['variant']=='identity'}
        for leaf in protected:raw['nodes'][leaf]['values']=[1.,1.,1.]
        folder=OUT/f'fold_{fold["fold_id"]}';saved=h.read(folder/'candidate.json');assert saved['nodes']==raw['nodes']
        audit=h.read(folder/'membership.json');assert audit['train_pair_ids']==ids and audit['protected_leaves']==sorted(protected)
        for leaf in set(leaves):
            indices=[i for i,v in enumerate(leaves) if v==leaf]
            assert audit['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=[i for i in indices if rows[ids[i]]['variant']=='identity'])
        for r in [r for r in records if r['method']==CANDIDATE and r['fold_id']==fold['fold_id']]:
            assert r['pair_id'] in held;row=rows[r['pair_id']]
            assert PortableTree(saved).predict_one(vector(r['pair_id']))==r['parameters']
            image,reference,mask,score,output=h.render(row,r['parameters']);path=folder/(r['pair_id']+'.png')
            assert h.digest(path)==r['output_sha256'];np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
            np.testing.assert_array_equal(output[~mask],image[~mask]);assert np.count_nonzero(np.any(output!=image,axis=2))==r['changed_input_pixels']
            assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,image,score)==r['no_correction']
        fits+=1
    assert fits==26 and summarize(records)==h.read(OUT/'summary.json')
    h.write(target,dict(status='pass',independent_endpoint_vectors=47,independent_tree_refits=26,new_output_metric_replays=47,
        exact_imported_baseline_predictions=94,source_separation_and_fitting_membership_verified=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 47 endpoint vectors, 26 refits, 47 new image replays and exact 94 baseline records.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else train()
