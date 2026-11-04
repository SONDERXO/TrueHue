"""Paper-method diagnostic: constrain color components to face geometry first."""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract
from src.skin_masking.skin_mask import create_candidate_mask_bgr
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.face_constrained_component import face_constrained_component,VERSION


def main():
    out=ROOT/'outputs/rule_mask_ordering_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/correction_training_preparation_v1'
    reviews=read(ROOT/'outputs/focused_mask_review24_import_v1/reconciled_reviews.json')
    prior={r['image_id']:r for r in (json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    baseline_hashes=read(parent/'verification.json')['evidence_sha256']
    config=get_config();base_spec,base_identity=contract(ROOT)
    tracked=[Path(__file__),ROOT/'docs/rule-mask-ordering-protocol.md',
        ROOT/'src/skin_masking/face_constrained_component.py',ROOT/'src/skin_masking/face_outline_experiment.py',
        ROOT/'outputs/focused_mask_review24_import_v1/reconciled_reviews.json',parent/'attempts.jsonl',
        ROOT/'outputs/focused_mask_review24_v1/reserved_training_check.json']
    tracked.extend(ROOT/p for p in base_spec['dependency_sha256'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in tracked}
    payload=dict(version=VERSION,baseline_measurement_contract=base_identity,input_sha256=hashes,
        policy='same HSV AND YCrCb; same landmarks; oval before component; existing anatomy exclusions',
        color_thresholds_changed=False,learned_segmentation_used=False)
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    reserved={r['image_id'] for r in read(tracked[6])['sources']}
    assert len(reviews)==24 and not reserved&{r['image_id'] for r in reviews}
    out.mkdir()
    for name in ['geometry','masks','boards']:(out/name).mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(contract=payload,contract_sha256=identity,selected_ids=[r['image_id'] for r in reviews],
        existing_mst_lookup_applicable=False,reserved_check_access=False))
    write('run_status.json',dict(status='running'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    records=[]
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def tile(image,label,mask=None):
        shown=image.copy()
        if mask is not None:
            support=mask>0;shown[support]=np.rint(.65*shown[support]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
        return shown
    try:
        for review in reviews:
            image_id=review['image_id'];name=review['source_id'];ref=prior[image_id]['reference_measurement']
            p=parent/'images'/f'{name}_reference.png';assert digest(p)==baseline_hashes[f'images/{name}_reference.png']
            image=cv2.imread(str(p));baseline_path=parent/'images'/f'{name}_reference_mask.png'
            baseline=cv2.imread(str(baseline_path),0) if baseline_path.exists() else np.zeros((256,256),np.uint8)
            if baseline_path.exists():assert digest(baseline_path)==baseline_hashes[f'images/{name}_reference_mask.png']
            clipped=np.zeros_like(baseline);candidate=np.zeros_like(baseline)
            record=dict(image_id=image_id,source_id=name,status='unavailable',baseline_decision=review['decision'],
                baseline_exact_notes=review['notes'],source_suitability='reject_monochrome_reference' if name=='55166' else 'not_newly_assessed',
                training_eligible=False,baseline_pixels=int(np.count_nonzero(baseline)))
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=image_id,phase='reviewed_training_rule_mask_comparison'))+'\n')
            try:
                if ref.get('face_count')!=1 or 'face_box' not in ref:raise ValueError('Exactly one existing-detector face required')
                box=tuple(ref['face_box']);x,y,w,h=box
                points,margin,_=prepare.detect_landmarks_with_margin(image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                if points is None:raise ValueError('Required landmarks unavailable; no semantic fallback')
                crop=image[y:y+h,x:x+w];color=create_candidate_mask_bgr(crop)
                _,oval=restrict_to_face_outline(np.full((h,w),255,np.uint8),points)
                exclusion=build_feature_exclusion_mask(crop,points,dilation=0)
                _,mouth=exclude_complete_mouth(np.full((h,w),255,np.uint8),points)
                exclusion=cv2.bitwise_or(exclusion,mouth)
                revised=face_constrained_component(color,oval,exclusion)
                candidate[y:y+h,x:x+w]=revised
                clipped[y:y+h,x:x+w]=cv2.bitwise_and(baseline[y:y+h,x:x+w],oval)
                for label,mask in [('colors',color),('oval',oval),('excluded',exclusion)]:save(out/'geometry'/f'{name}_{label}.png',mask)
                np.save(out/'geometry'/f'{name}_landmarks.npy',points)
                record.update(status='technical_support_available' if np.count_nonzero(candidate)>=1000 else 'insufficient_support',
                    face_box=list(box),landmark_margin=margin,
                    candidate_pixels_outside_oval=int(np.count_nonzero((revised>0)&(oval==0))),
                    candidate_excluded_anatomy_pixels=int(np.count_nonzero((revised>0)&(exclusion>0))))
            except (ValueError,RuntimeError,cv2.error) as error:record['reason']=str(error)
            record.update(candidate_pixels=int(np.count_nonzero(candidate)),clipped_baseline_pixels=int(np.count_nonzero(clipped)),
                added_pixels=int(np.count_nonzero((candidate>0)&(baseline==0))),removed_pixels=int(np.count_nonzero((baseline>0)&(candidate==0))))
            save(out/'masks'/f'{name}_candidate.png',candidate);save(out/'masks'/f'{name}_clipped.png',clipped)
            save(out/'boards'/f'{name}.png',np.hstack([tile(image,name+' reference'),tile(image,'Saved baseline',baseline),
                tile(image,'Baseline oval clip',clipped),tile(image,'Rule-ordering candidate',candidate)]))
            records.append(record)
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            print(name,record['status'],record['baseline_pixels'],'->',record['candidate_pixels'],flush=True)
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
        write('summary.json',dict(status='complete_diagnostic_not_promoted',sources=24,statuses=dict(Counter(r['status'] for r in records)),
            learned_segmentation_used=False,color_thresholds_changed=False,existing_mst_lookup_applicable=False,
            reserved_check_access=False,correction_models_fitted=0,candidate_ita_mst_calls=0,training_admissions=0))
        spec=dict(batch='rule_order24',manifest_sha256=digest(out/'plan.json'),review_scope='rule_ordering_reference_mask_only',
            panel_labels=['Reference','Saved baseline','Baseline oval clip','Rule-ordering candidate'],
            review_instructions='Rule-based diagnostic only. Same photos; no final mask adoption. Existing notes remain unchanged. Rightmost candidate retains original color thresholds.',
            records=[dict(image_id=r['image_id'],source_id=r['source_id'],status='pending_review' if r['status']=='technical_support_available' else r['status'],panel_count=4,
                failure_reason=r.get('reason'),comparison_note=f'Baseline: {r["baseline_decision"]}; {r["baseline_exact_notes"] or "no note"}. Status: {r["status"]}. Pixels {r["baseline_pixels"]} → {r["candidate_pixels"]}. Source: {r["source_suitability"]}.') for r in records])
        template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
        page=template.replace('__BATCH__','rule_order24').replace('__BATCH_LINKS__','Rule-based diagnostic').replace('__DATA__',json.dumps(spec).replace('<','\\u003c'))
        page=page.replace('href="review.html"','href="../focused_mask_review24_v1/review.html"',1).replace('All batches','Original review')
        page=page.replace('Training review · batch rule_order24','Rule-based mask comparison · same 24 photos')
        page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',spec['review_instructions'])
        (out/'review.html').write_text(page,encoding='utf-8');(out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
        write('run_status.json',dict(status='complete_diagnostic_not_promoted'))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)));raise


if __name__=='__main__':main()
