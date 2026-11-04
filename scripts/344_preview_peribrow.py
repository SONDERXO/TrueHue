"""Fixed saved-pixel comparison of additional peribrow skin; no fitting."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport,apply_shared_parameters
from src.skin_masking.correction_facial_features import include_brows_lips
from src.skin_masking.peribrow_correction import include_features_and_peribrow
from src.ita_estimation.semantic_measurement import contract


def main():
    parent=ROOT/'outputs/face_neck_support_v1';out=ROOT/'outputs/peribrow_support_v2'
    if out.exists():raise FileExistsError(out)
    rows=json.loads((parent/'records.json').read_text());identity=contract(ROOT)[1]
    out.mkdir();(out/'cases').mkdir();records=[];sections=[]
    (out/'plan.json').write_text(json.dumps(dict(cases=[r['case_id'] for r in rows],
        radius_rule='ceil_face_width_times_0.02',allowed_added_classes=[1,10],
        correction_code_sha256=hashlib.sha256((ROOT/'src/skin_masking/peribrow_correction.py').read_bytes()).hexdigest(),
        parameters=[.85,1.05,.95],measurement_contract_sha256=identity,new_inferences=0,model_fits=0),indent=2))
    for row in rows:
        folder=parent/Path(row['board_path']).parent
        im=cv2.imread(str(folder/'input.png'));face=cv2.imread(str(folder/'face_mask.png'),0)
        neck=cv2.imread(str(folder/'neck_mask.png'),0);combined=cv2.imread(str(folder/'combined_mask.png'),0)
        cats=cv2.imread(str(folder/'categories.png'),0);base=FaceNeckSupport(face,neck,combined,{})
        old=include_brows_lips(base,cats);new=include_features_and_peribrow(base,cats)
        added=(new.correction_mask>0)&(old.correction_mask==0)
        assert np.array_equal(new.measurement_mask,face)
        assert not added[~np.isin(cats,[1,10])].any()
        a=apply_shared_parameters(im,old,.85,1.05,.95);b=apply_shared_parameters(im,new,.85,1.05,.95)
        assert np.array_equal(a[~added],b[~added])
        overlay=im.copy();overlay[added]=np.rint(.5*im[added]+.5*np.array([0,255,255])).astype(np.uint8)
        target=out/'cases'/row['case_id'];target.mkdir()
        for name,arr in [('added.png',added.astype(np.uint8)*255),('correction_mask.png',new.correction_mask),
            ('measurement_mask.png',new.measurement_mask),('board.png',np.hstack((im,overlay,a,b)))]:assert cv2.imwrite(str(target/name),arr)
        records.append(dict(case_id=row['case_id'],added_pixels=int(added.sum()),report=new.report))
        sections.append('<h2>'+row['case_id']+'</h2><img src="cases/'+row['case_id']+'/board.png">')
    assert contract(ROOT)[1]==identity
    (out/'records.json').write_text(json.dumps(records,indent=2))
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Skin around eyebrows</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}</style><h1>Include skin around the eyebrows</h1><p>Original; new correction pixels in yellow; previous support; new support. Same illustrative settings, not model predictions. Facial measurement mask stays unchanged; only nearby predicted skin is added.</p>'+''.join(sections),encoding='utf-8')
    result=dict(cases=len(records),cases_with_additions=sum(r['added_pixels']>0 for r in records),
        total_added_pixels=sum(r['added_pixels'] for r in records),measurement_masks_unchanged=True,
        output_changes_confined_to_added_skin=True,new_parser_inferences=0,model_fits=0,
        earlier_preferred_support_data_superseded_for_future_fitting=True)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
