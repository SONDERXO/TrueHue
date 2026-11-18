"""Independently check actual-pixel preparation, separate masks and projection."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.photographic_target_diagnostic import distort,case_matrix,metrics
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
OUT=ROOT/'outputs/aligned_correction_preparation_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)

def main():
    data=read(OUT/'results_PRIVATE.json');plan=read(OUT/'plan_PRIVATE.json');bound=read(OUT/'final_input_sha256_PRIVATE.json')
    assert all(sha(p)==h for p,h in bound.items())
    recipes={r['id']:r for r in case_matrix()};clean={r['source_case']:r for r in data['records'] if r['recipe']=='clean'}
    counts=dict(scenes=0,normalized_pixels=0,measurement_replays=0,alpha_projections=0,protected_pixels=0,regional_metrics=0)
    for r in data['records']:
        assert not r['training_admitted'] and not r['calibration_admitted'] and not r['scientific_admission']
        source=rgb(r['source_path']);actual=rgb(r['scene_path']);reference=rgb(r['reference_path'])
        np.testing.assert_array_equal(source,reference)
        expected,_,_=distort(source,np.ones(source.shape[:2]),recipes[r['recipe']]);np.testing.assert_array_equal(actual,expected);counts['scenes']+=1
        folder=OUT/'cases'/r['case_id'];bridge=r.get('input_bridge')
        if bridge and (folder/'input.png').exists():
            left,top,right,bottom=bridge['native_bounds'];native=actual[top:bottom,left:right]
            norm=cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR)
            np.testing.assert_array_equal(norm,rgb(folder/'input.png'));counts['normalized_pixels']+=1
        if r['status']=='available':
            mask=cv2.imread(str(folder/'measurement_mask.png'),0)
            s=compute_masked_lab_statistics(cv2.imread(str(folder/'input.png')),mask,1000)
            assert s['valid'] and np.count_nonzero(mask)>=1000
            for name in ('ita_degrees','mean_l_star','mean_a_star','mean_b_star'):assert r['raw_features']['input_'+name]==s[name]
            counts['measurement_replays']+=1
        else:assert r['raw_features'] is None
        alpha=np.zeros(actual.shape[:2],float)
        if r['alpha_path']:
            alpha=np.load(r['alpha_path'],allow_pickle=False);norm=np.load(folder/'correction_alpha_normalized.npy',allow_pickle=False)
            veto=cv2.imread(str(folder/'protected_normalized.png'),0)>0
            left,top,right,bottom=bridge['native_bounds'];size=(right-left,bottom-top)
            projected=cv2.resize(norm,size,interpolation=cv2.INTER_LINEAR)
            protection=cv2.resize(veto.astype(np.float32),size,interpolation=cv2.INTER_AREA)>0;projected[protection]=0
            expected=np.zeros(actual.shape[:2],float);expected[top:bottom,left:right]=projected
            np.testing.assert_array_equal(alpha,expected)
            actual_protection=cv2.imread(r['protected_path'],0)>0
            guard=np.zeros(alpha.shape,bool);guard[top:bottom,left:right]=protection
            np.testing.assert_array_equal(guard,actual_protection);assert not alpha[guard].any()
            assert np.isfinite(alpha).all() and np.all((alpha>=0)&(alpha<=1))
            counts['alpha_projections']+=1;counts['protected_pixels']+=int(guard.sum())
        origin=clean[r['source_case']]
        assert r['reference_support_available']==(origin['status']=='available' and origin['alpha_path'] is not None)
        if r['reference_support_available']:
            scoring=(np.load(origin['alpha_path'],allow_pickle=False)>0)|(alpha>0)
            np.testing.assert_array_equal(cv2.imread(r['scoring_path'],0)>0,scoring)
            assert metrics(actual,reference,scoring)==r['input_region_metrics'];counts['regional_metrics']+=1
        else:assert r['input_region_metrics'] is None
        assert metrics(actual,reference,np.ones(alpha.shape,bool))==r['input_scene_metrics']
    assert counts['scenes']==756 and all(sha(p)==h for p,h in bound.items())
    result=dict(passed=True,**counts,bound_source_hashes=len(bound),measurement_contract_sha256=data['measurement_contract_sha256'],new_fits=0,new_image_forwards=0,verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
