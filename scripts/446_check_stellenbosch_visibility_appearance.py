"""One fixed enhanced aligned recognition input, original-pixel measurement."""
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
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.faceocc_development import evaluate_parent

BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PARENT=ROOT/'outputs/stellenbosch_parser_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')
def save(p,v):
    if not cv2.imwrite(str(p),v):raise IOError(str(p))

def prepare():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for rel in ['scripts/446_check_stellenbosch_visibility_appearance.py','scripts/447_run_stellenbosch_visibility_appearance_logits.py',
        'docs/stellenbosch-faceocc-appearance-protocol-2026-11-05.md','src/skin_masking/segmentation_appearance_probe.py','tests/test_segmentation_appearance_probe.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    effective=dict(version='original_alignment_then_recognition_only_'+VERSION,
        parent_contract_sha256=read(PARENT/'contract_PRIVATE.json')['sha256'],measurement='original_pixels',
        geometry_parent_and_threshold_unchanged=True,dependency_sha256=bound)
    identity=hashlib.sha256(json.dumps(effective,sort_keys=True).encode()).hexdigest()
    OUT.mkdir();(OUT/'logits').mkdir();write(OUT/'contract_PRIVATE.json',dict(contract=effective,sha256=identity))
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    attempts=[]
    rows=read(PARENT/'results_PRIVATE.json')['records']
    for row in rows:
        if row['parent_report']['status']!='success':continue
        assert 'measurement_report' in row
        folder=OUT/row['case_id'];folder.mkdir();original=BASE/row['case_id']
        image=cv2.imread(str(original/'input.png'));points=np.load(original/'landmarks.npy',allow_pickle=False)
        aligned,matrix,_=align_input(image,points,template)
        assert np.array_equal(aligned,cv2.imread(str(PARENT/row['case_id']/'aligned.png')))
        enhanced=parser_input(aligned);save(folder/'aligned_original.png',aligned);save(folder/'aligned_candidate.png',enhanced)
        write(folder/'matrix.json',matrix.tolist())
        attempts.append(dict(image_id=row['case_id'],case_index=row['case_index'],aligned_path=str(folder/'aligned_candidate.png')))
    assert len(rows)==30 and len(attempts)==25 and all(sha(p)==h for p,h in bound.items())
    for p in OUT.rglob('*'):
        if p.is_file():bound[str(p)]=sha(p)
    write(OUT/'inference_plan.json',dict(attempts=attempts,input_sha256=bound))
    print('Frozen30 attempts /25candidate original-alignment recognition inputs /5retained early failures.')

