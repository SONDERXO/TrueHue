"""Prepare normal/stress candidate lanes from 26 approved references, not trees."""
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.distortion_generation.three_variant_recipe import render_rgb,VARIANTS,VERSION
from src.distortion_generation.paper_gamma import legacy_to_paper_parameters
from src.model_training.recovery_targets import fit_recovery_target
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.evaluation.mask_support_quality import support_retention
h=importlib.import_module('256_compare_clean_control_tree_depth')
prepare=importlib.import_module('11_prepare_training_manifests')
PARENT=ROOT/'outputs/endpoint_feature_tree_v1';OUT=ROOT/'outputs/primary_training_preparation_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    parent=h.read(PARENT/'plan.json');verified=h.read(PARENT/'verification.json');assert verified['status']=='pass'
    for path,sha in verified['evidence_sha256'].items():assert h.digest(PARENT/path)==sha
    controls=[r for r in parent['rows'] if r['variant']=='identity'];assert len(controls)==26
    historical={r['source_image_id']:r for r in parent['rows'] if r['cohort']=='historical' and r['variant']!='identity'}
    prepared=ROOT/'outputs/correction_training_preparation_v1'
    prior={r['image_id']:r for r in map(__import__('json').loads,(prepared/'attempts.jsonl').read_text(encoding='utf-8').splitlines())}
    sources=[]
    for r in controls:
        source=r['source_image_id'];old=historical.get(source)
        severity=old['severity_probe'] if old else prior[source]['assigned_severity']
        notes=r.get('review_concern',r.get('exact_review_notes',''))
        sources.append(dict(source_image_id=source,source_id=r['pair_id'].split('__')[0],duplicate_group_id=r['duplicate_group_id'],
            reference_path=r['reference_path'],reference_mask_path=r['reference_mask_path'],
            recorded_reference_concerns=notes,severity=severity,existing_control=r))
    config=get_config();spec,identity=contract(ROOT);assert identity==parent['measurement_contract_sha256']
    lookup_path=ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json';lookup=DevelopmentMonotoneLookup(h.read(lookup_path),identity)
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/primary-data-preparation-protocol.md',PARENT/'plan.json',PARENT/'verification.json',
        lookup_path,prepared/'attempts.jsonl',ROOT/'src/distortion_generation/three_variant_recipe.py',ROOT/'src/model_training/recovery_targets.py',
        ROOT/'src/model_training/facial_endpoint_features.py',ROOT/'src/evaluation/mask_support_quality.py']
    paths.extend(ROOT/path for path in spec['dependency_sha256'])
    for s in sources:paths.extend(ROOT/s[k] for k in ('reference_path','reference_mask_path'))
    hashes=dict(parent['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'geometry').mkdir()
    h.write(OUT/'plan.json',dict(status='frozen_before_preparation',sources=sources,attempts=104,recipe_version=VERSION,
        input_sha256=hashes,measurement_contract_sha256=identity,feature_schema=parent['features'],
        future_tree_settings=parent['settings'],source_groups=26,roles='exposed training/development only; reserved roles unopened',
        old_stress_training_preserved=True,new_model_fits=0))
    detector=lambda image:prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    provider=prepare.detect_landmarks_with_margin;captured=[]
    def capture(*args,**kwargs):
        result=provider(*args,**kwargs)
        if result[0] is not None:captured.append(result[0].copy())
        return result
    prepare.detect_landmarks_with_margin=capture;records=[]
    try:
        for source in sources:
            name=source['source_id'];reference=cv2.imread(str(ROOT/source['reference_path']))
            ref_mask=cv2.imread(str(ROOT/source['reference_mask_path']),0)>0;rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB)
            common={k:v for k,v in source.items() if k!='existing_control'}
            records.append(dict(common,pair_id=name+'__primary_identity',variant='identity',lane='approved_original_control',
                training_eligible=True,existing_approval_only=True,input_path=source['reference_path'],input_mask_path=source['reference_mask_path'],
                paper_target=[1.,1.,1.],features={k:source['existing_control'][k] for k in parent['baseline_features']},
                endpoint_features=facial_endpoint_features(reference,ref_mask)['features']))
            for variant in VARIANTS:
                stem=name+'_'+variant;captured.clear()
                transformed,_=render_rgb(rgb,source['severity'],variant)
                _,clipping=render_rgb(rgb[ref_mask][:,None,:],source['severity'],variant)
                generated=rgb.copy();generated[ref_mask]=transformed[ref_mask];bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
                def masker(square,box):
                    x,y,w,height=box
                    return prepare.compute_versioned_skin_mask(square[y:y+height,x:x+w],square,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
                measured=measure(bgr,detector,masker)
                input_path=OUT/'images'/(stem+'.png');assert cv2.imwrite(str(input_path),bgr)
                mask=measured.mask if measured.mask is not None else np.zeros(ref_mask.shape,np.uint8)
                mask_path=OUT/'images'/(stem+'_mask.png');assert cv2.imwrite(str(mask_path),mask)
                if captured:np.save(OUT/'geometry'/(stem+'_landmarks.npy'),captured[-1])
                record=dict(common,pair_id=name+'__primary_'+variant,variant=variant,lane='input_failure_hold',
                    training_eligible=False,exact_input_mask_review='pending',clipping=clipping,measurement=measured.report,
                    input_path=input_path.relative_to(ROOT).as_posix(),input_mask_path=mask_path.relative_to(ROOT).as_posix(),
                    input_sha256=h.digest(input_path),input_mask_sha256=h.digest(mask_path))
                if measured.report['status']=='success':
                    features=dict(measured.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
                    fit=fit_recovery_target(generated,rgb,mask>0,ref_mask)
                    screen=support_retention(ref_mask,mask>0,mask>0)
                    record.update(features=features,endpoint_features=facial_endpoint_features(measured.image,mask>0)['features'],
                        target_fit=fit,support_screen=screen,lane='target_unavailable_hold')
                    if fit['parameters'] is not None:
                        record.update(paper_target=list(legacy_to_paper_parameters(*fit['parameters']).values()))
                        if clipping['clipped_pixels']>0:record['lane']='clipped_stress_pending_mask_review'
                        elif not screen['screen_pass']:record['lane']='unclipped_mask_screen_hold'
                        else:record['lane']='primary_pending_exact_mask_review'
                records.append(record)
            h.write(OUT/'attempts.json',records);print(name,'prepared',flush=True)
    finally:prepare.detect_landmarks_with_margin=provider
    assert len(records)==104
    lanes={lane:sum(r['lane']==lane for r in records) for lane in sorted({r['lane'] for r in records})}
    primary=[r for r in records if r['lane']=='primary_pending_exact_mask_review']
    h.write(OUT/'primary_review_queue.json',primary)
    h.write(OUT/'summary.json',dict(status='preparation_complete_no_tree_fitting',lanes=lanes,attempts=104,sources=26,
        primary_candidate_pairs=len(primary),primary_candidate_sources=len({r['source_image_id'] for r in primary}),
        primary_severity_counts={s:sum(r['severity']==s for r in primary) for s in sorted({r['severity'] for r in records})},
        primary_variants={v:sum(r['variant']==v for r in primary) for v in VARIANTS},new_distorted_training_admissions=0,
        correction_tree_fits=0,active_demo_changed=False,reserved_sources_opened=0))
    print(lanes)


if __name__=='__main__':main()
