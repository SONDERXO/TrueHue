"""Recompute all168 input masks, fixed CPU logits, then one recovery comparison."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from scipy.io import loadmat
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import measure
from src.ita_estimation.faceocc_development import contract,evaluate_parent
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.skin_masking.correction_preview import render_preview
from src.model_training.support_shift_diagnostic import compare_masks,fit_current_support,outside_changes
from src.model_training.photographic_target_diagnostic import metrics
from src.model_training.blended_recovery_targets import render_rgb8
from src.correction.seamless_blend import apply_blended

PARENT=ROOT/'outputs/ffhq_correction_targets_v1'
SOURCE=ROOT/'outputs/ffhq_clear_lens_correction_v1'
OUT=ROOT/'outputs/ffhq_distorted_input_support_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,data):p.write_text(json.dumps(data,indent=2),encoding='utf-8')
def save(p,array):
    if not cv2.imwrite(str(p),array):raise IOError(str(p))
def rgb(p):return cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
def key(row):return row['source_id']+'__'+row['case']['id']


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    spec,identity=contract(ROOT)
    hashes=read(PARENT/'plan.json')['input_sha256']
    hashes.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for p in [Path(__file__),ROOT/'scripts/425_run_distorted_support_logits.py',ROOT/'scripts/369_run_faceocc_logits.py',
        ROOT/'src/model_training/support_shift_diagnostic.py',ROOT/'tests/test_support_shift_diagnostic.py',
        ROOT/'docs/distorted-input-support-protocol-2026-11-05.md']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    originals=read(PARENT/'results.json')['records'];assert len(originals)==168
    OUT.mkdir();(OUT/'logits').mkdir()
    write(OUT/'plan.json',dict(status='frozen_before_new_inference',input_sha256=hashes,contract=spec,
        contract_sha256=identity,attempts=[key(r) for r in originals],training_admitted=False))
    cfg=get_config();helper=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    net=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];attempts=[]
    for i,old in enumerate(originals,1):
        image_id=key(old);folder=OUT/image_id;folder.mkdir();cached={}
        rec=dict(image_id=image_id,case_index=i,source_id=old['source_id'],case=old['case'],
            status='failed',training_admitted=False,MST=None)
        def landmarks(im,box):
            points,margin,status=helper.detect_landmarks_with_margin(im,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cached['landmark_details']=dict(margin=margin,status=status)
            cached['points']=None if points is None else points+np.array(box[:2]);return cached['points']
        class Parser:
            def categories_bgr(self,im):cached['categories']=net.categories_bgr(im);return cached['categories']
        try:
            path=PARENT/old['source_id']/old['case']['id']/'distorted.png'
            image=cv2.imread(str(path));parent=measure(image,detector,landmarks,Parser())
            rec.update(parent_report=parent.report,landmark_details=cached.get('landmark_details'),input_sha256=sha(path))
            if parent.image is not None:save(folder/'input.png',parent.image)
            if parent.mask is not None:save(folder/'baseline_mask.png',parent.mask)
            if cached.get('points') is not None:np.save(folder/'landmarks.npy',cached['points'])
            if 'categories' in cached:save(folder/'categories.png',cached['categories'])
            if parent.report['status']=='success':
                aligned,matrix,bridge=align_input(parent.image,cached['points'],template)
                save(folder/'aligned.png',aligned)
                rec.update(status='inference_ready',matrix=matrix.tolist(),bridge=bridge)
                attempts.append(dict(image_id=image_id,case_index=i,aligned_path=str(folder/'aligned.png')))
            else:rec['reason']=parent.report.get('reason','Parent measurement failed')
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        write(folder/'preparation.json',rec)
        with (OUT/'preparation_records.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(rec)+'\n')
        records.append(rec)
        print(str(i)+'/168 '+image_id+' '+rec['status'],flush=True)
    assert all(sha(p)==h for p,h in hashes.items())
    write(OUT/'baseline.json',records)
    bound=dict(hashes)
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))
    print('Available alignments: '+str(len(attempts))+'/168',flush=True)


def finalize():
    if (OUT/'results.json').exists():raise FileExistsError('Already finalised')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']}
    assert set(predictions)=={r['image_id'] for r in plan['attempts']}
    oldrows={key(r):r for r in read(PARENT/'results.json')['records']}
    source_choices={r['id']:r['transparent_glasses'] for r in read(SOURCE/'results.json')['records']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];cards=[];visual={k:[] for k in ['combined_cool_under','stress_combined_under']}
    for rec in read(OUT/'baseline.json'):
        folder=OUT/rec['image_id'];sid=rec['source_id'];case=rec['case']['id'];old=oldrows[rec['image_id']]
        reference=rgb(PARENT/sid/'reference.png');image=rgb(PARENT/sid/case/'distorted.png')
        bgr=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        source_alpha=np.load(SOURCE/sid/'alpha.npy',allow_pickle=False);score=source_alpha>0
        source_mask=cv2.imread(str(SOURCE/sid/'correction_mask.png'),0)
        source_protected=cv2.imread(str(SOURCE/sid/'protected_mask.png'),0)>0
        output=image.copy();new_overlay=bgr.copy()
        rec.update(status='pipeline_failed_no_correction',recovery_available=False,
            input_metrics=old['input_metrics'],fixed_alpha_metrics=old['output_metrics'],
            original_scoring_pixels=int(score.sum()),MST=None)
        try:
            if rec.get('parent_report',{}).get('status')!='success':raise ValueError(rec.get('reason','Parent failed'))
            prediction=predictions.get(rec['image_id'])
            if not prediction or prediction['status']!='success':raise ValueError((prediction or {}).get('reason','Alignment/prediction unavailable'))
            lp=OUT/prediction['logits_path'];assert sha(lp)==prediction['logits_sha256']
            logits=np.load(lp,allow_pickle=False);points=np.load(folder/'landmarks.npy',allow_pickle=False)
            baseline=cv2.imread(str(folder/'baseline_mask.png'),0);categories=cv2.imread(str(folder/'categories.png'),0)
            parent=SimpleNamespace(report=rec['parent_report'],image=bgr,mask=baseline)
            service=evaluate_parent(parent,points,template,lambda _:logits)
            rec['measurement_report']=service.report
            if service.mask is not None:
                save(folder/'measurement_mask.png',service.mask)
                original_measurement=cv2.imread(str(ROOT/'outputs/ffhq_mask_support_v1'/sid/'candidate_mask.png'),0)
                rec['measurement_comparison']=compare_masks(original_measurement,service.mask)
            visible=map_visible_mask((logits>0).astype(np.uint8)*255,image.shape[:2],np.array(rec['matrix']))
            mode='clear' if source_choices[sid] else ('opaque' if sid=='29617' else 'uncertain')
            preview=render_preview(bgr,baseline,categories,points,visible,glasses=mode)
            alpha=preview.alpha;current=preview.support.correction_mask
            save(folder/'correction_mask.png',current);save(folder/'protected_mask.png',preview.protected.astype(np.uint8)*255)
            save(folder/'neck_mask.png',preview.support.neck_mask);save(folder/'visible_face.png',visible)
            np.save(folder/'alpha.npy',alpha)
            rec.update(correction_report=preview.report,correction_comparison=compare_masks(source_mask,current),
                mean_absolute_alpha_shift=float(np.abs(source_alpha-alpha).mean()),
                correction_available=True,source_glasses_choice=mode)
            fit=fit_current_support(image,reference,source_alpha,alpha);rec['fit']=fit
            if fit.get('parameters') is None:
                rec.update(status='target_unavailable_no_correction',reason=fit['status'])
            else:
                output=render_rgb8(image,alpha,fit['parameters'])
                _,xx=np.nonzero(baseline);width=int(xx.max()-xx.min()+1)
                actual,checked,_=apply_blended(bgr,current,fit['parameters'],face_width=width,protected=preview.protected)
                assert np.array_equal(alpha,checked) and np.array_equal(output,cv2.cvtColor(actual,cv2.COLOR_BGR2RGB))
                assert np.array_equal(output[preview.protected],image[preview.protected])
                assert np.array_equal(output[alpha==0],image[alpha==0])
                rec.update(status='recovery_available_not_admitted',recovery_available=True,
                    renderer_parity=True,new_protected_unchanged=True)
            selected=current>0
            new_overlay[selected]=np.rint(.6*bgr[selected]+.4*np.array([0,255,0])).astype(np.uint8)
            lost=(source_mask>0)&~selected
            new_overlay[lost]=np.rint(.6*bgr[lost]+.4*np.array([255,0,255])).astype(np.uint8)
        except (ValueError,RuntimeError,cv2.error) as error:rec['reason']=str(error)
        save(folder/'pipeline_output.png',cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
        rec['output_metrics_original_score']=metrics(output,reference,score)
        rec['outside_source_changes']=outside_changes(output,image,source_alpha,source_protected)
        rec['regresses_vs_fixed_alpha_MAE']=rec['output_metrics_original_score']['rgb8_mae_codes']>old['output_metrics']['rgb8_mae_codes']
        rec['regresses_vs_input_deltaE00']=rec['output_metrics_original_score']['relative_deltaE00_mean']>old['input_metrics']['relative_deltaE00_mean']
        old_output=cv2.imread(str(PARENT/sid/case/'recovery.png'))
        board=np.hstack([cv2.cvtColor(reference,cv2.COLOR_RGB2BGR),bgr,new_overlay,old_output,cv2.cvtColor(output,cv2.COLOR_RGB2BGR)])
        save(folder/'board.png',board)
        if case in visual:
            label=np.full((26,board.shape[1],3),255,np.uint8)
            cv2.putText(label,sid+' '+case+' '+rec['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
            visual[case].append(np.vstack([label,board]))
        write(folder/'result.json',rec)
        records.append(rec)
        cards.append('<h2>'+rec['image_id']+'</h2><p>'+rec['status']+'</p><img loading="lazy" src="'+rec['image_id']+'/board.png">')
        print(rec['image_id']+' '+rec['status'],flush=True)
    for name,boards in visual.items():
        for i in range(0,len(boards),3):save(OUT/(name+'_contact_'+str(i//3+1)+'.png'),np.vstack(boards[i:i+3]))
    layers={}
    for layer in ['clean','core','composite_stress_design']:
        rows=[r for r in records if r['case']['layer']==layer];available=[r for r in rows if r['recovery_available']]
        corrections=[r for r in rows if r.get('correction_available')]
        layers[layer]=dict(attempts=len(rows),recovery_available=len(available),failed=len(rows)-len(available),
            measurement_successes=sum(r.get('measurement_report',{}).get('status')=='success' for r in rows),
            correction_available=len(corrections),
            input_MAE=float(np.mean([r['input_metrics']['rgb8_mae_codes'] for r in rows])),
            fixed_alpha_MAE=float(np.mean([r['fixed_alpha_metrics']['rgb8_mae_codes'] for r in rows])),
            current_alpha_MAE_all_attempts=float(np.mean([r['output_metrics_original_score']['rgb8_mae_codes'] for r in rows])),
            current_alpha_deltaE00_all_attempts=float(np.mean([r['output_metrics_original_score']['relative_deltaE00_mean'] for r in rows])),
            mean_correction_consistency_iou=float(np.mean([r['correction_comparison']['consistency_iou'] for r in corrections])) if corrections else None,
            original_protection_changed_cases=sum(r['outside_source_changes']['changed_source_protected_pixels']>0 for r in rows),
            cases_with_original_support_missed=sum(r.get('fit',{}).get('missed_original_scoring_pixels',0)>0 for r in rows),
            deltaE_regressions_vs_input=sum(r['regresses_vs_input_deltaE00'] for r in rows))
    assert len(records)==168 and all(sha(p)==h for p,h in plan['input_sha256'].items())
    result=dict(records=records,layers=layers,attempts=168,new_FaceOcc_forwards=run['forwards'],
        parent_successes=sum(r.get('parent_report',{}).get('status')=='success' for r in records),
        fits_attempted=sum('fit' in r and r['fit']['fit_intersection_pixels']>0 for r in records),
        nonclean_fits=sum('fit' in r and r['fit']['fit_intersection_pixels']>0 and r['case']['layer']!='clean' for r in records),
        new_variants=0,tree_fits=0,MST_fits=0,admissions=0,automatic_predictions=False,
        scoring_includes_missed_source_support=True,prior_packages_unchanged=True)
    write(OUT/'results.json',result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Distorted-input masks and recovery</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}</style>'+
        '<h1>Actual input masking: all168 retained</h1><p>Reference; distorted input; new correction green/lost source support pink; '+
        'previous fixed-alpha oracle; new input-alpha oracle. No learned predictions/admissions. Failed cases show unchanged input output. '+
        'All recovery scores use original source support, including missed regions. New support may affect previously protected pixels.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Source attribution</a></p>'+''.join(cards),encoding='utf-8')
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


def verify():
    plan=read(OUT/'inference_plan.json');manifest=read(OUT/'sha256.json');result=read(OUT/'results.json')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    assert all(sha(OUT/p)==h for p,h in manifest.items())
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    predictions={r['image_id']:r for r in read(OUT/'inference.json')['records']};replays=0
    clean_mask_parities=0
    for rec in result['records']:
        folder=OUT/rec['image_id'];sid=rec['source_id'];case=rec['case']['id']
        image=rgb(PARENT/sid/case/'distorted.png');reference=rgb(PARENT/sid/'reference.png')
        output=rgb(folder/'pipeline_output.png');source_alpha=np.load(SOURCE/sid/'alpha.npy',allow_pickle=False)
        assert metrics(output,reference,source_alpha>0)==rec['output_metrics_original_score']
        if rec.get('correction_available'):
            baseline=cv2.imread(str(folder/'baseline_mask.png'),0);bgr=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            points=np.load(folder/'landmarks.npy',allow_pickle=False)
            prediction=predictions[rec['image_id']];logits=np.load(OUT/prediction['logits_path'],allow_pickle=False)
            service=evaluate_parent(SimpleNamespace(report=rec['parent_report'],image=bgr,mask=baseline),points,template,lambda _:logits)
            assert service.report==rec['measurement_report']
            assert np.array_equal(service.mask,cv2.imread(str(folder/'measurement_mask.png'),0))
            preview=render_preview(bgr,baseline,cv2.imread(str(folder/'categories.png'),0),points,
                cv2.imread(str(folder/'visible_face.png'),0),glasses=rec['source_glasses_choice'])
            alpha=np.load(folder/'alpha.npy',allow_pickle=False)
            assert np.array_equal(preview.alpha,alpha)
            if rec['recovery_available']:assert np.array_equal(render_rgb8(image,alpha,rec['fit']['parameters']),output)
            if case=='clean':
                clean_mask_parities+=int(np.array_equal(preview.support.correction_mask,cv2.imread(str(SOURCE/sid/'correction_mask.png'),0)))
                assert np.array_equal(output,reference)
            replays+=1
        else:assert np.array_equal(output,image)
    destination=ROOT/'outputs/ffhq_distorted_input_support_verification_v1';destination.mkdir()
    report=dict(all_attempt_metrics_checks=168,saved_service_correction_replays=replays,
        clean_masks_equal_saved_source=clean_mask_parities,refits=0,new_inference=0,
        parent_manifest_sha256=sha(OUT/'sha256.json'),all_input_and_artifact_hashes_unchanged=True)
    write(destination/'verification.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true');parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    verify() if args.verify else finalize() if args.finalize else prepare()
