"""Isolated removal-only generation-mask experiment on all38 square attempts.

Hair veto is applied to clean-source generation support, not to estimation.
No correction learner is loaded; no production tables or labels are changed.
"""
import csv
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
from src.distortion_generation.generate_distortions import transform_rgb
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,image):
    if not cv2.imwrite(str(p),image):raise OSError(p)


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    baseline=ROOT/'outputs/controlled_square256_v1'
    tables=ROOT/'data/manifests/controlled_square256_v1'
    output=ROOT/'outputs/hair_clean_generation_v1'
    if output.exists():raise FileExistsError(output)
    with (tables/'all_pairs_audit.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    screen_path=ROOT/'outputs/square_mask_quality_v1/summary.json'
    old_screen={r['pair_id']:r for r in json.loads(screen_path.read_text())['pairs']}
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    paths=[Path(__file__),tables/'all_pairs_audit.csv',screen_path,
           ROOT/'data/manifests/square_mask_quality_v1/screen_policy.json',
           model,ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
           ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
           ROOT/'data/manifests/material_review_v1/material_review_labels.json',
           ROOT/'scripts/11_prepare_training_manifests.py',
           ROOT/'src/evaluation/mask_support_quality.py']
    for row in rows:paths.extend([ROOT/row['reference_path'],ROOT/row['input_path'],ROOT/row['generation_mask_path']])
    hashes={str(p):digest(p) for p in paths}
    output.mkdir(parents=True);(output/'run-status.json').write_text('{"status":"running"}')
    policy=dict(version='hair_clean_generation_v1',generation='existing square source mask AND NOT clean-input predicted hair',
                scope='All38 same attempts, same parameters, fresh saved-input measurements',
                estimation='unchanged v2_complete_mouth_v1 HSV AND YCrCb',
                correction='unchanged material_hair_veto_v1; no new expansion',
                screening='same existing exploratory .5 estimation/.8 correction, quadrants>=100pixels',
                status='Development experiment; changed generation denominator; no eligibility promotion, no fitting')
    (output/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model);results=[];sources=[];boards=[]
    try:
        for source_id in sorted({r['source_image_id'] for r in rows}):
            attempts=[r for r in rows if r['source_image_id']==source_id]
            reference=cv2.imread(str(ROOT/attempts[0]['reference_path']))
            original_mask=cv2.imread(str(ROOT/attempts[0]['generation_mask_path']),0)>0
            categories=segmenter.categories_bgr(reference)
            cleaned=hair_veto_support(categories,original_mask)
            assert not np.any(cleaned&~original_mask)
            assert not np.any(cleaned&(categories==1))
            if cleaned.sum()<1000:raise ValueError('Insufficient cleaned source support: '+source_id)
            stem=source_id.replace('/','_')
            save(output/(stem+'_generation_mask.png'),cleaned.astype(np.uint8)*255)
            sources.append(dict(source_image_id=source_id,before_pixels=int(original_mask.sum()),
                                after_pixels=int(cleaned.sum()),removed_predicted_hair=int((original_mask&~cleaned).sum())))
            rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB);ref=rgb.astype(float)/255;panels=[]
            for row in attempts:
                pair=row['pair_id'];params={k:float(row['distortion_'+k]) for k in ['gamma','red_gain','blue_gain']}
                raw=transform_rgb(ref,**params,clip=False);generated=ref.copy();generated[cleaned]=np.clip(raw[cleaned],0,1)
                encoded=np.rint(generated*255).astype(np.uint8)
                np.testing.assert_array_equal(encoded[~cleaned],rgb[~cleaned])
                if row['variant']=='identity_control':np.testing.assert_array_equal(encoded,rgb)
                save(output/(pair+'_input.png'),cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR))
                image=cv2.imread(str(output/(pair+'_input.png')))
                boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
                estimate=np.zeros(cleaned.shape,bool);support=np.zeros_like(estimate)
                record=dict(pair_id=pair,source_image_id=source_id,historical_table_use=row['table_use'],
                            clipped_pixels=int((cleaned&((raw<0)|(raw>1)).any(axis=2)).sum()),
                            face_count=len(boxes),status='expected_single_face')
                if len(boxes)==1:
                    x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w]
                    result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
                    estimate[y:y+h,x:x+w]=result.mask>0
                    stats=compute_masked_lab_statistics(crop,result.mask,1000)
                    record.update(skin_pixels=stats['skin_pixels'],ita_degrees=stats['ita_degrees'],
                        status='success' if result.landmarks_available and stats['valid'] else 'landmarks_unavailable' if not result.landmarks_available else stats['reason'])
                    if record['status']=='success':
                        material=np.zeros_like(estimate)
                        material[y:y+h,x:x+w]=material_checked_support(crop,result.mask>0,result.exclusion_mask>0)
                        input_categories=segmenter.categories_bgr(image)
                        support=hair_veto_support(input_categories,material)
                        assert not np.any(support&(input_categories==1))
                        assert not np.any(support[y:y+h,x:x+w]&(result.exclusion_mask>0))
                for name,mask in [('estimation',estimate),('correction',support)]:save(output/(pair+'_'+name+'.png'),mask.astype(np.uint8)*255)
                record['against_original_generation']=support_retention(original_mask,estimate,support)
                record['against_cleaned_generation']=support_retention(cleaned,estimate,support)
                record['previous_screen_pass']=old_screen[pair]['quantitative']['screen_pass']
                record['diagnostic_screen_pass']=record['status']=='success' and record['against_cleaned_generation']['screen_pass']
                # Distinguish changed reference denominator from changed input/output masks.
                old_input=cv2.imread(str(ROOT/row['input_path']))
                old_estimate=cv2.imread(str(baseline/'masks'/(pair+'_estimation.png')),0)>0
                old_support=cv2.imread(str(baseline/'masks'/(pair+'_correction.png')),0)>0
                record.update(input_changed_pixels=int(np.any(image!=old_input,axis=2).sum()),
                              estimation_changed_pixels=int((estimate!=old_estimate).sum()),
                              correction_changed_pixels=int((support!=old_support).sum()),
                              old_support_against_cleaned_generation=support_retention(cleaned,old_estimate,old_support))
                results.append(record)
                comparison=[]
                for label,shown,mask in [('Baseline support',old_input,old_support),('Hair-clean support',image,support)]:
                    panel=shown.copy();panel[mask]=np.rint(.55*panel[mask]+.45*np.array([0,220,0])).astype(np.uint8)
                    panel=cv2.copyMakeBorder(panel,30,0,0,0,cv2.BORDER_CONSTANT)
                    cv2.putText(panel,row['variant']+' '+label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.33,(255,255,255),1)
                    comparison.append(panel)
                panels.append(np.hstack(comparison))
                with (output/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
                print(pair+': '+str(record['diagnostic_screen_pass']),flush=True)
            name=stem+'_comparison.png';save(output/name,np.vstack(panels));boards.append((source_id,name))
        assert len(results)==38
        assert hashes=={p:digest(p) for p in hashes},'Baseline changed'
        summary=dict(status='complete',attempts=38,sources=sources,pairs=results,input_sha256=hashes,
                     status_counts=dict(Counter(r['status'] for r in results)),
                     training_screen_pass_before=sum(r['previous_screen_pass'] for r in results if r['historical_table_use']=='train'),
                     training_screen_pass_candidate=sum(r['diagnostic_screen_pass'] for r in results if r['historical_table_use']=='train'),
                     warning='Generation-policy experiment; no cohort promotion or model fit. Denominator changes are not evidence of improved segmentation.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'review-index.md').write_text('# Hair-clean generation experiment\n\nBaseline versus candidate correction support, not learned corrections.\n\n'+'\n'.join(f'- [{source}]({name})' for source,name in boards),encoding='utf-8')
        (output/'run-status.json').write_text('{"status":"complete"}',encoding='utf-8')
        print(json.dumps({k:summary[k] for k in ['status_counts','training_screen_pass_before','training_screen_pass_candidate']}))
    finally:segmenter.close()


if __name__=='__main__':main()
