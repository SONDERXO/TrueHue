"""Fixed input-only rule-factor diagnostic on 20 reviewed development pairs."""
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
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.face_constrained_component import face_constrained_component
from src.skin_masking.face_outline_experiment import restrict_to_face_outline
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
from src.evaluation.mask_support_quality import support_retention

ARMS=('and_original','ycrcb_original','and_oval','ycrcb_oval')


def main():
    out=ROOT/'outputs/table2_input_mask_robustness_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    audit=ROOT/'outputs/accepted_training_pair_audit_v1'
    for name,sha in read(audit/'verification.json')['evidence_sha256'].items():assert digest(audit/name)==sha
    selected=[r for r in read(audit/'source_pair_dispositions.json') if r.get('input_technical_pass')]
    assert len(selected)==20
    parent=ROOT/'outputs/correction_training_preparation_v1'
    prior={r['image_id']:r for r in (json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    old=read(parent/'verification.json')['evidence_sha256']
    spec,identity=contract(ROOT);config=get_config()
    paths=[Path(__file__),ROOT/'docs/table2-input-mask-robustness-protocol.md',audit/'source_pair_dispositions.json',
        ROOT/'src/skin_masking/ycrcb_candidate.py',ROOT/'src/skin_masking/face_constrained_component.py',
        ROOT/'src/skin_masking/face_outline_experiment.py',ROOT/'src/evaluation/mask_support_quality.py']
    paths.extend(ROOT/p for p in spec['dependency_sha256'])
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for name in ['geometry','masks','boards']:(out/name).mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_candidate_processing',selected_ids=[r['image_id'] for r in selected],
        arms=ARMS,input_sha256=hashes,original_measurement_contract=identity,
        candidate_lookup_applicable=False,existing_thresholds_only=True))
    write('run_status.json',dict(status='running'))
    prepare=importlib.import_module('11_prepare_training_manifests')
    records=[];parity=0
    def save(p,image):
        if not cv2.imwrite(str(p),image):raise OSError(p)
    def load(name,suffix,gray=False):
        relative=f'images/{name}_{suffix}.png';path=parent/relative
        assert digest(path)==old[relative]
        return cv2.imread(str(path),0 if gray else cv2.IMREAD_COLOR)
    def panel(image,label,mask=None):
        shown=image.copy()
        if mask is not None:
            support=mask>0;shown[support]=np.rint(.65*shown[support]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown
    try:
        for selected_row in selected:
            image_id=selected_row['image_id'];s=prior[image_id];name=s['source_id']
            ref_mask=load(name,'reference_mask',True)>0
            frames={};frame_records={}
            for frame,report_name in [('reference','reference_measurement'),('input','input_measurement')]:
                image=load(name,frame);baseline=load(name,frame+'_mask',True)
                report=s[report_name];record=dict(status='unavailable',arms={})
                masks={arm:np.zeros_like(baseline) for arm in ARMS}
                with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:
                    stream.write(json.dumps(dict(image_id=image_id,frame=frame,phase='reviewed_training_input_robustness'))+'\n')
                try:
                    if report.get('face_count')!=1 or 'face_box' not in report:raise ValueError('Exactly one frame-local detector face required')
                    box=tuple(report['face_box']);x,y,w,h=box
                    points,margin,_=prepare.detect_landmarks_with_margin(image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
                    if points is None:raise ValueError('Frame-local landmarks unavailable; no reference fallback')
                    crop=image[y:y+h,x:x+w]
                    and_colors=create_candidate_mask_bgr(crop);y_colors=ycrcb_color_candidate(crop)
                    excluded=build_feature_exclusion_mask(crop,points,dilation=0)
                    _,mouth=exclude_complete_mouth(np.full((h,w),255,np.uint8),points)
                    excluded=cv2.bitwise_or(excluded,mouth)
                    _,oval=restrict_to_face_outline(np.full((h,w),255,np.uint8),points)
                    full_oval=np.zeros_like(baseline);full_oval[y:y+h,x:x+w]=oval
                    key=name+'_'+frame
                    for suffix,mask in [('and_colors',and_colors),('ycrcb_colors',y_colors),('excluded',excluded),('oval',oval)]:save(out/'geometry'/f'{key}_{suffix}.png',mask)
                    np.save(out/'geometry'/f'{key}_landmarks.npy',points)
                    for color_name,colors in [('and',and_colors),('ycrcb',y_colors)]:
                        for ordering in ['original','oval']:
                            arm=color_name+'_'+ordering
                            native=(cv2.bitwise_and(keep_largest_connected_component(colors),cv2.bitwise_not(excluded)) if ordering=='original'
                                else face_constrained_component(colors,oval,excluded))
                            masks[arm][y:y+h,x:x+w]=native
                            assert not np.any((native>0)&(excluded>0))
                    np.testing.assert_array_equal(masks['and_original'],baseline)
                    parity+=1
                    for arm,mask in masks.items():
                        support=mask>0
                        record['arms'][arm]=dict(selected_pixels=int(support.sum()),minimum_pixels_pass=bool(support.sum()>=1000),
                            outside_oval_pixels=int(np.count_nonzero(support&(full_oval==0))),
                            support_screen=support_retention(ref_mask,support,support))
                    record.update(status='available',face_box=list(box),landmark_margin=margin,baseline_parity=True)
                except (ValueError,RuntimeError,cv2.error) as error:record['reason']=str(error)
                for arm,mask in masks.items():save(out/'masks'/f'{name}_{frame}_{arm}.png',mask)
                frames[frame]=(image,masks);frame_records[frame]=record
            comparison={}
            if all(frame_records[f]['status']=='available' for f in ['reference','input']):
                for arm in ARMS:
                    a=frames['reference'][1][arm]>0;b=frames['input'][1][arm]>0
                    union=int(np.count_nonzero(a|b));intersection=int(np.count_nonzero(a&b))
                    comparison[arm]=dict(reference_input_jaccard=intersection/union if union else None,
                        input_added_pixels=int(np.count_nonzero(b&~a)),input_lost_pixels=int(np.count_nonzero(a&~b)),
                        reference_mask_changed=not np.array_equal(a,ref_mask))
            board=[panel(frames['input'][0],name+' distorted input'),panel(frames['reference'][0],'Original reviewed support',ref_mask.astype(np.uint8)*255)]
            board.extend(panel(frames['input'][0],arm,frames['input'][1][arm]) for arm in ARMS)
            save(out/'boards'/f'{name}.png',np.vstack([np.hstack(board[:3]),np.hstack(board[3:])]))
            records.append(dict(image_id=image_id,source_id=name,original_review_notes=selected_row['exact_notes'],
                clipping=selected_row['clipping'],frames=frame_records,comparison=comparison,training_eligible=False))
            with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(records[-1])+'\n')
            print(name,{f:frame_records[f]['status'] for f in frame_records},flush=True)
        assert all(digest(ROOT/p)==sha for p,sha in hashes.items()) and contract(ROOT)[1]==identity
        summary=dict(status='complete_diagnostic_no_adoption',sources=20,frames=40,baseline_parity_checks=parity,arms={})
        for arm in ARMS:
            available=[r['frames']['input']['arms'][arm] for r in records if arm in r['frames']['input']['arms']]
            summary['arms'][arm]=dict(available_inputs=len(available),minimum_pixels_pass=sum(r['minimum_pixels_pass'] for r in available),
                support_screen_pass=sum(r['support_screen']['screen_pass'] for r in available),
                total_outside_oval_pixels=sum(r['outside_oval_pixels'] for r in available))
        summary.update(clipped_inputs=sum(r['clipping']['clipped_pixels']>0 for r in records),
            candidate_ita_mst_calls=0,model_fits=0,training_admissions=0,reserved_validation_test_access=False)
        write('summary.json',summary)
        sections=''.join(f'<section><h2>{r["source_id"]}</h2><p>Original reference note: {r["original_review_notes"] or "none"}. Clipped pixels: {r["clipping"]["clipped_pixels"]}. Candidate masks are unreviewed.</p><img loading="lazy" src="boards/{r["source_id"]}.png"></section>' for r in records)
        (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Fixed Table2 input-mask robustness</title><style>body{font:16px system-ui;background:#171923;color:#eee;margin:28px}img{max-width:100%}section{border-top:1px solid #666;margin:24px 0}</style><h1>Fixed Table2 inputs: rule-factor diagnostic</h1><p>20 already reviewed sources, no automatic approval. Same reference generation support for all screens; no source-mask substitution at inference. More support is not skin accuracy. Original masking/calibration remain unchanged.</p>'+sections,encoding='utf-8')
        write('run_status.json',dict(status='complete_diagnostic_no_adoption'))
        print(json.dumps(summary,indent=2))
    except Exception as error:
        write('run_status.json',dict(status='failed',completed=len(records),error=str(error)));raise


if __name__=='__main__':main()
