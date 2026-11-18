"""Frozen private30-image preparation; preserves decimal labels, never fits."""
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
from src.data_preparation.stellenbosch_preparation import select_subjects,CONDITIONS
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import measure
from src.ita_estimation.faceocc_development import contract,evaluate_parent
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.faceocc_mediapipe_bridge import align_input

OUT=ROOT/'outputs/stellenbosch_bounded_preparation_v1'
PARENT=ROOT/'outputs/stellenbosch_received_data_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def save(p,array):
    if not cv2.imwrite(str(p),array):raise IOError(str(p))


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    spec,identity=contract(ROOT);receipt=read(PARENT/'protocol.json');data=Path(receipt['dataset_location'])
    selected=select_subjects(read(PARENT/'subjects_PRIVATE.json'))
    files={r['path']:r for r in read(PARENT/'files_PRIVATE.json')}
    hashes=read(ROOT/'outputs/mst_cohort_source_investigation_v1/investigation.json')['input_sha256']
    hashes.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for path in [Path(__file__),ROOT/'scripts/431_run_stellenbosch_preparation_logits.py',
        ROOT/'scripts/369_run_faceocc_logits.py',ROOT/'src/data_preparation/stellenbosch_preparation.py',
        ROOT/'tests/test_stellenbosch_preparation.py',ROOT/'docs/stellenbosch-bounded-preparation-protocol-2026-11-05.md']:
        hashes[str(path)]=sha(path)
    archive=Path(receipt['archive_location']);assert sha(archive)==receipt['archive_sha256']
    hashes[str(archive)]=receipt['archive_sha256']
    attempts=[]
    for subject_index,row in enumerate(selected,1):
        label=data/row['publisher_folder']/'monk_scale_value.json';hashes[str(label)]=row['label_sha256']
        for condition in CONDITIONS:
            rel=row['publisher_folder']+'/front-facing/'+condition+'.jpeg';path=data/rel
            assert sha(path)==files[rel]['sha256'];hashes[str(path)]=files[rel]['sha256']
            attempts.append(dict(case_id=f'case_{len(attempts)+1:02d}',case_index=len(attempts)+1,
                subject_index=subject_index,subject_key=row['subject_key'],source_path=str(path),
                condition=condition,source_mst_exact_decimal=row['exact_decimal'],source_mst_raw_value=row['raw_value'],
                source_mst_raw_type=row['raw_type'],sampling_stratum=row['sampling_stratum'],
                integer_category=None,training_admitted=False,calibration_admitted=False))
    assert len(attempts)==30 and all(sha(p)==h for p,h in hashes.items())
    OUT.mkdir();(OUT/'logits').mkdir()
    write(OUT/'plan_PRIVATE.json',dict(status='frozen_before_pixels_and_inference',selection=attempts,
        selected_subjects=selected,source_score_policy='preserved_continuous_1_to_10_no_integer_rounding',
        contract=spec,contract_sha256=identity,input_sha256=hashes,calibration_fits=0))
    cfg=get_config();helper=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    net=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];inference=[]
    for row in attempts:
        folder=OUT/row['case_id'];folder.mkdir();cached={};rec=dict(row,status='failed')
        def landmarks(im,box):
            points,margin,status=helper.detect_landmarks_with_margin(im,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cached['landmark_details']=dict(margin=margin,status=status)
            cached['points']=None if points is None else points+np.array(box[:2]);return cached['points']
        class Parser:
            def categories_bgr(self,im):cached['categories']=net.categories_bgr(im);return cached['categories']
        try:
            raw=Path(row['source_path']).read_bytes();(folder/'source.jpeg').write_bytes(raw)
            image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
            parent=measure(image,detector,landmarks,Parser())
            rec.update(parent_report=parent.report,landmark_details=cached.get('landmark_details'))
            if parent.image is not None:save(folder/'input.png',parent.image)
            if parent.mask is not None:save(folder/'baseline_mask.png',parent.mask)
            if cached.get('points') is not None:np.save(folder/'landmarks.npy',cached['points'])
            if 'categories' in cached:save(folder/'categories.png',cached['categories'])
            if parent.report['status']=='success':
                aligned,matrix,bridge=align_input(parent.image,cached['points'],template)
                save(folder/'aligned.png',aligned)
                rec.update(status='inference_ready',matrix=matrix.tolist(),bridge=bridge)
                inference.append(dict(image_id=row['case_id'],case_index=row['case_index'],aligned_path=str(folder/'aligned.png')))
            else:rec['reason']=parent.report.get('reason','Parent measurement failed')
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        write(folder/'preparation_PRIVATE.json',rec);records.append(rec)
        print(row['case_id']+' '+row['condition']+' '+rec['status'],flush=True)
    assert all(sha(p)==h for p,h in hashes.items())
    write(OUT/'baseline_PRIVATE.json',records)
    bound=dict(hashes)
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=inference,input_sha256=bound))
    print('Available alignments: '+str(len(inference))+'/30',flush=True)


def finalize():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
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
                rec.update(status=result.report['status'],measurement_report=result.report)
                replays+=1
            else:rec.update(status='model_failed',reason=pred['reason'])
        if image is not None:
            raw=cv2.imread(str(folder/'source.jpeg'))
            native=cv2.copyMakeBorder(raw,16,16,16,16,cv2.BORDER_CONSTANT,value=(30,30,30))
            shown=[]
            for name in ['baseline_mask.png','measurement_mask.png']:
                mask=cv2.imread(str(folder/name),0) if (folder/name).exists() else np.zeros(image.shape[:2],np.uint8)
                overlay=image.copy();chosen=mask>0
                overlay[chosen]=np.rint(.6*image[chosen]+.4*np.array([0,255,0])).astype(np.uint8);shown.append(overlay)
            mask=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros(image.shape[:2],np.uint8)
            pixels=image.copy();pixels[mask==0]=35
            board=np.hstack([native]+shown+[pixels]);save(folder/'board.png',board)
            title=np.full((26,board.shape[1],3),255,np.uint8)
            cv2.putText(title,rec['case_id']+' '+rec['condition']+' '+rec['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
            boards.append(np.vstack([title,board]))
        rec['file_sha256']={p.name:sha(p) for p in folder.iterdir() if p.is_file()}
        records.append(rec)
        cards.append('<h2>'+rec['case_id']+' '+rec['condition']+'</h2><p>'+rec['status']+'</p><img src="'+rec['case_id']+'/board.png">')
    for i in range(0,len(boards),3):save(OUT/f'contact_{i//3+1:02d}.png',np.vstack(boards[i:i+3]))
    summary=dict(attempts=30,source_subject_keys=10,parent_successes=sum(r['parent_report']['status']=='success' for r in records),
        FaceOcc_forwards=run['forwards'],measurement_successes=sum(r['status']=='success' for r in records),
        failed_attempts=sum(r['status']!='success' for r in records),saved_service_replays=replays,
        original_images224_working_images256=True,calibration_fits=0,tree_fits=0,admissions=0,
        decimal_labels_preserved=True,integer_categories_created=False,source_and_history_hashes_unchanged=True)
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><title>Private measurement preparation</title>'+
        '<style>body{font:18px system-ui;max-width:1350px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Private local research:30fixed cases</h1><p>Do not share dataset images/labels/gallery without author consent. '+
        'Native224px original padded only for display; parent measurement overlay; FaceOcc overlay; selected pixels. '+
        'Inference uses whole-frame256px interpolation. Scores hidden from boards; no calibration or automatic admissions.</p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
