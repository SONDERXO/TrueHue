"""One fixed face-first bridge on the same private30 sources; no calibration."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from scipy.io import loadmat
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import measure
from src.ita_estimation.faceocc_development import contract,evaluate_parent
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.fixed_face_input_bridge import crop_face,native_projection,VERSION

OUT=ROOT/'outputs/stellenbosch_face_crop_v1'
BASE=ROOT/'outputs/stellenbosch_bounded_preparation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def save(p,array):
    if not cv2.imwrite(str(p),array):raise IOError(str(p))


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    spec,identity=contract(ROOT);previous=read(BASE/'results_PRIVATE.json')['records']
    hashes=read(BASE/'inference_plan.json')['input_sha256']
    hashes.update({str(BASE/p):h for p,h in read(BASE/'sha256.json').items()})
    for p in [Path(__file__),ROOT/'scripts/434_run_stellenbosch_crop_logits.py',
        ROOT/'src/skin_masking/fixed_face_input_bridge.py',ROOT/'tests/test_fixed_face_input_bridge.py',
        ROOT/'docs/stellenbosch-face-crop-protocol-2026-11-05.md']:
        hashes[str(p)]=sha(p)
    assert len(previous)==30 and all(sha(p)==h for p,h in hashes.items())
    effective=dict(version=VERSION,base_measurement_contract=identity,
        crop_rule='native_square_ceil_1p5_max_box_side_center_shift_inside_no_padding',
        source_box='saved_baseline256_detector_box',minimum_normalized_pixels=1000,
        native_adequacy_established=False,source_sha256=hashes[str(ROOT/'src/skin_masking/fixed_face_input_bridge.py')])
    effective_sha=hashlib.sha256(json.dumps(effective,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    OUT.mkdir();(OUT/'logits').mkdir()
    write(OUT/'plan_PRIVATE.json',dict(status='frozen_before_crop_inference',input_sha256=hashes,
        effective_contract=effective,effective_contract_sha256=effective_sha,base_contract=spec,
        original_case_ids=[r['case_id'] for r in previous],calibration_admitted=False))
    cfg=get_config();helper=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    net=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];attempts=[]
    fields=['case_id','case_index','subject_index','subject_key','source_path','condition',
        'source_mst_exact_decimal','source_mst_raw_value','source_mst_raw_type','sampling_stratum']
    for old in previous:
        rec={k:old[k] for k in fields};rec.update(status='failed',calibration_admitted=False,training_admitted=False,MST=None)
        folder=OUT/rec['case_id'];folder.mkdir();cached={}
        def landmarks(im,box):
            points,margin,status=helper.detect_landmarks_with_margin(im,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cached['landmark_details']=dict(margin=margin,status=status)
            cached['points']=None if points is None else points+np.array(box[:2]);return cached['points']
        class Parser:
            def categories_bgr(self,im):cached['categories']=net.categories_bgr(im);return cached['categories']
        try:
            source=cv2.imread(rec['source_path'])
            native,bridge=crop_face(source,old['parent_report']['face_box'])
            save(folder/'native_crop.png',native);rec['input_bridge']=bridge
            parent=measure(native,detector,landmarks,Parser());rec['parent_report']=parent.report
            rec['landmark_details']=cached.get('landmark_details')
            if parent.image is not None:save(folder/'input.png',parent.image)
            if parent.mask is not None:save(folder/'baseline_mask.png',parent.mask)
            if cached.get('points') is not None:np.save(folder/'landmarks.npy',cached['points'])
            if 'categories' in cached:save(folder/'categories.png',cached['categories'])
            if parent.report['status']=='success':
                aligned,matrix,alignment=align_input(parent.image,cached['points'],template)
                save(folder/'aligned.png',aligned)
                rec.update(status='inference_ready',matrix=matrix.tolist(),alignment_report=alignment)
                attempts.append(dict(image_id=rec['case_id'],case_index=rec['case_index'],aligned_path=str(folder/'aligned.png')))
            else:rec['reason']=parent.report.get('reason','Parent failed')
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        write(folder/'preparation_PRIVATE.json',rec);records.append(rec)
        print(rec['case_id']+' '+rec['status'],flush=True)
    assert all(sha(p)==h for p,h in hashes.items())
    write(OUT/'baseline_PRIVATE.json',records)
    bound=dict(hashes)
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))
    print('Available alignments '+str(len(attempts))+'/30',flush=True)


def finalize():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json') and all(sha(p)==h for p,h in plan['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']}
    assert set(predictions)=={r['image_id'] for r in plan['attempts']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];cards=[];boards=[];replays=0
    for rec in read(OUT/'baseline_PRIVATE.json'):
        folder=OUT/rec['case_id'];image=cv2.imread(str(folder/'input.png'))
        if rec['status']=='inference_ready':
            pred=predictions[rec['case_id']]
            if pred['status']=='success':
                path=OUT/pred['logits_path'];assert sha(path)==pred['logits_sha256']
                logits=np.load(path,allow_pickle=False);points=np.load(folder/'landmarks.npy',allow_pickle=False)
                baseline=cv2.imread(str(folder/'baseline_mask.png'),0)
                parent=SimpleNamespace(report=rec['parent_report'],image=image,mask=baseline)
                result=evaluate_parent(parent,points,template,lambda _:logits)
                replay=evaluate_parent(parent,points,template,lambda _:logits)
                assert result.report==replay.report and np.array_equal(result.mask,replay.mask)
                assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')))
                if result.mask is not None:
                    assert not result.mask[baseline==0].any();save(folder/'measurement_mask.png',result.mask)
                    projected,accounting=native_projection(result.mask,rec['input_bridge'])
                    save(folder/'measurement_native_grid.png',projected);rec['native_accounting']=accounting
                rec.update(status=result.report['status'],measurement_report=result.report)
                replays+=1
            else:rec.update(status='model_failed',reason=pred['reason'])
        if image is not None:
            source=cv2.imread(rec['source_path']);native=cv2.imread(str(folder/'native_crop.png'))
            context=cv2.copyMakeBorder(source,16,16,16,16,cv2.BORDER_CONSTANT,value=(30,30,30))
            canvas=np.full_like(image,30);height,width=native.shape[:2];top=(256-height)//2;left=(256-width)//2
            canvas[top:top+height,left:left+width]=native
            mask=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros(image.shape[:2],np.uint8)
            overlay=image.copy();sel=mask>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8)
            pixels=image.copy();pixels[~sel]=35
            board=np.hstack([context,canvas,overlay,pixels]);save(folder/'board.png',board)
            label=np.full((26,board.shape[1],3),255,np.uint8)
            cv2.putText(label,rec['case_id']+' '+rec['condition']+' '+rec['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            boards.append(np.vstack([label,board]))
        rec['file_sha256']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        records.append(rec);cards.append('<h2>'+rec['case_id']+' '+rec['condition']+'</h2><p>'+rec['status']+'</p><img src="'+rec['case_id']+'/board.png">')
    for i in range(0,len(boards),3):save(OUT/f'contact_{i//3+1:02d}.png',np.vstack(boards[i:i+3]))
    summary=dict(attempts=30,source_subject_keys=10,parent_successes=sum(r.get('parent_report',{}).get('status')=='success' for r in records),
        FaceOcc_forwards=run['forwards'],normalized_guard_successes=sum(r['status']=='success' for r in records),
        failed_attempts=sum(r['status']!='success' for r in records),saved_service_replays=replays,
        baseline_wholeframe_successes=0,native_adequacy_established=False,calibration_admissions=0,
        calibration_fits=0,tree_fits=0,decimal_scores_preserved=True,source_history_unchanged=True,
        effective_contract_sha256=read(OUT/'plan_PRIVATE.json')['effective_contract_sha256'])
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><title>Private fixed face crop</title>'+
        '<style>body{font:18px system-ui;max-width:1350px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Private30-case face-first bridge</h1><p>Original224 scene padded; exact native crop padded without enlargement; '+
        'normalized256 measurement overlay; selected pixels. Scores not displayed. Larger masks do not create native detail. '+
        'Research only; do not share images/labels/gallery without author consent. No calibration or training admissions.</p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
