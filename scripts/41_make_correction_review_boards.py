"""Group the integrated correction outputs by source for visual inspection."""
import csv
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.correction.correct_image import LEGACY_POLICY,MATERIAL_HAIR_POLICY


def main():
    output=ROOT/get_config().OUTPUTS_ROOT/'integrated_correction_v1';boards=output/'review_boards'
    if boards.exists():raise FileExistsError('Review boards exist; refusing overwrite')
    boards.mkdir();rows=[];table=ROOT/'data/manifests/controlled_training_v1'
    for name in ('train.csv','development_validation.csv','clipped_stress.csv'):
        with (table/name).open(newline='',encoding='utf-8') as stream:rows+=list(csv.DictReader(stream))
    gallery=['# Integrated correction review','',
        'Rows: dark, bright/warm, color shift when available. Columns: reference, input, legacy correction, material + hair veto.',
        '','These are the same small development/training/stress examples; no new independent evaluation.','']
    for source in sorted({r['source_image_id'] for r in rows}):
        selected=sorted([r for r in rows if r['source_image_id']==source],key=lambda r:('dark','bright_warm','color_shift').index(r['variant']))
        strips=[]
        for row in selected:
            pair=row['pair_id'];panels=[]
            paths=[Path(row['source_path']),ROOT/row['input_path'],
                output/'pairs'/pair/LEGACY_POLICY/'corrected.png',output/'pairs'/pair/MATERIAL_HAIR_POLICY/'corrected.png']
            for title,path in zip(('Reference','Input','Legacy','Material + hair veto'),paths):
                image=cv2.imread(str(path))
                if image is None:raise ValueError('Missing board image: '+str(path))
                image=cv2.copyMakeBorder(cv2.resize(image,(224,224)),30,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(image,title+' | '+row['variant'],(3,19),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,255,255),1);panels.append(image)
            strips.append(np.hstack(panels))
        filename=source.replace('/','_')+'__review.png'
        if not cv2.imwrite(str(boards/filename),np.vstack(strips)):raise OSError('Board write failed')
        gallery.append('- ['+source+'](review_boards/'+filename+')')
    gallery += ['', 'Supplemental point-review inputs (mask-regression checks; no ideal correction target):','',
        '- [Paint example](points/fairface__train_16798.jpg__color_shift/comparison.png)',
        '- [Hair example](points/fairface__train_29962.jpg__clean/comparison.png)']
    (output/'review-index.md').write_text('\n'.join(gallery)+'\n',encoding='utf-8')
    print(json.dumps(dict(source_boards=len({r['source_image_id'] for r in rows}),corrected_pairs=len(rows),index=str(output/'review-index.md')),indent=2))


if __name__=='__main__':main()
