"""Matched-cohort diagnostics and compact before/after hair-filter review board."""
import csv
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config


def main():
    folder=ROOT/get_config().OUTPUTS_ROOT/'semantic_support_channels_v1'
    destination=folder/'matched_cohort_summary.json'
    if destination.exists(): raise FileExistsError('Summary already exists')
    with (folder/'broader_mask_diagnostics.csv').open(newline='',encoding='utf-8') as stream:rows=list(csv.DictReader(stream))
    methods=('original','material_checked','semantic_face_skin','semantic_hair_veto')
    result={}
    for variant in ('clean','color_shift'):
        selected=[r for r in rows if r['variant']==variant and all(r[m+'_available']=='True' for m in methods)]
        result[variant]=dict(common_inputs=len(selected),means={m:{k:float(np.mean([float(r[m+'_'+k]) for r in selected])) for k in ('coverage','extra_pixels')} for m in methods})
    result['warning']='Matched-success mask diagnostics only; generation-region overlap is not ground-truth skin accuracy, and excluded inputs remain in the availability ledger.'
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
    board=[]
    for key in ('fairface__train_29962.jpg__clean','fairface__val_10480.jpg__clean','fairface__train_16798.jpg__color_shift'):
        image=cv2.imread(str(folder/'broader'/(key+'.png')))
        if image is None or image.shape[:2]!=(576,768):raise ValueError('Unexpected comparison sheet')
        # Native grid: input/original/material above face-skin/hair-veto/categories.
        panels=[image[:288,:256].copy(),image[:288,512:768].copy(),image[288:,256:512].copy()]
        for panel,title in zip(panels,('Input: '+key,'Previous color-checked support','With semantic hair veto')):
            panel[:32]=0;cv2.putText(panel,title,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.34,(0,255,255),1)
        board.append(np.hstack(panels))
    if not cv2.imwrite(str(folder/'hair_filter_review_board.png'),np.vstack(board)):raise OSError('Review-board write failed')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
