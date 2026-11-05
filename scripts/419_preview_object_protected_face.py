"""Reusable single-photo preview with explicit glasses choice; never trains."""
import argparse
import hashlib
import html
import importlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.correction_preview import GLASSES_MODES,render_preview
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.ita_estimation.nostril_measurement import measure
from src.ita_estimation.faceocc_development import contract,evaluate_parent
from src.utilities.config import get_config

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def save(p,data):
    if not cv2.imwrite(str(p),data):raise IOError(str(p))


def load_saved_case(case_id):
    """Read a bound saved case; the caller supplies the glasses choice separately."""
    base=ROOT/'outputs/ffhq_mask_support_v1';other=ROOT/'outputs/ffhq_object_protection_v1'
    rows={r['id']:r for r in read(base/'results.json')['records']}
    if case_id not in rows:raise ValueError('Case is not in the fixed saved FFHQ package')
    row=rows[case_id];folder=base/case_id
    hashes=read(other/'plan.json')['input_sha256']
    hashes.update({str(other/p):h for p,h in read(other/'sha256.json').items()})
    if not all(sha(p)==h for p,h in hashes.items()):raise ValueError('Saved input changed')
    image=cv2.imread(str(folder/'input.png'))
    facial=cv2.imread(str(folder/'baseline_mask.png'),0)
    categories=cv2.imread(str(folder/'categories.png'),0)
    points=np.load(folder/'landmarks.npy',allow_pickle=False)
    visible=cv2.imread(str(other/case_id/'visible_face.png'),0)
    return image,facial,categories,points,visible,dict(source='saved_FFHQ_case',case_id=case_id,
        source_path=row['source_path'],new_inference=0,input_sha256=hashes,
        measurement_candidate_path=str(folder/'candidate_mask.png'))


def write_preview(folder,image,result,metadata):
    folder.mkdir(parents=True,exist_ok=True)
    support=result.support
    shown=image.copy();sel=support.correction_mask>0
    shown[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8)
    measurement=image.copy();measurement[support.measurement_mask==0]=35
    detail=image.copy();lens=result.lens_interiors>0;rim=result.approximate_rims>0
    detail[lens]=np.rint(.6*image[lens]+.4*np.array([0,255,0])).astype(np.uint8)
    detail[rim]=np.rint(.6*image[rim]+.4*np.array([255,0,255])).astype(np.uint8)
    for name,array in [('input',image),('overlay',shown),('correction_mask',support.correction_mask),
        ('measurement_mask',support.measurement_mask),('neck_mask',support.neck_mask),
        ('protected_mask',result.protected.astype(np.uint8)*255),('lens_interiors',result.lens_interiors),
        ('approximate_rims',result.approximate_rims),('operator_demo',result.output),
        ('board',np.hstack([image,shown,measurement,detail,result.output]))]:
        save(folder/(name+'.png'),array)
    np.save(folder/'alpha.npy',result.alpha)
    write(folder/'report.json',dict(result.report,provenance=metadata))
    status='Choose clear or opaque glasses before using this mask further.' if result.report['requires_glasses_choice'] else 'Development preview only; mask and reference quality remain unverified.'
    (folder/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Object-protected face preview</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Object-protected correction preview</h1><p><b>'+status+'</b></p><p>Glasses choice: '+
        html.escape(result.report['glasses_choice'])+'. No automatic glasses-type classification.</p>'+
        '<p>Original; correction green; baseline facial measurement pixels; lens green/approximate rims pink; '+
        'fixed illustrative correction. Measurement excludes eyes and lenses regardless of correction choice. '+
        'Rims are approximated; beard/hair/object/neck errors remain possible. No trained correction or MST assignment.</p>'+
        '<img src="board.png"><p>Source: '+html.escape(str(metadata.get('source_path','saved input')))+'</p>',encoding='utf-8')
    write(folder/'sha256.json',{p.name:sha(p) for p in folder.iterdir() if p.is_file()})


def dependencies():
    spec,identity=contract(ROOT);hashes={}
    def collect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k=='dependency_sha256':hashes.update({str(ROOT/p):h for p,h in v.items()})
                else:collect(v)
    collect(spec)
    for name in ['scripts/419_preview_object_protected_face.py','scripts/420_run_preview_faceocc.py',
        'src/skin_masking/correction_preview.py','src/skin_masking/clear_lens_correction.py',
        'src/skin_masking/object_protected_correction.py','src/skin_masking/continuous_correction.py',
        'src/skin_masking/face_neck_support.py','src/correction/seamless_blend.py','src/distortion_generation/paper_gamma.py']:
        hashes[str(ROOT/name)]=sha(ROOT/name)
    return hashes,identity


