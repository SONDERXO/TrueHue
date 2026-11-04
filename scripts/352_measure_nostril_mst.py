"""One actual418-image pass, retaining all exclusion evidence and failures."""
import csv
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import contract,measure
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard


def main():
    out=ROOT/'outputs/nostril_mst_measurement_v4'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    table=ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv'
    with table.open(encoding='utf-8-sig',newline='') as f:rows=sorted(csv.DictReader(f),key=lambda r:r['image_id'])
    assert len(rows)==len({r['image_id'] for r in rows})==418
    assert all(r['historical_ita_use'].strip()=='include' and r['metadata_matches']=='1' for r in rows)
    old=json.loads((ROOT/'outputs/semantic_mst_measurement_v1/summary.json').read_text())
    assert {r['image_id'] for r in rows}=={r['image_id'] for r in old['records']}
    spec,identity=contract(ROOT)
    paths=[Path(__file__),table,ROOT/'docs/nostril-mst-single-cycle-protocol-2026-11-01.md',
           ROOT/'src/demo/service.py',ROOT/'src/correction/seamless_blend.py']+[Path(r['image_path']) for r in rows]
    hashes={str(p):digest(p) for p in paths}
    for p,h in spec['parent_contract']['dependency_sha256'].items():assert digest(ROOT/p)==h
    selected=set(json.loads((ROOT/'outputs/semantic_mst_verification_v1/diagnostic_selection.json').read_text())['image_ids'])
    out.mkdir()
    for name in ['masks','categories','landmarks','nostril_guards','boards']:(out/name).mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='frozen_before_measurement',contract=spec,
        measurement_contract_sha256=identity,image_ids=[r['image_id'] for r in rows],
        diagnostic_ids=sorted(selected),input_sha256=hashes,role='previously_exposed_mapping_development',
        reserved_pixel_access=0,correction_tree_fits=0,old_lookup_used=False),indent=2))
    prepare=importlib.import_module('11_prepare_training_manifests');config=get_config();cache={}
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def landmarks(im,box):
        points,_,_=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        cache['points']=None if points is None else points+np.array(box[:2]);return cache['points']
    class Parser:
        def __init__(self):self.net=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx');self.last=None
        def categories_bgr(self,im):self.last=self.net.categories_bgr(im);return self.last
    parser=Parser();records=[]
    for index,row in enumerate(rows,1):
        parser.last=None;cache.clear()
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(
            image_id=row['image_id'],subject_id=row['subject_id'],role='previously_exposed_mapping_development',phase='frozen_nostril_excluded_measurement'))+'\n')
        result=measure(cv2.imread(row['image_path']),detector,landmarks,parser)
        sid=row['image_id'].replace('/','_')
        record=dict(image_id=row['image_id'],subject_id=row['subject_id'],source_path=row['image_path'],
            source_mst_label=int(row['source_mst_label']),lighting=row['source_lighting'],source_sha256=hashes[str(Path(row['image_path']))],
            measurement_contract_sha256=identity,**result.report)
        # report already contains mask_review; use one explicit status, never approvals.
        if parser.last is not None:
            cp=out/'categories'/(sid+'.png');assert cv2.imwrite(str(cp),parser.last)
            record.update(category_path=cp.relative_to(out).as_posix(),category_sha256=digest(cp))
        if cache.get('points') is not None:
            lp=out/'landmarks'/(sid+'.npy');np.save(lp,cache['points'])
            record.update(landmarks_path=lp.relative_to(out).as_posix(),landmarks_sha256=digest(lp))
        if result.mask is not None:
            mp=out/'masks'/(sid+'.png');assert cv2.imwrite(str(mp),result.mask)
            record.update(mask_path=mp.relative_to(out).as_posix(),mask_sha256=digest(mp))
        if record['status']=='success':
            selected_pixels=result.mask>0;geometry=build_face_coverage(result.image,cache['points'])
            guard=nostril_guard(result.mask.shape,cache['points'])
            checks=dict(selected_forbidden_parser_pixels=int((selected_pixels&~np.isin(parser.last,[1,10])).sum()),
                selected_anatomical_exclusion_pixels=int((selected_pixels&(geometry.exclusion_mask>0)).sum()),
                selected_nostril_guard_pixels=int((selected_pixels&guard).sum()))
            assert all(v==0 for v in checks.values());record['exclusion_checks']=checks
            gp=out/'nostril_guards'/(sid+'.png');assert cv2.imwrite(str(gp),guard.astype(np.uint8)*255)
            record.update(nostril_guard_path=gp.relative_to(out).as_posix(),nostril_guard_sha256=digest(gp))
        if row['image_id'] in selected and result.image is not None:
            mask=result.mask if result.mask is not None else np.zeros((256,256),np.uint8)
            shown=result.image.copy();chosen=mask>0;shown[chosen]=np.rint(.5*shown[chosen]+.5*np.array([0,255,0])).astype(np.uint8)
            bp=out/'boards'/(sid+'.png');assert cv2.imwrite(str(bp),np.hstack((result.image,shown,cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR))))
            record['board_path']=bp.relative_to(out).as_posix()
        records.append(record)
        with (out/'records.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
        if index%25==0 or index==len(rows):print(f'{index}/418; {sum(r["status"]=="success" for r in records)} available',flush=True)
    assert contract(ROOT)[1]==identity and all(digest(p)==h for p,h in hashes.items())
    summary=dict(status='complete_unreviewed_nostril_excluded_measurements',records=records,attempts=418,
        successes=sum(r['status']=='success' for r in records),failure_stages=dict(Counter(r['stage'] for r in records if r['status']!='success')),
        measurement_contract_sha256=identity,input_sha256=hashes,new_mask_approvals=0,correction_tree_fits=0)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['records','input_sha256']},indent=2))


if __name__=='__main__':main()
