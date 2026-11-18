"""Independent RGB8 rendering, protection and metric checks on all attempts."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
from skimage.color import rgb2lab,deltaE_ciede2000
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/face_local_action_comparison_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    d=read(OUT/'results_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    parent={r['case_id']:r for r in read(ROOT/'outputs/aligned_action_tree_comparison_v1/results_PRIVATE.json')['records']}
    pred={r['case_id']:r for r in read(ROOT/'outputs/face_local_action_models_v1/models_PRIVATE.json')['predictions']}
    counts=dict(records=0,outputs=0,region_metrics=0,scene_metrics=0);outputhashes={}
    for r in d['records']:
        p=prep[r['case_id']];q=pred[r['case_id']];im=rgb(p['scene_path']);ref=rgb(p['reference_path']);ready=p['status']=='available'
        assert r['parent']==parent[r['case_id']]['paths']['aligned_tree'] and r['candidate']['parameters']==q['parameters']
        alpha=np.load(p['alpha_path'],allow_pickle=False) if ready else np.zeros(im.shape[:2],float)
        guard=cv2.imread(p['protected_path'],0)>0 if p.get('protected_path') else np.zeros(alpha.shape,bool)
        scoring=cv2.imread(p['scoring_path'],0)>0 if p['reference_support_available'] else None
        expected=im.copy()
        if ready:
            params=q['parameters'];x=im.astype(float)/255.;corrected=np.clip(x**params[0]*[params[1],1,params[2]],0,1)
            expected=np.rint((x*(1-alpha[:,:,None])+corrected*alpha[:,:,None])*255).astype(np.uint8);expected[alpha==0]=im[alpha==0]
        actual=rgb(r['output_path']);assert np.array_equal(expected,actual)
        assert np.array_equal(actual[guard],im[guard]) and np.array_equal(actual[alpha==0],im[alpha==0])
        assert r['candidate']['changed_channels']==int(np.count_nonzero(actual!=im))
        for region,mask in [('region_metrics',scoring),('scene_metrics',np.ones(alpha.shape,bool))]:
            if mask is None:assert r['candidate'][region] is None;continue
            a=actual[mask].astype(float);b=ref[mask].astype(float);metric=r['candidate'][region]
            assert abs(float(np.abs(a-b).mean())-metric['rgb8_mae_codes'])<1e-12
            de=float(deltaE_ciede2000(rgb2lab(a/255),rgb2lab(b/255)).mean())
            assert abs(de-metric['relative_deltaE00_mean'])<1e-10 and int(mask.sum())==metric['scoring_pixels'];counts[region]+=1
        outputhashes[r['output_path']]=sha(r['output_path']);counts['outputs']+=1;counts['records']+=1
    assert counts['records']==756
    for cohort,layers in d['summary'].items():
        for layer,s in layers.items():
            rr=[r for r in d['records'] if r['cohort']==cohort and r['layer']==layer];scored=[r for r in rr if r['reference_available']]
            for method in ('parent','candidate'):
                m=s['methods'][method];assert m['changed']==sum(r[method]['changed_channels']>0 for r in rr)
                assert abs(m['region_MAE']-float(np.mean([r[method]['region_metrics']['rgb8_mae_codes'] for r in scored])))<1e-12
                assert m['harms']==sum(r[method]['region_metrics']['rgb8_mae_codes']>r['input_region_metrics']['rgb8_mae_codes'] for r in scored)
    receipt=dict(passed=True,checks=counts,source_hashes=len(bound),output_sha256=outputhashes,new_fits=0,
        result_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print('PASS',counts)

if __name__=='__main__':main()
