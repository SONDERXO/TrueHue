"""Frozen composed candidate on preselected new sources; no fits/admission."""
import argparse
from collections import defaultdict,Counter
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
from src.ita_estimation.faceocc_development import evaluate_parent
from src.skin_masking.fixed_face_input_bridge import crop_face,native_projection
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.segmentation_appearance_probe import parser_input
from src.skin_masking.faceocc_mediapipe_bridge import align_input
OUT=ROOT/'outputs/stellenbosch_new_subjects_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def save(p,v):
    if not cv2.imwrite(str(p),v):raise IOError(str(p))

def prepare():
    if (OUT/'preparation_PRIVATE.json').exists():raise FileExistsError('Prepared; no repeat inference')
    plan=read(OUT/'plan_PRIVATE.json');bound=plan['input_sha256']
    assert all(sha(p)==h for p,h in bound.items())
    contract=dict(version='new_source_anchor_then_frozen_crop_parser_and_aligned_visibility_CLAHE_v1',
        prior_candidate_sha256='a5aadb1b26072cc863ef2416a8928598ad52f075e59a3f1489592b93ab38f9f1',
        source_anchor='same085detector_original_fullscene256_before_native1p5crop',measurement='original_crop_pixels',
        exact_old_source_pipeline_equivalence=False,source_dependencies=bound)
    identity=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    write(OUT/'contract_PRIVATE.json',dict(contract=contract,sha256=identity))
    cfg=get_config();helper=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    parser=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];attempts=[];parser_count=0
    for row in plan['selection']:
        rec=dict(row,status='failed',stage='source_anchor');folder=OUT/rec['case_id'];folder.mkdir();cached={}
        def landmarks(im,box):
            p,margin,status=helper.detect_landmarks_with_margin(im,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cached['landmark_details']=dict(margin=margin,status=status)
            cached['points']=None if p is None else p+np.array(box[:2]);return cached['points']
        class Parser:
            def categories_bgr(self,im):
                enhanced=parser_input(im);save(folder/'parser_input.png',enhanced)
                cached['categories']=parser.categories_bgr(enhanced);return cached['categories']
        try:
            raw=Path(rec['source_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==rec['source_sha256']
            (folder/'source.jpeg').write_bytes(raw);source=cv2.imread(rec['source_path']);assert source.shape==(224,224,3)
            anchors=detector(cv2.resize(source,(256,256),interpolation=cv2.INTER_LINEAR));rec['anchor_face_count']=len(anchors)
            if len(anchors)!=1:raise ValueError('Exactly one original full-scene anchor face required')
            native,bridge=crop_face(source,anchors[0]);save(folder/'native_crop.png',native);rec['input_bridge']=bridge
            rec['stage']='parent_measurement';parent=measure(native,detector,landmarks,Parser());rec['parent_report']=parent.report
            if parent.image is not None:save(folder/'input.png',parent.image)
            if parent.mask is not None:save(folder/'parent_mask.png',parent.mask)
            if cached.get('points') is not None:np.save(folder/'landmarks.npy',cached['points'])
            if 'categories' in cached:save(folder/'categories.png',cached['categories']);parser_count+=1
            rec['landmark_details']=cached.get('landmark_details')
            if parent.report['status']!='success':raise ValueError(parent.report.get('reason','Parent measurement failed'))
            aligned,matrix,_=align_input(parent.image,cached['points'],template)
            save(folder/'aligned_original.png',aligned);save(folder/'aligned_candidate.png',parser_input(aligned));write(folder/'matrix.json',matrix.tolist())
            attempts.append(dict(image_id=rec['case_id'],case_index=rec['case_index'],aligned_path=str(folder/'aligned_candidate.png')))
            rec['status']='inference_ready'
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        records.append(rec);print(rec['case_id']+' '+rec['status'],flush=True)
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'preparation_PRIVATE.json',dict(records=records,parser_forwards=parser_count))
    bound=dict(bound);bound[str(OUT/'plan_PRIVATE.json')]=sha(OUT/'plan_PRIVATE.json')
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))
    print('Frozen available FaceOcc inputs '+str(len(attempts))+'/30; parser forwards '+str(parser_count))

