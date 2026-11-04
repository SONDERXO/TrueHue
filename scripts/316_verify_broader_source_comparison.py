"""Verify saved membership, leaf means, features and new image outputs; no refits."""
import importlib
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.portable_tree import PortableTree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors
h=importlib.import_module('256_compare_clean_control_tree_depth')
runner=importlib.import_module('315_run_broader_source_comparison')
OUT=runner.OUT


def main():
    destination=OUT/'verification.json'
    if destination.exists():raise FileExistsError(destination)
    plan=h.read(OUT/'plan.json');rows={r['pair_id']:r for r in plan['rows']}
    ready=h.read(runner.READY/'plan.json');rv=h.read(runner.READY/'verification.json')
    assert h.digest(runner.READY/'plan.json')==plan['readiness_plan_sha256']
    assert h.digest(ROOT/plan['protocol'])==plan['protocol_sha256']
    assert h.digest(Path(runner.__file__))==plan['runner_sha256']
    for p,sha in plan['implementation_dependencies_sha256'].items():assert h.digest(ROOT/p)==sha
    for p,sha in rv['input_sha256'].items():assert h.digest(ROOT/p)==sha
    assert plan['folds']==ready['folds'] and plan['C_ordered_fit_candidates']==ready['C_ordered_fit_candidates']
    assert plan['settings']=={'max_depth':3,'random_state':42,'min_samples_leaf':1}
    lookup_path=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    assert h.digest(lookup_path)==plan['lookup_sha256']
    lookup=DevelopmentMonotoneLookup(h.read(lookup_path),plan['measurement_contract_sha256'])
    for p,row in rows.items():
        for path,sha in [('input_path','input_sha256'),('input_mask_path','input_mask_sha256')]:assert h.digest(ROOT/row[path])==row[sha]
        image=cv2.imread(str(ROOT/row['input_path']));mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        stats=compute_masked_lab_statistics(image,mask,1000);assert stats['valid']
        features={name:float(stats[key]) for name,key in zip(FEATURES,FEATURE_KEYS)}
        features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        for ch,name in [(2,'red'),(1,'green'),(0,'blue')]:
            values=image[:,:,ch][mask]
            features['input_'+name+'_zero_fraction']=float(np.count_nonzero(values==0)/len(values))
            features['input_'+name+'_full_fraction']=float(np.count_nonzero(values==255)/len(values))
        assert [features[k] for k in plan['features']]==row['features'],p
    trees={};checked=0
    def check_tree(method,path,expected):
        nonlocal checked
        payload=h.read(path);tree=PortableTree(payload)
        membership=h.read(path.with_name(method+'_membership.json'))
        assert membership['train_pair_ids']==expected
        leaves=defaultdict(list)
        for i,p in enumerate(expected):leaves[tree.leaf_id(rows[p]['features'])].append(i)
        protected=[]
        for leaf,indices in leaves.items():
            control=[i for i in indices if rows[expected[i]]['stratum']=='original_control']
            assert membership['membership'][str(leaf)]==dict(training_indices=indices,identity_indices=control)
            target=[1.,1.,1.] if control else np.mean([rows[expected[i]]['target_direct_gamma_red_blue'] for i in indices],axis=0)
            np.testing.assert_allclose(payload['nodes'][leaf]['values'],target,rtol=0,atol=1e-12)
            if control:protected.append(leaf)
        assert sorted(protected)==membership['protected_leaves']
        checked+=1
        return tree
    for method in ['A','B']:
        trees[(method,'shared')]=check_tree(method,OUT/'shared'/(method+'.json'),plan[method+'_ordered_fit_candidates'])
    reuse={(r['method'],r['held_group']):r for r in plan['historical_reusable_trees']}
    for f in plan['folds']:
        group=f['held_group'];folder=OUT/f'fold_{f["fold_id"]}'
        assert h.read(folder/'membership.json')==f
        ids=[p for p in plan['C_ordered_fit_candidates'] if rows[p]['duplicate_group_id']!=group]
        held=[p for p,r in rows.items() if r['duplicate_group_id']==group]
        assert ids==f['C_ordered_training_pair_ids'] and held==f['evaluation_pair_ids']
        assert not {rows[p]['source_image_id'] for p in ids}&{rows[p]['source_image_id'] for p in held}
        trees[('C',group)]=check_tree('C',folder/'C.json',ids)
        for method in ['A','B']:
            if (method,group) in reuse:
                info=reuse[(method,group)];assert h.digest(ROOT/info['tree_path'])==info['tree_sha256']
                assert all(rows[p]['duplicate_group_id']!=group for p in info['ordered_training_pair_ids'])
                trees[(method,group)]=PortableTree(h.read(ROOT/info['tree_path']))
            else:
                assert all(rows[p]['duplicate_group_id']!=group for p in plan[method+'_ordered_fit_candidates'])
                trees[(method,group)]=trees[(method,'shared')]
    records=h.read(OUT/'predictions.json');assert len(records)==363
    assert {(r['method'],r['pair_id']) for r in records}=={(m,p) for m in ['A','B','C'] for p in rows}
    old={(r['method'],r['pair_id']):r for r in h.read(ROOT/'outputs/reviewed_primary_comparison_v1/predictions.json')}
    replayed=reused=0
    for record in records:
        row=rows[record['pair_id']];group=row['duplicate_group_id']
        assert record['parameters']==trees[(record['method'],group)].predict_one(row['features'])
        assert record['source_image_id']==row['source_image_id']
        path=ROOT/record['output_path'];assert h.digest(path)==record['output_sha256']
        if record['reused']:
            oldmethod='frozen_endpoint_baseline' if record['method']=='A' else 'primary_candidate'
            prior=old[(oldmethod,record['pair_id'])]
            assert record['original_record']==prior
            for key in ['parameters','metrics','no_correction','changed_input_pixels','output_sha256']:assert record[key]==prior[key]
            reused+=1;continue
        # Independent direct operator rendering, not the runner's render helper.
        image=cv2.cvtColor(cv2.imread(str(ROOT/row['input_path'])),cv2.COLOR_BGR2RGB)
        reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        support=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        output=image.copy();output[support]=np.rint(transform_rgb(image.astype(float)/255,*record['parameters'])[support]*255).astype(np.uint8)
        np.testing.assert_array_equal(output,cv2.cvtColor(cv2.imread(str(path)),cv2.COLOR_BGR2RGB))
        assert np.array_equal(output[~support],image[~support])
        assert record['changed_input_pixels']==int(np.count_nonzero(np.any(output!=image,axis=2)))
        assert record['metrics']==image_errors(reference,output,score)
        assert record['no_correction']==image_errors(reference,image,score)
        replayed+=1
    assert checked==34 and replayed==153 and reused==210
    assert runner.aggregate(records,rows)==h.read(OUT/'summary.json')
    h.write(destination,dict(status='pass',independent_feature_vectors=121,new_tree_membership_and_leaf_mean_checks=34,
        verification_refits=0,new_image_metric_replays=153,historical_predictions_preserved_verbatim=210,
        source_separated_folds=32,reserved_evaluation_accesses=0,demo_changed=False,
        verifier_sha256=h.digest(Path(__file__)),evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS:121 features,34 tree memberships/leaf means,153 new image replays,210 verbatim historical records; zero verification refits.')


if __name__=='__main__':main()
