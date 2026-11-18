"""Native-detail and latest-mask private boards, with frozen input identities."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PARENT=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_usability_screen_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for p in [Path(__file__),ROOT/'docs/stellenbosch-usability-screen-protocol-2026-11-05.md']:bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    boards=[];cases=[]
    for r in read(PARENT/'results_PRIVATE.json')['records']:
        folder=BASE/r['case_id'];image=cv2.imread(str(folder/'input.png'));native=cv2.imread(str(folder/'native_crop.png'))
        canvas=np.full_like(image,35);side=native.shape[0];start=(256-side)//2;canvas[start:start+side,start:start+side]=native
        mask=cv2.imread(str(PARENT/r['case_id']/'measurement_mask.png'),0) if r['status']=='success' else np.zeros((256,256),np.uint8)
        selected=mask>0;overlay=image.copy();overlay[selected]=np.rint(.6*image[selected]+.4*np.array([0,255,0])).astype(np.uint8)
        pixels=image.copy();pixels[~selected]=35
        x0,y0,x1,y1=r['input_bridge']['native_bounds']
        projected=cv2.imread(str(PARENT/r['case_id']/'native_grid.png'),0) if r['status']=='success' else np.zeros((224,224),np.uint8)
        nm=projected[y0:y1,x0:x1]>0;native_overlay=native.copy()
        native_overlay[nm]=np.rint(.6*native[nm]+.4*np.array([0,255,0])).astype(np.uint8)
        zoom=cv2.resize(native_overlay,(256,256),interpolation=cv2.INTER_NEAREST)
        label=np.full((26,1024,3),255,np.uint8)
        cv2.putText(label,r['case_id']+' '+r['condition']+' '+r['status']+' nativeSide='+str(side)+' selectedNative='+str(int(nm.sum())),(4,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        boards.append(np.vstack([label,np.hstack([canvas,overlay,pixels,zoom])]))
        cases.append(dict(case_id=r['case_id'],status=r['status'],source_sha256=sha(Path(r['source_path'])),
            native_crop_sha256=sha(folder/'native_crop.png'),measurement_mask_sha256=sha(PARENT/r['case_id']/'measurement_mask.png') if r['status']=='success' else None))
    assert len(cases)==30
    for i in range(10):assert cv2.imwrite(str(OUT/f'contact_{i+1:02d}.png'),np.vstack(boards[3*i:3*i+3]))
    (OUT/'cases_PRIVATE.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private final usability screen</h1><p>Native crop padded without enlargement; normalized selected overlay; selected original colours; native mask nearest-neighbour zoom (not added detail). Failed cases retain empty selection. Scores hidden; assistant review is not independent or pixel truth. Research only; no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print('30 private native-detail boards prepared; scores hidden; no inference or mask changes.')

if __name__=='__main__':main()
