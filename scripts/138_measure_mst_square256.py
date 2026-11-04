"""Reprocess exactly the fixed reviewed MST-E development cohort at square256."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out=ROOT/'outputs/mst_square256_measurement_v1'
    if out.exists():raise FileExistsError(out)
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    table=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    with table.open(encoding='utf-8-sig',newline='') as f:rows=sorted(csv.DictReader(f),key=lambda r:r['image_id'])
    assert len(rows)==len({r['image_id'] for r in rows})==418
    assert all(r['historical_ita_use'].strip()=='include' and r['historical_quality_review'] in ['good','acceptable'] and r['metadata_matches']=='1' for r in rows)
    specification,identity=contract(ROOT)
    chosen=[r['image_id'] for r in sorted(rows,key=lambda r:hashlib.sha256(('seed42/'+r['image_id']).encode()).hexdigest())[:12]]
    tracked=[table,Path(__file__),ROOT/'docs/mst-square256-calibration-protocol.md']+[Path(r['image_path']) for r in rows]
    hashes={str(p):digest(p) for p in tracked}
    out.mkdir();(out/'masks').mkdir();(out/'boards').mkdir()
    (out/'contract.json').write_text(json.dumps(dict(contract=specification,measurement_contract_sha256=identity),indent=2))
    (out/'selection.json').write_text(json.dumps(dict(attempt_ids=[r['image_id'] for r in rows],diagnostic_ids=chosen,status='frozen_before_measurement'),indent=2))
    (out/'run_status.json').write_text('{"status":"running"}')
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def mask(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w].copy(),image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    records=[]
    for index,row in enumerate(rows,1):
        result=measure(cv2.imread(row['image_path'],cv2.IMREAD_COLOR),detector,mask)
        stem=row['image_id'].replace('/','_');saved_mask=None
        if result.mask is not None:
            saved_mask='masks/'+stem+'.png'
            if not cv2.imwrite(str(out/saved_mask),result.mask):raise OSError('Mask write failed')
        record=dict(image_id=row['image_id'],subject_id=row['subject_id'],source_mst_label=int(row['source_mst_label']),
            source_path=row['image_path'],historical_quality_review=row['historical_quality_review'],
            historical_ita=float(row['ita_degrees']),measurement_contract_sha256=identity,
            new_square_mask_review='not_human_reviewed',mask_path=saved_mask,**result.report)
        records.append(record)
        if row['image_id'] in chosen and result.image is not None:
            mask_pixels=np.zeros_like(result.image) if result.mask is None else cv2.cvtColor(result.mask,cv2.COLOR_GRAY2BGR)
            overlay=result.image.copy()
            if result.mask is not None:
                selected=result.mask>0;overlay[selected]=np.rint(.55*overlay[selected]+.45*np.array([0,220,0])).astype(np.uint8)
            panels=[]
            for title,pixels in [('Square256',result.image),('Measurement mask',mask_pixels),(result.report['status'],overlay)]:
                shown=cv2.copyMakeBorder(pixels,28,0,0,0,cv2.BORDER_CONSTANT)
                cv2.putText(shown,title,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.45,(255,255,255),1);panels.append(shown)
            if not cv2.imwrite(str(out/'boards'/(stem+'.png')),np.hstack(panels)):raise OSError('Board write failed')
        with (out/'records.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
        if index%20==0:print(f'Measured {index}/418',flush=True)
    assert all(digest(Path(p))==h for p,h in hashes.items())
    assert contract(ROOT)[1]==identity
    from collections import Counter
    summary=dict(status='complete_development_measurement_no_lookup',attempts=len(records),
        successes=sum(r['status']=='success' for r in records),failure_stages=dict(Counter(r['stage'] for r in records if r['status']!='success')),
        measurement_contract_sha256=identity,records=records,input_sha256=hashes,
        selected_diagnostic_ids=chosen,new_source_exposures=0,correction_fits=0,
        production_lookup_exported=False,limitations='Historically exposed/reviewed cohort; new square masks not human-approved; calibration-development only, not untouched evaluation.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'run_status.json').write_text('{"status":"complete"}')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['records','input_sha256','selected_diagnostic_ids']},indent=2))


if __name__=='__main__':main()
