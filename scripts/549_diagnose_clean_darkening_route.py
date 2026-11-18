"""Saved-tree grouping/target/component diagnosis; no fits or model forwards."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.portable_tree import PortableTree
from src.model_training.split_control_candidate import predict_split
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.whole_scene_features import scene_features
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.gamma_identity_feasibility import fixed_gain_identity_bounds

OUT=ROOT/'outputs/clean_darkening_route_diagnosis_v1'
CID='case_28__clean'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)


def main():
    if OUT.exists():raise FileExistsError(OUT)
    M=ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json'
    T=ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json'
    E=ROOT/'outputs/mst_excluded_clean_gate_comparison_v1/results_PRIVATE.json'
    model=read(M);table={r['case_id']:r for r in read(T)}
    rows=[r for r in read(E)['records'] if r['suite']=='fold_working256']
    query=next(r for r in rows if r['case_id']==CID)
    fold=next(f for f in model['folds'] if f['held_key']==query['subject_id'])
    assert query['subject_id'] not in {table[c]['subject_id'] for c in fold['training_cases']}
    paths=[M,T,E,Path(__file__),ROOT/'docs/clean-darkening-route-audit-protocol-2026-11-07.md',
        ROOT/'src/evaluation/gamma_identity_feasibility.py',ROOT/'src/model_training/portable_tree.py',
        ROOT/'src/model_training/blended_recovery_targets.py',ROOT/'src/model_training/split_control_candidate.py']
    bindings={str(p):sha(p) for p in paths}
    def bind(path):
        path=Path(path);bindings[str(path)]=sha(path);return path
    def route(tree,vector):
        node=tree['root'];steps=[]
        while tree['nodes'][node]['kind']=='split':
            split=tree['nodes'][node];feature=split['feature'];v=float(np.float32(vector[feature]));left=v<=split['threshold']
            steps.append(dict(node=node,feature=tree['feature_names'][feature],input_float32=v,
                threshold=split['threshold'],branch='left' if left else 'right'))
            node=split['left'] if left else split['right']
        assert PortableTree(tree).leaf_id(vector)==node
        return node,steps
    heads={}
    for name,columns in [('gamma',[0]),('gains',[1,2])]:
        tree=fold['model']['heads'][name]['tree'];leaf,steps=route(tree,query['features'])
        member_indices=[i for i,x in enumerate(fold['training_features']) if PortableTree(tree).leaf_id(x)==leaf]
        cases=[fold['training_cases'][i] for i in member_indices]
        values=np.array([table[c]['target'] for c in cases])[:,columns]
        np.testing.assert_allclose(values.mean(axis=0),tree['nodes'][leaf]['values'],atol=1e-12,rtol=0)
        x=np.array([fold['training_features'][i] for i in member_indices])
        heads[name]=dict(leaf=leaf,route=steps,prediction=tree['nodes'][leaf]['values'],members=cases,
            fitting_rows=len(cases),source_photos=len({table[c]['source_case'] for c in cases}),
            publisher_groups=len({table[c]['subject_id'] for c in cases}),
            recipe_counts=dict(Counter(table[c]['case']['id'] for c in cases)),
            target_mean=values.mean(axis=0).tolist(),target_min=values.min(axis=0).tolist(),
            target_max=values.max(axis=0).tolist(),
            feature_ranges=[dict(feature=n,minimum=float(x[:,i].min()),maximum=float(x[:,i].max()),
                query=float(query['features'][i]),query_outside_member_range=bool(query['features'][i]<x[:,i].min() or query['features'][i]>x[:,i].max()))
                for i,n in enumerate(fold['model']['feature_names'])])
    gamma=PortableTree(fold['model']['heads']['gamma']['tree'])
    clean=[(c,x) for c,x in zip(fold['training_cases'],fold['training_features']) if table[c]['case']['id']=='clean']
    assert len(clean)==27 and all(table[c]['target']==[1.,1.,1.] for c,_ in clean)
    clean_summary=dict(fitting_rows=len(clean),leaf_counts=dict(Counter(str(gamma.leaf_id(x)) for _,x in clean)),
        scene_l50_min=min(x[8] for _,x in clean),scene_l50_max=max(x[8] for _,x in clean),
        query_scene_l50=query['features'][8])
    counterparts=[]
    for c in sorted({table[c]['source_case']+'__clean' for c in heads['gamma']['members']}):
        i=fold['training_cases'].index(c);x=fold['training_features'][i]
        counterparts.append(dict(case_id=c,leaf=gamma.leaf_id(x),target=table[c]['target'],
            scene_l50=x[8],face_l=x[0]))
    image=rgb(bind(query['image_path']));reference=rgb(bind(query['reference_path']))
    mask=cv2.imread(str(bind(query['mask_path'])),0)>0
    assert np.array_equal(image,reference) and table[CID]['target']==[1.,1.,1.]
    stats=compute_masked_lab_statistics(cv2.cvtColor(image,cv2.COLOR_RGB2BGR),mask.astype(np.uint8)*255)
    assert stats['valid'] and stats['skin_pixels']==3906
    for i,k in enumerate(['mean_l_star','mean_a_star','mean_b_star','ita_degrees']):assert stats[k]==query['features'][i]
    scene=rgb(bind(ROOT/'outputs/whole_scene_correction_v1/case_28/clean/scene_input.png'))
    assert scene_features(scene)==table[CID]['scene_features']
    parameters=predict_split(fold['model'],query['features'])
    assert parameters==query['paths']['signed']['parameters']
    assert query['signed_decision']['apply_correction'] and query['paths']['frozen']['changed_channels']==0
    settings=dict(neutral=[1.,1.,1.],gamma_only=[parameters[0],1.,1.],gains_only=[1.,parameters[1],parameters[2]],full=parameters)
    OUT.mkdir();components={};pixels={}
    for name,params in settings.items():
        output=render_rgb8(image,mask.astype(float),params);assert np.array_equal(output[~mask],image[~mask])
        assert cv2.imwrite(str(OUT/(name+'.png')),cv2.cvtColor(output,cv2.COLOR_RGB2BGR));pixels[name]=output
        components[name]=dict(parameters=params,rgb_mae=float(np.abs(output.astype(float)-reference.astype(float))[mask].mean()),changed_channels=int(np.count_nonzero(output!=image)))
    assert np.array_equal(pixels['neutral'],image)
    assert np.array_equal(pixels['full'],rgb(bind(ROOT/'outputs/mst_excluded_clean_gate_comparison_v1/fold_working256'/CID/'signed.png')))
    assert abs(components['full']['rgb_mae']-query['paths']['signed']['reference_metrics']['rgb8_mae_codes'])<1e-12
    context=[]
    for row in rows:
        if not row['case_id'].startswith('case_28__'):continue
        vector=row['features'];leaf=None;prediction=None
        if vector is not None:
            leaf,_=route(fold['model']['heads']['gamma']['tree'],vector)
            prediction=predict_split(fold['model'],vector)
            original=next(r for r in model['records'] if r['case_id']==row['case_id'])
            assert prediction==original['paths']['split_ungated']['parameters']
        context.append(dict(case_id=row['case_id'],recipe=row['recipe'],features_available=vector is not None,
            gamma_leaf=leaf,parameters=prediction,target=table[row['case_id']]['target'],
            gate=row['signed_decision'],input_error=row['input_reference_metrics'],
            result_error=row['paths']['signed']['reference_metrics']))
    assert len(context)==14
    bounds=[]
    for row in rows:
        if row['recipe']!='clean' or not row['paths'].get('frozen',{}).get('changed_channels'):continue
        im=rgb(bind(row['image_path']));mk=cv2.imread(str(bind(row['mask_path'])),0)>0
        gains=row['paths']['frozen']['parameters'][1:]
        result=fixed_gain_identity_bounds(im,mk,*gains)
        assert result['fixed_gain_identity_impossible']
        bounds.append(dict(case_id=row['case_id'],fixed_gains=gains,certificate=result))
    assert len(bounds)==3
    overlay=image.copy();overlay[mask]=np.rint(.6*image[mask]+.4*np.array([0,255,0])).astype(np.uint8)
    panels=[image,overlay,pixels['gamma_only'],pixels['gains_only'],pixels['full']]
    title=np.full((26,1280,3),255,np.uint8)
    cv2.putText(title,'Clean input | correction area | gamma only | gains only | full',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
    assert cv2.imwrite(str(OUT/'components_board.png'),cv2.cvtColor(np.vstack([title,np.hstack(panels)]),cv2.COLOR_RGB2BGR))
    result=dict(case_id=CID,held_key=fold['held_key'],features=query['features'],statistics=stats,
        gate=query['signed_decision'],clean_target=table[CID]['target'],heads=heads,
        fitting_clean_summary=clean_summary,clean_counterparts=counterparts,
        components=components,same_original_conditions=context,retained_clean_fixed_gain_certificates=bounds,
        new_predictive_fits=0,new_target_fits=0,image_model_forwards=0,component_arithmetic_replays=4,
        annotation_or_mask_adoption=False,production_adopted=False)
    (OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
    assert all(sha(p)==h for p,h in bindings.items())
    print(json.dumps(dict(gamma_leaf={k:v for k,v in heads['gamma'].items() if k in ['leaf','route','fitting_rows','source_photos','publisher_groups','recipe_counts','target_mean']},
        clean_summary=clean_summary,components=components,retained_clean_gamma_only_infeasible=len(bounds)),indent=2))


if __name__=='__main__':main()
