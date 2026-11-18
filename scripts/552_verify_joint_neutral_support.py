"""Independent manual tree/range reconstruction and RGB8 checks; no fits."""
from pathlib import Path
import json,hashlib,sys,struct
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
OUT=ROOT/'outputs/joint_neutral_support_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def rounded(x):return [struct.unpack('f',struct.pack('f',float(v)))[0] for v in x]

def route(tree,x):
    i=0
    while tree['nodes'][i]['kind']=='split':
        n=tree['nodes'][i];i=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
    return i

def main():
    result=read(OUT/'results_PRIVATE.json');bindings=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bindings.items())
    folds=read(ROOT/'outputs/split_control_comparison_v1/results_PRIVATE.json')['folds']
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    table={r['case_id']:r for r in read(ROOT/'outputs/whole_scene_correction_v1/prepared_rows_PRIVATE.json')}
    models={};independent={};leaf_checks=0;fitting_clean=0
    for key,model,cases,features in [(f['held_key'],f['model'],f['training_cases'],f['training_features']) for f in folds]+[('full',full['split'],full['training_cases'],full['training_features'])]:
        if key!='full':assert all(table[c]['subject_id']!=key for c in cases)
        models[key]=model;independent[key]={}
        for name in ('gamma','gains'):
            tree=model['heads'][name]['tree'];groups={}
            for cid,x in zip(cases,features):groups.setdefault(route(tree,rounded(x)),[]).append((cid,rounded(x)))
            independent[key][name]={}
            for leaf,members in groups.items():
                matrix=np.array([x for _,x in members]);cleans=sum(table[c]['case']['id']=='clean' for c,_ in members)
                expected=dict(minimum=matrix.min(axis=0).tolist(),maximum=matrix.max(axis=0).tolist(),rows=len(members),clean_rows=cleans)
                assert expected==result['policies'][key]['heads'][name][str(leaf)]
                independent[key][name][leaf]=expected;leaf_checks+=1
        fitting_clean+=sum(table[c]['case']['id']=='clean' for c in cases)
    assert fitting_clean==result['fitting_clean_checks']==290
    records=result['records'];actions=0;renders=0;ref_scores=0;scene_scores=0
    for r in records:
        key=r['subject_id'] if r['suite']=='fold_working256' else 'full';params=[1.,1.,1.]
        if key=='full':assert r['subject_id'] not in full['training_keys']
        if r['features'] is not None:
            x=rounded(r['features']);outputs=[];support=True;details={}
            for name in ('gamma','gains'):
                tree=models[key]['heads'][name]['tree'];leaf=route(tree,x);m=independent[key][name][leaf]
                axes=[i for i,v in enumerate(x) if not m['minimum'][i]<=v<=m['maximum'][i]]
                support=support and not axes;clean=m['clean_rows']>0
                raw=tree['nodes'][leaf]['values'];outputs+=([1.]*len(raw) if clean else raw)
                details[name]=dict(leaf=leaf,outside_axes=axes,clean_anchored=clean)
            params=outputs if support else [1.,1.,1.]
            assert r['policy']==dict(parameters=params,supported=bool(support),heads=details);actions+=1
        else:assert r['policy'] is None
        if r['image_path'] is None:continue
        image=rgb(r['image_path']);reference=rgb(r['reference_path']);mask=cv2.imread(r['mask_path'],0)>0 if r['mask_path'] else np.zeros(image.shape[:2],bool)
        for method in ('policy_ungated','policy_gated'):
            apply=method=='policy_ungated' or bool(r['gate'] and r['gate']['apply_correction'])
            p=params if apply else [1.,1.,1.]
            unit=image.astype(np.float64)/255.
            corrected=np.clip(unit**p[0]*np.array([p[1],1.,p[2]]),0.,1.)
            expected=image.copy();expected[mask]=np.rint(corrected[mask]*255).astype(np.uint8)
            actual=rgb(r['output_paths'][method]);np.testing.assert_array_equal(expected,actual)
            assert np.array_equal(actual[~mask],image[~mask])
            item=r['paths'][method];assert item['parameters']==p and item['changed_channels']==int(np.count_nonzero(actual!=image));renders+=1
            for region,scoremask in [('reference_metrics',cv2.imread(r['reference_mask_path'],0)>0 if r['reference_available'] else None),('scene_metrics',np.ones(mask.shape,bool) if r['input_scene_metrics'] is not None else None)]:
                if scoremask is None:assert item[region] is None;continue
                a=actual[scoremask].astype(float);b=reference[scoremask].astype(float)
                mae=float(np.abs(a-b).mean());de=float(deltaE_ciede2000(rgb2lab(a/255),rgb2lab(b/255)).mean())
                assert abs(mae-item[region]['rgb8_mae_codes'])<1e-12
                assert abs(de-item[region]['relative_deltaE00_mean'])<1e-10
                assert int(scoremask.sum())==item[region]['scoring_pixels']
                if region=='reference_metrics':ref_scores+=1
                else:scene_scores+=1
    # Independently recompute displayed photo-weighted means and coverage.
    for suite,layers in result['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in records if r['suite']==suite and r['layer']==layer]
            assert s['attempts']==len(rr)
            for name,m in s['methods'].items():
                assert m['changed_cases']==sum(r['paths'].get(name,{}).get('changed_channels',0)>0 for r in rr)
                for region in ('reference_metrics','scene_metrics'):
                    scored=[r for r in rr if r['paths'].get(name,{}).get(region) is not None]
                    for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                        values=[r['paths'][name][region][metric] for r in scored]
                        expected=sum(values)/len(values) if values else None
                        saved=m[region+'_'+metric]
                        assert expected==saved if expected is None else abs(expected-saved)<1e-10
    assert all(sha(p)==h for p,h in bindings.items())
    verification=dict(passed=True,leaf_metadata_checks=leaf_checks,fitting_clean_occurrences=fitting_clean,
        independent_action_checks=actions,independent_rgb8_renders=renders,reference_metric_checks=ref_scores,
        scene_metric_checks=scene_scores,source_hashes=len(bindings),new_fits=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    # Four fixed boards per sheet; every board remains full-size on disk.
    sheets=OUT/'contact_sheets';sheets.mkdir(exist_ok=True)
    for start in range(0,len(result['boards']),4):
        panels=[]
        for p in result['boards'][start:start+4]:
            im=rgb(OUT/p);panels.append(cv2.resize(im,(1200,round(im.shape[0]*1200/im.shape[1]))))
        sheet=np.vstack(panels);assert cv2.imwrite(str(sheets/f'{start//4:02d}.png'),cv2.cvtColor(sheet,cv2.COLOR_RGB2BGR))
    print(json.dumps(verification,indent=2))

if __name__=='__main__':main()
