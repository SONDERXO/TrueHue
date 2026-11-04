"""Frozen lighter qualitative cycle; saved original set, no tuning or fits."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from scipy.io import loadmat
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import contract,measure
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.ita_estimation.faceocc_veto_candidate import combine_saved

OUT=ROOT/'outputs/faceocc_light_comparison_v1'
ANNOT=ROOT/'outputs/faceocc_broader_annotation_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=read(ANNOT/'manifest.json');selection=read(ANNOT/'selection.json')
    available={r['image_id']:r for r in manifest['rows']}
    user_ids=[r['image_id'] for r in selection['rows'] if r['lane']=='exposed_challenge']
    assert len(user_ids)==4 and len(selection['rows'])==24
    paths=[ANNOT/'manifest.json',ANNOT/'selection.json',Path(__file__),ROOT/'scripts/376_run_faceocc_light_logits.py',
        ROOT/'docs/faceocc-light-review-amendment-2026-11-01.md',ROOT/'models/faceocc_candidate_v1/model.safetensors',
        ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat',
        ROOT/'src/skin_masking/faceocc_mediapipe_bridge.py',ROOT/'src/skin_masking/faceocc_coordinates.py',
        ROOT/'src/ita_estimation/faceocc_veto_candidate.py']
    hashes={str(p):digest(p) for p in paths}
    for r in manifest['rows']:
        p=ANNOT/r['image_path'];assert digest(p)==r['image_sha256'];hashes[str(p)]=digest(p)
    for name in ['continuous_correction_r2','seamless_support_v5']:
        for p in (ROOT/'outputs'/name).rglob('*'):
            if p.is_file():hashes[str(p)]=digest(p)
    spec,identity=contract(ROOT)
    OUT.mkdir();(OUT/'logits').mkdir()
    (OUT/'plan.json').write_text(json.dumps(dict(status='frozen_before_predictions',rows=selection['rows'],
        user_review_ids=user_ids,measurement_contract_sha256=identity,parent_contract=spec,
        input_sha256=hashes,technical_failures=manifest['technical_failures'],
        design='qualitative_assistant_all_user_four_no_polygon_groundtruth',fits=0),indent=2))
    prep=importlib.import_module('11_prepare_training_manifests');config=get_config();cache={}
    detector=lambda im:prep._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def landmarks(im,box):
        p,_,_=prep.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        cache['points']=None if p is None else p+np.array(box[:2]);return cache['points']
    class Parser:
        def __init__(self):self.net=DenseFaceParser(ROOT/config.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx');self.last=None
        def categories_bgr(self,im):self.last=self.net.categories_bgr(im);return self.last
    parser=Parser();template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];inference=[]
    for index,row in enumerate(selection['rows'],1):
        rec=dict(image_id=row['image_id'],lane=row['lane'],case_index=index,admitted=False)
        if row['image_id'] not in available:
            rec.update(status='source_unavailable',reason='Original MP4 still-image decode failure retained');records.append(rec);continue
        r=available[row['image_id']];image=cv2.imread(str(ANNOT/r['image_path']))
        cache.clear();parser.last=None
        with (OUT/'access_ledger.jsonl').open('a') as f:f.write(json.dumps(dict(image_id=row['image_id'],role=row['role'],phase='frozen_qualitative_baseline_and_bridge'))+'\n')
        result=measure(image,detector,landmarks,parser)
        rec.update(parent_report=result.report,status=result.report['status'])
        folder=OUT/('case_'+str(index));folder.mkdir();assert cv2.imwrite(str(folder/'input.png'),image)
        if result.report['status']=='success':
            assert cv2.imwrite(str(folder/'baseline_mask.png'),result.mask)
            assert cv2.imwrite(str(folder/'categories.png'),parser.last);np.save(folder/'landmarks.npy',cache['points'])
            try:
                aligned,matrix,bridge=align_input(image,cache['points'],template)
                assert cv2.imwrite(str(folder/'aligned.png'),aligned)
                rec.update(status='inference_ready',matrix=matrix.tolist(),bridge_report=bridge)
                inference.append(dict(image_id=row['image_id'],case_index=index,aligned_path=str(folder/'aligned.png')))
            except ValueError as error:rec.update(status='alignment_failed',reason=str(error))
        else:rec['reason']=result.report.get('reason')
        rec['saved_sha256']={str(p):digest(p) for p in folder.iterdir()}
        records.append(rec)
        with (OUT/'baseline_records.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
        print(str(index)+'/24: '+rec['status'],flush=True)
    assert contract(ROOT)[1]==identity and all(digest(p)==h for p,h in hashes.items())
    (OUT/'baseline.json').write_text(json.dumps(dict(records=records),indent=2))
    inference_hashes=dict(hashes)
    for r in records:inference_hashes.update(r.get('saved_sha256',{}))
    (OUT/'inference_plan.json').write_text(json.dumps(dict(attempts=inference,input_sha256=inference_hashes,
        original_attempts=24,user_review_ids=user_ids),indent=2))


def finalize():
    if (OUT/'summary.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'plan.json');baseline=read(OUT/'baseline.json');ip=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==digest(OUT/'inference_plan.json')
    assert all(digest(p)==h for p,h in ip['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']};records=[];cards=[];boards=[]
    for old in baseline['records']:
        rec=dict(old);i=rec['case_index'];folder=OUT/('case_'+str(i))
        if old['status']=='inference_ready':
            pred=predictions[old['image_id']]
            if pred['status']=='success':
                lp=OUT/pred['logits_path'];assert digest(lp)==pred['logits_sha256']
                image=cv2.imread(str(folder/'input.png'));mask=cv2.imread(str(folder/'baseline_mask.png'),0)
                candidate,visible,report=combine_saved(image,mask,np.load(lp),np.array(old['matrix']))
                assert not candidate[mask==0].any()
                rec.update(status=report['status'],candidate_report=report)
                for name,array in [('candidate_mask.png',candidate),('mapped_visible.png',visible)]:assert cv2.imwrite(str(folder/name),array)
                panels=[]
                for sel in [mask>0,candidate>0]:
                    shown=image.copy();shown[sel]=np.rint(.5*shown[sel]+.5*np.array([0,255,0])).astype(np.uint8);panels.append(shown)
                board=np.hstack([image]+panels);assert cv2.imwrite(str(folder/'board.png'),board)
                rec['board_path']='case_'+str(i)+'/board.png';rec['candidate_sha256']=digest(folder/'candidate_mask.png')
                label=np.full((25,768,3),255,np.uint8)
                cv2.putText(label,str(i)+' '+old['image_id']+' '+str(round(report['retained_fraction']*100,1))+'%',(4,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
                boards.append(np.vstack((label,board)))
                cards.append('<h2>'+str(i)+' '+old['image_id']+'</h2><img src="'+rec['board_path']+'">')
            else:rec.update(status='model_failed',reason=pred['reason'])
        if 'board_path' not in rec:cards.append('<h2>'+str(i)+' '+old['image_id']+'</h2><p>'+rec['status']+': '+str(rec.get('reason'))+'</p>')
        records.append(rec)
    for i in range(0,len(boards),4):cv2.imwrite(str(OUT/('contact_'+str(i//4+1)+'.png')),np.vstack(boards[i:i+4]))
    assert all(digest(p)==h for p,h in ip['input_sha256'].items())
    summary=dict(records=records,attempts=24,model_outputs=len(run['records']),
        candidate_available=sum(r['status']=='success' for r in records),
        user_review_ids=plan['user_review_ids'],qualitative_only=True,adopted=False,fits=0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    (OUT/'all_results.html').write_text('<!doctype html><meta charset="utf-8"><title>Full qualitative comparison</title><style>body{font:18px system-ui;max-width:1200px;margin:auto;padding:20px}img{width:100%}</style><h1>All24attempts: original / previous measurement / +FaceOcc</h1><p>No dense ground truth or accuracy claim. Fixed user subset was selected before predictions. All failures retained.</p>'+''.join(cards),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))


if __name__=='__main__':finalize() if '--finalize' in sys.argv else prepare()
