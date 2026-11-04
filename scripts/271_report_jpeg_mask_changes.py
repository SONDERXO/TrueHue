"""Show worst mask agreement changes; overlap is not skin-label accuracy."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'outputs/endpoint_full_path_jpeg_v1';parent=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    rows={r['pair_id']:r for r in read(folder/'plan.json')['rows']}
    inputs={(r['pair_id'],r['encoding']):r for r in read(parent/'predictions.json')}
    records=read(folder/'attempts.json');statistics=[];boards=[]
    for encoding in ('lossless','jpeg95','jpeg85'):
        part=[r for r in records if r['encoding']==encoding];values=[]
        for r in part:
            row=rows[r['pair_id']];old=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
            new=cv2.imread(str(folder/'images'/(r['pair_id']+'_'+encoding+'_mask.png')),0)>0
            union=int((new|old).sum());iou=float((new&old).sum()/union) if union else None
            assert iou==r['original_mask_iou'];values.append(iou)
        worst=min(part,key=lambda r:r['original_mask_iou'])
        statistics.append(dict(encoding=encoding,frames=len(part),mean_iou=float(np.mean(values)),min_iou=min(values),worst_pair_id=worst['pair_id']))
        if encoding=='lossless':continue
        row=rows[worst['pair_id']];image=cv2.imread(str(parent/inputs[(worst['pair_id'],encoding)]['encoded_input_path']))
        old=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        new=cv2.imread(str(folder/'images'/(worst['pair_id']+'_'+encoding+'_mask.png')),0)>0
        old_overlay=image.copy();old_overlay[old]=(.5*old_overlay[old]+[0,150,0]).astype(np.uint8)
        new_overlay=image.copy();new_overlay[new]=(.5*new_overlay[new]+[0,150,0]).astype(np.uint8)
        changes=image.copy();changes[new&~old]=[0,0,255];changes[old&~new]=[255,0,0]
        board=np.hstack((image,old_overlay,new_overlay,changes));header=np.full((50,board.shape[1],3),245,np.uint8)
        cv2.putText(header,f'{worst["pair_id"]} {encoding} IoU {worst["original_mask_iou"]:.3f}',(6,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(20,20,20),1)
        cv2.putText(header,'Input / original mask / rerun mask / red added, blue removed',(6,42),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,20,20),1)
        name='worst_mask_'+encoding+'.png';assert cv2.imwrite(str(folder/name),np.vstack((header,board)));boards.append(name)
    (folder/'mask_agreement_report.json').write_text(json.dumps(dict(status='verified_mask_agreement_only',statistics=statistics,
        caveat='Original candidate masks are not ground truth; new masks have no inferred human approval.',
        producer_sha256=sha(Path(__file__)),board_sha256={name:sha(folder/name) for name in boards}),indent=2),encoding='utf-8')
    print(json.dumps(statistics))


if __name__=='__main__':main()
