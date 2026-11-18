"""Independent native RGB8 outputs, common supports and attempt-ledger checks."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/aligned_action_tree_comparison_v1';P=ROOT/'outputs/aligned_correction_preparation_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    prepared={r['case_id']:r for r in read(P/'results_PRIVATE.json')['records']}
    model=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json');pred={r['case_id']:r for r in model['predictions']}
    old={(r['suite'],r['case_id']):r for r in read(ROOT/'outputs/image_loss_action_tree_comparison_v1/results_PRIVATE.json')['records']}
    assert all(sha(p)==h for p,h in bound.items())
    counts=dict(records=0,rgb8_outputs=0,region_metrics=0,scene_metrics=0,protected_outputs=0)
    for r in data['records']:
        source=prepared[r['case_id']];q=pred[r['case_id']];prior=old[r['old_feature_suite'],r['case_id']]
        assert r['new_features']==q['features'] and r['old_features']==prior['features'] and not r['scientific_admission']
        for rk,pk in [('image_path','scene_path'),('reference_path','reference_path'),('alpha_path','alpha_path'),('protected_path','protected_path'),('scoring_path','scoring_path')]:assert r[rk]==source[pk]
        im=rgb(r['image_path']);ref=rgb(r['reference_path']);ready=source['status']=='available' and source['alpha_path'] is not None
        alpha=np.load(source['alpha_path'],allow_pickle=False) if ready else np.zeros(im.shape[:2],float)
        guard=cv2.imread(source['protected_path'],0)>0 if source['protected_path'] else np.zeros(alpha.shape,bool)
        scoring=cv2.imread(source['scoring_path'],0)>0 if source['reference_support_available'] else None
        oldparams=prior['paths'].get('action_tree',{}).get('parameters') if prior['features'] is not None and ready else None
        params={'identity':[1.,1.,1.],'parent_controls_new_alpha':oldparams,'aligned_tree':q['parameters'] if ready else None}
        for name,p in params.items():
            actual=rgb(r['output_paths'][name]);expected=im.copy()
            if p is not None:
                x=im.astype(float)/255.;target=np.clip(x**p[0]*[p[1],1.,p[2]],0,1)
                expected=np.rint((x*(1-alpha[:,:,None])+target*alpha[:,:,None])*255).astype(np.uint8)
                expected[alpha==0]=im[alpha==0]
            np.testing.assert_array_equal(actual,expected)
            assert np.array_equal(actual[alpha==0],im[alpha==0]) and np.array_equal(actual[guard],im[guard]);counts['protected_outputs']+=1
            item=r['paths'][name];assert item['parameters']==p and item['prediction_available']==(p is not None)
            assert item['changed_channels']==int(np.count_nonzero(actual!=im));counts['rgb8_outputs']+=1
            for region,mask in [('region_metrics',scoring),('scene_metrics',np.ones(alpha.shape,bool))]:
                if mask is None:assert item[region] is None;continue
                a=actual[mask].astype(float);b=ref[mask].astype(float)
                assert abs(float(np.abs(a-b).mean())-item[region]['rgb8_mae_codes'])<1e-12
                de=float(deltaE_ciede2000(rgb2lab(a/255),rgb2lab(b/255)).mean())
                assert abs(de-item[region]['relative_deltaE00_mean'])<1e-10
                assert int(mask.sum())==item[region]['scoring_pixels'];counts[region]+=1
        counts['records']+=1
    for cohort,layers in data['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in data['records'] if r['cohort']==cohort and r['layer']==layer]
            assert len(rr)==s['attempts'] and sum(r['reference_available'] for r in rr)==s['region_scored']
            for name,m in s['methods'].items():
                assert m['prediction_available']==sum(r['paths'][name]['prediction_available'] for r in rr)
                assert m['changed']==sum(r['paths'][name]['changed_channels']>0 for r in rr)
                scored=[r for r in rr if r['reference_available']]
                assert m['region_harms']==sum(r['paths'][name]['region_metrics']['rgb8_mae_codes']>r['input_region_metrics']['rgb8_mae_codes'] for r in scored)
                assert m['region_benefits']==sum(r['paths'][name]['region_metrics']['rgb8_mae_codes']<r['input_region_metrics']['rgb8_mae_codes'] for r in scored)
                for region,eligible in [('region_metrics',scored),('scene_metrics',rr)]:
                    for metric in ('rgb8_mae_codes','relative_deltaE00_mean'):
                        expected=float(np.mean([r['paths'][name][region][metric] for r in eligible])) if eligible else None
                        actual=m[region+'_'+metric];assert actual is None if expected is None else abs(expected-actual)<1e-12
                        keys={r['subject_id'] for r in eligible}
                        expected=float(np.mean([np.mean([r['paths'][name][region][metric] for r in eligible if r['subject_id']==k]) for k in keys])) if keys else None
                        actual=m['equal_key_'+region+'_'+metric];assert actual is None if expected is None else abs(expected-actual)<1e-12
            common=[r for r in rr if r['reference_available'] and all(r['paths'][n]['prediction_available'] for n in ('parent_controls_new_alpha','aligned_tree'))]
            assert len(common)==s['both_predictions_region_scored']
            for name,actual in s['both_predictions_region_mae'].items():
                expected=float(np.mean([r['paths'][name]['region_metrics']['rgb8_mae_codes'] for r in common])) if common else None
                assert actual is None if expected is None else abs(expected-actual)<1e-12
    assert counts['records']==756 and all(sha(p)==h for p,h in bound.items())
    result=dict(passed=True,**counts,source_hashes=len(bound),new_fits=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
