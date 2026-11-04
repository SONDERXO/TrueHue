"""Run the explicitly authorized existing parser with complete-face support."""
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage


def main():
    config=get_config();base=ROOT/config.OUTPUTS_ROOT
    parent=base/'anatomical_face_coverage_v1';out=base/'semantic_face_coverage_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    records=read(parent/'records.json');assert len(records)==24
    model=ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx'
    assert digest(model)==read(model.with_suffix('.provenance.json'))['sha256']=='0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f'
    _,old_contract=contract(ROOT)
    dependencies=[Path(__file__),model,model.with_suffix('.provenance.json'),parent/'records.json',
        ROOT/'src/skin_masking/semantic_face_coverage.py',ROOT/'src/skin_masking/anatomical_face_coverage.py',
        ROOT/'src/skin_masking/face_parsing_experiment.py',ROOT/'src/skin_masking/face_outline_experiment.py',
        ROOT/'src/skin_masking/landmark_exclusion.py',ROOT/'src/skin_masking/mouth_exclusion.py']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in dependencies}
    out.mkdir()
    for name in ['categories','masks','boards']:(out/name).mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='frozen_before_parser_inference',cases=[r['case_id'] for r in records],
        input_sha256=hashes,old_measurement_contract_sha256=old_contract,
        user_authorization='Allow the existing parser for masking',
        new_method='19class_skin_nose_components_associated_with_selected_face_plus_anatomical_exclusions',
        ITA_MST_calls=0,correction_fits=0,old_mask_approvals_transferred=False),indent=2),encoding='utf-8')
    parser=DenseFaceParser(model);output=[]
    for old in records:
        sid=old['case_id'];ip=ROOT/old['image_path'];bp=ROOT/old['baseline_path']
        assert digest(ip)==old['source_sha256'] and digest(bp)==old['baseline_sha256']
        landmarks_path=parent/'masks'/f'{sid}_landmarks.npy'
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(dict(source_image_id=old['source_image_id'],role='train',image_path=old['image_path'],
                phase='user_authorized_existing_parser_face_mask_repair'))+'\n')
        image=cv2.imread(str(ip));baseline=cv2.imread(str(bp),0);points=np.load(landmarks_path)
        categories=parser.categories_bgr(image)
        category_path=out/'categories'/f'{sid}.png';assert cv2.imwrite(str(category_path),categories)
        r=dict(case_id=sid,source_image_id=old['source_image_id'],image_path=old['image_path'],
            source_sha256=digest(ip),baseline_path=old['baseline_path'],baseline_sha256=digest(bp),
            landmarks_path=landmarks_path.relative_to(ROOT).as_posix(),landmarks_sha256=digest(landmarks_path),
            category_path=category_path.relative_to(out).as_posix(),category_sha256=digest(category_path),
            old_judgment=old['old_judgment'],candidate_approved=False,training_admitted=False)
        try:result=build_semantic_face_coverage(image,points,categories)
        except ValueError as error:
            r.update(status='unavailable',reason=str(error));output.append(r);continue
        for suffix,mask in [('',result.mask),('_alpha',result.alpha),('_exclusions',result.exclusion_mask)]:
            assert cv2.imwrite(str(out/'masks'/f'{sid}{suffix}.png'),mask)
        mask_path=out/'masks'/f'{sid}.png';alpha_path=out/'masks'/f'{sid}_alpha.png'
        panels=[]
        for title,alpha in [('Input',np.zeros(image.shape[:2],float)),('Existing color mask',.5*(baseline>0)),
                ('Repaired face mask',.5*result.alpha/255),('New binary mask',None)]:
            shown=cv2.cvtColor(result.mask,cv2.COLOR_GRAY2BGR) if alpha is None else np.rint(image*(1-alpha[:,:,None])+np.array([0,255,0])*alpha[:,:,None]).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,24,0,0,0,cv2.BORDER_CONSTANT)
            cv2.putText(shown,title,(4,17),cv2.FONT_HERSHEY_SIMPLEX,.43,(255,255,255),1);panels.append(shown)
        board=out/'boards'/f'{sid}.png';assert cv2.imwrite(str(board),np.hstack(panels))
        selected=result.mask>0;before=baseline>0
        r.update(status='candidate_available',report=result.report,mask_path=mask_path.relative_to(out).as_posix(),
            mask_sha256=digest(mask_path),alpha_sha256=digest(alpha_path),board_path=board.relative_to(out).as_posix(),
            added_pixels=int((selected&~before).sum()),removed_pixels=int((before&~selected).sum()))
        output.append(r);print(sid,r['added_pixels'],r['removed_pixels'],flush=True)
    assert contract(ROOT)[1]==old_contract
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    (out/'records.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    sections=[]
    for r in output:
        sections.append('<section><h2>'+html.escape(r['case_id'])+'</h2><p>Previous exact-mask judgment: '+
            html.escape(json.dumps(r['old_judgment'],ensure_ascii=False))+'</p>'+
            ('<img loading="lazy" src="'+r['board_path']+'">' if 'board_path' in r else '<p>'+html.escape(r['reason'])+'</p>')+'</section>')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Repaired face-mask coverage</title>'
        '<style>body{font:17px system-ui;background:#151923;color:#eee;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}section{border-top:1px solid #777;margin:25px 0}</style>'
        '<h1>Repaired face-mask coverage</h1><p>Existing local face parser, with explicit eye/brow/mouth exclusions. '
        'Forehead and chin may extend beyond the old detector box; hair, glasses, ears, neck and background parser classes are excluded. '
        'Parser errors, facial hair and paint remain possible. Previous approvals apply only to previous masks. '
        'This new mask is not yet used for ITA/MST, training or the demo.</p>'+''.join(sections),encoding='utf-8')
    summary=dict(cases=len(output),available=sum(r['status']=='candidate_available' for r in output),
        old_measurement_contract_unchanged=True,correction_fits=0,ITA_MST_calls=0,existing_masks_replaced=0,
        new_mask_approvals=0,parser_hash=digest(model),
        methodology_change='User-authorized semantic segmentation plus anatomical rules; not the old rule-only mask.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
