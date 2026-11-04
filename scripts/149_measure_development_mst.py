"""Input-only square256→ITA→experimental MST feature report; no correction."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--image',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    if args.output_dir.exists():raise FileExistsError(args.output_dir)
    config=get_config();spec,identity=contract(ROOT)
    folder=ROOT/'outputs/mst_monotone_square256_v1';path=folder/'development_lookup.json'
    verification=json.loads((folder/'artifact_verification.json').read_text())
    checksum=hashlib.sha256(path.read_bytes()).hexdigest()
    if checksum!=verification['lookup_sha256']:raise ValueError('Lookup checksum mismatch')
    lookup=DevelopmentMonotoneLookup(json.loads(path.read_text()),identity)
    prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def mask(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    original=hashlib.sha256(args.image.read_bytes()).hexdigest()
    result=measure(cv2.imread(str(args.image),cv2.IMREAD_COLOR),detector,mask)
    report=dict(**result.report,measurement_contract_sha256=identity,lookup_sha256=checksum,input_sha256=original,
        proposal_complete=False,final_validated=False,correction_applied=False,
        mst_status='unavailable_due_to_measurement_failure',mst_label=None,mst_index=None,
        limitation='Experimental mapping with weak held-subject accuracy and incomplete output-category coverage. Not production correction or calibrated complexion truth.')
    if result.report['status']=='success':
        label=lookup.label(result.report['features']['input_ita_degrees'])
        report.update(mst_status='experimental_development_estimate',mst_label=label,mst_index=label-1,
            correction_input_features={**result.report['features'],'input_mst_index':label-1})
    assert hashlib.sha256(args.image.read_bytes()).hexdigest()==original
    args.output_dir.mkdir(parents=True);(args.output_dir/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if result.report['status']!='success':raise SystemExit(2)


if __name__=='__main__':main()
