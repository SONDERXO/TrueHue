"""Source-grouped side-by-side boards for the frozen parameter/mask diagnostic."""
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
    base=ROOT/get_config().OUTPUTS_ROOT/'mask_parameter_diagnosis_v1';boards=base/'review_boards'
    if boards.exists():raise FileExistsError('Diagnostic boards exist')
    boards.mkdir();table=ROOT/'data/manifests/controlled_training_v1';rows=[]
    for name in ('train.csv','development_validation.csv','clipped_stress.csv'):
        with (table/name).open(newline='',encoding='utf-8') as stream:rows+=list(csv.DictReader(stream))
    index=['# Mask versus parameter diagnosis','',
        'Columns: reference / input / tree with current mask / known parameters with current mask / known parameters with source mask (oracle).',
        '','Known parameters and source masks are diagnostic information unavailable to the deployed correction model.','']
    for source in sorted({r['source_image_id'] for r in rows}):
        selected=sorted([r for r in rows if r['source_image_id']==source],key=lambda r:('dark','bright_warm','color_shift').index(r['variant']))
        strips=[]
        for row in selected:
            pair=row['pair_id'];panels=[]
            paths=[Path(row['source_path']),ROOT/row['input_path']]+[base/'pairs'/(pair+'__'+method+'.png') for method in ('tree_current_mask','known_current_mask','known_source_mask_oracle')]
            for title,path in zip(('Reference','Input','Tree/current','Known/current','Known/source ORACLE'),paths):
                image=cv2.imread(str(path))
                if image is None:raise ValueError('Missing diagnostic image: '+str(path))
                panel=cv2.copyMakeBorder(cv2.resize(image,(224,224)),30,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(panel,title+' | '+row['variant'],(3,19),cv2.FONT_HERSHEY_SIMPLEX,.32,(0,255,255),1);panels.append(panel)
            strips.append(np.hstack(panels))
        name=source.replace('/','_')+'__diagnosis.png'
        if not cv2.imwrite(str(boards/name),np.vstack(strips)):raise OSError('Board write failed')
        index.append('- ['+source+'](review_boards/'+name+')')
    index += ['', 'Each pair also has a three-by-three factorial/mask comparison in `pairs/`.',
        'Scoring splits: training reconstruction / one-source development validation / nonindependent clipped stress.']
    (base/'review-index.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
    print(json.dumps(dict(source_boards=len({r['source_image_id'] for r in rows}),diagnosed_pairs=len(rows)),indent=2))


if __name__=='__main__':main()
