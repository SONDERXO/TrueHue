"""Align saved development parents; never opens the candidate holdout."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2,numpy as np
from scipy.io import loadmat
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.ita_estimation.faceocc_development import contract
P=ROOT/'outputs/group_diversity_parent_screen_v1';OUT=ROOT/'outputs/group_diversity_final_masks_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed preparation')
    assert read(P/'verification_PRIVATE.json')['passed'];data=read(P/'results_PRIVATE.json');bound=read(P/'input_sha256_PRIVATE.json')
    spec,identity=contract(ROOT)
    bound.update({str(ROOT/p):h for p,h in spec['dependency_sha256'].items()})
    for rel in ('scripts/602_prepare_diversity_occlusion.py','scripts/603_run_diversity_faceocc.py','scripts/369_run_faceocc_logits.py',
                'docs/group-diversity-occlusion-protocol-2026-11-08.md'):
        p=ROOT/rel;bound[str(p)]=sha(p)
    for p in (P/'results_PRIVATE.json',P/'verification_PRIVATE.json'):bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    OUT.mkdir();(OUT/'logits').mkdir();records=[];attempts=[]
    for i,old in enumerate(data['records'],1):
        assert old['role']=='development_candidate'
        r=dict(old);folder=OUT/r['case_id'];folder.mkdir()
        r.update(status='unavailable',stage='parent_measurement',scientific_admission=False)
        if old['status']=='parent_available':
            parent=P/r['case_id']
            for name in ('input.png','landmarks.npy','parent_mask.png','categories.png'):
                p=parent/name;bound[str(p)]=sha(p)
            try:
                image=cv2.imread(str(parent/'input.png'));points=np.load(parent/'landmarks.npy',allow_pickle=False)
                aligned,matrix,details=align_input(image,points,template)
                path=folder/'aligned.png';assert cv2.imwrite(str(path),aligned);bound[str(path)]=sha(path)
                r.update(status='inference_ready',stage='FaceOcc_pending',alignment=details,matrix=matrix.tolist())
                attempts.append(dict(image_id=r['case_id'],case_index=i,aligned_path=str(path)))
            except (ValueError,RuntimeError,cv2.error) as e:r.update(stage='alignment',reason=str(e))
        records.append(r)
    assert len(records)==96 and len(attempts)<=83
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'preparation_PRIVATE.json').write_text(json.dumps(dict(records=records,measurement_contract=spec,measurement_contract_sha256=identity),indent=2),encoding='utf-8')
    (OUT/'inference_plan.json').write_text(json.dumps(dict(attempts=attempts,input_sha256=bound,holdout_image_reads=0,new_fits=0),indent=2),encoding='utf-8')
    print('Prepared',len(attempts),'raw aligned inputs /96development attempts; holdout closed.')

if __name__=='__main__':main()
