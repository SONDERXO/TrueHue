"""Add fixed unclipped exposure/identity probes to existing training sources only."""
import csv
import importlib
import json
from pathlib import Path
import shutil
import sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.correction.correct_image import MATERIAL_HAIR_POLICY,LEGACY_POLICY
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters,TRANSFORM_VERSION
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS,pair_table_row
from src.data_preparation.source_group_folds import source_group_folds

POLICY_VERSION='controlled_exposure_identity_v1'
VARIANTS={'identity_control':dict(gamma=1.,red_gain=1.,blue_gain=1.),
          'mild_bright_exposure':dict(gamma=1.10,red_gain=1.,blue_gain=1.)}


def write_csv(path,rows,fields):
    with path.open('x',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def main():
    api=importlib.import_module('39_correct_image');helper=importlib.import_module('29_compare_correction_boundaries')
    draw=importlib.import_module('31_guard_correction_support').sheet
    config=get_config();base=ROOT/config.OUTPUTS_ROOT
    old=ROOT/'data/manifests/controlled_training_v1';tables=ROOT/'data/manifests/controlled_training_v2'
    out=base/'controlled_training_v2'
    if tables.exists() or out.exists():raise FileExistsError('Revised table/output exists; refusing overwrite')
    selected_path=ROOT/'data/manifests/controlled_development_v1/selected_sources.csv'
    selected=helper.read(selected_path);sources=sorted([r for r in selected if r['partition']=='train'],key=lambda r:r['image_id'])
    originals={name:helper.read(old/name) for name in ('train.csv','development_validation.csv','clipped_stress.csv','excluded_pairs.csv')}
    if len(sources)!=7 or any(r['controlled_development_eligible']!='True' for r in sources):raise ValueError('Expected existing seven eligible training sources')
    if {r['image_id'] for r in sources}!={r['source_image_id'] for r in originals['train.csv']}:raise ValueError('Training-source set changed')
    heldout={r['source_image_id'] for r in originals['development_validation.csv']}
    if heldout&{r['image_id'] for r in sources}:raise ValueError('Development source entered augmentation')
    paths=[Path(__file__),ROOT/'src/data_preparation/source_group_folds.py',ROOT/'src/data_preparation/controlled_training_table.py',
        ROOT/'src/distortion_generation/generate_distortions.py',ROOT/'scripts/39_correct_image.py',ROOT/'src/correction/correct_image.py',
        ROOT/'src/utilities/config.py',ROOT/'scripts/11_prepare_training_manifests.py',selected_path,
        ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,
        ROOT/config.SELFIE_SEGMENTER_MODEL_PATH,ROOT/'data/manifests/material_review_v1/material_review_labels.json']
    paths += [old/name for name in originals]
    for row in sources:paths += [Path(row['image_path']),base/'controlled_training_v1'/(row['image_id'].replace('/','_')+'_generation_mask.png')]
    hashes={str(p):api.digest(p) for p in paths}
    tables.mkdir();out.mkdir();(out/'inputs').mkdir();(out/'masks').mkdir();(out/'review_boards').mkdir()
    status_path=out/'run_status.json'
    def status(state,**kw):status_path.write_text(json.dumps(dict(state=state,**kw),indent=2),encoding='utf-8')
    status('running',training_sources=7,expected_augmentation_attempts=14)
    policy=dict(policy_version=POLICY_VERSION,table_version='controlled_training_v2',variants=VARIANTS,
        source_scope='Existing seven training sources only; no validation source augmentation',
        generation_scope='binary_source_skin_mask_only',generation_boundary_blending='none',
        mask_version='v2_complete_mouth_v1',correction_mask_policy=MATERIAL_HAIR_POLICY,transform_version=TRANSFORM_VERSION,
        failure_policy='Keep every attempted row; failed features blank; clipped successes stress-only',
        frozen_tables='Original development_validation.csv,clipped_stress.csv,excluded_pairs.csv copied byte-for-byte',
        feature_policy='Four explicit saved-input Lab/ITA columns only; no target/provenance columns enter X',
        old_rows='Original train rows retained verbatim as field values, including original policy_version; new rows have the augmentation policy_version',
        learner_status='No fitting; frozen prototype runtime used only to check availability/features/masks; its predictions are not new targets',
        note='Development data revision only. Ordinary source references are not calibrated color truth. Identity means no synthetic transform, not a claim that the photo needs no real-world correction.')
    (tables/'augmentation_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    augmentation=[];runtime_checks=[];runtime=None
    try:
        runtime=api.CorrectionRuntime()
        for record in sources:
            image_id=record['image_id'];stem=image_id.replace('/','_');clean=cv2.imread(record['image_path'])
            if clean is None:raise ValueError('Unreadable source: '+image_id)
            baseline=runtime.correct(clean,LEGACY_POLICY)
            source_mask=baseline.estimation_mask
            prior_mask=cv2.imread(str(base/'controlled_training_v1'/(stem+'_generation_mask.png')),0)>0
            np.testing.assert_array_equal(source_mask,prior_mask)
            np.testing.assert_allclose([baseline.features[k] for k in FEATURES],[float(record[k]) for k in FEATURE_KEYS],atol=.00005,rtol=0)
            generation_path=out/'masks'/(stem+'_generation_mask.png')
            if not cv2.imwrite(str(generation_path),source_mask.astype(np.uint8)*255):raise OSError('Generation-mask write failed')
            reference_rgb=cv2.cvtColor(clean,cv2.COLOR_BGR2RGB);reference=reference_rgb.astype(float)/255
            previews=[];titles=[]
            for variant,parameters in VARIANTS.items():
                pair=stem+'__'+variant;raw=transform_rgb(reference,**parameters,clip=False)
                clipping=int((source_mask&((raw<0)|(raw>1)).any(axis=2)).sum())
                generated=reference.copy();generated[source_mask]=np.clip(raw[source_mask],0,1)
                encoded=np.rint(generated*255).astype(np.uint8)
                np.testing.assert_array_equal(encoded[~source_mask],reference_rgb[~source_mask])
                if variant=='identity_control':np.testing.assert_array_equal(encoded,reference_rgb)
                input_path=out/'inputs'/(pair+'_input.png')
                if not cv2.imwrite(str(input_path),cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR)):raise OSError('Input write failed')
                saved=cv2.imread(str(input_path));np.testing.assert_array_equal(cv2.cvtColor(saved,cv2.COLOR_BGR2RGB),encoded)
                check=dict(pair_id=pair,variant=variant,clipped_pixel_count=clipping)
                try:
                    result=runtime.correct(saved,MATERIAL_HAIR_POLICY)
                    # Only the freshly decoded input statistics enter the feature row.
                    feature=dict(processing_status='success',exclusion_reason='',**{key:result.features[name] for key,name in zip(FEATURE_KEYS,FEATURES)})
                    if variant=='identity_control':
                        assert result.features==baseline.features
                        np.testing.assert_array_equal(result.estimation_mask,source_mask)
                    for name,mask in [('estimation',result.estimation_mask),('correction',result.correction_mask)]:
                        if not cv2.imwrite(str(out/'masks'/(pair+'__'+name+'.png')),mask.astype(np.uint8)*255):raise OSError('Runtime mask write failed')
                    check.update(status='available',estimation_pixels=int(result.estimation_mask.sum()),correction_pixels=int(result.correction_mask.sum()),
                        correction_policy=result.metadata['mask_policy'],correction_model_sha256=result.metadata['correction_model_sha256'])
                    overlay=saved.copy();overlay[result.correction_mask]=np.rint(.5*saved[result.correction_mask]+.5*np.array([0,200,0])).astype(np.uint8)
                except Exception as error:
                    feature=dict(processing_status='excluded',exclusion_reason='input_runtime_failure: '+str(error));check.update(status='excluded',error=str(error));overlay=saved.copy()
                target=inverse_parameters(**parameters)
                metadata=dict(pair_id=pair,source_image_id=image_id,source_path=record['image_path'],source_split=record['source_split'],partition='train',
                    duplicate_group_id=record['duplicate_group_id'],variant=variant,mask_version=policy['mask_version'],transform_version=TRANSFORM_VERSION,
                    policy_version=POLICY_VERSION,distortion_gamma=parameters['gamma'],distortion_red_gain=parameters['red_gain'],distortion_blue_gain=parameters['blue_gain'],
                    clipped_pixel_count=clipping,generation_skin_pixels=int(source_mask.sum()),input_path=input_path.relative_to(ROOT).as_posix(),
                    generation_mask_path=generation_path.relative_to(ROOT).as_posix(),intended_use='controlled_development_not_final_thesis',feature_source='saved_distorted_input_only')
                row=pair_table_row(metadata,feature,target);augmentation.append(row);runtime_checks.append(check)
                with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(pair_id=pair,table_use=row['table_use'],runtime_check=check))+'\n')
                previews += [reference_rgb,encoded,cv2.cvtColor(overlay,cv2.COLOR_BGR2RGB)]
                titles += ['Source reference',variant,'Current correction support']
            draw(out/'review_boards'/(stem+'__augmentation.png'),previews,titles,columns=3)
            status('running',augmentation_attempts_completed=len(augmentation))
        if len(augmentation)!=14:raise ValueError('Missing augmentation attempts')
        combined_train=originals['train.csv']+[r for r in augmentation if r['table_use']=='train']
        all_rows=sum(originals.values(),[])+augmentation
        if len({r['pair_id'] for r in all_rows})!=len(all_rows):raise ValueError('Duplicate pair IDs')
        fields=list(originals['train.csv'][0]);write_csv(tables/'train.csv',combined_train,fields)
        write_csv(tables/'augmentation_attempts.csv',augmentation,fields)
        write_csv(tables/'all_pairs_audit.csv',all_rows,fields)
        for use,name in [('excluded','augmentation_excluded_pairs.csv'),('stress_only','augmentation_clipped_stress.csv')]:
            write_csv(tables/name,[r for r in augmentation if r['table_use']==use],fields)
        for name in ('development_validation.csv','clipped_stress.csv','excluded_pairs.csv'):
            shutil.copyfile(old/name,tables/name)
            if api.digest(old/name)!=api.digest(tables/name):raise ValueError('Frozen held-out table changed')
        np.testing.assert_equal(helper.read(tables/'train.csv')[:len(originals['train.csv'])],originals['train.csv'])
        folds=source_group_folds(helper.read(tables/'train.csv'))
        fold_spec=dict(status='planned_only_no_models_fitted',folds=folds,
            note='Inner checks over training-source/known-duplicate groups only; subject identity separation remains unverified. Development source19 and clipped stress rows never enter these folds.')
        (tables/'source_group_folds.json').write_text(json.dumps(fold_spec,indent=2),encoding='utf-8')
        (out/'runtime_checks.json').write_text(json.dumps(runtime_checks,indent=2),encoding='utf-8')
        if not all(api.digest(Path(p))==value for p,value in hashes.items()):raise RuntimeError('Original inputs changed during build')
        summary=dict(table_version='controlled_training_v2',old_training_pairs=16,augmentation_attempts=14,
            augmentation_routing=dict(Counter(r['table_use'] for r in augmentation)),training_pairs=len(combined_train),training_sources=7,
            training_variants=dict(Counter(r['variant'] for r in combined_train)),new_clipped_pixels=sum(r['clipped_pixel_count'] for r in augmentation),
            full_identity_training_pairs=sum(all(float(r[k])==1. for k in TARGETS) for r in combined_train),
            frozen_development_pairs=3,frozen_stress_pairs=4,frozen_excluded_pairs=1,total_audit_attempts=len(all_rows),
            planned_inner_source_folds=len(folds),model_feature_columns=list(FEATURES),model_target_columns=list(TARGETS),
            generation_policy_versions=sorted({r['policy_version'] for r in combined_train}),correction_mask_policy=MATERIAL_HAIR_POLICY,
            input_sha256=hashes,output_table_sha256={p.name:api.digest(p) for p in sorted(tables.iterdir()) if p.is_file()},
            note='No learner fitted, predictions are not targets, no validation/stress promotion or source expansion. Existing mask-limited cases remain explicit and are not automatically reapproved.')
        (tables/'schema_and_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        status('complete',training_pairs=len(combined_train),augmentation_attempts=14)
        print(json.dumps({k:v for k,v in summary.items() if k not in ('input_sha256','output_table_sha256')},indent=2))
    except Exception as error:
        status('failed',error=str(error),augmentation_attempts_completed=len(augmentation));raise
    finally:
        if runtime is not None:runtime.close()


if __name__=='__main__':main()
