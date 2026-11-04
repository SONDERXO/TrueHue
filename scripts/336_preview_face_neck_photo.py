"""Choose a photo and preview separate face-measurement/neck-correction support."""
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
from src.ita_estimation.semantic_measurement import measure,contract
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.face_neck_support import build_face_neck_support


def main():
    p=argparse.ArgumentParser(description='Preview face+neck support; no correction model or MST lookup.')
    p.add_argument('--image',type=Path);p.add_argument('--open',action='store_true')
    features=p.add_mutually_exclusive_group()
    features.add_argument('--include-brows-lips',dest='include_brows_lips',action='store_true',help='Include eyebrows/lips in correction support only (preferred default)')
    features.add_argument('--exclude-brows-lips',dest='include_brows_lips',action='store_false',help='Historical face+neck-only comparison')
    p.set_defaults(include_brows_lips=True)
    args=p.parse_args();chosen=args.image
    if chosen is None:
        import tkinter as tk
        from tkinter import filedialog
        window=tk.Tk();window.withdraw()
        value=filedialog.askopenfilename(title='Choose a photo for face and neck coverage',
            filetypes=[('Photos','*.png *.jpg *.jpeg *.webp *.bmp'),('All files','*.*')])
        window.destroy()
        if not value:return
        chosen=Path(value)
    config=get_config();spec,identity=contract(ROOT)
    encoded=chosen.read_bytes();photo=cv2.imdecode(np.frombuffer(encoded,np.uint8),cv2.IMREAD_COLOR)
    if photo is None:raise ValueError('Could not decode selected photo')
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    landmark_record={}
    def landmarks(im,box):
        points,_,_=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        full=None if points is None else points+np.array(box[:2])
        landmark_record['points']=full
        return full
    class RecordingParser:
        def __init__(self):
            self.parser=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
            self.categories=None
        def categories_bgr(self,im):
            self.categories=self.parser.categories_bgr(im);return self.categories
    parser=RecordingParser();measurement=measure(photo,detector,landmarks,parser)
    out=ROOT/config.OUTPUTS_ROOT/('face_neck_photo_'+uuid.uuid4().hex[:12]);out.mkdir(parents=True)
    report=dict(source_path=str(chosen.resolve()),source_sha256=hashlib.sha256(encoded).hexdigest(),
        measurement=measurement.report,measurement_contract_sha256=identity,
        correction_model_used=False,mst_lookup_used=False,beard_specific_model=False,
        preview_only=True,source_original_unchanged=True)
    if measurement.report['status']!='success':
        (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print('No preview: '+measurement.report.get('reason','measurement unavailable')+'. Report: '+str(out))
        return
    support=build_face_neck_support(measurement.image,measurement.mask,parser.categories,face_count=1)
    before_features=support.correction_mask.copy()
    if args.include_brows_lips:
        from src.skin_masking.complete_brow_area import include_complete_brow_area
        support=include_complete_brow_area(measurement.image,support,parser.categories,landmark_record['points'])
    report['neck']=support.report;image=measurement.image;overlay=image.copy()
    for selected,color in [(support.measurement_mask>0,[0,255,0]),(support.neck_mask>0,[255,255,0])]:
        overlay[selected]=np.rint(.5*image[selected]+.5*np.array(color)).astype(np.uint8)
    feature_additions=(support.correction_mask>0)&(before_features==0)
    extra_skin=feature_additions&np.isin(parser.categories,[1,10])
    overlay[extra_skin]=np.rint(.5*image[extra_skin]+.5*np.array([0,255,0])).astype(np.uint8)
    pigment=feature_additions&~extra_skin
    overlay[pigment]=np.rint(.5*image[pigment]+.5*np.array([255,0,255])).astype(np.uint8)
    report['correction_only_brows_lips_enabled']=args.include_brows_lips
    report['support_policy']='user_preferred_complete_brow_area_v3' if args.include_brows_lips else 'historical_face_neck_only'
    for name,array in [('input.png',image),('overlay.png',overlay),('face_measurement_mask.png',support.measurement_mask),
                       ('neck_correction_mask.png',support.neck_mask),('combined_correction_mask.png',support.correction_mask)]:
        assert cv2.imwrite(str(out/name),array)
    if args.include_brows_lips:assert cv2.imwrite(str(out/'brows_lips_correction_only_mask.png'),feature_additions.astype(np.uint8)*255)
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    feature_note=' Green also includes eligible skin across the full eyebrow area for correction. Pink: eyebrows and lips. The separate measurement mask remains unchanged.' if args.include_brows_lips else ''
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Face and neck preview</title><style>body{font:18px system-ui;margin:30px}main{display:flex;gap:20px;flex-wrap:wrap}img{width:256px}figure{margin:0}</style><h1>Face and visible neck</h1><p>Green: facial correction skin. Cyan: additional neck correction support.'+feature_note+' Neck pixels do not enter ITA/MST. No correction model or MST lookup is run. Inspect boundaries and exclusions; this is an unapproved candidate, not guaranteed skin detection.</p><main>'+''.join('<figure><figcaption>'+title+'</figcaption><img src="'+name+'"></figure>' for title,name in [('Photo','input.png'),('Face + neck support','overlay.png'),('Neck only','neck_correction_mask.png')])+'</main>',encoding='utf-8')
    print('Saved face/neck preview: '+str(out))
    if args.open or args.image is None:webbrowser.open((out/'review.html').resolve().as_uri())


if __name__=='__main__':main()
