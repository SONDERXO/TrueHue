"""Preview the user-authorized full-face parser mask on a selected photo."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import uuid
import webbrowser

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage


def main():
    parser=argparse.ArgumentParser(description='Preview full-face coverage without running correction or ITA/MST.')
    parser.add_argument('--image',type=Path)
    parser.add_argument('--output-dir',type=Path)
    parser.add_argument('--open',action='store_true',dest='open_result')
    parser.add_argument('--edit',action='store_true',help='Open the local facial-hair exclusion brush')
    parser.add_argument('--suggest-facial-hair',action='store_true',help='Research-only auxiliary suggestion; not enabled by default')
    args=parser.parse_args()
    chosen=args.image
    if chosen is None:
        import tkinter as tk
        from tkinter import filedialog
        root=tk.Tk();root.withdraw()
        selected=filedialog.askopenfilename(title='Choose a photo for the face-mask preview',
            filetypes=[('Photos','*.jpg *.jpeg *.png *.webp *.bmp'),('All files','*.*')])
        root.destroy()
        if not selected:return
        chosen=Path(selected)
    config=get_config();out=args.output_dir or ROOT/config.OUTPUTS_ROOT/('face_mask_preview_'+uuid.uuid4().hex[:12])
    if out.exists():raise FileExistsError(out)
    encoded=chosen.read_bytes();photo=cv2.imdecode(np.frombuffer(encoded,np.uint8),cv2.IMREAD_COLOR)
    if photo is None:raise ValueError('Could not open this photo')
    image=cv2.resize(photo,(config.IMAGE_SIZE,config.IMAGE_SIZE),interpolation=cv2.INTER_LINEAR)
    prepare=importlib.import_module('11_prepare_training_manifests')
    boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    if len(boxes)!=1:raise ValueError('Choose a photo with exactly one clear face')
    points,_,status=prepare.detect_landmarks_with_margin(image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH)
    if points is None:raise ValueError('Facial landmarks unavailable: '+status)
    points=points+np.array(boxes[0][:2])
    model=ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx'
    model_sha=hashlib.sha256(model.read_bytes()).hexdigest()
    if model_sha!='0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f':
        raise ValueError('Existing parser model does not match the documented asset')
    categories=DenseFaceParser(model).categories_bgr(image)
    result=build_semantic_face_coverage(image,points,categories)
    alpha=.5*result.alpha.astype(float)/255
    overlay=np.rint(image*(1-alpha[:,:,None])+np.array([0,255,0])*alpha[:,:,None]).astype(np.uint8)
    out.mkdir(parents=True)
    for name,array in [('input.png',image),('mask.png',result.mask),('alpha.png',result.alpha),
            ('overlay.png',overlay),('categories.png',categories)]:
        if not cv2.imwrite(str(out/name),array):raise OSError(out/name)
    report=dict(result.report,source_path=str(chosen.resolve()),source_sha256=hashlib.sha256(encoded).hexdigest(),
        original_shape=list(photo.shape),preview_shape=list(image.shape),parser_sha256=model_sha,
        ITA_MST_calls=0,correction_applied=False,preview_only=True)
    suggestion=None
    if args.suggest_facial_hair:
        from src.skin_masking.facial_hair_exclusion import FacialHairAuxiliary,lower_face_suggestion
        auxiliary=ROOT/config.MODELS_ROOT/'facial_hair_auxiliary_v1/fcn_mobilenetv2_fp.onnx'
        if not auxiliary.is_file():
            report['facial_hair_suggestion_status']='auxiliary_model_unavailable; preferred mask preserved'
        else:
            aux=FacialHairAuxiliary(auxiliary).categories_bgr(image)
            suggestion,suggestion_report=lower_face_suggestion(result.mask,categories,aux)
            cv2.imwrite(str(out/'experimental_suggestion.png'),suggestion.astype(np.uint8)*255)
            report['facial_hair_suggestion']=suggestion_report
            report['facial_hair_suggestion_status']='experimental_not_applied; failed clean-skin checks'
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Face mask preview</title>'
        '<style>body{font:18px system-ui;background:#151923;color:#eee;margin:30px}main{display:flex;gap:20px;flex-wrap:wrap}img{width:min(28vw,512px);min-width:230px}figure{margin:0}figcaption{margin:10px 0}</style>'
        '<h1>Face mask preview</h1><p>Facial skin support with parser and landmark exclusions. '
        'Inspect hair, glasses and other objects; predictions can be wrong. No correction or skin-tone estimate is applied.</p>'
        '<main><figure><figcaption>Photo</figcaption><img src="input.png"></figure>'
        '<figure><figcaption>Selected skin</figcaption><img src="overlay.png"></figure>'
        '<figure><figcaption>Binary mask</figcaption><img src="mask.png"></figure></main>',encoding='utf-8')
    print('Saved face-mask preview:',out.resolve())
    if args.edit:
        from src.demo.mask_editor import open_mask_editor
        open_mask_editor(out,suggestion=suggestion)
    elif args.open_result or args.image is None:webbrowser.open((out/'review.html').resolve().as_uri())


if __name__=='__main__':main()
