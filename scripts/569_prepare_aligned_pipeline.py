"""Frozen original-frame preflight and actual-input normalized mask preparation."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,importlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2,numpy as np
from scipy.io import loadmat
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import measure
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.fixed_face_input_bridge import crop_face
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.model_training.photographic_target_diagnostic import case_matrix,distort
OUT=ROOT/'outputs/aligned_correction_preparation_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))

def initialize():
    cfg=get_config();helper=importlib.import_module('11_prepare_training_manifests')
    parser=DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    detector=lambda im:helper._detect_face_boxes(im,ROOT/cfg.FACE_MODEL_PATH,.85)
    def parent(im):
        cache={}
        def landmarks(image,box):
            p,margin,status=helper.detect_landmarks_with_margin(image,box,ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cache['landmark_details']=dict(margin=margin,status=status)
            cache['points']=None if p is None else p+np.array(box[:2]);return cache['points']
        class Parser:
            def categories_bgr(self,image):
                cache['categories']=parser.categories_bgr(image);return cache['categories']
        return measure(im,detector,landmarks,Parser()),cache
    return detector,parent

def plan():
    if (OUT/'plan_PRIVATE.json').exists():return read(OUT/'plan_PRIVATE.json')
    if OUT.exists():raise FileExistsError('Unbound output folder exists')
    paths=[ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json',ROOT/'outputs/frozen_split_subject_check_v1/results_PRIVATE.json']
    rows=[]
    for cohort,path in zip(('development','later'),paths):
        for r in read(path)['records']:
            rows.append(dict(source_case=r['case_id'],cohort=cohort,subject_id=r['subject_key'],condition=r['condition'],source_path=r['source_path'],source_sha256=r['source_sha256'],source_mst_exact_decimal=r['source_mst_exact_decimal']))
    assert len(rows)==54 and not ({r['subject_id'] for r in rows if r['cohort']=='development'} & {r['subject_id'] for r in rows if r['cohort']=='later'})
    helper=importlib.import_module('419_preview_object_protected_face');bound,identity=helper.dependencies()
    deps=paths+[Path(__file__),ROOT/'docs/aligned-correction-pipeline-protocol-2026-11-07.md',ROOT/'src/skin_masking/fixed_face_input_bridge.py',ROOT/'src/model_training/aligned_correction_support.py',ROOT/'src/model_training/photographic_target_diagnostic.py']
    bound.update({str(p):sha(p) for p in deps});bound.update({r['source_path']:r['source_sha256'] for r in rows})
    assert all(sha(p)==h for p,h in bound.items())
    contract=dict(version='actual_input_native_face1p5_desktop_raw_masks_blended_native_v1',desktop_measurement_contract=identity,anchor_threshold=.85,face_context=1.5,minimum_pixels=1000,parser_appearance='original_not_CLAHE',FaceOcc_appearance='original_aligned_not_CLAHE',glasses='uncertain',scientific_admission=False)
    digest=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    result=dict(sources=rows,input_sha256=bound,contract=contract,measurement_contract_sha256=digest,recipes=case_matrix(),attempts=756,training_admitted=False,calibration_admitted=False)
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',result);return result

def preflight():
    frozen=plan();target=OUT/'fullframe_preflight_PRIVATE.json'
    if target.exists():raise FileExistsError('Full-frame preflight exists; no repeat forwards')
    _,parent=initialize();records=[];base=OUT/'fullframe_preflight';base.mkdir()
    for s in frozen['sources']:
        folder=base/s['source_case'];folder.mkdir()
        image=cv2.imread(s['source_path']);result,cache=parent(image)
        if result.image is not None:save(folder/'input.png',result.image)
        if result.mask is not None:save(folder/'mask.png',result.mask)
        r=dict(source_case=s['source_case'],cohort=s['cohort'],subject_id=s['subject_id'],report=result.report)
        write(folder/'report_PRIVATE.json',r);records.append(r)
        print('Full-frame parent:',s['source_case'],result.report['status'],result.report.get('skin_pixels'),flush=True)
    summary=dict(attempts=54,parent_success=sum(r['report']['status']=='success' for r in records),failure_stages=dict(Counter(r['report']['stage'] for r in records if r['report']['status']!='success')),new_FaceOcc_forwards=0,new_fits=0)
    write(target,dict(summary=summary,records=records));assert all(sha(p)==h for p,h in frozen['input_sha256'].items());print(json.dumps(summary),flush=True)

def prepare():
    frozen=plan()
    if not (OUT/'fullframe_preflight_PRIVATE.json').exists():raise ValueError('Complete full-frame preflight first')
    if (OUT/'preparation_PRIVATE.json').exists() or (OUT/'cases').exists():raise FileExistsError('Preparation exists; preserve partial artifacts, no repeat inference')
    detector,parent=initialize();template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    base=OUT/'cases';base.mkdir();(OUT/'references').mkdir();(OUT/'logits').mkdir();records=[];attempts=[];count=0
    for s in frozen['sources']:
        original=cv2.imread(s['source_path']);assert original is not None and sha(s['source_path'])==s['source_sha256']
        ref=OUT/'references'/(s['source_case']+'.png');save(ref,original)
        for case in frozen['recipes']:
            count+=1;cid=s['source_case']+'__'+case['id'];folder=base/cid;folder.mkdir()
            scene,recipe,role=distort(cv2.cvtColor(original,cv2.COLOR_BGR2RGB),np.ones(original.shape[:2]),case)
            image=cv2.cvtColor(scene,cv2.COLOR_RGB2BGR);save(folder/'scene_input.png',image)
            r=dict(s,case_id=cid,case_index=count,recipe=case['id'],layer=case['layer'],distortion=recipe,status='failed',stage='actual_input_anchor',scene_path=str(folder/'scene_input.png'),reference_path=str(ref),training_admitted=False,calibration_admitted=False)
            try:
                anchors=detector(cv2.resize(image,(256,256),interpolation=cv2.INTER_LINEAR));r['anchor_face_count']=len(anchors)
                if len(anchors)!=1:raise ValueError('Exactly one actual-input anchor face required')
                native,bridge=crop_face(image,anchors[0]);r['input_bridge']=bridge;save(folder/'native_input.png',native)
                result,cache=parent(native);r['stage']='parent_measurement';r['parent_report']=result.report
                if result.image is not None:save(folder/'input.png',result.image)
                if result.mask is not None:save(folder/'parent_mask.png',result.mask)
                if cache.get('points') is not None:np.save(folder/'landmarks.npy',cache['points'],allow_pickle=False)
                if 'categories' in cache:save(folder/'categories.png',cache['categories'])
                r['landmark_details']=cache.get('landmark_details')
                if result.report['status']!='success':raise ValueError(result.report.get('reason','Parent measurement failed'))
                aligned,matrix,details=align_input(result.image,cache['points'],template)
                save(folder/'aligned.png',aligned);write(folder/'matrix.json',matrix.tolist());r['alignment']=details
                attempts.append(dict(image_id=cid,case_index=count,aligned_path=str(folder/'aligned.png')))
                r['status']='inference_ready';r['stage']='FaceOcc_pending'
            except (ValueError,RuntimeError,cv2.error) as e:r['reason']=str(e)
            write(folder/'preparation_PRIVATE.json',r);records.append(r)
        print('Prepared actual inputs:',s['source_case'],count,'/756;',len(attempts),'FaceOcc-ready',flush=True)
    assert count==756 and all(sha(p)==h for p,h in frozen['input_sha256'].items())
    write(OUT/'preparation_PRIVATE.json',dict(records=records,attempts=756,inference_ready=len(attempts)))
    bound=dict(frozen['input_sha256']);bound[str(OUT/'plan_PRIVATE.json')]=sha(OUT/'plan_PRIVATE.json')
    for a in attempts:bound[a['aligned_path']]=sha(a['aligned_path'])
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--preflight',action='store_true')
    preflight() if cli.parse_args().preflight else prepare()