def finalize():
    if (OUT/'results_PRIVATE.json').exists():raise FileExistsError('Already finalized')
    plan=read(OUT/'inference_plan.json');run=read(OUT/'inference.json')
    assert run['plan_sha256']==sha(OUT/'inference_plan.json') and all(sha(p)==h for p,h in plan['input_sha256'].items())
    predictions={r['image_id']:r for r in run['records']}
    assert set(predictions)=={r['image_id'] for r in plan['attempts']}
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];boards=[];totals=defaultdict(Counter);replays=0
    for old in read(PARENT/'results_PRIVATE.json')['records']:
        rec={k:old[k] for k in ['case_id','case_index','subject_index','subject_key','condition','source_path','source_mst_exact_decimal','source_mst_raw_value','source_mst_raw_type','sampling_stratum','input_bridge','parent_report']}
        rec.update(status='failed',baseline_status=old['status'],calibration_admitted=False,training_admitted=False,MST=None)
        original=BASE/rec['case_id'];folder=OUT/rec['case_id'];prior=PARENT/rec['case_id']
        image=cv2.imread(str(original/'input.png'));empty=np.zeros(image.shape[:2],np.uint8)
        oldmask=cv2.imread(str(prior/'measurement_mask.png'),0) if (prior/'measurement_mask.png').exists() else empty
        newmask=empty.copy();aligned=enhanced=np.full_like(image,35)
        if old['parent_report']['status']=='success':
            pred=predictions[rec['case_id']]
            aligned=cv2.imread(str(folder/'aligned_original.png'));enhanced=cv2.imread(str(folder/'aligned_candidate.png'))
            if pred['status']=='success':
                path=OUT/pred['logits_path'];assert sha(path)==pred['logits_sha256']
                logits=np.load(path,allow_pickle=False);points=np.load(original/'landmarks.npy',allow_pickle=False)
                parent=SimpleNamespace(report=old['parent_report'],image=image,mask=cv2.imread(str(prior/'parent_mask.png'),0))
                def predictor(actual):
                    assert np.array_equal(actual,aligned) and np.array_equal(parser_input(actual),enhanced)
                    return logits
                result=evaluate_parent(parent,points,template,predictor)
                replay=evaluate_parent(parent,points,template,predictor)
                assert result.report==replay.report and np.array_equal(result.mask,replay.mask)
                assert np.array_equal(result.matrix,np.array(read(folder/'matrix.json')))
                if result.mask is not None:
                    newmask=result.mask;save(folder/'measurement_mask.png',newmask)
                    native,counts=native_projection(newmask,rec['input_bridge']);save(folder/'native_grid.png',native);rec['native_accounting']=counts
                    assert not newmask[parent.mask==0].any()
                rec.update(status=result.report['status'],measurement_report=result.report,logits_path=str(path),logits_sha256=pred['logits_sha256']);replays+=1
            else:rec.update(status='model_failed',reason=pred['reason'])
        else:rec['reason']=old.get('reason') or old['parent_report'].get('reason')
        added=(newmask>0)&(oldmask==0);lost=(oldmask>0)&(newmask==0)
        rec['mask_change']=dict(added=int(added.sum()),lost=int(lost.sum()))
        cell=totals[rec['sampling_stratum']];cell.update(attempts=1,old_success=int(old['status']=='success'),new_success=int(rec['status']=='success'))
        panels=[image,aligned,enhanced]
        for mask in [oldmask,newmask]:
            overlay=image.copy();sel=mask>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8);panels.append(overlay)
        delta=image.copy();delta[added]=np.rint(.6*image[added]+.4*np.array([255,0,255])).astype(np.uint8)
        delta[lost]=np.rint(.6*image[lost]+.4*np.array([255,255,0])).astype(np.uint8);panels.append(delta)
        label=np.full((26,1536,3),255,np.uint8)
        cv2.putText(label,rec['case_id']+' '+rec['condition']+' '+old['status']+' -> '+rec['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,np.hstack(panels)]));records.append(rec)
    for i in range(10):save(OUT/f'contact_{i+1:02d}.png',np.vstack(boards[3*i:3*i+3]))
    summary=dict(attempts=30,FaceOcc_candidate_forwards=run['forwards'],unchanged_early_failures=5,saved_service_replays=replays,
        baseline_successes=sum(r['baseline_status']=='success' for r in records),candidate_successes=sum(r['status']=='success' for r in records),
        gained=sum(r['status']=='success' and r['baseline_status']!='success' for r in records),regressed=sum(r['status']!='success' and r['baseline_status']=='success' for r in records),
        added_normalized_pixels=sum(r['mask_change']['added'] for r in records),lost_normalized_pixels=sum(r['mask_change']['lost'] for r in records),
        by_preexisting_stratum={k:dict(v) for k,v in totals.items()},calibration_fits=0,tree_fits=0,admissions=0,original_pixel_measurement_only=True,
        effective_contract_sha256=read(OUT/'contract_PRIVATE.json')['sha256'])
    write(OUT/'results_PRIVATE.json',dict(summary=summary,records=records))
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private aligned FaceOcc appearance candidate</h1><p>Original; aligned original; aligned enhanced model input; old final green; new final green; additions pink/losses cyan. Unavailable stages blank. No skin-truth/admission claim. Research only; do not redistribute.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in plan['input_sha256'].items())
    write(OUT/'sha256.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
