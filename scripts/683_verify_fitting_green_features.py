"""Independent formula, affine-mask reconstruction, source and role replay."""
from pathlib import Path
from collections import Counter
import hashlib,json,math
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/fitting_green_features_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def main():
    target=OUT/'verification_with_metadata_PRIVATE.json';assert not target.exists()
    d=read(OUT/'features_PRIVATE.json');ready=read(ROOT/'outputs/green_channel_design_readiness_v1/readiness_PRIVATE.json')
    parent=read(ROOT/'outputs/colour_nonharm_models_v1/models_PRIVATE.json')
    metadata={r['case_id']:r for folder in ('aligned_correction_preparation_v1','expanded_correction_inputs_v1') for r in read(ROOT/'outputs'/folder/'results_PRIVATE.json')['records']}
    clean_metadata={r['case_id']:r for r in read(ROOT/'outputs/group_diversity_final_masks_v1/results_PRIVATE.json')['records']}
    assets={r['case_id']:r for r in ready['assets']};assert len(d['records'])==len(assets)==910
    counts=dict(rows=0,quantile_scalar_checks=0,log_contrast_checks=0,raw_measurements=0,reconstructed_masks=0,native_projections=0)
    assert {r['case_id'] for r in d['records']}==set(assets)
    values={}
    def percentile(a,p):
        rank=(len(a)-1)*p/100.;lo=math.floor(rank);hi=math.ceil(rank)
        return a[lo]+(a[hi]-a[lo])*(rank-lo)
    for r in d['records']:
        a=assets[r['case_id']]
        original=metadata[r['case_id']]
        assert r['raw_features']==original['raw_features'] and r['input_bridge']==original['input_bridge']
        assert r['native_mask_path']==original['measurement_native_path']
        for k in ('image_path','mask_path','role','subject_id'):assert r[k]==a[k]
        image=cv2.imread(r['image_path']);mask=cv2.imread(r['mask_path'],0)
        assert image.shape==(256,256,3) and mask.shape==(256,256) and set(np.unique(mask))<={0,255}
        assert int(np.count_nonzero(mask))==r['skin_pixels']>=1000
        assert sha(r['image_path'])==a['inherited_image_sha256']
        if a['inherited_mask_sha256']:assert sha(r['mask_path'])==a['inherited_mask_sha256']
        else:
            p=r['provenance'];assert p['method']=='exact_reconstruction_from_inherited_cached_artifacts'
            for k in ('parent_mask_path','landmarks_path','logits_path','alignment_path'):
                assert sha(p[k])==parent['input_sha256'][p[k]]
            baseline=cv2.imread(p['parent_mask_path'],0)
            logits=np.load(p['logits_path'],allow_pickle=False);matrix=np.asarray(p['matrix'],float)
            origin=clean_metadata[original['source_case']] if original['recipe']=='clean' else original
            assert p['matrix']==origin['matrix']
            valid=cv2.warpAffine(np.full((256,256),255,np.uint8),matrix,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            selected=np.where((logits>0)&(valid>0),255,0).astype(np.uint8)
            visible=cv2.warpAffine(selected,cv2.invertAffineTransform(matrix),(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            expected=np.where((baseline!=0)&(visible!=0),255,0).astype(np.uint8)
            assert np.array_equal(expected,mask);counts['reconstructed_masks']+=1
        bridge=r['input_bridge'];left,top,right,bottom=bridge['native_bounds']
        projection=np.zeros(bridge['source_shape'][:2],np.uint8)
        projection[top:bottom,left:right]=cv2.resize(mask,(right-left,bottom-top),interpolation=cv2.INTER_NEAREST)
        assert np.array_equal(projection,cv2.imread(r['native_mask_path'],0));counts['native_projections']+=1
        if r['native_mask_historically_bound']:assert sha(r['native_mask_path'])==parent['input_sha256'][r['native_mask_path']]
        green=sorted(map(int,image[:,:,1][mask>0]));q=[percentile(green,p) for p in (10,50,90)]
        obtained=[r['features'][k] for k in d['feature_names']]
        for a,b in zip(q,obtained[:3]):assert abs(a-b)<1e-10;counts['quantile_scalar_checks']+=1
        assert abs(math.log((q[2]+1)/(q[0]+1))-obtained[3])<1e-12;counts['log_contrast_checks']+=1
        lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[:,:,0]*=100./255;lab[:,:,1:]-=128.
        means=[round(float(np.mean(lab[:,:,k][mask>0])),4) for k in range(3)]
        raw=r['raw_features']
        assert means==[raw['input_mean_l_star'],raw['input_mean_a_star'],raw['input_mean_b_star']]
        ita=round(math.degrees(math.atan((means[0]-50)/means[2])),4)
        assert ita==raw['input_ita_degrees'];counts['raw_measurements']+=4
        assert r['valid'];counts['rows']+=1;values[r['case_id']]=r
    fitting={r['case_id'] for r in d['records'] if r['role']=='fitting'}
    reserved={r['case_id'] for r in d['records'] if r['role']=='reserved_clean'}
    assert fitting==set(parent['full']['training_cases']) and reserved=={r['case_id'] for r in parent['full']['reserved_clean_vectors']}
    for f in parent['folds']:
        assert set(f['training_cases'])<=fitting
        assert all(values[c]['subject_id']!=f['held_key'] for c in f['training_cases'])
    expected_pairs={}
    for r in values.values():
        if r['role']!='fitting' or r['recipe']=='clean':continue
        clean=r['source_case']+'__clean'
        if clean in fitting:expected_pairs[r['case_id']]={n:r['features'][n]-values[clean]['features'][n] for n in d['feature_names']}
    assert len(expected_pairs)==len(d['source_pairs'])
    for p in d['source_pairs']:assert p['delta']==expected_pairs[p['case_id']]
    for recipe,report in d['fitting_pair_behaviour'].items():
        rows=[p for p in d['source_pairs'] if p['recipe']==recipe];assert len(rows)==report['pairs']
        for n,s in report['features'].items():
            v=sorted(p['delta'][n] for p in rows);median=(v[(len(v)-1)//2]+v[len(v)//2])/2
            assert s==dict(min=v[0],median=median,max=v[-1],lower=sum(z<0 for z in v),equal=sum(z==0 for z in v),higher=sum(z>0 for z in v))
    for p,h in d['input_sha256'].items():assert sha(p)==h
    assert counts['rows']==910 and counts['reconstructed_masks']==683
    receipt=dict(passed=True,checks=counts,source_hashes=len(d['input_sha256']),source_pairs_checked=len(expected_pairs),
        features_sha256=sha(OUT/'features_PRIVATE.json'),verifier_sha256=sha(Path(__file__)),
        limitation='Independent quantile/log/raw-statistics, direct affine mask replay and native projection; fitting/reserved roles only.',
        previous_receipt_sha256=sha(OUT/'verification_PRIVATE.json'),
        supersedes='verification_PRIVATE.json: verifier was extended with metadata assertions during the first run; this clean rerun is authoritative.',
        new_fits=0,new_model_forwards=0,evaluation_only_rows=0,holdout_image_reads=0)
    target.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
