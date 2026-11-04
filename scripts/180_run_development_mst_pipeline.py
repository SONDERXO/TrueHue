"""Explicit experimental MST runner; requires a chosen saved development fold."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.model_training.portable_tree import PortableTree
from src.correction.development_mst_pipeline import DevelopmentMSTPipeline

EXPERIMENTS={'baseline5':'table2_reviewed_ten_source_evaluation_v1',
    'chroma9':'table2_chroma_distribution_comparison_v1','clean-leaf':'table2_clean_leaf_policy_v1'}


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def build_pipeline(experiment,fold_id):
    started=time.perf_counter()
    if experiment not in EXPERIMENTS or type(fold_id) is not int or not 1<=fold_id<=10:
        raise ValueError('Explicit known experiment and fold1..10required')
    folder=ROOT/'outputs'/EXPERIMENTS[experiment]
    plan=read(folder/('fit_plan.json' if experiment=='baseline5' else 'plan.json'))
    summary=read(folder/'summary.json');verify=read(folder/'verification.json')
    if digest(folder/'summary.json')!=verify['summary_sha256']:raise ValueError('Experiment summary checksum mismatch')
    if summary['gate']['passed']:raise ValueError('Runner scope expects explicitly failed-gate development artifacts')
    _,identity=contract(ROOT)
    if any(r['measurement_contract_sha256']!=identity for r in plan['rows']):raise ValueError('Experiment measurement contract mismatch')
    path=folder/f'fold_{fold_id}/decision_tree.json';model=PortableTree(read(path))
    if tuple(model.feature_names)!=tuple(plan['features']):raise ValueError('Experiment feature schema mismatch')
    artifact=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'
    if any(r['lookup_sha256']!=digest(artifact) for r in plan['rows']):raise ValueError('Lookup checksum mismatch')
    lookup=DevelopmentMonotoneLookup(read(artifact),identity)
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    def detector(image):return prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    def masker(image,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(image[y:y+h,x:x+w],image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    pipeline=DevelopmentMSTPipeline(detector,masker,lookup,model,identity)
    provenance=dict(experiment=experiment,fold_id=fold_id,tree_sha256=digest(path),lookup_sha256=digest(artifact),
        summary_sha256=digest(folder/'summary.json'),measurement_contract_sha256=identity,
        initialization_ms=(time.perf_counter()-started)*1000,network_calls=False,active_model_changed=False,
        warning='Explicit saved development fold, not an approved release model; fold choice must not be optimized on outputs')
    return pipeline,provenance


def save_result(folder,result,provenance):
    folder=Path(folder)
    if folder.exists():raise FileExistsError('Refusing existing output directory')
    folder.mkdir(parents=True)
    (folder/'report.json').write_text(json.dumps({**result.report,'provenance':provenance},indent=2,allow_nan=False),encoding='utf-8')
    for name,pixels in [('square_input.png',result.image),('measurement_mask.png',result.mask),('corrected.png',result.corrected)]:
        if pixels is not None and not cv2.imwrite(str(folder/name),pixels):raise OSError(folder/name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True);parser.add_argument('--experiment',choices=EXPERIMENTS,required=True)
    parser.add_argument('--fold-id',type=int,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.output_dir.exists():raise FileExistsError('Refusing existing output directory')
    original=digest(args.image);image=cv2.imread(str(args.image));pipeline,provenance=build_pipeline(args.experiment,args.fold_id)
    result=pipeline.run(image)
    if digest(args.image)!=original:raise RuntimeError('Input changed during inference')
    save_result(args.output_dir,result,{**provenance,'input_path':str(args.image.resolve()),'input_sha256':original})
    print(json.dumps(dict(status=result.report['status'],mst=result.report['mst'],parameters=result.report['parameters'],output=str(args.output_dir.resolve())),indent=2))
    if result.corrected is None:raise SystemExit(2)


if __name__=='__main__':main()
