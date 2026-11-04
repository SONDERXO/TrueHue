"""The single predeclared primary-data fit versus the frozen endpoint baseline."""
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
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.square_measurement import contract
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
PARENT=ROOT/'outputs/endpoint_feature_tree_v1';IMPORTED=ROOT/'outputs/primary_mask_review_import_v1'
OUT=ROOT/'outputs/reviewed_primary_comparison_v1';METHODS=('frozen_endpoint_baseline','primary_candidate')


def summarize(records):
    filters={'clean':lambda r:r['variant']=='identity','primary_all':lambda r:r['cohort']=='primary',
        'primary_lighten':lambda r:r['cohort']=='primary' and r['variant']=='gamma_lighten',
        'primary_darken':lambda r:r['cohort']=='primary' and r['variant']=='gamma_darken',
        'primary_color':lambda r:r['cohort']=='primary' and r['variant']=='color',
        'primary_exposure':lambda r:r['cohort']=='primary' and r['variant']=='exposure',
        'stress_21':lambda r:r['cohort']!='primary' and r['variant']!='identity',
        'original_47':lambda r:r['cohort']!='primary','all':lambda r:True}
    aggregates=[];gates={}
    for method in METHODS:
        for scope,include in filters.items():
            part=[r for r in records if r['method']==method and include(r)];source_ids=sorted({r['source_image_id'] for r in part})
            source_errors=[np.mean([r['metrics']['ciede2000_source_mask'] for r in part if r['source_image_id']==s]) for s in source_ids]
            source_unchanged=[np.mean([r['no_correction']['ciede2000_source_mask'] for r in part if r['source_image_id']==s]) for s in source_ids]
            aggregates.append(dict(method=method,scope=scope,pairs=len(part),sources=len(source_ids),successful=len(part),failed=0,
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part])),
                no_correction=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in part])),
                source_equal_ciede2000=float(np.mean(source_errors)),source_equal_no_correction=float(np.mean(source_unchanged)),
                changed_pairs=sum(r['changed_input_pixels']>0 for r in part)))
        harms=[r['pair_id'] for r in records if r['method']==method and r['variant']=='identity' and r['changed_input_pixels']]
        def a(scope):return next(r for r in aggregates if r['method']==method and r['scope']==scope)
        gates[method]=dict(clean_unchanged=not harms,harmed_clean_ids=harms,
            primary_improves=a('primary_all')['mean_ciede2000']<a('primary_all')['no_correction'],
            overall_improves=a('all')['mean_ciede2000']<a('all')['no_correction'],
            primary_source_equal_improves=a('primary_all')['source_equal_ciede2000']<a('primary_all')['source_equal_no_correction'])
        gates[method]['passed']=gates[method]['clean_unchanged'] and gates[method]['primary_improves'] and gates[method]['overall_improves']
    return dict(aggregates=aggregates,gates=gates,new_tree_fits=26,source_groups=26,evaluation_pairs=105,predictions=210,
        training_rows_before_fold_exclusion=84,accepted_primary_rows=58,original_controls=26,
        active_demo_changed=False,scope='single preregistered exposed-development comparison; no independent final validation',
        stopping_rule='If primary_candidate fails, stop small-model trials and record data/method blocker; no sweep or source exception.')


