"""Cached-frame/identity/scene/outcome verification. No model or source rereads."""
from pathlib import Path
import csv,hashlib,json,math
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/scin_nine_support_screen_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    result=read(OUT/'results_PRIVATE.json');plan=read(OUT/'plan_PRIVATE.json');preflight=read(OUT/'identity_preflight_PRIVATE.json')
    artifacts=read(OUT/'artifact_sha256_PRIVATE.json');assert all(sha(OUT/p)==h for p,h in artifacts.items())
    assert all(sha(p)==h for p,h in result['input_sha256'].items())
    policy=read(ROOT/'outputs/scin_exploratory_policy_v1/roster_PRIVATE.json')
    assert len(result['records'])==len(preflight['sources'])==len(policy)==9
    aliases=read(OUT/'alias_hashes_PRIVATE.json')['records'];assert len(aliases)==10
    with (ROOT/'data/manifests/source_preparation_v1/source_audit_and_partitions.csv').open(encoding='utf-8-sig',newline='') as f:
        locked={r['decoded_pixel_sha256'] for r in csv.DictReader(f) if r['partition'] not in ('train','training','development_train') and r['decoded_pixel_sha256']}
    seen={};checks=[]
    for row,original,frozen in zip(result['records'],preflight['sources'],policy):
        assert row['case_id']==original['case_id']==frozen['case_id']
        assert row['reference_labels']==frozen['reference_labels']
        assert row['source_sha256']==original['source_sha256']
        own=[r for r in aliases if r['case_id']==row['case_id']]
        assert len({r['sha256'] for r in own})==1 and own[0]['sha256']==row['source_sha256']
        image=cv2.imread(str(OUT/row['source_case']/'source_full.png'));assert image is not None
        assert list(image.shape)==row['source_shape']
        assert hashlib.sha256(image.tobytes()).hexdigest()==row['decoded_BGR_sha256']
        # Old partition fingerprints include the shape string, unlike initial preflight's BGR-only hash.
        compatible=hashlib.sha256(str(image.shape).encode()+image.tobytes()).hexdigest()
        conflict=compatible in locked
        assert not conflict,'Established locked exact overlap: quarantine, do not admit.'
        assert compatible not in seen;seen[compatible]=row['source_case']
        rgb=image[:,:,::-1];n=image.shape[0]*image.shape[1]
        mean=[int(rgb[:,:,i].astype(np.uint64).sum())/n for i in range(3)]
        lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)[:,:,0];hist=np.bincount(lab.ravel(),minlength=256);cum=np.cumsum(hist)
        levels=np.arange(256,dtype=np.float32)*(100/255);quantiles=[]
        for q in (.1,.5,.9):
            position=(n-1)*q;i=math.floor(position);fraction=position-i
            a=int(np.searchsorted(cum,i+1));b=int(np.searchsorted(cum,min(i+1,n-1)+1))
            quantiles.append(float(levels[a])*(1-fraction)+float(levels[b])*fraction)
        values=[math.log((mean[0]+1)/(mean[1]+1)),math.log((mean[2]+1)/(mean[1]+1)),*quantiles,
                int(np.count_nonzero(np.min(rgb,axis=2)==0))/n,int(np.count_nonzero(np.max(rgb,axis=2)==255))/n]
        expected=dict(zip(('scene_log_r_over_g','scene_log_b_over_g','scene_l_p10','scene_l_p50','scene_l_p90','scene_any_zero_fraction','scene_any_full_fraction'),values))
        for name,v in expected.items():assert math.isclose(v,row['scene_features'][name],abs_tol=1e-10,rel_tol=1e-10)
        assert row['native_anchor_boxes']==[] and row['status']=='unavailable' and row['raw_features'] is None
        assert row['calls']=={'detector_forwards':1,'landmarker_helper_calls':0,'parser_forwards':0}
        assert not row['training_admitted'] and not row['calibration_admitted'] and row['verified_person_id'] is None
        checks.append(dict(source_case=row['source_case'],scene_checks=7,shape_prefixed_BGR_sha256=compatible,
                           saved_locked_exact_overlap=False,anchor_count=0,reference_labels_preserved=True))
    inference=read(OUT/'inference.json');assert inference['records']==[] and inference['forwards']==0
    report=dict(passed=True,cases=9,alias_files=10,unique_exact_decoded_groups=9,scene_scalar_checks=63,
        checks=checks,source_rereads=0,new_forwards=0,new_fits=0,holdout_reads=0,
        locked_hash_format_clarification='Initial preflight compared BGR-only to historical shape-prefixed BGR. This independent cached-frame verification uses the compatible shape-prefixed format; zero matches. Initial artifacts preserved.',
        duplicate_limit='No exact duplicate among9 and no matches in checked saved locked hashes; not global duplicate/person clearance.',
        results_sha256=sha(OUT/'results_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(report,indent=2)+'\n');print('PASS:9 outcomes/10aliases/9 cached-frame identities/63scenevalues/zero savedlocked exact overlaps;zero new calls.')


if __name__=='__main__':main()
