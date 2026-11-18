"""Verify native calibration measurements and coverage; no model calls or fits."""
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.ita_estimation.faceocc_veto_candidate import combine_saved
OUT=ROOT/'outputs/labelled_brightness_screen_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def interval(v):
    v=Decimal(v)
    return '[1,3)' if v<3 else '[3,5)' if v<5 else '[5,7)' if v<7 else '[7,9)' if v<9 else '[9,10]'
def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve prior verification')
    d=read(OUT/'results_PRIVATE.json');plan=read(OUT/'plan_PRIVATE.json');inf=read(OUT/'inference.json')
    artifacts=read(OUT/'artifact_sha256_PRIVATE.json')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    assert inf['forwards']==len(inf['records'])==len(read(OUT/'inference_plan.json')['attempts'])
    predictions={r['image_id']:r for r in inf['records']}
    assert len(d['records'])==30
    roster={f'bright_{i:02d}': r for i,r in enumerate(read(ROOT/'outputs/labelled_brightness_coverage_review_v1/candidate_roster_PRIVATE.json'),1)}
    groups=defaultdict(list);strata=defaultdict(list);checks=[];shared=[];gained=[];lost=[];exact=0;replayed=0
    for r in d['records']:
        cid=r['source_case'];folder=OUT/cid;oldr=dict(status=r['status'],source_mst_exact_decimal=roster[cid]['source_mst_exact_decimal'])
        assert r['source_mst_exact_decimal']==oldr['source_mst_exact_decimal']
        groups[r['subject_id']].append(r);strata[interval(r['source_mst_exact_decimal'])].append(r)
        available=r['status']=='available';before=oldr['status']=='available'
        if available and not before:gained.append(cid)
        if before and not available:lost.append(cid)
        if 'input_bridge' in r:
            b=r['input_bridge'];l,t,rr,bb=b['native_bounds'];side=rr-l
            image=cv2.imread(r['source_path'])
            np.testing.assert_array_equal(image[t:bb,l:rr],cv2.imread(str(folder/'native_input.png')))
        if cid in predictions:
            p=predictions[cid];assert sha(OUT/p['logits_path'])==p['logits_sha256']
            im=cv2.imread(str(folder/'input.png'));parent=cv2.imread(str(folder/'parent_mask.png'),0)
            mask,_,rep=combine_saved(im,parent,np.load(OUT/p['logits_path'],allow_pickle=False),np.array(read(folder/'matrix.json')))
            np.testing.assert_array_equal(mask,cv2.imread(str(folder/'measurement_mask.png'),0))
            idx=np.floor(np.arange(side)*256/side).astype(int)
            expected=np.zeros(image.shape[:2],np.uint8);expected[t:bb,l:rr]=mask[idx[:,None],idx[None,:]]
            np.testing.assert_array_equal(expected,cv2.imread(str(folder/'measurement_native.png'),0))
            if available:
                lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
                lab[:,:,0]*=100/255;lab[:,:,1:]-=128
                selected=lab[mask>0]
                lval,aval,bval=[round(float(selected[:,i].mean()),4) for i in range(3)]
                itaval=round(math.degrees(math.atan((lval-50)/bval)),4)
                expected_features=dict(input_mean_l_star=lval,input_mean_a_star=aval,input_mean_b_star=bval,input_ita_degrees=itaval)
                assert expected_features==r['raw_features'],cid
                assert len(selected)>=1000
            replayed+=1
        checks.append(dict(source_case=cid,status=r['status'],old_status=oldr['status'],label_preserved=True,
            source_hash_matches=sha(r['source_path'])==r['source_sha256'],native_pixels=r.get('native_counts',{}).get('selected_native_grid_locations')))
    coverage={k:dict(attempted_photos=len(v),attempted_subjects=len({r['subject_id'] for r in v}),
        available_photos=sum(r['status']=='available' for r in v),
        available_subjects=len({r['subject_id'] for r in v if r['status']=='available'})) for k,v in strata.items()}
    ranges={k:max(r['raw_features']['input_ita_degrees'] for r in v)-min(r['raw_features']['input_ita_degrees'] for r in v)
        for k,v in groups.items() if all(r['status']=='available' for r in v)}
    result=dict(passed=True,attempts=30,subject_groups=len(groups),cached_masks_replayed=replayed,
        feature_vectors_independently_verified=sum(r['status']=='available' for r in d['records']),
        new_available=d['summary']['available'],
        
        descriptive_score_interval_coverage=coverage,complete_subject_ita_ranges=ranges,checks=checks,
        results_sha256=sha(OUT/'results_PRIVATE.json'),artifact_manifest_sha256=sha(OUT/'artifact_sha256_PRIVATE.json'),
        verifier_sha256=sha(Path(__file__)),new_forwards=0,new_fits=0,holdout_reads=0,
        calibration_admitted=False,disposition='Measurement preparation verified; mask/support and coverage do not establish calibration eligibility. No fit.',
        limitation='Prediction-mask replay is software verification, not dense skin truth; ITA ranges are not mapping accuracy.')
    assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in d['input_sha256'].items())
    dest.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print('PASS: all30 outcomes, cached mask/native/feature replays and bound hashes unchanged.')

    print('Coverage',json.dumps(coverage));print('Complete-subject ITA ranges',json.dumps(ranges))
if __name__=='__main__':main()
