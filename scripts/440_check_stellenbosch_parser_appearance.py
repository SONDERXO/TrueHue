"""Single fixed parser-only CLAHE candidate; original-pixel measurements private."""
import argparse
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.segmentation_appearance_probe import parser_input,VERSION
from src.skin_masking.face_parsing_experiment import DenseFaceParser,facial_skin
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.faceocc_development import evaluate_parent
from src.model_training.facial_endpoint_features import facial_endpoint_features

BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
OUT=ROOT/'outputs/stellenbosch_parser_appearance_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def save(p,v):
    if not cv2.imwrite(str(p),v):raise IOError(str(p))

def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(BASE/'inference_plan.json')['input_sha256']
    bound.update({str(BASE/p):h for p,h in read(BASE/'sha256.json').items()})
    for rel in ['scripts/440_check_stellenbosch_parser_appearance.py','scripts/441_run_stellenbosch_appearance_logits.py',
        'src/skin_masking/segmentation_appearance_probe.py','tests/test_segmentation_appearance_probe.py',
        'docs/stellenbosch-parser-appearance-protocol-2026-11-05.md']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    effective=dict(version=VERSION,parent_effective_contract=read(BASE/'plan_PRIVATE.json')['effective_contract_sha256'],
        measurement_pixels='unchanged_original256',parser_copy_only=True,dependency_sha256=bound)
    identity=hashlib.sha256(json.dumps(effective,sort_keys=True).encode()).hexdigest()
    OUT.mkdir();(OUT/'logits').mkdir();write(OUT/'contract_PRIVATE.json',dict(contract=effective,sha256=identity))
    net=DenseFaceParser(ROOT/'models/face_parser_experimental_v1/resnet18.onnx')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    prior={r['image_id']:r for r in read(BASE/'inference.json')['records']}
    records=[];attempts=[];forwards=0
    for old in read(BASE/'results_PRIVATE.json')['records']:
        folder=OUT/old['case_id'];folder.mkdir();previous=BASE/old['case_id']
        image=cv2.imread(str(previous/'input.png'));original=image.copy()
        rec={k:old[k] for k in ['case_id','case_index','subject_index','subject_key','condition','source_path','source_mst_exact_decimal','source_mst_raw_type','source_mst_raw_value','sampling_stratum','input_bridge']}
        rec.update(status='failed',calibration_admitted=False,training_admitted=False,MST=None,baseline_status=old['status'])
        parent=dict(status='failed',stage='saved_detector',features=None)
        try:
            if not (previous/'landmarks.npy').exists():raise ValueError('Original detector failure retained; landmarks unavailable')
            points=np.load(previous/'landmarks.npy',allow_pickle=False)
            enhanced=parser_input(image);save(folder/'parser_input.png',enhanced)
            categories=net.categories_bgr(enhanced);forwards+=1;save(folder/'categories.png',categories)
            guard=nostril_guard(image.shape[:2],points)
            probe=(build_face_coverage(image,points).mask>0)&~guard
            oldcat=cv2.imread(str(previous/'categories.png'),0)
            rec['probe']=dict(pixels=int(probe.sum()),old_skin_nose=int((facial_skin(oldcat)&probe).sum()),
                new_skin_nose=int((facial_skin(categories)&probe).sum()))
            parent['stage']='semantic_mask'
            semantic=build_semantic_face_coverage(image,points,categories)
            mask=semantic.mask.copy();mask[guard]=0;save(folder/'parent_mask.png',mask)
            stats=compute_masked_lab_statistics(image,mask,1000)
            parent.update(stage='measurement',statistics=stats)
            if not stats['valid']:raise ValueError(stats['reason'])
            features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
            features.update(facial_endpoint_features(image,mask>0)['features'])
            parent.update(status='success',features=features)
            aligned,_,_=align_input(image,points,template);save(folder/'aligned.png',aligned)
            if old['case_id'] in prior:
                pred=prior[old['case_id']];assert pred['status']=='success'
                assert np.array_equal(aligned,cv2.imread(str(previous/'aligned.png')))
                path=BASE/pred['logits_path'];assert sha(path)==pred['logits_sha256']
                rec.update(logits_path=str(path),logits_sha256=sha(path),logits_reused=True)
            else:
                attempts.append(dict(image_id=old['case_id'],case_index=old['case_index'],aligned_path=str(folder/'aligned.png')))
                rec['logits_reused']=False
            rec['status']='inference_ready'
        except (ValueError,RuntimeError,cv2.error) as error:
            parent.update(status='failed',reason=str(error));rec['reason']=str(error)
        assert np.array_equal(image,original)
        rec['parent_report']=parent;records.append(rec)
        print(rec['case_id']+' '+rec['status'],flush=True)
    assert all(sha(p)==h for p,h in bound.items())
    write(OUT/'preparation_PRIVATE.json',dict(records=records,parser_forwards=forwards))
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))
    print(json.dumps(dict(parser_forwards=forwards,new_FaceOcc_requests=len(attempts),reused_logits=sum(r.get('logits_reused',False) for r in records)),indent=2))

