"""One saved-output scope/recovery candidate; no inference, fitting or admission."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.upper_face_measurement_candidate import build,VERSION
from src.skin_masking.fixed_face_input_bridge import native_projection
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.reference_point_review import compare_points
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
OUT=ROOT/'outputs/upper_face_measurement_candidate_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    for root in [PARENT,IMPORTED,REVIEW]:bound.update({str(root/p):h for p,h in read(root/'sha256.json').items()})
    for rel in ['scripts/465_check_upper_face_measurement.py','src/skin_masking/upper_face_measurement_candidate.py','tests/test_upper_face_measurement_candidate.py','docs/upper-face-measurement-protocol-2026-11-06.md']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    contract=dict(version=VERSION,parent_contract=read(PARENT/'contract_PRIVATE.json')['sha256'],
        rule='geometry_upper_to_nasal_base_without_features_nostrils_AND_visibility_AND_classes_0_1_10',
        scope_changed=True,dependency_sha256=bound)
    identity=hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()
    OUT.mkdir();(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    records=[];boards=[];predictions={};totals=defaultdict(Counter);replays=0
    for old in read(PARENT/'results_PRIVATE.json')['records']:
        folder=PARENT/old['case_id'];target=OUT/old['case_id'];target.mkdir();image=cv2.imread(str(folder/'input.png'))
        r={k:old[k] for k in ['case_id','subject_key','condition','sampling_stratum','source_mst_exact_decimal','input_bridge']}
        r.update(status='failed',baseline_status=old['status'],calibration_admitted=False,training_admitted=False,MST=None)
        previous=cv2.imread(str(folder/'measurement_mask.png'),0) if (folder/'measurement_mask.png').exists() else np.zeros((256,256),np.uint8)
        mask=np.zeros_like(previous);native=None
        if 'logits_path' in old:
            assert sha(PARENT/old['logits_path'])==old['logits_sha256']
            p=np.load(folder/'landmarks.npy',allow_pickle=False);cat=cv2.imread(str(folder/'categories.png'),0)
            logits=np.load(PARENT/old['logits_path'],allow_pickle=False);matrix=np.array(read(folder/'matrix.json'))
            mask,report=build(image,p,cat,logits,matrix);again,rr=build(image,p,cat,logits,matrix)
            assert np.array_equal(mask,again) and report==rr;replays+=1
            stats=compute_masked_lab_statistics(image,mask,1000)
            r.update(status='success' if stats['valid'] else 'failed',statistics=stats,mask_report=report,reason=None if stats['valid'] else stats['reason'])
            assert cv2.imwrite(str(target/'mask.png'),mask)
            native,account=native_projection(mask,old['input_bridge']);r['native_accounting']=account
            assert cv2.imwrite(str(target/'native_grid.png'),native)
        else:r['reason']=old.get('reason') or old.get('parent_report',{}).get('reason')
        predictions[old['case_id']]=native
        added=(mask>0)&(previous==0);lost=(previous>0)&(mask==0)
        r['change']=dict(added=int(added.sum()),lost=int(lost.sum()))
        panels=[image]
        for m in [previous,mask]:
            overlay=image.copy();sel=m>0;overlay[sel]=np.rint(.6*image[sel]+.4*np.array([0,255,0])).astype(np.uint8);panels.append(overlay)
        delta=image.copy();delta[added]=np.rint(.6*image[added]+.4*np.array([255,0,255])).astype(np.uint8)
        delta[lost]=np.rint(.6*image[lost]+.4*np.array([255,255,0])).astype(np.uint8);panels.append(delta)
        label=np.full((26,1024,3),255,np.uint8)
        cv2.putText(label,r['case_id']+' '+r['condition']+' '+old['status']+' -> '+r['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,np.hstack(panels)]));records.append(r)
        totals[r['sampling_stratum']].update(attempts=1,baseline_success=int(old['status']=='success'),candidate_success=int(r['status']=='success'))
    bindings=read(REVIEW/'prediction_bindings_PRIVATE.json');actual=read(IMPORTED/'actual_export_PRIVATE.json')
    native_predictions={}
    for review_id,binding in bindings.items():
        grid=predictions[binding['case_id']]
        if grid is None:native_predictions[review_id]=None
        else:
            x0,y0,x1,y1=binding['native_bounds'];native_predictions[review_id]=grid[y0:y1,x0:x1]>0
    point_result=compare_points(actual['rows'],native_predictions)
    oldpoints=read(IMPORTED/'comparison_PRIVATE.json')
    assert point_result['summary'].get('skin_available')==oldpoints['summary']['skin_available']
    assert point_result['summary'].get('unwanted_available')==oldpoints['summary']['unwanted_available']
    for i in range(10):assert cv2.imwrite(str(OUT/f'contact_{i+1:02d}.png'),np.vstack(boards[3*i:3*i+3]))
    summary=dict(attempts=30,baseline_successes=29,candidate_successes=sum(r['status']=='success' for r in records),
        technical_regressions=sum(r['baseline_status']=='success' and r['status']!='success' for r in records),
        saved_mask_replays=replays,added_normalized_pixels=sum(r['change']['added'] for r in records),lost_normalized_pixels=sum(r['change']['lost'] for r in records),
        by_descriptive_stratum={k:dict(v) for k,v in totals.items()},baseline_actual_points=oldpoints['summary'],candidate_actual_points=point_result['summary'],
        scope_changed=True,independent_validation=False,new_forwards=0,new_fits=0,admissions=0,effective_contract_sha256=identity)
    for name,value in [('results_PRIVATE.json',dict(summary=summary,records=records)),('actual_point_comparison_PRIVATE.json',point_result),('contract_PRIVATE.json',dict(contract=contract,sha256=identity))]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private single upper-face candidate</h1><p>Original; old whole-face measurement; candidate upper-face measurement; additions pink/losses cyan. Scope changes, including deliberate genuine lower-face skin losses. No skin truth/admission or new detail; no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
