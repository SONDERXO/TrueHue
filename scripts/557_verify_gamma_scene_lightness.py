"""Verify eleven fixed fits, then reuse independent joint-policy RGB checks."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.gamma_scene_lightness_restriction import EXCLUDED

read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    M=ROOT/'outputs/gamma_scene_lightness_models_v1/models_PRIVATE.json';models=read(M)
    assert all(sha(p)==h for p,h in models['input_sha256'].items())
    prior=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json')
    base={f['held_key']:f for f in prior['folds']}
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    leafmeans=0;routes=0
    items=[]
    for f in models['folds']:
        b=base[f['held_key']]
        assert f['training_cases']==b['training_cases'] and f['training_features']==b['training_features'] and f['held_cases']==b['held_cases']
        assert all(table[c]['subject_id']!=f['held_key'] for c in f['training_cases'])
        items.append((f['model'],b['model'],f['training_cases'],f['training_features']))
    assert models['full_training_cases']==full['training_cases'] and models['full_training_features']==full['training_features']
    items.append((models['full_model'],full['split'],full['training_cases'],full['training_features']))
    for model,old,cases,x in items:
        assert model['heads']['gains']==old['heads']['gains']
        assert model['feature_names']==old['feature_names'] and model['target_names']==old['target_names']
        tree=model['heads']['gamma']['tree'];names=model['feature_names'];indices=[names.index(n) for n in EXCLUDED]
        assert all(n['feature'] not in indices for n in tree['nodes'] if n['kind']=='split')
        y=np.array([table[c]['target'][0] for c in cases]);normal=model['heads']['gamma']['normalization']
        np.testing.assert_allclose(normal['mean'],[y.mean()],rtol=0,atol=1e-12)
        np.testing.assert_allclose(normal['population_std'],[y.std()],rtol=0,atol=1e-12)
        np.testing.assert_allclose(normal['scale'],[y.std() if y.std()!=0 else 1.],rtol=0,atol=1e-12)
        portable=PortableTree(tree);leaves=np.array([portable.leaf_id(row) for row in x]);routes+=len(x)
        for leaf in set(leaves.tolist()):
            assert abs(y[leaves==leaf].mean()-tree['nodes'][leaf]['values'][0])<1e-12;leafmeans+=1
    comparison=read(ROOT/'outputs/gamma_scene_lightness_comparison_v1/results_PRIVATE.json')
    oldpolicy=read(ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json')
    oldrows={(r['suite'],r['case_id']):r for r in oldpolicy['records']}
    foldmodels={f['held_key']:f['model'] for f in models['folds']}
    gatefolds={f['held_key']:f['model'] for f in read(ROOT/'outputs/benefit_aware_gate_v1/results_PRIVATE.json')['folds']}
    invariant=0
    for r in comparison['records']:
        old=oldrows[r['suite'],r['case_id']]
        assert r['features']==old['features'] and r['gate']==old['gate']
        for name in ('image_path','reference_path','mask_path','reference_mask_path'):assert r[name]==old[name]
        if r['image_path'] is not None:
            for name in ('policy_ungated','policy_gated'):assert r['paths']['previous_'+name]==old['paths'][name]
        if r['features'] is None:continue
        model=foldmodels[r['subject_id']] if r['suite']=='fold_working256' else models['full_model']
        g=gatefolds[r['subject_id']] if r['suite']=='fold_working256' else full['gate']
        assert r['subject_id'] not in g['training_keys']
        score=float(np.dot((np.array(r['features'])-g['mean'])/g['scale'],g['coefficient'])+g['intercept'])
        assert abs(score-r['gate']['logit'])<1e-10 and (score>0)==r['gate']['apply_correction']
        x=list(r['features']);changed=x.copy()
        for n in EXCLUDED:changed[model['feature_names'].index(n)]=1e5
        assert PortableTree(model['heads']['gamma']['tree']).predict_one(x)==PortableTree(model['heads']['gamma']['tree']).predict_one(changed)
        invariant+=1
    # This existing verifier traverses original node arrays independently and
    # reconstructs PNG pixels with separate NumPy arithmetic, without fitting.
    source=(ROOT/'scripts/552_verify_joint_neutral_support.py').read_text(encoding='utf-8')
    def replace(old,new):
        nonlocal source
        assert old in source,old
        source=source.replace(old,new)
    replace('outputs/joint_neutral_support_v1','outputs/gamma_scene_lightness_comparison_v1')
    replace("    folds=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json')['folds']", "    revised=read(ROOT/'outputs/gamma_scene_lightness_models_v1/models_PRIVATE.json')\n    folds=revised['folds']")
    replace("    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')", "    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json');full['split']=revised['full_model']")
    exec(compile(source,str(ROOT/'scripts/552_verify_joint_neutral_support.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
    out=ROOT/'outputs/gamma_scene_lightness_comparison_v1';v=read(out/'verification_PRIVATE.json')
    v.update(gamma_fits_verified=11,raw_gamma_leaf_means=leafmeans,gamma_training_routes=routes,
        raw_gamma_lightness_invariance=invariant,gates_and_gains_frozen=True,previous_policy_records_bound=True,
        rgb_verifier_source_sha256=sha(ROOT/'scripts/552_verify_joint_neutral_support.py'))
    (out/'verification_PRIVATE.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
    print('Verified11gamma artifacts,',leafmeans,'raw leaf means,',invariant,'raw-gamma invariance and frozen-gate checks.')

if __name__=='__main__':main()
