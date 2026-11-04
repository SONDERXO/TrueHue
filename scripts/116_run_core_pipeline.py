"""Run the core Python development pipeline with an explicit unavailable MST."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.correction.core_pipeline import CorePipeline
from src.correction.correct_image import ESTIMATION_VERSION
from src.model_training.portable_tree import PortableTree
from src.data_preparation.controlled_training_table import FEATURES,TARGETS

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build_pipeline():
    config=get_config();folder=ROOT/config.OUTPUTS_ROOT/'core_tree_portability_v2';path=folder/'decision_tree.json'
    verification=json.loads((folder/'verification.json').read_text());payload=json.loads(path.read_text())
    if digest(path)!=verification['export_sha256']:raise ValueError('Portable model checksum mismatch')
    model=PortableTree(payload);meta=payload['provenance']['source_metadata']
    if tuple(model.feature_names)!=FEATURES or tuple(model.target_names)!=TARGETS or meta['mask_version']!=ESTIMATION_VERSION:raise ValueError('Frozen model schema/version mismatch')
    face=ROOT/config.FACE_MODEL_PATH;landmarks=ROOT/config.FACE_LANDMARKER_MODEL_PATH
    if not face.is_file() or not landmarks.is_file():raise FileNotFoundError('Local face and landmark models required; no download')
    prepare=importlib.import_module('11_prepare_training_manifests')
    def detect(image):return prepare._detect_face_boxes(image,face,.85)
    def mask(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w].copy(),image,box,landmarks,ESTIMATION_VERSION)
    provenance=dict(portable_tree_sha256=digest(path),source_model_sha256=verification['source_model_sha256'],
        face_detector_sha256=digest(face),landmarker_sha256=digest(landmarks),face_detection_threshold=.85,
        network_calls=False,correction_scope='Existing facial estimation support only; no neck implementation')
    return CorePipeline(detect,mask,model),provenance

def save_result(folder,image,result,provenance):
    folder=Path(folder)
    if folder.exists():raise FileExistsError('Output exists; refusing overwrite')
    folder.mkdir(parents=True)
    report={**result.report,'provenance':provenance}
    (folder/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    if result.correction is None:
        (folder/'failure.json').write_text(json.dumps(report,indent=2,allow_nan=False));return
    correction=result.correction
    for name,value in [('corrected.png',correction.corrected_bgr),('estimation_mask.png',correction.estimation_mask.astype(np.uint8)*255),('correction_mask.png',correction.correction_mask.astype(np.uint8)*255)]:
        if not cv2.imwrite(str(folder/name),value):raise OSError('Output image write failed')
    overlay=image.copy();mask=correction.correction_mask;overlay[mask]=np.rint(.5*image[mask]+[0,100,0]).astype(np.uint8)
    panels=[];size=get_config().IMAGE_SIZE
    for title,value in [('Input',image),('Development correction',correction.corrected_bgr),('Application mask',overlay)]:
        shown=cv2.resize(value,(size,size));shown=cv2.copyMakeBorder(shown,28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,title,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.40,(255,255,255),1);panels.append(shown)
    if not cv2.imwrite(str(folder/'comparison.png'),np.hstack(panels)):raise OSError('Comparison write failed')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--image',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    if args.output_dir.exists():raise FileExistsError('Output exists; refusing overwrite')
    try:
        checksum=digest(args.image);image=cv2.imread(str(args.image));pipeline,provenance=build_pipeline()
        result=pipeline.run(image)
        if digest(args.image)!=checksum:raise RuntimeError('Input changed during processing')
        save_result(args.output_dir,image,result,{**provenance,'input_path':str(args.image.resolve()),'input_sha256':checksum})
        print(json.dumps(dict(status=result.report['status'],failed_stage=result.report['failed_stage'],mst=result.report['mst'],proposal_complete=False,output=str(args.output_dir.resolve())),indent=2))
        if result.correction is None:raise SystemExit(2)
    except (OSError,ValueError,RuntimeError,cv2.error) as error:
        if not args.output_dir.exists():args.output_dir.mkdir(parents=True)
        report=dict(status='failed',failed_stage='initialization_or_io',reason=str(error),proposal_complete=False)
        (args.output_dir/'failure.json').write_text(json.dumps(report,indent=2));raise
if __name__=='__main__':main()
