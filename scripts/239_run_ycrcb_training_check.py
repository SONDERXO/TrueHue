"""Replay reviewed masks, then open the declared separate training-check phase."""
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
from src.ita_estimation.ycrcb_measurement import measure as candidate_measure,contract
from src.ita_estimation.square_measurement import measure as baseline_measure,MASK_VERSION
from src.distortion_generation.three_variant_recipe import render_rgb
from src.data_preparation.color_reference_quality import assess_color_reference


def main():
    out=ROOT/'outputs/ycrcb_training_check20_v1'
    if (out/'attempts.jsonl').exists() or (out/'run_status.json').exists():raise FileExistsError('Check already attempted')
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');frozen=read(out/'candidate_measurement_contract.json')
    assert contract(ROOT)[1]==plan['candidate_contract_sha256']==frozen['sha256']
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    assert digest(ROOT/'docs/ycrcb-training-check-protocol.md')==plan['protocol_sha256']
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    def landmark_provider(im,box):return prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)[0]
    def baseline_masker(im,box):
        x,y,w,h=box
        return prepare.compute_versioned_skin_mask(im[y:y+h,x:x+w],im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    # Verify packaging has not changed the candidate previously reviewed.
    development=ROOT/'outputs/color_cast_ycrcb_refinement_v1'
    for name,sha in read(development/'verification.json')['evidence_sha256'].items():assert digest(development/name)==sha
    rows=[json.loads(x) for x in (ROOT/'outputs/three_variant_training_candidates_v1/attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    rows={(r['source_image_id'],r['variant']):r for r in rows}
    replay_count=0
    for record in read(development/'attempts.json'):
        for frame,variant in [('reference','identity'),('color','color')]:
            row=rows[(record['image_id'],variant)];image=cv2.imread(str(ROOT/row['input_path']))
            measured=candidate_measure(image,detector,landmark_provider)
            expected=cv2.imread(str(development/'masks'/f'{record["source_id"]}_{frame}_candidate.png'),0)
            np.testing.assert_array_equal(measured.mask,expected);replay_count+=1
    assert replay_count==40
    write('development_replay.json',dict(status='pass',exact_reviewed_mask_parity=40,check_images_opened_before_pass=0))
    write('run_status.json',dict(status='running_check_phase_open'))
    for folder in ['images','boards']:(out/folder).mkdir()
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def panel(im,label,mask):
        shown=im.copy()
        if mask is not None:
            selected=mask>0;shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown
    parent=ROOT/'outputs/correction_training_preparation_v1'
    old=read(parent/'verification.json')['evidence_sha256'];records=[]
    try:
        for selected in plan['selected']:
            image_id=selected['image_id'];name=Path(image_id).stem
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=image_id,
                phase='frozen_candidate_training_mask_check',origin=selected['check_origin'],candidate_contract_sha256=frozen['sha256']))+'\n')
            relative=f'images/{name}_reference.png';p=parent/relative
            assert digest(p)==old[relative]
            reference=cv2.imread(str(p));assert reference.shape==(256,256,3)
            quality=assess_color_reference(reference)
            shifted_rgb,clipping=render_rgb(cv2.cvtColor(reference,cv2.COLOR_BGR2RGB),'medium','color')
            shifted=cv2.cvtColor(shifted_rgb,cv2.COLOR_RGB2BGR)
            save(out/'images'/f'{name}_reference.png',reference);save(out/'images'/f'{name}_color.png',shifted)
            frames={};panels=[]
            for frame,image in [('reference',reference),('color',shifted)]:
                baseline=baseline_measure(image,detector,baseline_masker)
                candidate=candidate_measure(image,detector,landmark_provider)
                for arm,result in [('baseline',baseline),('candidate',candidate)]:
                    if result.mask is not None:save(out/'images'/f'{name}_{frame}_{arm}_mask.png',result.mask)
                frames[frame]=dict(baseline=baseline.report,candidate=candidate.report,
                    candidate_mask_available=candidate.mask is not None,
                    candidate_pixels=int(np.count_nonzero(candidate.mask)) if candidate.mask is not None else 0)
                panels.extend([panel(image,name+' '+frame,None),panel(image,frame+' baseline',baseline.mask),panel(image,frame+' YCrCb candidate',candidate.mask)])
            save(out/'boards'/f'{name}.png',np.hstack(panels))
            record=dict(image_id=image_id,source_id=name,duplicate_group_id=selected['duplicate_group_id'],
                check_origin=selected['check_origin'],reference_sha256=digest(p),source_quality=quality,
                color_probe='fixed global medium color-only diagnostic; no assigned MST category',
                color_probe_clipping=clipping,frames=frames,human_decision='pending',training_eligible=False)
            records.append(record)
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            print(name,{f:frames[f]['candidate']['status'] for f in frames},flush=True)
        assert contract(ROOT)[1]==frozen['sha256']
        summary=dict(status='check_complete_pending_human_review',sources=20,development_replay_parity=40,
            candidate_contract_sha256=frozen['sha256'],candidate_reference_statuses=dict(Counter(r['frames']['reference']['candidate']['status'] for r in records)),
            candidate_color_statuses=dict(Counter(r['frames']['color']['candidate']['status'] for r in records)),
            baseline_reference_statuses=dict(Counter(r['frames']['reference']['baseline']['status'] for r in records)),
            baseline_color_statuses=dict(Counter(r['frames']['color']['baseline']['status'] for r in records)),
            exact_monochrome_sources=[r['source_id'] for r in records if r['source_quality']['exact_achromatic']],
            mst_lookup_calls=0,tree_fits=0,training_admissions=0,final_validation_test_access=False,
            source_exposure='Already processed training sources; now exposed to frozen-candidate check, not a final evaluation')
        write('summary.json',summary)
        data=dict(batch='ycrcb_check20',manifest_sha256=digest(out/'plan.json'),review_scope='frozen_candidate_reference_and_global_color_check_only',
            panel_labels=['Reference photo','Reference baseline','Reference YCrCb candidate','Global color probe','Probe baseline','Probe YCrCb candidate'],
            review_instructions='Review candidate masks in panels3and6. Accept only if both masks AND source photo are usable; reject or uncertain otherwise. Note source issues separately. Failed detection/landmarks do not get a forced mask. No candidate change has been made from these outcomes.',
            records=[dict(image_id=r['image_id'],source_id=r['source_id'],panel_count=6,
                status='pending_review' if all(r['frames'][f]['candidate']['status']=='success' for f in ['reference','color']) else 'pipeline_failed',
                failure_reason='; '.join(f+': '+r['frames'][f]['candidate'].get('reason','success') for f in ['reference','color'] if r['frames'][f]['candidate']['status']!='success') or None,
                comparison_note='Source check: '+r['source_quality']['status']+'. Candidate: reference '+r['frames']['reference']['candidate']['status']+', color '+r['frames']['color']['candidate']['status']+'. This is a separate training check, not final testing.') for r in records])
        template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
        page=template.replace('__BATCH__','ycrcb_check20').replace('__BATCH_LINKS__','Frozen policy · separate20-source check').replace('__DATA__',json.dumps(data).replace('<','\\u003c'))
        page=page.replace('href="review.html"','href="../color_cast_ycrcb_refinement_v1/review.html"',1).replace('All batches','Development review')
        page=page.replace('Training review · batch ycrcb_check20','Frozen YCrCb mask check · 20 photos')
        page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',data['review_instructions'])
        page=page.replace('#panels{display:grid;grid-template-columns:repeat(4,','#panels{display:grid;grid-template-columns:repeat(3,')
        (out/'review.html').write_text(page,encoding='utf-8');(out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
        write('run_status.json',dict(status='check_complete_pending_human_review'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)));raise


if __name__=='__main__':main()
