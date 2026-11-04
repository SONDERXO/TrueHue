"""Fixed five-versus-nine facial feature experiment and independent replay."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.model_training.facial_chromatic_features import facial_chromatic_features,ADDITIONS
from src.model_training.portable_tree import PortableTree,export_tree
from src.model_training.training_identity_leaf_policy import protect_identity_leaves
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
OUT=ROOT/'outputs/chromatic_feature_tree_v1';PARENT=ROOT/'outputs/accepted_clean_control_comparison_v1'
METHODS=('baseline5','chromatic9')


def summarize(records):
    aggregates=[];gates={}
    for method in METHODS:
        for scope in ('historical_all','historical_clean','historical_distorted','new_clean','combined'):
            part=h.selected(records,method,scope)
            aggregates.append(dict(method=method,scope=scope,pairs=len(part),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in part])),
                changed_pairs=sum(r['changed_input_pixels']>0 for r in part)))
        harms=[r['pair_id'] for r in h.selected(records,method,'combined') if r['variant']=='identity' and r['changed_input_pixels']]
        improves=aggregates[-1]['mean_ciede2000']<aggregates[-1]['no_correction']
        gates[method]=dict(overall_improves=improves,clean_unchanged=not harms,harmed_clean_ids=harms,passed=improves and not harms)
    return dict(aggregates=aggregates,gates=gates,regression_fits=52,held_predictions=82,active_demo_changed=False,
                evidence_role='exposed development only')


def train():
    if OUT.exists():raise FileExistsError(OUT)
    plan=h.read(PARENT/'plan.json');assert h.read(PARENT/'verification.json')['status']=='pass'
    hashes=dict(plan['input_sha256'])
    for path in (Path(__file__),Path(h.__file__),ROOT/'src/model_training/facial_chromatic_features.py',ROOT/'docs/chromatic-feature-tree-protocol.md',PARENT/'plan.json',PARENT/'verification.json'):
        hashes[path.relative_to(ROOT).as_posix()]=h.digest(path)
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    plan=dict(plan,input_sha256=hashes,methods=METHODS,feature_sets=dict(baseline5=plan['features'],chromatic9=plan['features']+list(ADDITIONS)))
    OUT.mkdir();h.write(OUT/'plan.json',plan)
    rows={r['pair_id']:r for r in plan['rows']};extra={}
    for pair,row in rows.items():
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        result=facial_chromatic_features(image,mask);assert result['valid'];extra[pair]=result['features']
    h.write(OUT/'features.json',extra);records=[]
    for fold in plan['folds']:
        ids=fold['historical_train_ids']+fold['new_control_train_ids']
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in fold['held_pair_ids']}
        folder=OUT/f'fold_{fold["fold_id"]}';folder.mkdir()
        for method in METHODS:
            columns=plan['feature_sets'][method]
            def vector(p):return [{**rows[p],**extra[p]}[k] for k in columns]
            x=[vector(p) for p in ids]
            raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),columns,plan['target_names'],dict(method=method,held_group=fold['held_group'],gamma_convention='direct_exponent'))
            payload,audit=protect_identity_leaves(raw,x,[rows[p]['variant']=='identity' for p in ids]);tree=PortableTree(payload)
            h.write(folder/(method+'.json'),payload);h.write(folder/(method+'_membership.json'),dict(train_pair_ids=ids,**audit))
            for pair in fold['held_pair_ids']:
                row=rows[pair];params=tree.predict_one(vector(pair));image,reference,mask,score,output=h.render(row,params)
                path=folder/(pair+'_'+method+'.png');assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                assert np.array_equal(output[~mask],image[~mask])
                records.append(dict(pair_id=pair,method=method,fold_id=fold['fold_id'],variant=row['variant'],cohort=row['cohort'],parameters=params,
                    changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),metrics=image_errors(reference,output,score),
                    no_correction=image_errors(reference,image,score),output_sha256=h.digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');extra=h.read(OUT/'features.json');rows={r['pair_id']:r for r in plan['rows']}
    parent=h.read(PARENT/'plan.json');assert plan['rows']==parent['rows'] and plan['folds']==parent['folds']
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    for pair,row in rows.items():
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
        expected=[]
        for axis in (1,2):
            pixels=np.sort(lab[:,:,axis][mask].astype(float)-128)
            def percentile(q):
                index=(len(pixels)-1)*q;low=int(np.floor(index));high=int(np.ceil(index))
                return float(pixels[low]+(index-low)*(pixels[high]-pixels[low]))
            expected.extend([percentile(.5),percentile(.75)-percentile(.25)])
        assert dict(zip(ADDITIONS,expected))==extra[pair]
    records=h.read(OUT/'predictions.json');assert len(records)==82 and len({(r['pair_id'],r['method']) for r in records})==82
    fits=0
    for fold in plan['folds']:
        ids=fold['historical_train_ids']+fold['new_control_train_ids'];held=set(fold['held_pair_ids'])
        assert held=={p for p,r in rows.items() if r['duplicate_group_id']==fold['held_group']} and set(ids)==set(rows)-held
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        for method in METHODS:
            columns=plan['feature_sets'][method]
            def vector(p):return [{**rows[p],**extra[p]}[k] for k in columns]
            x=[vector(p) for p in ids]
            raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),columns,plan['target_names'],{})
            rawtree=PortableTree(raw);leaves=[rawtree.leaf_id(v) for v in x]
            protected={leaf for p,leaf in zip(ids,leaves) if rows[p]['variant']=='identity'}
            for leaf in protected:raw['nodes'][leaf]['values']=[1.,1.,1.]
            folder=OUT/f'fold_{fold["fold_id"]}';saved=h.read(folder/(method+'.json'));assert saved['nodes']==raw['nodes']
            audit=h.read(folder/(method+'_membership.json'));assert audit['train_pair_ids']==ids and audit['protected_leaves']==sorted(protected)
            for leaf in set(leaves):
                indices=[i for i,value in enumerate(leaves) if value==leaf]
                assert audit['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=[i for i in indices if rows[ids[i]]['variant']=='identity'])
            for r in [r for r in records if r['method']==method and r['fold_id']==fold['fold_id']]:
                assert r['pair_id'] in held;row=rows[r['pair_id']]
                assert PortableTree(saved).predict_one(vector(r['pair_id']))==r['parameters']
                image,reference,mask,score,output=h.render(row,r['parameters']);path=folder/(r['pair_id']+'_'+method+'.png')
                assert h.digest(path)==r['output_sha256'];np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
                np.testing.assert_array_equal(output[~mask],image[~mask]);assert np.count_nonzero(np.any(output!=image,axis=2))==r['changed_input_pixels']
                assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,image,score)==r['no_correction']
            fits+=1
    assert fits==52 and summarize(records)==h.read(OUT/'summary.json')
    old={r['pair_id']:r for r in h.read(PARENT/'predictions.json') if r['method']=='new_clean_sources'}
    for r in records:
        if r['method']=='baseline5':assert r['parameters']==old[r['pair_id']]['parameters'] and r['metrics']==old[r['pair_id']]['metrics']
    h.write(target,dict(status='pass',independent_feature_vectors=41,independent_refits=52,output_and_metric_replays=82,
        source_separation_and_training_membership_verified=True,baseline_parent_parity=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 41 independent chromatic vectors, 52 refits, 82 output replays and baseline parity.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else train()
