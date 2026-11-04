"""Fixed75 variant attempts on all15 follow-up sources; no fitting.

Paired HSV/YCrCb and YCrCb-only measurements, no feature fallback or fitting.
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

IDS={'51446','83205','42532','84364','7994','69531','56444','55007','31154','67454','40048','67583','47217','60162','63870'}


def main():
    config=get_config();helper=importlib.import_module('64_audit_training_coverage')
    prepare=importlib.import_module('11_prepare_training_manifests');ycb=importlib.import_module('56_compare_ycrcb_estimation')
    output=ROOT/config.OUTPUTS_ROOT/'training_source60_variants_v1';tables=ROOT/'data/manifests/training_source60_variants_v1'
    if output.exists() or tables.exists():raise FileExistsError('Check exists')
    disposition=ROOT/'data/manifests/training_source60_screen_v1/source_dispositions.json'
    candidates=[r for r in json.loads(disposition.read_text())['observations'] if r['status']=='promising_variant_followup_only']
    assert {Path(r['image_id']).stem for r in candidates}==IDS
    source_audit=ROOT/'data/manifests/controlled_development_v1/source_audit.csv'
    sources={r['image_id']:r for r in helper.read(source_audit)}
    policy_source=ROOT/'data/manifests/source_screening_followup_v1/policy.json'
    variants=json.loads(policy_source.read_text())['variants20555']
    exposure=ROOT/'data/manifests/development_exposure_additions.jsonl'
    exposed={json.loads(line)['image_id'] for line in exposure.read_text().splitlines() if line}
    assert all(r['image_id'] in exposed and sources[r['image_id']]['partition']=='train' for r in candidates)
    model=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    assert helper.digest(model)==json.loads(model.with_suffix('.provenance.json').read_text())['sha256']
    tracked=[Path(__file__),disposition,source_audit,policy_source,exposure,
        ROOT/'scripts/11_prepare_training_manifests.py',ROOT/'scripts/56_compare_ycrcb_estimation.py',
        ROOT/'src/skin_masking/material_checked_support.py',ROOT/'src/skin_masking/selfie_material_segmenter.py',
        ROOT/'src/skin_masking/additions_boundary_experiment.py',ROOT/'src/skin_masking/lower_face_boundary_experiment.py',
        ROOT/'src/ita_estimation/compute_ita.py',ROOT/'src/evaluation/mask_support_quality.py',
        ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,model,
        ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]+[Path(sources[r['image_id']]['image_path']) for r in candidates]
    brightness=importlib.import_module('72_audit_brightness_features')
    schema_path=ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json'
    schema=json.loads(schema_path.read_text())
    tracked += [schema_path,ROOT/'scripts/72_audit_brightness_features.py']
    hashes={str(p):helper.digest(p) for p in tracked}
    output.mkdir(parents=True);tables.mkdir(parents=True);(output/'images').mkdir()
    policy=dict(version='training_source60_variants_v1',sources=sorted(IDS),variants=variants,
        generation='Resize256 before baseline estimation; hair-clean baseline source support; fixed binary transforms',
        estimator_comparison='Baseline HSV AND YCrCb vs fixed YCrCb-only, same detector/morphology/largestcomponent/exclusions',
        correction='Existing material/hair-veto supports plus guarded additions-only boundary',
        status='Pending sources,75attempts; frozen ten-feature schema; no model/feature policy selection, fallback, admission or fitting')
    (tables/'policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    (output/'run_status.json').write_text('{"status":"running"}',encoding='utf-8')
    segmenter=SelfieMaterialSegmenter(model)

    def estimate(image):
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        if len(boxes)!=1:return dict(status='expected_single_face',face_count=len(boxes)),None,None,None,None
        box=boxes[0];x,y,w,h=box;crop=image[y:y+h,x:x+w]
        base=prepare.compute_versioned_skin_mask(crop,image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        if not base.landmarks_available:return dict(status='landmarks_unavailable'),None,None,None,None
        exclude=base.exclusion_mask>0
        baseline=np.zeros(image.shape[:2],bool);baseline[y:y+h,x:x+w]=base.mask>0
        proposal=np.zeros_like(baseline);proposal[y:y+h,x:x+w]=ycb.ycrcb_mask(crop,exclude)
        methods={name:compute_masked_lab_statistics(image,mask.astype(np.uint8)*255,1000) for name,mask in [('baseline',baseline),('ycrcb',proposal)]}
        landmarks,_,_=prepare.detect_landmarks_with_margin(image,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        return dict(status='geometry_available',face_box=list(map(int,box)),estimators=methods),baseline,proposal,exclude,landmarks

    def support(image,mask,excluded,box,categories):
        x,y,w,h=box;full=np.zeros_like(mask)
        full[y:y+h,x:x+w]=material_checked_support(image[y:y+h,x:x+w],mask[y:y+h,x:x+w],excluded)
        return hair_veto_support(categories,full)

    def panel(image,mask,label):
        result=image.copy()
        if mask is not None:result[mask]=np.rint(.55*result[mask]+.45*np.array([0,220,0])).astype(np.uint8)
        result=cv2.copyMakeBorder(result,30,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(result,label[:43],(3,18),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1)
        return result

    results=[];source_results=[];links=[]
    try:
        for candidate in sorted(candidates,key=lambda r:r['image_id']):
            source=sources[candidate['image_id']];identifier=Path(source['image_path']).stem
            image=cv2.resize(cv2.imread(source['image_path']),(256,256),interpolation=cv2.INTER_LINEAR)
            source_record,base,_,_,_=estimate(image)
            if base is None or not source_record['estimators']['baseline']['valid']:raise ValueError('Clean candidate unavailable '+identifier)
            generation=hair_veto_support(segmenter.categories_bgr(image),base)
            if generation.sum()<1000:raise ValueError('Clean support too small')
            helper.save(output/'images'/(identifier+'_reference.png'),image)
            helper.save(output/'images'/(identifier+'_generation.png'),generation.astype(np.uint8)*255)
            source_results.append(dict(image_id=source['image_id'],**source_record,generation_pixels=int(generation.sum())))
            rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);reference=rgb.astype(float)/255;strips=[]
            for variant,parameters in variants.items():
                stem=identifier+'_'+variant;raw=transform_rgb(reference,**parameters,clip=False)
                generated=reference.copy();generated[generation]=np.clip(raw[generation],0,1)
                encoded=np.rint(generated*255).astype(np.uint8);np.testing.assert_array_equal(encoded[~generation],rgb[~generation])
                if variant=='identity_control':np.testing.assert_array_equal(encoded,rgb)
                helper.save(output/'images'/(stem+'_input.png'),cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR))
                saved=cv2.imread(str(output/'images'/(stem+'_input.png')))
                record,baseline,proposal,exclude,landmarks=estimate(saved)
                clipping=int((generation&((raw<0)|(raw>1)).any(axis=2)).sum())
                record.update(planned_development_fold=candidate['planned_development_fold'],image_id=source['image_id'],variant=variant,clipped_pixels=clipping,
                              inverse_targets=inverse_parameters(**parameters),training_eligible=False,
                              correction_status='unavailable',baseline_feature_fallback=False)
                record['brightness_features']=brightness.brightness_features(saved,baseline) if baseline is not None else dict(valid=False,reason='baseline_unavailable')
                if record['brightness_features']['valid'] and record['estimators']['baseline']['valid']:
                    stats=record['estimators']['baseline']
                    record['frozen_ten_features']={**{k:stats[v] for k,v in zip(schema['baseline_features'],['mean_l_star','mean_a_star','mean_b_star','ita_degrees'])},**record['brightness_features']['features']}
                    assert set(record['frozen_ten_features'])==set(schema['proposed_features'])
                corrected_support=None
                if baseline is not None:
                    box=record['face_box'];x,y,w,h=box;categories=segmenter.categories_bgr(saved)
                    supports={}
                    for name,mask in [('baseline',baseline),('ycrcb',proposal)]:
                        stats=record['estimators'][name]
                        if stats['valid']:supports[name]=support(saved,mask,exclude,box,categories)
                    if set(supports)=={'baseline','ycrcb'}:
                        try:
                            if landmarks is None:raise ValueError('Boundary landmarks unavailable')
                            crop,geometry=restrict_new_support(supports['baseline'][y:y+h,x:x+w],supports['ycrcb'][y:y+h,x:x+w],landmarks)
                            corrected_support=np.zeros_like(baseline);corrected_support[y:y+h,x:x+w]=crop
                            record.update(correction_status='available',boundary=geometry)
                        except ValueError as error:record.update(correction_status='boundary_unavailable',boundary_error=str(error))
                    for name,mask in [('baseline',baseline),('ycrcb',proposal)]:
                        # Report estimation retention even when correction is unavailable.
                        scoring_support=corrected_support if corrected_support is not None else np.zeros_like(mask)
                        record['estimators'][name]['retention']=support_retention(generation,mask,scoring_support)
                        helper.save(output/'images'/(stem+'_'+name+'_estimate.png'),mask.astype(np.uint8)*255)
                if corrected_support is not None:helper.save(output/'images'/(stem+'_support.png'),corrected_support.astype(np.uint8)*255)
                results.append(record)
                strips.append(np.hstack([panel(saved,None,variant+' input'),panel(saved,baseline,'Baseline measurement'),panel(saved,proposal,'YCrCb measurement'),panel(saved,corrected_support,'Correction: '+record['correction_status'])]))
                with (output/'attempts.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
                print(stem+': '+record['status']+'/'+record['correction_status'],flush=True)
            filename=identifier+'_variants.png';helper.save(output/filename,np.vstack(strips));links.append(f'- [{identifier}: all five variants]({filename})')
        assert len(results)==75
        assert hashes=={p:helper.digest(p) for p in hashes}
        summary=dict(status='complete',sources=source_results,attempts=results,input_sha256=hashes,
            geometry_status_counts=dict(Counter(r['status'] for r in results)),correction_status_counts=dict(Counter(r['correction_status'] for r in results)),
            warning='No automatic source/variant acceptance, no feature fallback or model fit. Source generation mask is not true skin; YCrCb-only support can include non-skin.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'review-index.md').write_text('# Fifteen sources:75 fixed variant attempts\n\nMask previews, not corrected outputs or training approval.\n\n'+'\n'.join(links),encoding='utf-8')
        (output/'run_status.json').write_text('{"status":"complete"}',encoding='utf-8')
        print(json.dumps(dict(geometry=summary['geometry_status_counts'],correction=summary['correction_status_counts'])))
    finally:segmenter.close()


if __name__=='__main__':main()