def run():
    if OUT.exists():raise FileExistsError(OUT)
    old=h.read(PARENT/'plan.json');accepted=h.read(IMPORTED/'accepted_primary_rows.json')
    imported=h.read(IMPORTED/'verification.json');assert imported['status']=='pass'
    for p,sha in imported['evidence_sha256'].items():assert h.digest(IMPORTED/p)==sha
    for p,sha in imported['dependency_sha256'].items():assert h.digest(ROOT/p)==sha
    assert h.read(PARENT/'verification.json')['status']=='pass'
    rows=old['rows']+accepted;assert len(rows)==105 and len({r['pair_id'] for r in rows})==105
    controls=[r for r in old['rows'] if r['variant']=='identity'];assert len(controls)==26
    fitting=controls+accepted
    # Reject identical image aliases rather than quietly double-weight targets.
    aliases={}
    for r in rows:
        key=h.digest(ROOT/r['input_path']);assert key not in aliases,('Image alias',r['pair_id'],aliases.get(key))
        aliases[key]=r['pair_id']
    _,identity=contract(ROOT);assert identity==old['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    vectors={}
    for r in rows:
        image=cv2.imread(str(ROOT/r['input_path']));mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features=={k:r[k] for k in old['baseline_features']}
        extra=facial_endpoint_features(image,mask);assert extra['valid'];features.update(extra['features'])
        if r['cohort']=='primary':assert all(features[k]==r[k] for k in old['features'])
        vectors[r['pair_id']]=[features[k] for k in old['features']]
    folds=[]
    for f in old['folds']:
        folds.append(dict(fold_id=f['fold_id'],held_group=f['held_group'],
            held_pair_ids=[r['pair_id'] for r in rows if r['duplicate_group_id']==f['held_group']],
            train_pair_ids=[r['pair_id'] for r in fitting if r['duplicate_group_id']!=f['held_group']]))
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/primary-training-single-comparison-protocol.md',ROOT/'docs/gamma-control-data-specification.md',
        PARENT/'verification.json',PARENT/'plan.json',PARENT/'predictions.json',IMPORTED/'verification.json',IMPORTED/'accepted_primary_rows.json',IMPORTED/'original_user_export.json']
    paths.extend(PARENT/p for p in h.read(PARENT/'verification.json')['evidence_sha256'])
    for r in rows:paths.extend(ROOT/r[k] for k in ('input_path','input_mask_path','reference_path','reference_mask_path'))
    hashes=dict(old['input_sha256']);hashes.update(imported['dependency_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    OUT.mkdir();h.write(OUT/'plan.json',dict(status='frozen_before_the_single_fit',rows=rows,folds=folds,features=old['features'],
        target_names=old['target_names'],settings=old['settings'],candidate_fit_ids=[r['pair_id'] for r in fitting],input_sha256=hashes,
        measurement_contract_sha256=identity,methods=METHODS,sample_weight=None,active_demo_changed=False))
    h.write(OUT/'features.json',vectors);by_id={r['pair_id']:r for r in rows};records=[]
    original={r['pair_id']:r for r in h.read(PARENT/'predictions.json') if r['method']=='paired_endpoint11'}
    for fold in folds:
        ids=fold['train_pair_ids'];x=[vectors[p] for p in ids]
        assert not {by_id[p]['source_image_id'] for p in ids}&{by_id[p]['source_image_id'] for p in fold['held_pair_ids']}
        raw=export_tree(DecisionTreeRegressor(**old['settings']).fit(x,[by_id[p]['paper_target'] for p in ids]),old['features'],old['target_names'],dict(
            training='approved_primary_only_plus_original_controls',held_group=fold['held_group'],gamma_convention='direct_exponent'))
        payload,audit=protect_identity_leaves(raw,x,[by_id[p]['variant']=='identity' for p in ids]);candidate=PortableTree(payload)
        baseline=PortableTree(h.read(PARENT/f'fold_{fold["fold_id"]}'/'candidate.json'))
        folder=OUT/f'fold_{fold["fold_id"]}';folder.mkdir();h.write(folder/'candidate.json',payload);h.write(folder/'membership.json',dict(train_pair_ids=ids,**audit))
        for pair in fold['held_pair_ids']:
            row=by_id[pair]
            for method,tree in ((METHODS[0],baseline),(METHODS[1],candidate)):
                params=tree.predict_one(vectors[pair]);image,reference,mask,score,output=h.render(row,params)
                assert np.array_equal(output[~mask],image[~mask]);path=folder/(pair+'_'+method+'.png')
                assert cv2.imwrite(str(path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                metrics=image_errors(reference,output,score)
                if method==METHODS[0] and pair in original:assert params==original[pair]['parameters'] and metrics==original[pair]['metrics']
                records.append(dict(pair_id=pair,source_image_id=row['source_image_id'],method=method,fold_id=fold['fold_id'],cohort=row['cohort'],variant=row['variant'],
                    parameters=params,changed_input_pixels=int(np.count_nonzero(np.any(output!=image,axis=2))),metrics=metrics,
                    no_correction=image_errors(reference,image,score),output_sha256=h.digest(path)))
        print('Fold',fold['fold_id'],'complete',flush=True)
    h.write(OUT/'predictions.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');rows={r['pair_id']:r for r in plan['rows']};vectors=h.read(OUT/'features.json')
    for p,sha in plan['input_sha256'].items():assert h.digest(ROOT/p)==sha
    admitted=h.read(IMPORTED/'accepted_primary_rows.json');old=h.read(PARENT/'plan.json')
    assert plan['rows']==old['rows']+admitted
    expected_fit=[r['pair_id'] for r in old['rows'] if r['variant']=='identity']+[r['pair_id'] for r in admitted]
    assert plan['candidate_fit_ids']==expected_fit and len(expected_fit)==84
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),plan['measurement_contract_sha256'])
    for pair,row in rows.items():
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        for channel,name in ((2,'red'),(1,'green'),(0,'blue')):
            counts=np.bincount(image[:,:,channel][mask],minlength=256)
            features['input_'+name+'_zero_fraction']=float(counts[0]/mask.sum());features['input_'+name+'_full_fraction']=float(counts[255]/mask.sum())
        assert vectors[pair]==[features[k] for k in plan['features']]
    records=h.read(OUT/'predictions.json');assert len(records)==210 and len({(r['method'],r['pair_id']) for r in records})==210
    fits=0
    for fold in plan['folds']:
        held={p for p,r in rows.items() if r['duplicate_group_id']==fold['held_group']}
        ids=[p for p in expected_fit if rows[p]['duplicate_group_id']!=fold['held_group']]
        assert held==set(fold['held_pair_ids']) and ids==fold['train_pair_ids']
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        x=[vectors[p] for p in ids];raw=export_tree(DecisionTreeRegressor(**plan['settings']).fit(x,[rows[p]['paper_target'] for p in ids]),plan['features'],plan['target_names'],{})
        rawtree=PortableTree(raw);leaves=[rawtree.leaf_id(v) for v in x];protected={leaf for p,leaf in zip(ids,leaves) if rows[p]['variant']=='identity'}
        for leaf in protected:raw['nodes'][leaf]['values']=[1.,1.,1.]
        folder=OUT/f'fold_{fold["fold_id"]}';saved=h.read(folder/'candidate.json');assert saved['nodes']==raw['nodes']
        membership=h.read(folder/'membership.json');assert membership['train_pair_ids']==ids and membership['protected_leaves']==sorted(protected)
        for leaf in set(leaves):
            indices=[i for i,v in enumerate(leaves) if v==leaf]
            assert membership['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=[i for i in indices if rows[ids[i]]['variant']=='identity'])
        baseline=PortableTree(h.read(PARENT/f'fold_{fold["fold_id"]}'/'candidate.json'))
        for r in [r for r in records if r['fold_id']==fold['fold_id']]:
            row=rows[r['pair_id']];assert r['pair_id'] in held
            tree=baseline if r['method']==METHODS[0] else PortableTree(saved);assert tree.predict_one(vectors[r['pair_id']])==r['parameters']
            image,reference,mask,score,output=h.render(row,r['parameters']);path=folder/(r['pair_id']+'_'+r['method']+'.png')
            assert h.digest(path)==r['output_sha256'];np.testing.assert_array_equal(cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB),output)
            np.testing.assert_array_equal(output[~mask],image[~mask]);assert np.count_nonzero(np.any(output!=image,axis=2))==r['changed_input_pixels']
            assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,image,score)==r['no_correction']
        fits+=1
    assert fits==26 and summarize(records)==h.read(OUT/'summary.json')
    original={r['pair_id']:r for r in h.read(PARENT/'predictions.json') if r['method']=='paired_endpoint11'}
    for r in records:
        if r['method']==METHODS[0] and r['pair_id'] in original:assert r['parameters']==original[r['pair_id']]['parameters'] and r['metrics']==original[r['pair_id']]['metrics']
    h.write(target,dict(status='pass',independent_feature_vectors=105,independent_candidate_refits=26,image_metric_replays=210,
        original_47_frozen_baseline_parity=True,exact_primary_admissions_and_source_separation=True,
        no_additional_candidate_search=True,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 105 vectors, 26 candidate refits, 210 image/metric replays and frozen baseline parity.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
