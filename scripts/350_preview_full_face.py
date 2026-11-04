"""Whole-face correction / separate nostril-guarded measurement preview."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import uuid
import webbrowser
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import contract,measure
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.full_face_support import build_full_face_support
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.face_neck_support import apply_shared_parameters
from src.correction.seamless_blend import apply_blended
from src.skin_masking.continuous_correction import continuous_support


def save_case(folder,image,face,categories,points,*,blend=True):
    support=continuous_support(build_full_face_support(image,face,categories,points,face_count=1))
    folder.mkdir(parents=True)
    overlay=image.copy();selected=support.correction_mask>0
    overlay[selected]=np.rint(.5*image[selected]+.5*np.array([0,255,0])).astype(np.uint8)
    overlay[support.neck_mask>0]=np.rint(.5*image[support.neck_mask>0]+.5*np.array([255,255,0])).astype(np.uint8)
    stats=compute_masked_lab_statistics(image,support.measurement_mask,1000)
    hard=apply_shared_parameters(image,support,.85,1.05,.95)
    _,xx=np.nonzero(face);face_width=int(xx.max()-xx.min()+1)
    soft,alpha,blend_report=apply_blended(image,support.correction_mask,[.85,1.05,.95],face_width=face_width)
    demo=soft if blend else hard
    if blend:
        colors=np.full_like(image,[0,255,0]);colors[support.neck_mask>0]=[255,255,0]
        opacity=.5*alpha[:,:,None]
        overlay=np.rint(image*(1-opacity)+colors*opacity).astype(np.uint8)
    assert np.array_equal(demo[~selected],image[~selected])
    for name,array in [('input.png',image),('overlay.png',overlay),('measurement_mask.png',support.measurement_mask),
        ('correction_mask.png',support.correction_mask),('neck_mask.png',support.neck_mask),
        ('correction_alpha.png',np.rint(alpha*255).astype(np.uint8)),('hard_operator_demo.png',hard),
        ('operator_demo.png',demo),('board.png',np.hstack((image,overlay,cv2.cvtColor(support.measurement_mask,cv2.COLOR_GRAY2BGR),demo)))]:
        assert cv2.imwrite(str(folder/name),array)
    return dict(report=support.report,statistics=stats,mst=None,old_lookup_compatible=False,
                correction_model_used=False,operator_parameters_are_illustrative=True,
                boundary_blending_enabled=blend,blend_report=blend_report)


def main():
    p=argparse.ArgumentParser();p.add_argument('--image',type=Path);p.add_argument('--cohort',action='store_true')
    p.add_argument('--open',action='store_true');p.add_argument('--hard-edges',action='store_true',help='Historical hard-mask operator comparison')
    args=p.parse_args();config=get_config()
    spec,identity=contract(ROOT)
    if args.cohort:
        out=ROOT/'outputs'/('continuous_face_support_v6_hard' if args.hard_edges else 'continuous_face_support_v6_soft')
        if out.exists():raise FileExistsError(out)
        out.mkdir();(out/'cases').mkdir()
        (out/'contract.json').write_text(json.dumps(dict(contract=spec,measurement_contract_sha256=identity),indent=2))
        rows=json.loads((ROOT/'outputs/preferred_support_cohort_v2/records.json').read_text())
        records=[];cards=[]
        for row in rows:
            if row['measurement']['status']!='success':continue
            sid=Path(row['image_id']).stem;folder=out/'cases'/sid
            image=cv2.imread(str(ROOT/row['input_path']));face=cv2.imread(str(ROOT/row['mask_paths']['face']),0)
            cats=cv2.imread(str(ROOT/Path(row['input_path']).parent/'categories.png'),0)
            points=np.load(ROOT/'outputs/complete_brow_area_v3/cases'/sid/'landmarks.npy')
            rec=save_case(folder,image,face,cats,points,blend=not args.hard_edges);rec['image_id']=row['image_id'];records.append(rec)
            cards.append('<h2>'+row['image_id']+'</h2><img src="cases/'+sid+'/board.png">')
        (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
        (out/'verification.json').write_text(json.dumps(dict(cases=len(records),measurement_contract_sha256=identity,
            new_mapping_fits=0,correction_tree_fits=0,parser_inferences=0,new_mask_approvals=0,
            old_mst_lookup_blocked=True,measurement_pixel_change_requires_recalibration=True),indent=2))
        body=''.join(cards)
    else:
        chosen=args.image
        if chosen is None:
            import tkinter as tk
            from tkinter import filedialog
            window=tk.Tk();window.withdraw();value=filedialog.askopenfilename(title='Choose a photo for whole-face correction support',filetypes=[('Photos','*.png *.jpg *.jpeg *.webp *.bmp'),('All files','*.*')]);window.destroy()
            if not value:return
            chosen=Path(value)
        raw=chosen.read_bytes();image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        prepare=importlib.import_module('11_prepare_training_manifests');saved={}
        detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
        def landmarks(im,box):
            points,_,_=prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
            saved['points']=None if points is None else points+np.array(box[:2]);return saved['points']
        class Parser:
            def __init__(self):self.net=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx');self.last=None
            def categories_bgr(self,im):self.last=self.net.categories_bgr(im);return self.last
        parser=Parser();measurement=measure(image,detector,landmarks,parser)
        out=ROOT/config.OUTPUTS_ROOT/('whole_face_photo_'+uuid.uuid4().hex[:12]);out.mkdir(parents=True)
        if measurement.report['status']!='success':
            (out/'report.json').write_text(json.dumps(measurement.report,indent=2));print('Measurement unavailable; report: '+str(out));return
        rec=save_case(out/'case',measurement.image,measurement.mask,parser.last,saved['points'],blend=not args.hard_edges)
        rec.update(source_path=str(chosen.resolve()),source_sha256=hashlib.sha256(raw).hexdigest(),
                   measurement=measurement.report,measurement_contract_sha256=identity)
        (out/'report.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
        body='<img src="case/board.png">'
    blend_note=' Inward-only edge blending is enabled; it cannot extend beyond the binary support.' if not args.hard_edges else ' Historical hard edges are enabled.'
    page='<!doctype html><meta charset="utf-8"><title>Whole-face correction support</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}</style><h1>Whole-face correction, separate skin measurement</h1><p>Panels: original; correction support (green face, cyan neck); measurement mask; fixed-setting operator demonstration. Everything inside the face outline is corrected, including hair, eyes, teeth and objects.'+blend_note+' Measurement excludes facial features and a conservative nasal-base guard. MST is unavailable until a matching calibration is prepared. No learned correction result is shown.</p>'+body
    (out/'review.html').write_text(page,encoding='utf-8');print('Saved: '+str(out))
    if args.open or (args.image is None and not args.cohort):webbrowser.open((out/'review.html').resolve().as_uri())


if __name__=='__main__':main()