def prepare_photo(source,folder,hashes):
    cfg=get_config();cached={};helper=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    def landmarks(im,box):
        points,margin,status=helper.detect_landmarks_with_margin(im,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
        cached['landmark_details']=dict(margin=margin,status=status)
        cached['points']=None if points is None else points+np.array(box[:2]);return cached['points']
    net=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    class Parser:
        def categories_bgr(self,im):cached['categories']=net.categories_bgr(im);return cached['categories']
    image=cv2.imdecode(np.frombuffer(source.read_bytes(),np.uint8),cv2.IMREAD_COLOR)
    parent=measure(image,detector,landmarks,Parser())
    write(folder/'parent_report.json',parent.report)
    if parent.image is not None:save(folder/'input.png',parent.image)
    if parent.report['status']!='success':raise ValueError(parent.report.get('reason','Parent measurement failed'))
    points=cached['points'];categories=cached['categories']
    save(folder/'baseline_mask.png',parent.mask);save(folder/'categories.png',categories)
    np.save(folder/'landmarks.npy',points)
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    aligned,matrix,bridge=align_input(parent.image,points,template)
    save(folder/'aligned.png',aligned)
    bound=dict(hashes);bound[str(folder/'aligned.png')]=sha(folder/'aligned.png')
    write(folder/'inference_request.json',dict(aligned_path=str(folder/'aligned.png'),input_sha256=bound))
    python=ROOT/'outputs/faceocc_inference_env_v1/Scripts/python.exe'
    if not python.exists():raise ValueError('Existing isolated FaceOcc environment required; none installed automatically')
    subprocess.run([str(python),'-B',str(ROOT/'scripts/420_run_preview_faceocc.py'),
        '--request',str(folder/'inference_request.json')],cwd=ROOT,check=True)
    prediction=read(folder/'inference.json')
    if prediction['request_sha256']!=sha(folder/'inference_request.json') or prediction['logits_sha256']!=sha(folder/'faceocc_logits.npy'):
        raise ValueError('Prediction binding failed')
    logits=np.load(folder/'faceocc_logits.npy',allow_pickle=False)
    measurement=evaluate_parent(parent,points,template,lambda _:logits)
    write(folder/'measurement_report.json',measurement.report)
    if measurement.mask is not None:save(folder/'candidate_measurement_mask.png',measurement.mask)
    visible=map_visible_mask((logits>0).astype(np.uint8)*255,parent.image.shape[:2],matrix)
    save(folder/'visible_face.png',visible)
    return parent.image,parent.mask,categories,points,visible,dict(source='explicit_photo_path',
        source_path=str(source),source_sha256=hashes[str(source)],new_inference=1,
        measurement_status=measurement.report['status'],landmark_details=cached['landmark_details'],bridge=bridge,
        matrix=matrix.tolist())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image',type=Path);group.add_argument('--saved-case')
    parser.add_argument('--glasses',choices=GLASSES_MODES,default='uncertain')
    args=parser.parse_args()
    folder=ROOT/'outputs'/('object_protected_preview_'+uuid.uuid4().hex[:12]);folder.mkdir()
    stage='input_binding'
    try:
        hashes,identity=dependencies()
        if args.image:
            source=args.image.resolve();hashes[str(source)]=sha(source)
        else:source=None
        write(folder/'plan.json',dict(input_sha256=hashes,glasses=args.glasses,
            source_path=str(source) if source else None,saved_case=args.saved_case,measurement_contract=identity))
        stage='saved_input' if source is None else 'photo_processing'
        data=load_saved_case(args.saved_case) if source is None else prepare_photo(source,folder,hashes)
        image,facial,categories,points,visible,metadata=data
        stage='correction_preview'
        result=render_preview(image,facial,categories,points,visible,glasses=args.glasses)
        if not all(sha(p)==h for p,h in hashes.items()):raise ValueError('Input/dependency changed during preview')
        write_preview(folder,image,result,metadata)
        print('Saved '+str(folder/'review.html'))
        print(result.report['status'])
    except (ValueError,RuntimeError,OSError,subprocess.CalledProcessError,cv2.error) as error:
        write(folder/'failure.json',dict(status='failed',stage=stage,reason=str(error),training_admitted=False))
        print('Preview failed; retained report: '+str(folder/'failure.json'),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':sys.exit(main())