def finalize():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert sha(OUT/'inference_plan.json')==run['plan_sha256']
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']}
    assert set(predictions)=={r['image_id'] for r in plan['attempts']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    data=read(OUT/'preparation_PRIVATE.json');records=data['records'];boards=[];replays=0;strata=defaultdict(Counter)
    for rec in records:
        folder=OUT/rec['case_id'];previous=BASE/rec['case_id'];image=cv2.imread(str(previous/'input.png'))
        if rec['status']=='inference_ready':
            if not rec['logits_reused']:
                pred=predictions[rec['case_id']]
                assert pred['status']=='success',pred
                rec['logits_path']=str(OUT/pred['logits_path']);rec['logits_sha256']=pred['logits_sha256']
            assert sha(rec['logits_path'])==rec['logits_sha256']
            logits=np.load(rec['logits_path'],allow_pickle=False);points=np.load(previous/'landmarks.npy',allow_pickle=False)
            mask=cv2.imread(str(folder/'parent_mask.png'),0)
            parent=SimpleNamespace(report=rec['parent_report'],image=image,mask=mask)
            result=evaluate_parent(parent,points,template,lambda _:logits)
            replay=evaluate_parent(parent,points,template,lambda _:logits)
            assert result.report==replay.report and np.array_equal(result.mask,replay.mask)
            assert np.array_equal(result.aligned,cv2.imread(str(folder/'aligned.png')))
            rec.update(status=result.report['status'],measurement_report=result.report)
            if result.mask is not None:
                save(folder/'measurement_mask.png',result.mask)
                native,accounting=native_projection(result.mask,rec['input_bridge']);save(folder/'native_grid.png',native);rec['native_accounting']=accounting
            replays+=1
        totals=strata[rec['sampling_stratum']];totals.update(attempts=1,baseline_success=int(rec['baseline_status']=='success'),candidate_success=int(rec['status']=='success'))
        if 'probe' in rec:totals.update(rec['probe'])
        oldmask=cv2.imread(str(previous/'measurement_mask.png'),0) if (previous/'measurement_mask.png').exists() else np.zeros(image.shape[:2],np.uint8)
        newmask=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros_like(oldmask)
        rec['mask_change']=dict(added=int(((newmask>0)&(oldmask==0)).sum()),lost=int(((oldmask>0)&(newmask==0)).sum()))
        enhanced=cv2.imread(str(folder/'parser_input.png')) if (folder/'parser_input.png').exists() else np.full_like(image,35)
        panels=[image,enhanced]
        for mask in [oldmask,newmask]:
            overlay=image.copy();sel=mask>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8);panels.append(overlay)
        delta=image.copy()
        if (folder/'categories.png').exists():
            oldcat=cv2.imread(str(previous/'categories.png'),0);newcat=cv2.imread(str(folder/'categories.png'),0)
            added=facial_skin(newcat)&~facial_skin(oldcat);delta[added]=np.rint(.6*image[added]+.4*np.array([255,0,255])).astype(np.uint8)
        panels.append(delta);board=np.hstack(panels);label=np.full((26,1280,3),255,np.uint8)
        cv2.putText(label,rec['case_id']+' '+rec['condition']+' '+rec['baseline_status']+' -> '+rec['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,board]))
    for i in range(10):save(OUT/f'contact_{i+1:02d}.png',np.vstack(boards[3*i:3*i+3]))
    summary=dict(attempts=30,parser_forwards=data['parser_forwards'],new_FaceOcc_forwards=run['forwards'],
        reused_FaceOcc_logits=sum(r.get('logits_reused',False) for r in records),saved_service_replays=replays,
        candidate_parent_successes=sum(r['parent_report']['status']=='success' for r in records),
        baseline_final_successes=sum(r['baseline_status']=='success' for r in records),candidate_final_successes=sum(r['status']=='success' for r in records),
        gained=sum(r['status']=='success' and r['baseline_status']!='success' for r in records),
        regressed=sum(r['status']!='success' and r['baseline_status']=='success' for r in records),
        by_preexisting_stratum={k:dict(v) for k,v in strata.items()},admissions=0,calibration_fits=0,tree_fits=0,
        original_pixel_measurement_only=True,native_adequacy_established=False,effective_contract_sha256=read(OUT/'contract_PRIVATE.json')['sha256'])
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private single parser appearance candidate</h1><p>Original; parser-only copy; old final mask; new final mask; new parser skin/nose additions (pink). Blank mask means unavailable. Original pixels only for measurement. No accuracy/admission claim; no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
