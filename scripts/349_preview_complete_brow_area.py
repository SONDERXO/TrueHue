"""Full brow-exclusion repair on staged references; no parser/MST/tree fit."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.face_neck_support import FaceNeckSupport,apply_shared_parameters
from src.skin_masking.complete_brow_area import include_complete_brow_area
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.ita_estimation.semantic_measurement import contract


def main():
    parent=ROOT/'outputs/preferred_support_cohort_v2';out=ROOT/'outputs/complete_brow_area_v3'
    if out.exists():raise FileExistsError(out)
    allrows=json.loads((parent/'records.json').read_text());rows=[r for r in allrows if r['measurement']['status']=='success']
    identity=contract(ROOT)[1];out.mkdir();(out/'cases').mkdir()
    (out/'plan.json').write_text(json.dumps(dict(cases=[r['image_id'] for r in rows],
        rule='full_original_anatomical_brow_exclusion_skin_only_with_eye_veto',
        measurement_contract_sha256=identity,new_parser_inferences=0,model_fits=0,
        source_code_sha256=hashlib.sha256((ROOT/'src/skin_masking/complete_brow_area.py').read_bytes()).hexdigest()),indent=2))
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    records=[];cards=[]
    for row in rows:
        im=cv2.imread(str(ROOT/row['input_path']));face=cv2.imread(str(ROOT/row['mask_paths']['face']),0)
        neck=cv2.imread(str(ROOT/row['mask_paths']['neck']),0);old=cv2.imread(str(ROOT/row['mask_paths']['combined']),0)
        cats=cv2.imread(str(ROOT/Path(row['input_path']).parent/'categories.png'),0)
        box=row['measurement']['face_box']
        points,_,status=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        if points is None:raise ValueError(status)
        points=points+np.array(box[:2])
        assert np.array_equal(build_semantic_face_coverage(im,points,cats).mask,face)
        base=FaceNeckSupport(face,neck,old,{})
        result=include_complete_brow_area(im,base,cats,points)
        assert np.array_equal(result.measurement_mask,face)
        added=(result.correction_mask>0)&(old==0)
        overlay=im.copy();skin=(result.correction_mask>0)&np.isin(cats,[1,10])
        overlay[skin]=np.rint(.5*im[skin]+.5*np.array([0,255,0])).astype(np.uint8)
        overlay[neck>0]=np.rint(.5*im[neck>0]+.5*np.array([255,255,0])).astype(np.uint8)
        pigment=(result.correction_mask>0)&np.isin(cats,[2,3,12,13])
        overlay[pigment]=np.rint(.5*im[pigment]+.5*np.array([255,0,255])).astype(np.uint8)
        prior=apply_shared_parameters(im,base,.85,1.05,.95);after=apply_shared_parameters(im,result,.85,1.05,.95)
        assert np.array_equal(prior[~added],after[~added])
        folder=out/'cases'/Path(row['image_id']).stem;folder.mkdir()
        for name,array in [('correction_mask.png',result.correction_mask),('measurement_mask.png',face),
            ('overlay.png',overlay),('board.png',np.hstack((im,overlay,prior,after)))]:assert cv2.imwrite(str(folder/name),array)
        np.save(folder/'landmarks.npy',points)
        record=dict(image_id=row['image_id'],report=result.report,new_pixels_vs_v2=int(added.sum()),
                    board_path=(folder/'board.png').relative_to(out).as_posix(),measurement_unchanged=True,approved=False)
        records.append(record);cards.append('<h2>'+row['image_id']+'</h2><img src="'+record['board_path']+'">')
    assert contract(ROOT)[1]==identity
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    page='<!doctype html><meta charset="utf-8"><title>Full eyebrow-area correction coverage</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}</style><h1>Full eyebrow-area skin included in correction</h1><p>Original; current correction overlay (skin green, neck cyan, brows/lips pink); earlier operator output; updated operator output. Measurement mask remains separate and unchanged. Same fixed illustrative settings, not learned predictions. This replaces the narrow added band with eligible skin throughout the anatomical eyebrow exclusion.</p>'+''.join(cards)
    (out/'review.html').write_text(page,encoding='utf-8')
    result=dict(status='full_brow_area_candidate_complete',cases=len(records),
        cases_with_more_pixels_than_v2=sum(r['new_pixels_vs_v2']>0 for r in records),
        all_eligible_brow_skin_included=True,measurement_masks_unchanged=True,
        saved_parser_maps_reused=True,landmark_mask_replays=len(rows),new_model_fits=0,
        legacy_review_correction_support_superseded=True)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
