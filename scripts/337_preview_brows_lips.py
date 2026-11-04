"""One correction-support comparison on saved pixels; no model inference/fits."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_neck_support import FaceNeckSupport,apply_shared_parameters
from src.skin_masking.correction_facial_features import include_brows_lips
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.semantic_measurement import contract


def main():
    parent=ROOT/'outputs/face_neck_support_v1';out=ROOT/'outputs/brows_lips_correction_v1'
    if out.exists():raise FileExistsError(out)
    rows=json.loads((parent/'records.json').read_text());assert len(rows)==21
    identity=contract(ROOT)[1];digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    paths=[parent/'records.json',ROOT/'src/skin_masking/correction_facial_features.py',Path(__file__),
        ROOT/'docs/brows-lips-correction-experiment-protocol.md']
    for row in rows:
        folder=parent/Path(row['board_path']).parent
        paths.extend(folder/name for name in ['input.png','face_mask.png','neck_mask.png','combined_mask.png','categories.png'])
    hashes={str(p):digest(p) for p in paths}
    out.mkdir();(out/'cases').mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='fixed_before_comparison',cases=[r['case_id'] for r in rows],
        input_sha256=hashes,parameters=[.85,1.05,.95],measurement_contract_sha256=identity,
        model_fits=0,new_parser_inferences=0),indent=2),encoding='utf-8')
    records=[];cards=[]
    for row in rows:
        folder=parent/Path(row['board_path']).parent
        image=cv2.imread(str(folder/'input.png'));face=cv2.imread(str(folder/'face_mask.png'),0)
        neck=cv2.imread(str(folder/'neck_mask.png'),0);combined=cv2.imread(str(folder/'combined_mask.png'),0)
        cats=cv2.imread(str(folder/'categories.png'),0)
        base=FaceNeckSupport(face,neck,combined,row['report']);candidate=include_brows_lips(base,cats)
        additions=(candidate.correction_mask>0)&(combined==0)
        baseline=apply_shared_parameters(image,base,.85,1.05,.95)
        result=apply_shared_parameters(image,candidate,.85,1.05,.95)
        assert np.array_equal(result[~additions],baseline[~additions])
        assert np.array_equal(face,candidate.measurement_mask)
        assert compute_masked_lab_statistics(image,face,1000)==row['facial_statistics']
        assert not additions[np.isin(cats,[4,5,6,11,17])].any()
        assert np.array_equal(apply_shared_parameters(image,candidate,1,1,1),image)
        overlay=image.copy();overlay[additions]=np.rint(.5*image[additions]+.5*np.array([255,0,255])).astype(np.uint8)
        target=out/'cases'/row['case_id'];target.mkdir()
        for name,array in [('additions.png',additions.astype(np.uint8)*255),('correction_mask.png',candidate.correction_mask),
            ('measurement_mask.png',candidate.measurement_mask),('baseline.png',baseline),('experiment.png',result),
            ('board.png',np.hstack((image,overlay,baseline,result)))]:assert cv2.imwrite(str(target/name),array)
        rec=dict(case_id=row['case_id'],report=candidate.report,added_pixels=int(additions.sum()),
            changed_pixels_relative_to_baseline=int(np.any(result!=baseline,axis=2).sum()),
            board_path=(target/'board.png').relative_to(out).as_posix(),quality_approved=False)
        records.append(rec)
        cards.append('<section><h2>'+html.escape(row['case_id'])+'</h2><p>Added pixels: '+str(rec['added_pixels'])+'</p><img src="'+rec['board_path']+'"></section>')
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    page='<!doctype html><meta charset="utf-8"><title>Correction-only eyebrows and lips</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}section{border-top:1px solid #aaa;padding-top:15px}</style><h1>Eyebrows and lips: correction-only experiment</h1><p>Panels: original; added pixels in pink; existing face+neck operator demo; same settings including eyebrows/lips. Settings are fixed illustrations, not trained-model predictions. Eyes and mouth-interior classes are not added. ITA/MST measurement pixels stay unchanged. Lip and brow colors may become less natural; parser errors remain.</p>'+''.join(cards)
    (out/'review.html').write_text(page,encoding='utf-8')
    summary=dict(status='experiment_complete_not_adopted',cases=21,
        cases_with_brow_additions=sum(r['report']['correction_only_brow_pixels']>0 for r in records),
        cases_with_lip_additions=sum(r['report']['correction_only_lip_pixels']>0 for r in records),
        measurement_masks_and_ITA_unchanged=True,output_outside_additions_matches_baseline=True,
        excluded_predicted_eye_mouth_glasses_hair_classes_not_added=True,new_parser_inferences=0,model_fits=0,
        measurement_contract_sha256=identity,demo_changed=False,new_approvals=0)
    (out/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
