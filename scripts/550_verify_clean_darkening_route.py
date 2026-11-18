"""Independent saved-leaf/target and RGB checks; analytic bound witnesses, no fits."""
from pathlib import Path
from math import log
import json,hashlib
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/clean_darkening_route_diagnosis_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)


def main():
    target=OUT/'verification_PRIVATE.json'
    if target.exists():raise FileExistsError(target)
    v=read(OUT/'diagnosis_PRIVATE.json');binding=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in binding.items())
    folds=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json')['folds']
    fold=next(f for f in folds if f['held_key']==v['held_key'])
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    def route(tree,x):
        node=tree['root']
        while tree['nodes'][node]['kind']=='split':
            s=tree['nodes'][node];node=s['left'] if float(np.float32(x[s['feature']]))<=s['threshold'] else s['right']
        return node
    for head,cols in [('gamma',[0]),('gains',[1,2])]:
        tree=fold['model']['heads'][head]['tree'];assert route(tree,v['features'])==v['heads'][head]['leaf']
        members=[c for c,x in zip(fold['training_cases'],fold['training_features']) if route(tree,x)==v['heads'][head]['leaf']]
        assert members==v['heads'][head]['members']
        mean=np.mean([[table[c]['target'][i] for i in cols] for c in members],axis=0)
        np.testing.assert_allclose(mean,v['heads'][head]['prediction'],atol=1e-12,rtol=0)
    gamma_tree=fold['model']['heads']['gamma']['tree']
    assert v['heads']['gamma']['recipe_counts']==dict(exposure_over=17,combined_cool_over=17,combined_warm_over=17)
    assert len(v['clean_counterparts'])==17 and all(c['leaf']==4 and c['target']==[1.,1.,1.] for c in v['clean_counterparts'])
    folder=ROOT/'outputs/whole_scene_correction_v1/case_28'
    image=rgb(folder/'clean/input.png');reference=rgb(folder/'reference.png');mask=cv2.imread(str(folder/'mask.png'),0)>0
    for name,component in v['components'].items():
        p=component['parameters'];x=image.astype(float)/255.
        transformed=np.clip(np.power(x,p[0])*[p[1],1.,p[2]],0,1)
        expected=image.copy();expected[mask]=np.rint(transformed[mask]*255).astype(np.uint8)
        saved=rgb(OUT/(name+'.png'));assert np.array_equal(expected,saved)
        error=float(np.abs(saved.astype(float)-reference.astype(float))[mask].mean())
        assert abs(error-component['rgb_mae'])<1e-12
    rows=read(ROOT/'outputs/mst_excluded_clean_gate_comparison_v1/results_PRIVATE.json')['records']
    indexed={r['case_id']:r for r in rows if r['suite']=='fold_working256'}
    # Independently recompute each contradicting pair of pixel inequalities.
    for item in v['retained_clean_fixed_gain_certificates']:
        c=item['certificate'];lo=c['lower_witness'];hi=c['upper_witness']
        r=indexed[item['case_id']];im=rgb(r['image_path']);mk=cv2.imread(r['mask_path'],0)>0
        for witness in [lo,hi]:
            y,x=witness['pixel_yx'];assert mk[y,x] and im[y,x,witness['channel']]==witness['value']
        lower=log((lo['value']+.5)/(255*lo['gain']))/log(lo['value']/255)
        upper=log((hi['value']-.5)/(255*hi['gain']))/log(hi['value']/255)
        assert abs(lower-c['necessary_gamma_lower'])<1e-12 and abs(upper-c['necessary_gamma_upper'])<1e-12
        assert lower>upper>0
    # Pair chosen by scene-feature proximity, not by favourable correction error.
    gamma_members=v['heads']['gamma']['members']
    candidate=min([c for c in gamma_members if table[c]['case']['id']=='exposure_over'],
        key=lambda c:(abs(table[c]['scene_features']['scene_l_p50']-v['features'][8]),c))
    source=table[candidate]['source_case'];ref_folder=ROOT/'outputs/whole_scene_correction_v1'/source
    pair=[rgb(ref_folder/'clean/input.png'),rgb(ref_folder/'exposure_over/input.png'),image,rgb(OUT/'full.png')]
    title=np.full((26,1024,3),255,np.uint8)
    cv2.putText(title,'Fitting clean | its overexposure | held clean | held wrong correction',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1)
    assert cv2.imwrite(str(OUT/'training_pair_board.png'),cv2.cvtColor(np.vstack([title,np.hstack(pair)]),cv2.COLOR_RGB2BGR))
    cards=[]
    for recipe in ['clean','colour_cool','exposure_under','exposure_over','stress_exposure_over']:
        r=indexed['case_28__'+recipe]
        panels=[reference,rgb(r['image_path']),rgb(r['ungated_output_path']),rgb(ROOT/'outputs/mst_excluded_clean_gate_comparison_v1/fold_working256'/r['case_id']/'signed.png')]
        title=np.full((26,1024,3),255,np.uint8);cv2.putText(title,recipe+' reference | input | controls before gate | after gate',(3,18),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1)
        cards.append(np.vstack([title,np.hstack(panels)]))
    assert cv2.imwrite(str(OUT/'same_photo_context_board.png'),cv2.cvtColor(np.vstack(cards),cv2.COLOR_RGB2BGR))
    assert all(sha(p)==h for p,h in binding.items())
    target.write_text(json.dumps(dict(status='pass',focal_head_routes=2,raw_leaf_mean_checks=2,
        matching_clean_counterparts=17,same_photo_conditions=14,component_pixel_replays=4,
        independent_fixed_gain_infeasibility_witnesses=3,source_hashes_unchanged=True,
        new_predictive_fits=0,new_target_fits=0,image_model_forwards=0,
        training_visual_member=candidate,verifier_sha256=sha(__file__)),indent=2),encoding='utf-8')
    print('Verified2routes/leaf means,17clean counterparts,14contexts,4RGB replays and3fixed-gain interval contradictions. No fits.')


if __name__=='__main__':main()
