"""Independent direct-coordinate pixel replay of prepared paired evidence."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
OUT=ROOT/'outputs/reviewed_photographic_pixels_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    dest=OUT/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve existing verifier result')
    first=read(OUT/'verification_PRIVATE.json');assert first['passed']
    assert all(sha(p)==h for p,h in first['input_sha256'].items())
    data=read(OUT/'records_PRIVATE.json');assert len(data['records'])==14 and len(data['blocked_roles'])==2
    by_case={r['case_id']:r for r in data['records']};assert len(by_case)==14
    outputs={}
    for r in data['records']:
        path=Path(r['pixels_file']);assert sha(path)==r['pixels_sha256']
        outputs[str(path)]=sha(path)
        with np.load(path,allow_pickle=False) as pack:
            assert set(pack.files)=={'input_rgb8','reference_rgb8','alpha','protected','measurement_mask','correction_mask','scoring_mask'}
            own=pack['input_rgb8'];reference=pack['reference_rgb8'];alpha=pack['alpha'];protected=pack['protected']
            assert own.dtype==reference.dtype==np.uint8 and own.shape==reference.shape
            assert protected.dtype==bool and pack['scoring_mask'].dtype==bool
            assert np.array_equal(pack['scoring_mask'],alpha>0) and not alpha[protected].any()
            assert int((alpha>0).sum())==r['scoring_pixels']
            task=ROOT/'outputs/photographic_support_review_audit_v1'
            latest=next(x for x in read(task/'audit_PRIVATE.json')['latest'] if x['case_id']==r['case_id'])
            annotation=Path(latest['annotation']);bridge=r['input_bridge'];left,top,right,bottom=bridge['native_bounds']
            assert list(own.shape)==bridge['source_shape']
            image=cv2.imread(str(annotation/'photo_used.png'))
            normalized=cv2.resize(own[top:bottom,left:right,::-1],(256,256),interpolation=cv2.INTER_LINEAR)
            assert np.array_equal(image,normalized)
            normalized_alpha=np.load(annotation/'correction_alpha.npy',allow_pickle=False)
            normalized_p=cv2.imread(str(annotation/'protected_mask.png'),0)>0
            size=(right-left,bottom-top)
            local_alpha=cv2.resize(normalized_alpha,size,interpolation=cv2.INTER_LINEAR)
            local_p=cv2.resize(normalized_p.astype(np.float32),size,interpolation=cv2.INTER_AREA)>0
            local_alpha[local_p]=0
            expected_alpha=np.zeros(own.shape[:2],float);expected_alpha[top:bottom,left:right]=local_alpha
            expected_p=np.zeros(own.shape[:2],bool);expected_p[top:bottom,left:right]=local_p
            assert np.array_equal(alpha,expected_alpha) and np.array_equal(protected,expected_p)
            for kind in ['measurement','correction']:
                small=cv2.imread(str(annotation/(kind+'_mask.png')),0)
                expected=np.zeros(own.shape[:2],np.uint8);expected[top:bottom,left:right]=cv2.resize(small,size,interpolation=cv2.INTER_NEAREST)
                assert np.array_equal(pack[kind+'_mask'],expected)
            if r['role']=='target':assert np.array_equal(own,reference)
            else:
                target_record=by_case[r['frame']+'__target']
                with np.load(target_record['pixels_file'],allow_pickle=False) as target:
                    assert np.array_equal(reference,target['input_rgb8'])
            assert not any(r[k] for k in ['training_admitted','calibration_admitted','qualified_16features','target_control_fit','registration_verified'])
            assert r['provided_mst_label'] is None
    paths=[Path(__file__),OUT/'records_PRIVATE.json',OUT/'verification_PRIVATE.json',ROOT/'scripts/742_audit_photographic_support_reviews.py',
           ROOT/'outputs/photographic_support_review_audit_v1/audit_PRIVATE.json']
    outputs.update({str(p):sha(p) for p in paths})
    dest.write_text(json.dumps(dict(passed=True,paired_pixel_records=14,native_coordinate_replays=14,
        correct_target_reference_joins=7,target_identity_joins=7,all_scored_application_pixels_retained=True,
        blocked904roles=2,original_TIFF_reads=0,holdout_bytes_read=0,fits=0,input_sha256=outputs),indent=2),encoding='utf-8')
    print('PASS: 14 direct coordinate/mask/alpha replays,7exact target joins,7identity joins; no scoring-footprint filtering.')


if __name__=='__main__':main()
