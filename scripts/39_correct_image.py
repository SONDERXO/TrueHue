"""Correct one local image with an explicit, versioned development mask policy."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.model_training.train_model import load_model
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.correction.correct_image import correct_from_estimate,MASK_POLICIES,LEGACY_POLICY,MATERIAL_HAIR_POLICY,ESTIMATION_VERSION
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CorrectionRuntime:
    """Reuses frozen development detection/masking; never accepts clean references."""
    def __init__(self):
        self.config=get_config();self.prepare=importlib.import_module('11_prepare_training_manifests')
        self.model_path=ROOT/self.config.CORRECTION_PROTOTYPE_MODEL_PATH
        metadata=json.loads(self.model_path.with_name('metadata.json').read_text())
        if tuple(metadata['feature_columns'])!=FEATURES or tuple(metadata['target_columns'])!=TARGETS:
            raise ValueError('Prototype model feature/target schema mismatch')
        if metadata['mask_version']!=ESTIMATION_VERSION:raise ValueError('Estimation version mismatch')
        self.model_sha256=digest(self.model_path)
        if self.model_sha256!=metadata['model_sha256']:raise ValueError('Prototype model checksum mismatch')
        self.model=load_model(str(self.model_path));self.segmenter=None;self.segmenter_sha256=None

    def correct(self,image_bgr,mask_policy=LEGACY_POLICY,protected_mask=None):
        if mask_policy not in MASK_POLICIES:raise ValueError('Unknown correction mask policy')
        if mask_policy==MATERIAL_HAIR_POLICY and self.segmenter is None:
            path=ROOT/self.config.SELFIE_SEGMENTER_MODEL_PATH
            provenance=json.loads(path.with_suffix('.provenance.json').read_text())
            checksum=digest(path)
            if checksum!=provenance['sha256']:raise ValueError('Segmenter model checksum mismatch')
            self.segmenter=SelfieMaterialSegmenter(path);self.segmenter_sha256=checksum
        started=time.perf_counter()
        boxes=self.prepare._detect_face_boxes(image_bgr,ROOT/self.config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:raise ValueError('Expected exactly one detected face; found '+str(len(boxes)))
        x,y,w,h=boxes[0];crop=image_bgr[y:y+h,x:x+w].copy()
        result=self.prepare.compute_versioned_skin_mask(crop,image_bgr,boxes[0],ROOT/self.config.FACE_LANDMARKER_MODEL_PATH,ESTIMATION_VERSION)
        if not result.landmarks_available:raise ValueError('Required landmarks unavailable')
        correction=correct_from_estimate(image_bgr,boxes[0],result.mask>0,result.exclusion_mask>0,
            self.model,mask_policy,self.segmenter,protected_mask)
        correction.metadata.update(correction_model_sha256=self.model_sha256,
            segmentation_model_sha256=self.segmenter_sha256 if mask_policy==MATERIAL_HAIR_POLICY else None,
            pipeline_ms_excluding_model_initialization=(time.perf_counter()-started)*1000,
            face_detection_score_threshold=.85)
        return correction

    def close(self):
        if self.segmenter is not None:self.segmenter.close();self.segmenter=None


def save_result(output,input_bgr,result,provenance=None):
    output=Path(output)
    if output.exists():raise FileExistsError('Output directory exists; refusing overwrite')
    output.mkdir(parents=True)
    for name,image in [('corrected.png',result.corrected_bgr),('estimation_mask.png',result.estimation_mask.astype(np.uint8)*255),('correction_mask.png',result.correction_mask.astype(np.uint8)*255)]:
        if not cv2.imwrite(str(output/name),image):raise OSError('Output image write failed')
    panels=[]
    overlay=input_bgr.copy();overlay[result.correction_mask]=np.rint(.5*input_bgr[result.correction_mask]+.5*np.array([0,200,0])).astype(np.uint8)
    for label,image in [('Input',input_bgr),('Corrected',result.corrected_bgr),('Correction support',overlay)]:
        panel=cv2.copyMakeBorder(cv2.resize(image,(256,256)),28,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(panel,label,(4,18),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,255,255),1);panels.append(panel)
    if not cv2.imwrite(str(output/'comparison.png'),np.hstack(panels)):raise OSError('Comparison write failed')
    record=dict(**result.metadata,features=result.features,parameters=result.parameters,provenance=provenance or {})
    (output/'metadata.json').write_text(json.dumps(record,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--mask-policy',choices=MASK_POLICIES,default=LEGACY_POLICY)
    parser.add_argument('--exclude-mask',type=Path,help='Optional same-size mask; nonzero pixels are always preserved')
    args=parser.parse_args()
    if args.output_dir.exists():raise FileExistsError('Output exists; refusing overwrite')
    source_sha=digest(args.image);image=cv2.imread(str(args.image))
    if image is None:raise ValueError('Unreadable input image')
    protected=None;protected_sha=None
    if args.exclude_mask:
        protected_image=cv2.imread(str(args.exclude_mask),cv2.IMREAD_GRAYSCALE)
        if protected_image is None or protected_image.shape!=image.shape[:2]:raise ValueError('Invalid exclusion image dimensions')
        protected=protected_image>0;protected_sha=digest(args.exclude_mask)
    runtime=None
    try:
        runtime=CorrectionRuntime();result=runtime.correct(image,args.mask_policy,protected)
        if digest(args.image)!=source_sha:raise RuntimeError('Source file changed during correction')
        save_result(args.output_dir,image,result,dict(input_path=str(args.image.resolve()),input_sha256=source_sha,protected_mask_sha256=protected_sha))
        print(json.dumps(dict(output=str(args.output_dir.resolve()),mask_policy=args.mask_policy,
            features=result.features,parameters=result.parameters,correction_pixels=int(result.correction_mask.sum())),indent=2))
    except Exception as error:
        if not args.output_dir.exists():args.output_dir.mkdir(parents=True)
        (args.output_dir/'failure.json').write_text(json.dumps(dict(input_path=str(args.image),mask_policy=args.mask_policy,error=str(error)),indent=2),encoding='utf-8')
        raise
    finally:
        if runtime is not None:runtime.close()


if __name__=='__main__':main()
