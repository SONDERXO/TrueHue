"""Independent seed/decision/alpha verification; no source originals or models."""
from pathlib import Path
import json,hashlib,math
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reviewed_ffhq_support_tasks_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=OUT/'independent_verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve independent verification')
    receipt=read(OUT/'verification_PRIVATE.json');assert all(sha(p)==h for p,h in receipt['input_sha256'].items())
    decisions={r['source_id']:r for r in read(ROOT/'outputs/existing_ffhq_reference_decisions_v1/decisions_PRIVATE.json')['rows']}
    queue=read(OUT/'queue.json');assert len(queue['tasks'])==11 and len(queue['blocked'])==1
    assert queue['blocked'][0]['case_id']=='ffhq_29863__reference'
    seen=[]
    for task in queue['tasks']:
        folder=OUT/task['folder'];assert sha(folder/'manifest.json')==task['manifest_sha256']
        manifest=read(folder/'manifest.json');assert set(p.name for p in folder.iterdir())==set(manifest['files'])|{'manifest.json'}
        for name,record in manifest['files'].items():assert sha(folder/name)==record['sha256']
        r=read(folder/'report.json');ident=r['input_bridge']['original_source_id'];seen.append(ident)
        assert r['reference_preference']==decisions[ident] and decisions[ident]['reference_appearance_decision']=='acceptable'
        assert not r['generated_fixture'] and not r['training_admitted'] and r['measurement_review']==r['correction_review']=='pending'
        old=ROOT/'outputs/ffhq_mask_support_v1'/ident
        image=cv2.imread(str(folder/'photo_used.png'));np.testing.assert_array_equal(image,cv2.imread(str(old/'input.png')))
        m=cv2.imread(str(folder/'measurement_mask.png'),0);c=cv2.imread(str(folder/'correction_mask.png'),0);p=cv2.imread(str(folder/'protected_mask.png'),0)
        np.testing.assert_array_equal(m,cv2.imread(str(old/'candidate_mask.png'),0));np.testing.assert_array_equal(c,cv2.imread(str(old/'correction_mask.png'),0));assert not p.any()
        distance=cv2.distanceTransform((c>0).astype(np.uint8),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
        t=np.clip(distance/max(2,math.ceil(.03*r['face_width'])),0,1).astype(float);alpha=t*t*(3-2*t);alpha[c==0]=0
        np.testing.assert_array_equal(alpha,np.load(folder/'correction_alpha.npy',allow_pickle=False));np.testing.assert_array_equal(alpha,np.load(old/'alpha.npy',allow_pickle=False))
        encoded=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32);encoded[:,:,0]*=100./255.;encoded[:,:,1:]-=128.;lab=encoded[m>0];means=[round(float(np.mean(lab[:,i])),4) for i in range(3)]
        stats=r['measurement_statistics'];assert stats['skin_pixels']==int((m>0).sum())>=1000
        for k,v in zip(['mean_l_star','mean_a_star','mean_b_star'],means):assert abs(stats[k]-round(float(v),4))<1e-8
        assert abs(stats['ita_degrees']-round(float(np.degrees(np.arctan((means[0]-50)/means[2]))),4))<1e-8
    assert set(seen)=={k for k,v in decisions.items() if v['reference_appearance_decision']=='acceptable'}
    dest.write_text(json.dumps(dict(passed=True,exact_decision_joins=11,exact_cached_image_and_masks=11,independent_alpha_checks=11,independent_Lab_ITA_checks=11,real_annotations=0,original_photo_reads=0,holdout_reads=0,queue_sha256=sha(OUT/'queue.json'),verifier_sha256=sha(__file__)),indent=2)+'\n')
    print('PASS:11 independent decision/image/mask/alpha/Lab/ITA checks; no original reads.')

if __name__=='__main__':main()
