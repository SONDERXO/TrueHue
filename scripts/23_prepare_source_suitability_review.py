"""Prepare current-mask/reference-quality evidence for 35 provisional sources."""
import importlib
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config


def main():
    common=importlib.import_module('16_compare_face_outline')
    prepare=importlib.import_module('11_prepare_training_manifests')
    checks=importlib.import_module('15_prepare_fairface_mask_review')
    csv_helper=importlib.import_module('21_synthetic_pair_pilot')
    path=ROOT/'data/manifests/source_preparation_v1/source_audit_and_partitions.csv'
    rows=sorted([r for r in common.read(path) if r['source_suitability']=='provisional_reviewed_candidate'],key=lambda r:r['image_id'])
    output=ROOT/'outputs/source_suitability_v1'
    if output.exists():
        raise FileExistsError('Review package exists')
    config=get_config()
    model=ROOT/config.FACE_LANDMARKER_MODEL_PATH
    yunet=ROOT/config.FACE_MODEL_PATH
    output.mkdir()
    tiles=[]; audit=[]
    for r in rows:
        image=cv2.imread(r['image_path'])
        boxes=prepare._detect_face_boxes(image,yunet,.85)
        if len(boxes)!=1:
            raise ValueError(r['image_id'])
        x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],model,'v2_complete_mouth_v1')
        stats=prepare.compute_masked_lab_statistics(crop,result.mask,1000)
        stats['skin_ratio_percent']=round(np.count_nonzero(result.mask)/(w*h)*100,2)
        if checks.measurement_differences(r,stats):
            raise ValueError('Stored versioned mask drift')
        tile=np.zeros((180,480,3),np.uint8)
        for i,panel in enumerate((image,crop,cv2.cvtColor(result.mask,cv2.COLOR_GRAY2BGR))):
            tile[20:,i*160:(i+1)*160]=cv2.resize(panel,(160,160),interpolation=cv2.INTER_NEAREST)
        cv2.putText(tile,r['image_id'],(3,14),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
        tiles.append(tile)
        dest=output/(r['image_id'].replace('/','_')+'.png')
        if not cv2.imwrite(str(dest),tile):
            raise OSError(dest)
        audit.append(dict(image_id=r['image_id'],partition=r['partition'],decision='pending',reason='',
            reviewer='Codex visual assessment',evidence=dest.relative_to(ROOT).as_posix()))
    for start in range(0,len(tiles),6):
        group=tiles[start:start+6]+[np.zeros_like(tiles[0])]*max(0,6-len(tiles[start:start+6]))
        cv2.imwrite(str(output/f'sheet_{start//6+1:02d}.png'),np.vstack([np.hstack(group[i:i+2]) for i in (0,2,4)]))
    csv_helper.write_csv(output/'review.csv',audit)
    print(f'{len(rows)} version-verified sources, original / face crop / current mask, six sheets.')


if __name__=='__main__':
    main()
