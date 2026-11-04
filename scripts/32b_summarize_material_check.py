"""Compare identical successful cases; preserve material-check abstentions."""
import csv
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config


def read(path):
    with path.open(encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    base = ROOT/get_config().OUTPUTS_ROOT
    old = base/'guarded_correction_support_v1'; new = base/'material_checked_support_v1'
    destination = new/'common_cohort_comparison.json'
    if destination.exists(): raise FileExistsError('Summary exists; refusing overwrite')
    previous = {(r['image_id'],r['variant']):r for r in read(old/'broader_mask_diagnostics.csv')}
    current = {(r['image_id'],r['variant']):r for r in read(new/'broader_mask_diagnostics.csv')}
    summary = {}
    for variant in ('clean','color_shift'):
        keys = sorted(k for k in current if k[1]==variant and k in previous)
        values = {}
        for name,records,prefix in [('original',previous,'original'),('guarded',previous,'guarded'),('material_checked',current,'material_checked')]:
            values[name] = {suffix:float(np.mean([float(records[k][prefix+'_'+suffix]) for k in keys])) for suffix in ('coverage','extra_pixels','added_pixels')}
        summary[variant] = dict(common_cases=len(keys),methods=values)
    omitted = sorted(set(previous)-set(current))
    summary['additional_unavailable_cases'] = [dict(image_id=k[0],variant=k[1]) for k in omitted]
    summary['warning'] = 'Common-success comparison is conditional, not overall reliability or skin accuracy. See all 92 attempts and failures in summary.json.'
    destination.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    rows = []
    for name in ('fairface__train_16798.jpg','fairface__train_29962.jpg','fairface__val_10480.jpg'):
        before = cv2.imread(str(old/'broader'/(name+'__color_shift.png')))
        after = cv2.imread(str(new/'broader'/(name+'__color_shift.png')))
        if before is None or after is None: raise ValueError('Missing review sheet')
        # Original sheets have four 256x288 panels; use input and both final panels.
        panels = [before[:288,:256],before[288:,256:],after[288:,256:]]
        labels = ['Input: '+name,'Previous guarded additions','Color-checked additions']
        for panel,label in zip(panels,labels):
            panel[:32] = 0
            cv2.putText(panel,label,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.34,(0,255,255),1)
        rows.append(np.hstack(panels))
    if not cv2.imwrite(str(new/'material_review_board.png'),np.vstack(rows)): raise OSError('Review write failed')
    print(json.dumps(summary,indent=2))


if __name__=='__main__': main()
