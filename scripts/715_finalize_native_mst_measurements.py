"""Finalize the fixed native MST measurements from saved logits, without fits."""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter,defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from scipy.io import loadmat
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.fixed_face_input_bridge import native_projection
OUT=ROOT/'outputs/native_mst_measurement_readiness_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    dest=OUT/'results_PRIVATE.json'
    if dest.exists():raise FileExistsError('Completed results exist; no regeneration')
    plan=read(OUT/'plan_PRIVATE.json');prep=read(OUT/'preparation_PRIVATE.json');inference=read(OUT/'inference.json')
    assert inference['plan_sha256']==sha(OUT/'inference_plan.json')
    bound=read(OUT/'inference_plan.json')['input_sha256'];assert all(sha(p)==h for p,h in bound.items())
    pred={r['image_id']:r for r in inference['records']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm'];rows=[]
    for old in prep['records']:
        r=dict(old,raw_features=None);folder=OUT/r['source_case'];im=cv2.imread(str(folder/'input.png'))
        if r['status']=='inference_ready':
            p=pred[r['source_case']]
            if p['status']=='success':
                assert sha(OUT/p['logits_path'])==p['logits_sha256']
                parent=cv2.imread(str(folder/'parent_mask.png'),0)
                m=evaluate_parent(SimpleNamespace(image=im,mask=parent,report=r['parent_report']),np.load(folder/'landmarks.npy',allow_pickle=False),template,
                    lambda _:np.load(OUT/p['logits_path'],allow_pickle=False))
                r['measurement_report']=m.report;r['status']='available' if m.report['status']=='success' else 'unavailable'
                if m.mask is not None:
                    assert cv2.imwrite(str(folder/'measurement_mask.png'),m.mask)
                    native,counts=native_projection(m.mask,r['input_bridge']);assert cv2.imwrite(str(folder/'measurement_native.png'),native)
                    r['native_counts']=counts
                if r['status']=='available':
                    r['raw_features']={f'input_{k}':m.report['statistics'][k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
                else:r['reason']=m.report.get('reason','Measurement failed')
            else:r.update(status='unavailable',reason=p.get('reason','FaceOcc unavailable'))
        shown=np.full((256,512,3),35,np.uint8)
        if im is not None:
            shown[:,:256]=im;shown[:,256:]=im
            if (folder/'measurement_mask.png').exists():shown[:,256:][cv2.imread(str(folder/'measurement_mask.png'),0)==0]=35
        else:
            original=cv2.imread(r['source_path']);shown[:,:256]=cv2.resize(original,(256,256))
        title=np.full((25,512,3),255,np.uint8);cv2.putText(title,r['source_case']+' '+r['status'],(4,17),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        assert cv2.imwrite(str(folder/'board.png'),np.vstack([title,shown]));rows.append(r)
    summary=dict(attempts=30,publisher_subjects=10,available=sum(r['status']=='available' for r in rows),counts=prep['counts'],
        FaceOcc_forwards=inference['forwards'],new_fits=0,calibration_admitted=False,holdout_reads=0)
    groups=defaultdict(list)
    for r in rows:groups[r['subject_id']].append(r)
    summary['subjects_complete_all_three']=sum(all(r['status']=='available' for r in a) for a in groups.values())
    assert all(sha(p)==h for p,h in bound.items())
    dest.write_text(json.dumps(dict(summary=summary,records=rows,measurement_contract_sha256=plan['measurement_contract_sha256'],input_sha256=bound),indent=2,allow_nan=False),encoding='utf-8')
    # Contact sheets preserve all failures and have no source-score labels.
    for start in range(0,30,5):
        sheet=np.vstack([cv2.imread(str(OUT/r['source_case']/'board.png')) for r in rows[start:start+5]])
        assert cv2.imwrite(str(OUT/f'sheet_{start//5:02d}.png'),sheet)
    (OUT/'artifact_sha256_PRIVATE.json').write_text(json.dumps({str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2))
    print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
