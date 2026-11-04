"""One fixed bridge preview of saved inputs, without model inference."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.faceocc_mediapipe_bridge import align_input


def main():
    out=ROOT/'outputs/faceocc_bridge_v1';parent=ROOT/'outputs/additional_mst_eligibility_v1'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    template_path=ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat'
    provenance=json.loads((template_path.parent/'template_provenance.json').read_text())
    assert digest(template_path)==provenance['sha256']
    template=loadmat(template_path)['lm'];assert template.shape==(68,3)
    source=json.loads((parent/'summary.json').read_text())
    hashes={str(p):digest(p) for p in [template_path,parent/'summary.json',Path(__file__),
        ROOT/'src/skin_masking/faceocc_mediapipe_bridge.py',ROOT/'src/skin_masking/faceocc_coordinates.py',
        ROOT/'docs/faceocc-bridge-protocol-2026-11-01.md']}
    for r in source['records']:
        if r['status']=='success':
            folder=parent/Path(r['board_path']).parent
            for name,h in r['saved_sha256'].items():
                assert digest(folder/name)==h;hashes[str(folder/name)]=h
    out.mkdir()
    (out/'plan.json').write_text(json.dumps(dict(attempts=[r['image_id'] for r in source['records']],
        input_sha256=hashes,template_sha256=provenance['sha256'],
        adaptation='fixed_MediaPipe_five_anchor_not_upstream_3DDFA',model_inference=False),indent=2))
    records=[];cards=[];boards=[]
    for index,r in enumerate(source['records'],1):
        rec=dict(image_id=r['image_id'],case_index=index,admitted=False)
        if r['status']!='success':
            rec.update(status='parent_failed',reason=r.get('reason'));records.append(rec);continue
        folder=parent/Path(r['board_path']).parent
        image=cv2.imread(str(folder/'input.png'));points=np.load(folder/'landmarks.npy')
        try:
            aligned,matrix,report=align_input(image,points,template)
            target=out/('case_'+str(index));target.mkdir()
            assert cv2.imwrite(str(target/'aligned.png'),aligned)
            original=image.copy();shown=aligned.copy()
            for j,(p,q) in enumerate(zip(report['anchors_xy'],report['aligned_anchors_xy'])):
                for canvas,xy in [(original,p),(shown,q)]:
                    xy=tuple(np.rint(xy).astype(int));cv2.circle(canvas,xy,3,(0,255,255),-1)
                    cv2.putText(canvas,str(j),xy,cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,255),1)
            board=np.hstack((original,shown));assert cv2.imwrite(str(target/'board.png'),board)
            label=np.full((25,512,3),255,np.uint8)
            cv2.putText(label,str(index)+' '+r['subject_id'],(8,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            boards.append(np.vstack((label,board)))
            rec.update(status='aligned_input_available',**report,forward_matrix=matrix.tolist(),
                inverse_matrix=cv2.invertAffineTransform(matrix).tolist(),
                aligned_sha256=digest(target/'aligned.png'),aligned_path=str((target/'aligned.png').relative_to(out)))
            cards.append('<h2>'+str(index)+' '+r['image_id']+'</h2><img src="case_'+str(index)+'/board.png">')
        except ValueError as error:
            rec.update(status='alignment_failed',reason=str(error))
        records.append(rec)
    assert all(digest(p)==h for p,h in hashes.items())
    for i in range(0,len(boards),4):cv2.imwrite(str(out/('contact_'+str(i//4+1)+'.png')),np.vstack(boards[i:i+4]))
    summary=dict(records=records,attempts=25,parent_failures=8,
        aligned_inputs=sum(r['status']=='aligned_input_available' for r in records),
        adaptation=True,upstream_landmark_equivalence=False,model_inferences=0,
        original_masks_unchanged=True,correction_changed=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>FaceOcc alignment bridge</title><style>body{font:18px system-ui;max-width:1000px;margin:auto;padding:20px}img{width:100%}</style><h1>Fixed MediaPipe-to-FaceOcc alignment</h1><p>Original; aligned input. Yellow anchors: eyes0/1, nose2, mouth3/4. This is a documented TrueHue adaptation, not upstream landmark equivalence. No segmentation predictions shown. Eight parent failures remain.</p>'+''.join(cards),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))


if __name__=='__main__':main()
