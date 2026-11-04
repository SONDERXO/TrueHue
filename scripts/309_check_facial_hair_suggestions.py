"""One fixed auxiliary check on exposed beard examples and clean controls."""
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
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.facial_hair_exclusion import FacialHairAuxiliary,lower_face_suggestion,apply_exclusions


def main():
    config=get_config();base=ROOT/config.OUTPUTS_ROOT;out=base/'facial_hair_suggestions_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    sources=['61590','75287','9654','36658','81108','72939','2434','25517','39083','63509','42965','77101']
    allocation=read(base/'correction_data_redesign_v1/selection.json');policy=read(base/'correction_data_redesign_v1/access_policy.json')
    attempts={r['source_id']:r for r in map(json.loads,(base/'correction_training_preparation_v1/attempts.jsonl').read_text().splitlines())}
    for sid in sources:training_candidate(attempts[sid]['image_id'],allocation,policy)
    cache={r['case_id'].split('_')[0]:r for r in read(base/'semantic_face_coverage_v1/records.json') if r['case_id'].endswith('_reference') or r['case_id'].endswith('_occlusion_regression')}
    model=ROOT/config.MODELS_ROOT/'facial_hair_auxiliary_v1/fcn_mobilenetv2_fp.onnx'
    auxiliary=FacialHairAuxiliary(model);primary=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    prepare=importlib.import_module('11_prepare_training_manifests')
    out.mkdir()
    for name in ['masks','categories','boards']:(out/name).mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='fixed_before_inference',source_ids=sources,
        groups='first6 visible-facial-hair development examples; last6 previously reviewed reference controls',
        rule='Only preferred skin below primary-parser nose bottom where auxiliary predicts background',
        automatically_apply=False,model_sha256=digest(model),parameter_sweep=False),indent=2),encoding='utf-8')
    records=[]
    for sid in sources:
        image_path=base/'correction_training_preparation_v1/images'/f'{sid}_reference.png'
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(dict(image_id=attempts[sid]['image_id'],role='train',image_path=str(image_path),phase='facial_hair_auxiliary_development_check'))+'\n')
        image=cv2.imread(str(image_path))
        if sid in cache:
            old=cache[sid];preferred=cv2.imread(str(base/'semantic_face_coverage_v1'/old['mask_path']),0)
            cats=cv2.imread(str(base/'semantic_face_coverage_v1'/old['category_path']),0)
        else:
            boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85);assert len(boxes)==1
            points,_,_=prepare.detect_landmarks_with_margin(image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH);assert points is not None
            cats=primary.categories_bgr(image)
            preferred=build_semantic_face_coverage(image,points+np.array(boxes[0][:2]),cats).mask
        aux=auxiliary.categories_bgr(image);veto,report=lower_face_suggestion(preferred,cats,aux)
        candidate,alpha=apply_exclusions(preferred,veto)
        for suffix,array in [('_preferred',preferred),('_suggestion',veto.astype(np.uint8)*255),('_candidate',candidate),('_alpha',alpha)]:
            assert cv2.imwrite(str(out/'masks'/f'{sid}{suffix}.png'),array)
        assert cv2.imwrite(str(out/'categories'/f'{sid}_primary.png'),cats)
        assert cv2.imwrite(str(out/'categories'/f'{sid}_auxiliary.png'),aux)
        panels=[]
        for title,mask in [('Photo',None),('Preferred full mask',preferred),('Suggestion (red)',veto),('If applied',candidate)]:
            shown=image.copy()
            if mask is not None:
                selected=mask>0;color=np.array([0,0,255] if title=='Suggestion (red)' else [0,255,0])
                shown[selected]=np.rint(.5*shown[selected]+.5*color).astype(np.uint8)
            shown=cv2.copyMakeBorder(shown,25,0,0,0,cv2.BORDER_CONSTANT);cv2.putText(shown,title,(3,17),cv2.FONT_HERSHEY_SIMPLEX,.43,(255,255,255),1);panels.append(shown)
        board=out/'boards'/f'{sid}.png';assert cv2.imwrite(str(board),np.hstack(panels))
        records.append(dict(source_id=sid,image_id=attempts[sid]['image_id'],image_sha256=digest(image_path),
            group='facial_hair_example' if sid in sources[:6] else 'reference_control',
            report=report,preferred_pixels=int((preferred>0).sum()),removed_pixels=int(veto.sum()),
            added_pixels=int(((candidate>0)&(preferred==0)).sum()),automatically_applied=False,
            board_path=board.relative_to(out).as_posix()))
        print(sid,report['suggested_pixels'],flush=True)
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    sections=''.join('<section><h2>'+r['source_id']+' · '+r['group']+'</h2><p>Suggested exclusion: '+str(r['removed_pixels'])+' pixels. This is not verified beard area.</p><img src="'+r['board_path']+'"></section>' for r in records)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Facial-hair exclusion suggestions</title><style>body{font:17px system-ui;background:#151923;color:#eee;margin:25px}img{width:100%;max-width:1300px}section{border-top:1px solid #777;padding:15px}</style><h1>Auxiliary exclusion check</h1><p>Preferred mask is preserved. Red regions are optional lower-face non-skin suggestions, not dedicated beard labels. Inspect skin loss; never apply silently.</p>'+sections,encoding='utf-8')


if __name__=='__main__':main()
