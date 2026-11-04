"""Bounded face/neck support demonstration, never a correction model trial."""
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.semantic_measurement import contract
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.face_neck_support import build_face_neck_support,apply_shared_parameters,FaceNeckSupport


def main():
    out=ROOT/'outputs/face_neck_support_v1'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    parents=read(ROOT/'outputs/semantic_face_coverage_v1/records.json')
    decisions=read(ROOT/'outputs/semantic_reference_mask_import_v1/decisions.json')
    accepted={r['case_id'] for r in decisions if r['mask_decision']=='accept'}
    cases=[]
    for r in parents:
        if r['case_id'] in accepted:
            cases.append(dict(case_id=r['case_id'],role='train',image_path=r['image_path'],
                source_sha256=r['source_sha256'],face_mask_path='outputs/semantic_face_coverage_v1/'+r['mask_path'],
                face_mask_sha256=r['mask_sha256'],category_path='outputs/semantic_face_coverage_v1/'+r['category_path'],
                category_sha256=r['category_sha256'],face_mask_approved=True))
    selected=set(read(ROOT/'outputs/semantic_mst_verification_v1/diagnostic_selection.json')['image_ids'])
    for r in read(ROOT/'outputs/semantic_mst_measurement_v1/summary.json')['records']:
        if r['image_id'] in selected:
            assert r['status']=='success' and r['face_count']==1
            cases.append(dict(case_id=r['image_id'].replace('/','_'),role='previously_exposed_mapping_development',
                image_path=r['source_path'],source_sha256=r['source_sha256'],
                face_mask_path='outputs/semantic_mst_measurement_v1/'+r['mask_path'],
                face_mask_sha256=r['mask_sha256'],category_path=None,face_mask_approved=False))
    assert len(cases)==21
    identity=contract(ROOT)[1];config=get_config()
    tracked=[Path(__file__),ROOT/'src/skin_masking/face_neck_support.py',
        ROOT/'src/distortion_generation/paper_gamma.py',ROOT/'docs/face-neck-support-protocol-2026-10-31.md',
        ROOT/'src/demo/service.py']
    hashes={str(p):digest(p) for p in tracked}
    for r in cases:
        assert digest(ROOT/r['image_path'])==r['source_sha256']
        assert digest(ROOT/r['face_mask_path'])==r['face_mask_sha256']
    out.mkdir();(out/'cases').mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='frozen_before_neck_inference',cases=cases,
        measurement_contract_sha256=identity,illustrative_parameters=[.85,1.05,.95],input_sha256=hashes,
        correction_tree_fits=0,calibration_fits=0,reserved_pixel_access=0),indent=2),encoding='utf-8')
    parser=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    records=[];cards=[]
    for r in cases:
        image=cv2.resize(cv2.imread(str(ROOT/r['image_path'])),(256,256),interpolation=cv2.INTER_LINEAR)
        face=cv2.imread(str(ROOT/r['face_mask_path']),0);before=face.copy()
        if r['category_path']:
            assert digest(ROOT/r['category_path'])==r['category_sha256']
            categories=cv2.imread(str(ROOT/r['category_path']),0)
        else:categories=parser.categories_bgr(image)
        support=build_face_neck_support(image,face,categories,face_count=1)
        assert np.array_equal(face,before) and np.array_equal(support.measurement_mask,before)
        assert compute_masked_lab_statistics(image,face,1000)==compute_masked_lab_statistics(image,support.measurement_mask,1000)
        result=apply_shared_parameters(image,support,.85,1.05,.95)
        faceonly=FaceNeckSupport(face,np.zeros_like(face),face,dict())
        facialresult=apply_shared_parameters(image,faceonly,.85,1.05,.95)
        assert np.array_equal(result[support.correction_mask==0],image[support.correction_mask==0])
        assert np.array_equal(apply_shared_parameters(image,support,1,1,1),image)
        assert np.array_equal(result[face>0],facialresult[face>0])
        folder=out/'cases'/r['case_id'];folder.mkdir()
        for name,array in [('input.png',image),('face_mask.png',face),('neck_mask.png',support.neck_mask),
                           ('combined_mask.png',support.correction_mask),('categories.png',categories),
                           ('face_only_operator_demo.png',facialresult),('face_neck_operator_demo.png',result)]:
            assert cv2.imwrite(str(folder/name),array)
        overlay=image.copy();overlay[face>0]=np.rint(.5*image[face>0]+.5*np.array([0,255,0])).astype(np.uint8)
        overlay[support.neck_mask>0]=np.rint(.5*image[support.neck_mask>0]+.5*np.array([255,255,0])).astype(np.uint8)
        board=np.hstack((image,overlay,facialresult,result));assert cv2.imwrite(str(folder/'board.png'),board)
        rec=dict(r,report=support.report,facial_statistics=compute_masked_lab_statistics(image,face,1000),
            neck_mask_sha256=digest(folder/'neck_mask.png'),board_path=(folder/'board.png').relative_to(out).as_posix(),
            neck_quality_approved=False,correction_model_used=False)
        records.append(rec)
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(
            image_path=r['image_path'],role=r['role'],phase='visible_neck_support_only'))+'\n')
        cards.append('<section><h2>'+html.escape(r['case_id'])+'</h2><p>'+html.escape(support.report['neck_status'])+
            ' · neck pixels: '+str(support.report['neck_pixels'])+'</p><img src="'+rec['board_path']+'"></section>')
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    summary=dict(status='support_candidate_complete_not_adopted',cases=len(records),
        neck_available=sum(r['report']['neck_pixels']>0 for r in records),
        neck_unavailable=sum(r['report']['neck_pixels']==0 for r in records),
        measurement_masks_and_statistics_unchanged=True,identity_and_outside_pixel_checks=21,
        reused_category_maps=6,new_category_inferences=15,new_neck_approvals=0,correction_tree_fits=0,
        parameters_source='fixed_illustrative_settings_not_model_predictions',measurement_contract_sha256=identity,
        demo_changed=False,reserved_pixel_access=0)
    (out/'verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    page='<!doctype html><meta charset="utf-8"><title>Face and neck support preview</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}section{border-top:1px solid #aaa;padding:15px}</style><h1>Face and visible neck: candidate support</h1><p>Panels: original; support (face green, neck cyan); face-only operator demonstration; face+neck operator demonstration. Both use the SAME fixed settings, not a trained model prediction. Neck availability is not quality approval. Face pixels alone supply ITA/MST. No new review is requested by this read-only page.</p>'+''.join(cards)
    (out/'review.html').write_text(page,encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
