"""Remove only HSV intersection on20color inputs and their20reference controls."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.evaluation.mask_support_quality import support_retention


def main():
    out=ROOT/'outputs/color_cast_ycrcb_refinement_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    source=ROOT/'outputs/three_variant_training_candidates_v1'
    for name,sha in read(source/'verification.json')['evidence_sha256'].items():assert digest(source/name)==sha
    rows=[json.loads(x) for x in (source/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    selected=[r for r in rows if r['variant']=='color'];controls={r['source_image_id']:r for r in rows if r['variant']=='identity'}
    assert len(selected)==20
    prior={r['image_id']:r for r in (json.loads(x) for x in (ROOT/'outputs/correction_training_preparation_v1/attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    config=get_config();spec,identity=contract(ROOT)
    paths=[Path(__file__),ROOT/'docs/color-cast-ycrcb-refinement-protocol.md',source/'verification.json',source/'attempts.jsonl',
        ROOT/'src/skin_masking/ycrcb_candidate.py',ROOT/'src/skin_masking/face_outline_experiment.py',ROOT/'src/evaluation/mask_support_quality.py']
    paths.extend(ROOT/p for p in spec['dependency_sha256'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for name in ['geometry','masks','boards']:(out/name).mkdir()
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_refinement',selected_ids=[r['source_image_id'] for r in selected],
        candidate='face_ycrcb_only_existing_exclusions_v1',input_sha256=hashes,
        old_measurement_contract_sha256=identity,candidate_mst_lookup_applicable=False,models_fitted=0))
    prepare=importlib.import_module('11_prepare_training_manifests');records=[];parity=0
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def panel(im,label,mask=None):
        shown=im.copy()
        if mask is not None:
            selected=mask>0;shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
        return shown
    for row in selected:
        image_id=row['source_image_id'];name=row['source_id'];control=controls[image_id]
        ref_mask=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0
        frames={};metrics={}
        for frame,frame_row,report in [('reference',control,prior[image_id]['reference_measurement']),('color',row,row['measurement'])]:
            image=cv2.imread(str(ROOT/frame_row['input_path']));baseline=cv2.imread(str(ROOT/frame_row['input_mask_path']),0)
            candidate=np.zeros_like(baseline);record=dict(status='unavailable')
            with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=image_id,frame=frame,phase='training_ycrcb_refinement'))+'\n')
            try:
                if report.get('face_count')!=1:raise ValueError('Exactly one frame-local face required')
                box=tuple(report['face_box']);x,y,w,h=box
                points,margin,_=prepare.detect_landmarks_with_margin(image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                if points is None:raise ValueError('Frame-local landmarks unavailable')
                crop=image[y:y+h,x:x+w]
                colors=create_candidate_mask_bgr(crop);y_colors=ycrcb_color_candidate(crop)
                excluded=build_feature_exclusion_mask(crop,points,dilation=0)
                _,mouth=exclude_complete_mouth(np.full((h,w),255,np.uint8),points);excluded=cv2.bitwise_or(excluded,mouth)
                _,oval=restrict_to_face_outline(np.full((h,w),255,np.uint8),points)
                rebuilt=np.zeros_like(baseline);rebuilt[y:y+h,x:x+w]=cv2.bitwise_and(keep_largest_connected_component(colors),cv2.bitwise_not(excluded))
                np.testing.assert_array_equal(rebuilt,baseline);parity+=1
                candidate[y:y+h,x:x+w]=cv2.bitwise_and(keep_largest_connected_component(y_colors),cv2.bitwise_not(excluded))
                full_oval=np.zeros_like(baseline);full_oval[y:y+h,x:x+w]=oval
                for suffix,mask in [('and_colors',colors),('ycrcb_colors',y_colors),('excluded',excluded),('oval',oval)]:save(out/'geometry'/f'{name}_{frame}_{suffix}.png',mask)
                record.update(status='available',face_box=list(box),landmark_margin=margin,
                    baseline_pixels=int(np.count_nonzero(baseline)),candidate_pixels=int(np.count_nonzero(candidate)),
                    baseline_outside_oval_pixels=int(np.count_nonzero((baseline>0)&(full_oval==0))),
                    candidate_outside_oval_pixels=int(np.count_nonzero((candidate>0)&(full_oval==0))),
                    baseline_screen=support_retention(ref_mask,baseline>0,baseline>0),
                    candidate_screen=support_retention(ref_mask,candidate>0,candidate>0),
                    added_pixels=int(np.count_nonzero((candidate>0)&(baseline==0))),removed_pixels=int(np.count_nonzero((baseline>0)&(candidate==0))))
            except (ValueError,RuntimeError,cv2.error) as error:record['reason']=str(error)
            save(out/'masks'/f'{name}_{frame}_candidate.png',candidate)
            frames[frame]=(image,baseline,candidate);metrics[frame]=record
        ref,old_ref,new_ref=frames['reference'];color,old_color,new_color=frames['color']
        # One horizontal board allows reuse of the saved interactive review tool.
        save(out/'boards'/f'{name}.png',np.hstack([panel(ref,name+' reference'),panel(ref,'Reference baseline',old_ref),panel(ref,'Reference YCrCb',new_ref),
            panel(color,'Color-shift input'),panel(color,'Input baseline',old_color),panel(color,'Input YCrCb',new_color)]))
        records.append(dict(image_id=image_id,source_id=name,original_reference_notes=row['reference_notes'],
            frames=metrics,training_eligible=False,candidate_human_review='pending'))
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
    write('attempts.json',records)
    available=[r for r in records if r['frames']['color']['status']=='available']
    gains=[r for r in available if not r['frames']['color']['baseline_screen']['screen_pass'] and r['frames']['color']['candidate_screen']['screen_pass']]
    losses=[r for r in available if r['frames']['color']['baseline_screen']['screen_pass'] and not r['frames']['color']['candidate_screen']['screen_pass']]
    key=lambda r:(hashlib.sha256(('color_ycrcb_review_v1/'+r['image_id']).encode()).hexdigest(),r['image_id'])
    shortlist=sorted(gains,key=key)[:6]
    risk=sorted([r for r in available if r not in shortlist],key=lambda r:(0 if r in losses else 1,
        -(r['frames']['color']['candidate_outside_oval_pixels']-r['frames']['color']['baseline_outside_oval_pixels']),key(r)))[:2]
    shortlist+=risk
    summary=dict(status='single_factor_complete_pending_review',sources=20,frames=40,baseline_parity_checks=parity,
        old_color_screen_pass=sum(r['frames']['color']['baseline_screen']['screen_pass'] for r in available),
        new_color_screen_pass=sum(r['frames']['color']['candidate_screen']['screen_pass'] for r in available),
        screen_gains=[r['source_id'] for r in gains],screen_regressions=[r['source_id'] for r in losses],
        old_color_outside_oval_pixels=sum(r['frames']['color']['baseline_outside_oval_pixels'] for r in available),
        new_color_outside_oval_pixels=sum(r['frames']['color']['candidate_outside_oval_pixels'] for r in available),
        review_sources=[r['source_id'] for r in shortlist],candidate_ita_mst_calls=0,target_fits=0,tree_fits=0,
        active_mask_changed=False,reserved_validation_test_access=False)
    write('summary.json',summary)
    write('review_selection.json',dict(scope='candidate_reference_and_color_input_masks_only',selected_ids=[r['image_id'] for r in shortlist],
        reason='Up to6fixed-hash retention gains plus2regression/risk cases; not representative validation'))
    data=dict(batch='ycrcb_color8',manifest_sha256=digest(out/'plan.json'),review_scope='candidate_reference_and_color_input_masks_only',
        panel_labels=['Reference photo','Reference baseline','Reference YCrCb candidate','Color input','Input baseline','Input YCrCb candidate'],
        review_instructions='Review both YCrCb candidate masks (panels3and6). Accept only if both are usable; otherwise reject or uncertain and note which panel fails. Original notes are preserved; no automatic training admission.',
        records=[dict(image_id=r['image_id'],source_id=r['source_id'],status='pending_review',panel_count=6,
            comparison_note='Original reference note: '+(r['original_reference_notes'] or 'none')+'. Retention is a diagnostic, not skin accuracy.') for r in shortlist])
    template=(ROOT/'scripts/review_tools/training_review.html').read_text(encoding='utf-8')
    page=template.replace('__BATCH__','ycrcb_color8').replace('__BATCH_LINKS__','Small changed-mask comparison').replace('__DATA__',json.dumps(data).replace('<','\\u003c'))
    page=page.replace('href="review.html"','href="../three_variant_training_candidates_v1/review.html"',1).replace('All batches','All diagnostic sources')
    page=page.replace('Training review · batch ycrcb_color8','YCrCb-only color-cast comparison · '+str(len(shortlist))+' photos')
    page=page.replace('Check reference suitability and both masks. Green shows selected pixels. Accept records your review; processing failures remain excluded. No model approval occurs here.',data['review_instructions'])
    page=page.replace('<header>','<body class="large"><header>',1).replace('<input type="checkbox" id="large">','<input type="checkbox" id="large" checked>')
    (out/'review.html').write_text(page,encoding='utf-8');(out/'training_review.js').write_bytes((ROOT/'scripts/review_tools/training_review.js').read_bytes())
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
