"""Check20555's five fixed variants and screen the next18 unused TRAIN images.

No source is admitted, human label changed or correction learner fitted.
"""
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
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support
from src.skin_masking.additions_boundary_experiment import restrict_new_support
from src.evaluation.mask_support_quality import support_retention


def main():
    config=get_config();helper=importlib.import_module('64_audit_training_coverage')
    prepare=importlib.import_module('11_prepare_training_manifests')
    ycb=importlib.import_module('56_compare_ycrcb_estimation')
    output=ROOT/config.OUTPUTS_ROOT/'source_screening_followup_v1'
    tables=ROOT/'data/manifests/source_screening_followup_v1'
    if output.exists() or tables.exists():raise FileExistsError('Follow-up exists')
    audit_path=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    current_path=ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv'
    exposure_path=ROOT/'data/manifests/development_exposure_additions.jsonl'
    old_disposition=ROOT/'data/manifests/training_coverage_audit_v1/candidate_disposition.json'
    assert next(r for r in json.loads(old_disposition.read_text())['observations'] if r['image_id']=='fairface__train/20555.jpg')['status']=='promising_followup_only'
    all_rows=helper.read(audit_path);current=helper.read(current_path)
    previous_exposure=[json.loads(line) for line in exposure_path.read_text(encoding='utf-8').splitlines() if line]
    excluded={r['image_id'] for r in previous_exposure};groups={r['duplicate_group_id'] for r in current}
    pool=[r for r in all_rows if r['partition']=='train' and r['source_suitability']=='hold_unreviewed_source'
        and r['processing_status']=='success' and r['known_pipeline_development_exposure']=='False'
        and r['original_visual_decision']=='pending' and r['controlled_source_decision']=='not_assessed_in_this_pass'
        and r['duplicate_group_size']=='1' and r['duplicate_group_id'] not in groups and r['image_id'] not in excluded]
    if len(pool)<18:raise ValueError('Insufficient unused training sources')
    ordered=sorted(pool,key=lambda r:(float(r['mean_l_star']),r['image_id']));selected=[]
    for index,indices in enumerate(np.array_split(np.arange(len(ordered)),6),1):
        bucket=[ordered[int(i)] for i in indices]
        chosen=sorted(bucket,key=lambda r:hashlib.sha256(('coverage_seed42/'+r['image_id']).encode()).hexdigest())[:3]
        selected += [dict(r,sampling_bin=index) for r in chosen]
    source=next(r for r in all_rows if r['image_id']=='fairface__train/20555.jpg')
    assert len(selected)==len({r['image_id'] for r in selected})==18
    assert all(r['partition']=='train' and r['image_id'] not in excluded for r in selected)
    distortion_policy=ROOT/'data/manifests/controlled_development_v1/distortion_policy.json'
    params=json.loads(distortion_policy.read_text())['variants']
    params.update(identity_control=dict(gamma=1.,red_gain=1.,blue_gain=1.),mild_bright_exposure=dict(gamma=1.1,red_gain=1.,blue_gain=1.))
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert helper.digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    tracked=[Path(__file__),audit_path,current_path,old_disposition,distortion_policy,
        ROOT/'scripts/64_audit_training_coverage.py',ROOT/'scripts/56_compare_ycrcb_estimation.py',
        ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'src/skin_masking/additions_boundary_experiment.py',
        ROOT/'src/skin_masking/lower_face_boundary_experiment.py',ROOT/'src/evaluation/mask_support_quality.py',
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,model,
        ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]+[Path(r['image_path']) for r in selected+[source]]
    hashes={str(p):helper.digest(p) for p in tracked}
    output.mkdir(parents=True);tables.mkdir(parents=True);(output/'images').mkdir()
    policy=dict(version='source_screening_followup_v1',date='2026-10-24',selection='Same six native-Lrank bins/seed42hash,3perbin,TRAIN only; all18previous exposure IDs excluded',
        unused_pool_before=len(pool),selected_ids=[r['image_id'] for r in selected],
        variants20555=params,status='Development screening only; no automatic acceptance or training')
    (tables/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    (tables/'prior_exposure_snapshot.json').write_text(json.dumps(previous_exposure,indent=2),encoding='utf-8')
    with exposure_path.open('a',encoding='utf-8') as f:
        for r in selected:f.write(json.dumps(dict(image_id=r['image_id'],partition='train',date='2026-10-24',reason='source_screening_followup_v1 new-source development screen'))+'\n')
    (output/'run_status.json').write_text('{"state":"running"}',encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model)

    def measure(image):
        estimate=np.zeros(image.shape[:2],bool);exclude=np.zeros_like(estimate)
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        record=dict(status='expected_single_face',face_count=len(boxes),face_boxes=[[int(v) for v in box] for box in boxes])
        landmarks=None
        if len(boxes)==1:
            x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w]
            result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
            estimate[y:y+h,x:x+w]=result.mask>0;exclude[y:y+h,x:x+w]=result.exclusion_mask>0
            stats=compute_masked_lab_statistics(crop,result.mask,1000)
            record.update(**stats,landmarks_available=bool(result.landmarks_available),
                status='success' if stats['valid'] and result.landmarks_available else 'landmarks_unavailable' if not result.landmarks_available else stats['reason'])
            if result.landmarks_available:landmarks,_,_=prepare.detect_landmarks_with_margin(image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        return record,estimate,exclude,landmarks

    def panel(image,mask,label):
        shown=image.copy()
        if mask is not None:shown[mask]=np.rint(.55*shown[mask]+.45*np.array([0,220,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,30,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label[:42],(3,18),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
        return shown

    def application_support(image,estimate,exclude,box,categories):
        x,y,w,h=box;material=np.zeros_like(estimate)
        material[y:y+h,x:x+w]=material_checked_support(image[y:y+h,x:x+w],estimate[y:y+h,x:x+w],exclude[y:y+h,x:x+w])
        return hair_veto_support(categories,material)

    try:
        reference=cv2.resize(cv2.imread(source['image_path']),(256,256),interpolation=cv2.INTER_LINEAR)
        base,source_mask,_,_=measure(reference)
        if base['status']!='success':raise ValueError('20555 clean-source processing changed')
        categories=segmenter.categories_bgr(reference);generation=hair_veto_support(categories,source_mask)
        if generation.sum()<1000:raise ValueError('20555 source support too small')
        helper.save(output/'images/20555_reference.png',reference)
        helper.save(output/'images/20555_generation.png',generation.astype(np.uint8)*255)
        ref_rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB);ref=ref_rgb.astype(float)/255
        variants=[];variant_panels=[]
        for variant,parameters in params.items():
            raw=transform_rgb(ref,**parameters,clip=False);generated=ref.copy();generated[generation]=np.clip(raw[generation],0,1)
            encoded=np.rint(generated*255).astype(np.uint8);np.testing.assert_array_equal(encoded[~generation],ref_rgb[~generation])
            if variant=='identity_control':np.testing.assert_array_equal(encoded,ref_rgb)
            path=output/'images'/('20555_'+variant+'_input.png');helper.save(path,cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR))
            image=cv2.imread(str(path));record,estimate,exclude,landmarks=measure(image)
            clipping=int((generation&((raw<0)|(raw>1)).any(axis=2)).sum())
            record.update(variant=variant,clipped_pixels=clipping,inverse_targets=inverse_parameters(**parameters),
                          additions_boundary_status='unavailable_features',training_eligible=False)
            support=np.zeros_like(estimate)
            if record['status']=='success':
                box=record['face_boxes'][0];x,y,w,h=box;categories=segmenter.categories_bgr(image)
                baseline_support=application_support(image,estimate,exclude,box,categories)
                proposal=np.zeros_like(estimate);proposal[y:y+h,x:x+w]=ycb.ycrcb_mask(image[y:y+h,x:x+w],exclude[y:y+h,x:x+w])
                proposal_support=application_support(image,proposal,exclude,box,categories)
                try:
                    if landmarks is None:raise ValueError('No boundary landmarks')
                    bounded,metadata=restrict_new_support(baseline_support[y:y+h,x:x+w],proposal_support[y:y+h,x:x+w],landmarks)
                    support[y:y+h,x:x+w]=bounded
                    record.update(additions_boundary_status='available',boundary_metadata=metadata,
                                  retention=support_retention(generation,estimate,support))
                except ValueError as error:record.update(additions_boundary_status='unavailable',boundary_reason=str(error))
            for name,mask in [('estimate',estimate),('support',support)]:helper.save(output/'images'/('20555_'+variant+'_'+name+'.png'),mask.astype(np.uint8)*255)
            variants.append(record);variant_panels.append(np.hstack([panel(image,None,variant+' input'),panel(image,estimate,'Estimation'),panel(image,support,'Experimental support: '+record['additions_boundary_status'])]))
        helper.save(output/'20555_variants.png',np.vstack(variant_panels))
        new=[];boards={}
        for row in selected:
            image=cv2.resize(cv2.imread(row['image_path']),(256,256),interpolation=cv2.INTER_LINEAR)
            record,mask,exclude,_=measure(image);cleaned=np.zeros_like(mask)
            if record['status']=='success':cleaned=hair_veto_support(segmenter.categories_bgr(image),mask)
            stem=row['image_id'].replace('/','_')
            record.update(image_id=row['image_id'],source_path=row['image_path'],partition='train',sampling_bin=row['sampling_bin'],
                          original_human_decision=row['original_visual_decision'],training_eligible=False,
                          cleaned_generation_pixels=int(cleaned.sum()),newly_development_exposed=True)
            for name,pixels in [('input',image),('estimate',mask.astype(np.uint8)*255),('hairclean',cleaned.astype(np.uint8)*255)]:helper.save(output/'images'/(stem+'_'+name+'.png'),pixels)
            new.append(record);identifier=Path(row['image_path']).stem
            boards.setdefault(row['sampling_bin'],[]).append(np.hstack([panel(image,None,identifier+' '+record['status']),panel(image,mask,'Estimation'),panel(image,cleaned,'Hair-clean source')]))
            print(row['image_id']+': '+record['status'],flush=True)
        assert len(new)==18 and len(variants)==5
        assert hashes=={p:helper.digest(p) for p in hashes},'Original artifact changed'
        summary=dict(status='complete',source20555=base,variants20555=variants,new_source_attempts=new,
                     new_source_status_counts=dict(Counter(r['status'] for r in new)),input_sha256=hashes,
                     warning='Numerical success is not source/mask acceptance; no model fit or reserved-test use; neck support not evaluated.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        links=['- [20555 fixed variants](20555_variants.png)']
        for index,rows in sorted(boards.items()):
            filename=f'new_batch_bin_{index}.png';helper.save(output/filename,np.vstack(rows));links.append(f'- [New training sources: bin {index}]({filename})')
        (output/'review-index.md').write_text('# Source screening follow-up\n\nFixed20555probes and18new TRAIN candidates, no automatic training admission.\n\n'+'\n'.join(links),encoding='utf-8')
        (output/'run_status.json').write_text('{"state":"complete"}',encoding='utf-8')
        print(json.dumps(dict(variants=[dict(variant=r['variant'],status=r['status'],clipped=r['clipped_pixels'],support=r['additions_boundary_status'],screen=r.get('retention',{}).get('screen_pass')) for r in variants],new=summary['new_source_status_counts']),indent=2))
    finally:segmenter.close()


if __name__=='__main__':main()
