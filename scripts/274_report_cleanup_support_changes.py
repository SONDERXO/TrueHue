"""Show coverage recovery and maximum outside-reference addition without labels."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'outputs/jpeg_cleanup_order_v1';parent=ROOT/'outputs/endpoint_full_path_jpeg_v1';inputs=ROOT/'outputs/endpoint_jpeg_sensitivity_v1'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    rows={r['pair_id']:r for r in read(folder/'plan.json')['parent_rows']}
    encoded={(r['pair_id'],r['encoding']):r for r in read(inputs/'predictions.json')};records=read(folder/'attempts.json')
    selected=[('known_forehead_loss',next(r for r in records if r['pair_id']=='1398__table2_medium' and r['encoding']=='jpeg85')),
        ('largest_outside_reference_addition',max(records,key=lambda r:r['candidate_pixels_outside_reference']-r['baseline_pixels_outside_reference']))]
    artifacts=[]
    for label,r in selected:
        pair=r['pair_id'];encoding=r['encoding'];stem=pair+'_'+encoding;row=rows[pair]
        image=cv2.imread(str(inputs/encoded[(pair,encoding)]['encoded_input_path']))
        old=cv2.imread(str(parent/'images'/(stem+'_mask.png')),0)>0;new=cv2.imread(str(folder/'images'/(stem+'_mask.png')),0)>0
        before=image.copy();before[old]=(.5*before[old]+[0,150,0]).astype(np.uint8)
        after=image.copy();after[new]=(.5*after[new]+[0,150,0]).astype(np.uint8)
        top=np.hstack((image,before,after));bottom=np.hstack((cv2.imread(str(ROOT/row['reference_path'])),cv2.imread(str(parent/'images'/(stem+'_result.png'))),cv2.imread(str(folder/'images'/(stem+'_result.png')))))
        board=np.vstack((top,bottom));header=np.full((50,board.shape[1],3),245,np.uint8)
        cv2.putText(header,stem,(5,19),cv2.FONT_HERSHEY_SIMPLEX,.5,(20,20,20),1)
        cv2.putText(header,'Top: input / old mask / candidate. Bottom: reference / old result / candidate.',(5,40),cv2.FONT_HERSHEY_SIMPLEX,.43,(20,20,20),1)
        path=folder/(label+'.png');assert cv2.imwrite(str(path),np.vstack((header,board)))
        artifacts.append(dict(selection=label,pair_id=pair,encoding=encoding,path=path.name,sha256=sha(path),added_pixels=r['added_pixels'],
            additional_outside_reference_pixels=r['candidate_pixels_outside_reference']-r['baseline_pixels_outside_reference']))
    (folder/'visual_report.json').write_text(json.dumps(dict(status='diagnostic_boards_no_inferred_approval',boards=artifacts,producer_sha256=sha(Path(__file__))),indent=2),encoding='utf-8')
    print(json.dumps(artifacts))


if __name__=='__main__':main()