def finalize():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Finalized')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json') and all(sha(p)==h for p,h in plan['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']}
    assert set(predictions)=={r['image_id'] for r in plan['attempts']}
    data=read(OUT/'preparation_PRIVATE.json');records=data['records'];boards=[];replays=0;totals=defaultdict(Counter)
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    for r in records:
        folder=OUT/r['case_id'];image=cv2.imread(str(folder/'input.png')) if (folder/'input.png').exists() else None
        if r['status']=='inference_ready':
            pred=predictions[r['case_id']]
            if pred['status']=='success':
                path=OUT/pred['logits_path'];assert sha(path)==pred['logits_sha256']
                logits=np.load(path,allow_pickle=False);aligned=cv2.imread(str(folder/'aligned_original.png'));enhanced=cv2.imread(str(folder/'aligned_candidate.png'))
                def predictor(actual):
                    assert np.array_equal(actual,aligned) and np.array_equal(parser_input(actual),enhanced)
                    return logits
                parent=SimpleNamespace(report=r['parent_report'],image=image,mask=cv2.imread(str(folder/'parent_mask.png'),0))
                points=np.load(folder/'landmarks.npy',allow_pickle=False)
                result=evaluate_parent(parent,points,template,predictor);replay=evaluate_parent(parent,points,template,predictor)
                assert result.report==replay.report and np.array_equal(result.mask,replay.mask)
                assert np.array_equal(result.matrix,np.array(read(folder/'matrix.json')))
                if result.mask is not None:
                    assert not result.mask[parent.mask==0].any();save(folder/'measurement_mask.png',result.mask)
                    native,accounting=native_projection(result.mask,r['input_bridge']);save(folder/'native_grid.png',native);r['native_accounting']=accounting
                r.update(status=result.report['status'],stage='final_measurement',measurement_report=result.report,logits_path=pred['logits_path'],logits_sha256=pred['logits_sha256']);replays+=1
            else:r.update(status='model_failed',reason=pred['reason'])
        source=cv2.imread(str(folder/'source.jpeg'));context=cv2.copyMakeBorder(source,16,16,16,16,cv2.BORDER_CONSTANT,value=(35,35,35))
        input_image=image if image is not None else cv2.resize(source,(256,256),interpolation=cv2.INTER_LINEAR)
        canvas=np.full((256,256,3),35,np.uint8);zoom=canvas.copy()
        if (folder/'native_crop.png').exists():
            native=cv2.imread(str(folder/'native_crop.png'));side=native.shape[0];start=(256-side)//2;canvas[start:start+side,start:start+side]=native
            zoom=cv2.resize(native,(256,256),interpolation=cv2.INTER_NEAREST)
        mask=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros((256,256),np.uint8)
        selected=mask>0;overlay=input_image.copy();overlay[selected]=np.rint(.6*input_image[selected]+.4*np.array([0,255,0])).astype(np.uint8)
        pixels=input_image.copy();pixels[~selected]=35
        if (folder/'native_grid.png').exists():
            x0,y0,x1,y1=r['input_bridge']['native_bounds'];grid=cv2.imread(str(folder/'native_grid.png'),0)[y0:y1,x0:x1]>0
            native_overlay=native.copy();native_overlay[grid]=np.rint(.6*native[grid]+.4*np.array([0,255,0])).astype(np.uint8)
            zoom=cv2.resize(native_overlay,(256,256),interpolation=cv2.INTER_NEAREST)
        label=np.full((26,1280,3),255,np.uint8)
        cv2.putText(label,r['case_id']+' '+r['condition']+' '+r['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,np.hstack([context,canvas,overlay,pixels,zoom])]))
        totals[r['sampling_stratum']].update(attempts=1,technical_success=int(r['status']=='success'))
    for i in range(10):save(OUT/f'contact_{i+1:02d}.png',np.vstack(boards[3*i:3*i+3]))
    groups=defaultdict(list)
    for r in records:groups[r['subject_key']].append(r)
    summary=dict(attempts=30,new_publisher_keys=10,parser_forwards=data['parser_forwards'],FaceOcc_forwards=run['forwards'],
        final_successes=sum(r['status']=='success' for r in records),failed_attempts=sum(r['status']!='success' for r in records),
        complete_technical_subject_keys=sum(all(r['status']=='success' for r in g) for g in groups.values()),saved_service_replays=replays,
        by_preexisting_stratum={k:dict(v) for k,v in totals.items()},mapping_fits=0,tree_fits=0,admissions=0,
        actual_skin_unverified=True,unused_highest_interval_keys_remaining=0,
        effective_contract_sha256=read(OUT/'contract_PRIVATE.json')['sha256'])
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private new-source frozen candidate</h1><p>Original224scene padded; exact native crop padded; original normalized mask; selected colours; native-grid nearest zoom (not added detail). Scores hidden. Failed stages retained. Research only, no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
