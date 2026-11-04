"""Prepare original-only face crops for the preselected12diagnostic frames."""
import cv2
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/mst_region_quality_v1'
    if out.exists():raise FileExistsError(out)
    source=ROOT/'outputs/mst_square256_measurement_v1'
    summary=json.loads((source/'summary.json').read_text());selected=json.loads((source/'selection.json').read_text())['diagnostic_ids']
    rows={r['image_id']:r for r in summary['records']};out.mkdir();(out/'original_crops').mkdir()
    records=[];tiles=[]
    for index,image_id in enumerate(selected):
        row=rows[image_id];image=cv2.resize(cv2.imread(row['source_path']),(256,256),interpolation=cv2.INTER_LINEAR)
        x,y,w,h=row['face_box'];crop=image[y:y+h,x:x+w]
        filename=f'{index:02d}.png';assert cv2.imwrite(str(out/'original_crops'/filename),cv2.resize(crop,(384,384),interpolation=cv2.INTER_NEAREST))
        shown=cv2.resize(crop,(256,256));shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,f'{index:02d} '+image_id.split('/')[0],(2,19),cv2.FONT_HERSHEY_SIMPLEX,.38,(255,255,255),1);tiles.append(shown)
        records.append(dict(index=index,image_id=image_id,source_path=row['source_path'],face_box=row['face_box'],
            original_sha256=hashlib.sha256(Path(row['source_path']).read_bytes()).hexdigest(),mask_path=str((source/row['mask_path']).relative_to(ROOT)),
            mask_sha256=hashlib.sha256((source/row['mask_path']).read_bytes()).hexdigest()))
    assert cv2.imwrite(str(out/'original_contact.png'),cv2.vconcat([cv2.hconcat(tiles[i:i+3]) for i in range(0,12,3)]))
    (out/'inspection_manifest.json').write_text(json.dumps(dict(status='original_only_before_reference_points',records=records),indent=2))
    print('Prepared12original-only face crops; no point labels or measurements generated.')


if __name__=='__main__':main()
