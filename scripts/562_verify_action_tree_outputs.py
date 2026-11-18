"""Manual routing, independent RGB8 replay and metric/aggregate verification."""
from pathlib import Path
import hashlib,json,struct
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/image_loss_action_tree_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    models=read(ROOT/'outputs/image_loss_action_tree_models_v1/models_PRIVATE.json')
    folds={f['held_key']:f for f in models['folds']}
    full=read(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')
    old={(r['suite'],r['case_id']):r for r in read(ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json')['records']}
    assert all(sha(p)==h for p,h in bound.items())
    actions=0;renders=0;refchecks=0;scenechecks=0
    for r in data['records']:
        prior=old[r['suite'],r['case_id']]
        for k in ('features','gate','image_path','reference_path','mask_path','reference_mask_path'):assert r[k]==prior[k]
        params=[1.,1.,1.]
        if r['features'] is not None:
            model=folds[r['subject_id']]['model'] if r['suite']=='fold_working256' else models['full_model']
            if r['suite']!='fold_working256':assert r['subject_id'] not in full['training_keys']
            x=[struct.unpack('!f',struct.pack('!f',v))[0] for v in r['features']];tree=model['tree'];node=0
            while tree['nodes'][node]['kind']=='split':
                n=tree['nodes'][node];node=n['left'] if x[n['feature']]<=n['threshold'] else n['right']
            action=model['trace'][node]['action'];params=model['actions'][action]
            assert params==tree['nodes'][node]['values']
            assert r['policy']==dict(parameters=params,supported=True,leaf=node,action=action);actions+=1
        else:assert r['policy'] is None
        if r['image_path'] is None:continue
        assert r['paths']['previous_policy_gated']==prior['paths']['policy_gated']
        im=rgb(r['image_path']);ref=rgb(r['reference_path'])
        mask=cv2.imread(r['mask_path'],0)>0 if r['mask_path'] else np.zeros(im.shape[:2],bool)
        actual=rgb(r['output_paths']['action_tree']);expected=im.copy()
        unit=im[mask].astype(float)/255.
        expected[mask]=np.rint(np.clip(unit**params[0]*[params[1],1.,params[2]],0.,1.)*255).astype(np.uint8)
        np.testing.assert_array_equal(actual,expected);assert np.array_equal(actual[~mask],im[~mask]);renders+=1
        p=r['paths']['action_tree'];assert p['parameters']==params and p['changed_channels']==int(np.count_nonzero(im!=actual))
        for region,scoremask in [('reference_metrics',cv2.imread(r['reference_mask_path'],0)>0 if r['reference_available'] else None),('scene_metrics',np.ones(mask.shape,bool) if r['input_scene_metrics'] is not None else None)]:
            if scoremask is None:assert p[region] is None;continue
            a=actual[scoremask].astype(float);b=ref[scoremask].astype(float)
            assert abs(float(np.abs(a-b).mean())-p[region]['rgb8_mae_codes'])<1e-12
            de=float(deltaE_ciede2000(rgb2lab(a/255),rgb2lab(b/255)).mean())
            assert abs(de-p[region]['relative_deltaE00_mean'])<1e-10
            assert int(scoremask.sum())==p[region]['scoring_pixels']
            if region=='reference_metrics':refchecks+=1
            else:scenechecks+=1
    for suite,layers in data['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in data['records'] if r['suite']==suite and r['layer']==layer]
            assert len(rr)==s['attempts'] and s['support_abstentions']==0
            for name,m in s['methods'].items():
                assert m['changed_cases']==sum(r['paths'].get(name,{}).get('changed_channels',0)>0 for r in rr)
                scored=[r for r in rr if r['paths'].get(name,{}).get('reference_metrics') is not None]
                assert m['reference_harms']==sum(r['paths'][name]['reference_metrics']['rgb8_mae_codes']>r['input_reference_metrics']['rgb8_mae_codes'] for r in scored)
                for region in ('reference_metrics','scene_metrics'):
                    available=[r for r in rr if r['paths'].get(name,{}).get(region) is not None]
                    for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                        values=[r['paths'][name][region][metric] for r in available]
                        mean=sum(values)/len(values) if values else None;actual=m[region+'_'+metric]
                        assert actual is None if mean is None else abs(mean-actual)<1e-10
                        keys={r['subject_id'] for r in available}
                        km=float(np.mean([np.mean([r['paths'][name][region][metric] for r in available if r['subject_id']==k]) for k in keys])) if keys else None
                        actual=m['equal_key_'+region+'_'+metric]
                        assert actual is None if km is None else abs(km-actual)<1e-12
    duplicate=0
    for r in data['records']:
        if r['suite']=='fallback_native224' and r['recipe']=='clean' and r['reference_available']:
            for suite in ('borrowed_native224','input_native224'):
                other=next(x for x in data['records'] if x['suite']==suite and x['case_id']==r['case_id'])
                assert Path(r['output_paths']['action_tree']).read_bytes()==Path(other['output_paths']['action_tree']).read_bytes()
            duplicate+=1
    assert all(sha(p)==h for p,h in bound.items())
    result=dict(passed=True,action_replays=actions,rgb8_render_replays=renders,reference_metric_checks=refchecks,scene_metric_checks=scenechecks,
        native_clean_duplicate_checks=duplicate,source_hashes=len(bound),new_fits=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    sheets=OUT/'contact_sheets';sheets.mkdir(exist_ok=True)
    for start in range(0,len(data['boards']),4):
        panels=[]
        for path in data['boards'][start:start+4]:
            im=rgb(OUT/path);panels.append(cv2.resize(im,(1200,round(im.shape[0]*1200/im.shape[1]))))
        assert cv2.imwrite(str(sheets/f'{start//4:02d}.png'),cv2.cvtColor(np.vstack(panels),cv2.COLOR_RGB2BGR))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
