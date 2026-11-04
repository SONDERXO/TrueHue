"""Preview complete geometric face support, preserving calibrated masks."""
import argparse
import hashlib
import html
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.data_preparation.redesign_access import training_candidate
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.ita_estimation.square_measurement import contract


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--image',type=Path);parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args();config=get_config()
    out=args.output_dir or ROOT/config.OUTPUTS_ROOT/'anatomical_face_coverage_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(p):
        hashes[str(p.relative_to(ROOT))]=digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    _,contract_before=contract(ROOT)
    model=ROOT/config.FACE_LANDMARKER_MODEL_PATH
    cases=[]
    if args.image:
        cases=[dict(case_id='selected_photo',image_path=str(args.image.resolve()),baseline_path=None,
                    source_image_id='explicit_user_selected_photo',old_judgment=None)]
    else:
        allocation=read(ROOT/'outputs/correction_data_redesign_v1/selection.json')
        policy=read(ROOT/'outputs/correction_data_redesign_v1/access_policy.json')
        registry=read(ROOT/'outputs/reviewed_source_evidence32_v1/registry.json')
        references=[r for r in registry['rows'] if r['stratum']=='original_control' and r['evidence_origin'] in {'exact_three_source_review','exact_four_source_review'}]
        for r in references:
            cases.append(dict(case_id=Path(r['source_image_id']).stem+'_reference',image_path=r['input_path'],
                baseline_path=r['input_mask_path'],source_image_id=r['source_image_id'],old_judgment=r['exact_user_judgments']))
        export=read(ROOT/'outputs/additional_six_source_mask_review_v1/a.json')
        for r in read(ROOT/'outputs/additional_six_source_pairs_v1/primary_review_queue.json'):
            cases.append(dict(case_id=r['pair_id'],image_path=r['input_path'],baseline_path=r['input_mask_path'],
                source_image_id=r['source_image_id'],old_judgment=export['reviews'][r['pair_id']]))
        attempts_path=ROOT/'outputs/correction_training_preparation_v1/attempts.jsonl'
        hashes[str(attempts_path.relative_to(ROOT))]=digest(attempts_path)
        attempts={r['source_id']:r for r in map(json.loads,attempts_path.read_text().splitlines())}
        for sid in ['10567','61590','76067']:
            r=attempts[sid];folder=ROOT/'outputs/correction_training_preparation_v1/images'
            cases.append(dict(case_id=sid+'_occlusion_regression',image_path=(folder/f'{sid}_reference.png').relative_to(ROOT).as_posix(),
                baseline_path=(folder/f'{sid}_reference_mask.png').relative_to(ROOT).as_posix(),
                source_image_id=r['image_id'],old_judgment='Occlusion diagnostic only, not admission'))
        assert len(cases)==24
        for c in cases:training_candidate(c['source_image_id'],allocation,policy)
    for p in [Path(__file__),ROOT/'src/skin_masking/anatomical_face_coverage.py',model,
        ROOT/'src/skin_masking/face_outline_experiment.py',ROOT/'src/skin_masking/landmark_exclusion.py',
        ROOT/'src/skin_masking/mouth_exclusion.py']:
        hashes[str(p.relative_to(ROOT))]=digest(p)
    out.mkdir();(out/'masks').mkdir();(out/'boards').mkdir();records=[]
    (out/'plan.json').write_text(json.dumps(dict(status='fixed_before_preview',cases=cases,
        mask_version='anatomical_face_coverage_v1',input_sha256=hashes,
        role='coverage_development_only',current_measurement_contract_sha256=contract_before,
        no_ITA_MST_or_correction_calls=True),indent=2),encoding='utf-8')
    for case in cases:
        ip=Path(case['image_path']);ip=ip if ip.is_absolute() else ROOT/ip
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(dict(source_image_id=case['source_image_id'],image_path=str(ip),
                phase='user_requested_face_coverage_fix_preview',role='explicit_user_photo' if args.image else 'train'))+'\n')
        image=cv2.imread(str(ip));assert image is not None
        if args.image:image=cv2.resize(image,(config.IMAGE_SIZE,config.IMAGE_SIZE),interpolation=cv2.INTER_LINEAR)
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        record=dict(case,source_sha256=digest(ip),candidate_user_decision='not_requested',training_admitted=False)
        if len(boxes)!=1:
            record.update(status='unavailable',reason='Exactly one face required');records.append(record);continue
        box=boxes[0]
        points,margin,status=prepare.detect_landmarks_with_margin(image,box,model)
        if points is None:
            record.update(status='unavailable',reason=status);records.append(record);continue
        full_points=points+np.array(box[:2])
        try:result=build_face_coverage(image,full_points)
        except ValueError as error:
            record.update(status='unavailable',reason=str(error));records.append(record);continue
        baseline=np.zeros(image.shape[:2],np.uint8)
        if case['baseline_path']:
            bp=ROOT/case['baseline_path'];baseline=cv2.imread(str(bp),0);record['baseline_sha256']=digest(bp)
        sid=case['case_id'];mask_path=out/'masks'/f'{sid}.png';alpha_path=out/'masks'/f'{sid}_alpha.png'
        assert cv2.imwrite(str(mask_path),result.mask) and cv2.imwrite(str(alpha_path),result.alpha)
        np.save(out/'masks'/f'{sid}_landmarks.npy',full_points)
        panels=[]
        for title,alpha in [('Input',np.zeros(image.shape[:2],float)),('Existing mask',.5*(baseline>0)),
                ('New geometric coverage',.5*result.alpha/255),('New binary mask',None)]:
            shown=cv2.cvtColor(result.mask,cv2.COLOR_GRAY2BGR) if alpha is None else np.rint(image*(1-alpha[:,:,None])+np.array([0,255,0])*alpha[:,:,None]).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,24,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,title,(4,17),cv2.FONT_HERSHEY_SIMPLEX,.43,(255,255,255),1);panels.append(shown)
        board=out/'boards'/f'{sid}.png';assert cv2.imwrite(str(board),np.hstack(panels))
        selected=result.mask>0;old=baseline>0;exclusions=result.exclusion_mask>0;outline=result.face_outline>0
        record.update(status='candidate_available_requires_occlusion_review',landmark_margin=margin,face_box=list(map(int,box)),
            report=result.report,added_pixels=int((selected&~old).sum()),removed_pixels=int((old&~selected).sum()),
            old_selected_outside_outline=int((old&~outline).sum()),new_selected_outside_outline=int((selected&~outline).sum()),
            new_selected_in_exclusions=int((selected&exclusions).sum()),mask_path=mask_path.relative_to(out).as_posix(),
            mask_sha256=digest(mask_path),board_path=board.relative_to(out).as_posix())
        assert not (selected&(~outline|exclusions)).any()
        records.append(record);print(sid,record['added_pixels'],record['removed_pixels'],flush=True)
    assert contract(ROOT)[1]==contract_before
    assert all(digest(Path(p) if Path(p).is_absolute() else ROOT/p)==sha for p,sha in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    sections=[]
    for r in records:
        detail=html.escape(json.dumps(r['old_judgment'],ensure_ascii=False))
        sections.append('<section><h2>'+html.escape(r['case_id'])+'</h2><p>Old judgment: '+detail+'</p>'+
            ('<img loading="lazy" src="'+r['board_path']+'"><p>Added '+str(r['added_pixels'])+' pixels; removed '+str(r['removed_pixels'])+'. These counts are not skin accuracy.</p>' if 'board_path' in r else '<p>'+html.escape(r['reason'])+'</p>')+'</section>')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Face coverage repair</title>'
        '<style>body{font:17px system-ui;background:#151923;color:#eee;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}section{border-top:1px solid #777;margin:25px 0}</style>'
        '<h1>Face coverage repair preview</h1><p>Full-face outline with eyes, brows and outer mouth excluded. '
        'The candidate fills facial surface independently of color thresholds and is not clipped to the detector box. '
        'Hair, glasses and objects inside that outline are not reliably identified by geometry. '
        'No candidate mask is automatically approved or used for ITA/MST or correction.</p>'+''.join(sections),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(dict(cases=len(records),available=sum('mask_path' in r for r in records),
        measurement_contract_unchanged=True,model_fits=0,ITA_MST_calls=0,existing_masks_replaced=0,
        limitation='Geometric face surface is not automatic non-skin occlusion segmentation.'),indent=2),encoding='utf-8')


if __name__=='__main__':main()
