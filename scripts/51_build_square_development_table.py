"""Build separate square256 development pairs; no correction learner is used."""
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
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters,TRANSFORM_VERSION
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS,TARGETS,pair_table_row
from src.data_preparation.source_group_folds import source_group_folds
from src.skin_masking.material_checked_support import material_checked_support
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter,hair_veto_support

VERSION='controlled_square256_v1'


def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,image):
    if not cv2.imwrite(str(path),image):raise OSError(path)


def table(path,rows,fields):
    with path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def main():
    config=get_config();prepare=importlib.import_module('11_prepare_training_manifests')
    if config.IMAGE_SIZE!=256:raise ValueError('This version requires configured size256')
    old=ROOT/'data/manifests/controlled_training_v2/all_pairs_audit.csv'
    selected=ROOT/'data/manifests/controlled_development_v1/selected_sources.csv'
    attempts=read(old);sources=read(selected)
    if len(attempts)!=38 or len(sources)!=8:raise ValueError('Unexpected development cohort')
    source_lookup={r['image_id']:r for r in sources}
    for row in attempts:
        source=source_lookup[row['source_image_id']]
        if row['partition']!=source['partition'] or row['duplicate_group_id']!=source['duplicate_group_id']:
            raise ValueError('Source allocation mismatch')
    out=ROOT/config.OUTPUTS_ROOT/VERSION;tables=ROOT/'data/manifests'/VERSION
    if out.exists() or tables.exists():raise FileExistsError('Outputs exist; refusing overwrite')
    provenance=ROOT/config.SELFIE_SEGMENTER_MODEL_PATH
    if digest(provenance)!=json.loads(provenance.with_suffix('.provenance.json').read_text())['sha256']:
        raise ValueError('Segmentation model checksum mismatch')
    tracked=[old,selected,Path(__file__),ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH,
             ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH,provenance,
             provenance.with_suffix('.provenance.json'),ROOT/'src/utilities/config.py',
             ROOT/'scripts/11_prepare_training_manifests.py',
             ROOT/'src/distortion_generation/generate_distortions.py',
             ROOT/'src/data_preparation/controlled_training_table.py',
             ROOT/'src/ita_estimation/compute_ita.py',
             ROOT/'src/skin_masking/skin_mask.py',ROOT/'src/skin_masking/mouth_exclusion.py',
             ROOT/'src/skin_masking/landmark_exclusion.py',
             ROOT/'src/skin_masking/material_checked_support.py',
             ROOT/'src/skin_masking/guarded_correction_support.py',
             ROOT/'src/skin_masking/selfie_material_segmenter.py']
    tracked += [Path(r['image_path']) for r in sources]
    tracked += sorted((ROOT/'data/manifests/controlled_training_v2').glob('*.csv'))
    hashes={str(p):digest(p) for p in tracked}
    out.mkdir(parents=True);tables.mkdir(parents=True)
    for name in ['references','inputs','masks','review_boards']:(out/name).mkdir()
    status=out/'run_status.json'
    status.write_text('{"state":"running"}',encoding='utf-8')
    policy=dict(table_version=VERSION,policy_version=VERSION,source_manifest=str(selected),
                attempt_template=str(old),attempts=38,source_count=8,training_sources=7,
                reference_resize='256x256 INTER_LINEAR before generation mask and distortion',
                generation_scope='binary freshly computed source estimation mask only; no blending',
                variants='Exact per-attempt gamma/red/blue values inherited from template; no parameter search',
                mask_version='v2_complete_mouth_v1',correction_mask_policy='material_hair_veto_v1',
                transform_version=TRANSFORM_VERSION,feature_columns=list(FEATURES),target_columns=list(TARGETS),
                routing='Recompute failures and clipping. Never promote historical stress or exclusions. New clipping routes to stress.',
                limitations='Development only; no MST labels, no final method approval, no correction learner used.')
    (tables/'generation_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
    rows=[];checks=[];source_checks=[];boards=[]

    def measure(image):
        mask=np.zeros(image.shape[:2],bool);exclude=np.zeros_like(mask)
        boxes=prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
        info=dict(face_count=len(boxes),face_boxes=[[int(v) for v in b] for b in boxes])
        if len(boxes)!=1:return dict(processing_status='excluded',exclusion_reason='expected_single_face'),mask,exclude,info
        x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],ROOT/config.FACE_LANDMARKER_MODEL_PATH,'v2_complete_mouth_v1')
        mask[y:y+h,x:x+w]=result.mask>0;exclude[y:y+h,x:x+w]=result.exclusion_mask>0
        stats=compute_masked_lab_statistics(crop,result.mask,1000)
        info.update(skin_pixels=int(mask.sum()),landmarks_available=bool(result.landmarks_available))
        reason=('landmarks_unavailable' if not result.landmarks_available else stats['reason'])
        feature=dict(processing_status='success' if result.landmarks_available and stats['valid'] else 'excluded',
                     exclusion_reason=reason or '',**{key:stats[key] for key in FEATURE_KEYS})
        return feature,mask,exclude,info

    segmenter=SelfieMaterialSegmenter(provenance)
    try:
        for source in sorted(sources,key=lambda r:r['image_id']):
            source_id=source['image_id'];stem=source_id.replace('/','_')
            original=cv2.imread(source['image_path'])
            if original is None:raise ValueError('Unreadable source '+source_id)
            resized=cv2.resize(original,(256,256),interpolation=cv2.INTER_LINEAR)
            reference_path=out/'references'/(stem+'_reference.png');save(reference_path,resized)
            clean=cv2.imread(str(reference_path));np.testing.assert_array_equal(clean,resized)
            feature,generation_mask,_,source_info=measure(clean)
            source_checks.append(dict(source_image_id=source_id,**feature,**source_info))
            if feature['processing_status']!='success':raise ValueError('Source generation mask unavailable '+source_id)
            mask_path=out/'masks'/(stem+'_generation_mask.png');save(mask_path,generation_mask.astype(np.uint8)*255)
            rgb=cv2.cvtColor(clean,cv2.COLOR_BGR2RGB);reference=rgb.astype(float)/255
            panels=[]
            for prior in [r for r in attempts if r['source_image_id']==source_id]:
                pair='square256__'+prior['pair_id']
                params={key:float(prior['distortion_'+key]) for key in ['gamma','red_gain','blue_gain']}
                target=inverse_parameters(**params);raw=transform_rgb(reference,**params,clip=False)
                clipped=int((generation_mask & ((raw<0)|(raw>1)).any(axis=2)).sum())
                generated=reference.copy();generated[generation_mask]=np.clip(raw[generation_mask],0,1)
                encoded=np.rint(generated*255).astype(np.uint8)
                np.testing.assert_array_equal(encoded[~generation_mask],rgb[~generation_mask])
                if prior['variant']=='identity_control':np.testing.assert_array_equal(encoded,rgb)
                input_path=out/'inputs'/(pair+'_input.png');save(input_path,cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR))
                saved=cv2.imread(str(input_path));np.testing.assert_array_equal(cv2.cvtColor(saved,cv2.COLOR_BGR2RGB),encoded)
                feature,estimate,exclude,info=measure(saved)
                support=np.zeros_like(estimate)
                support_status='unavailable_input_features'
                if feature['processing_status']=='success':
                    x,y,w,h=info['face_boxes'][0]
                    material=np.zeros_like(estimate)
                    material[y:y+h,x:x+w]=material_checked_support(saved[y:y+h,x:x+w],estimate[y:y+h,x:x+w],exclude[y:y+h,x:x+w])
                    categories=segmenter.categories_bgr(saved)
                    support=hair_veto_support(categories,material)
                    assert not np.any(support & (categories==1))
                    assert not np.any(support & exclude)
                    support_status='available'
                for name,mask in [('estimation',estimate),('correction',support)]:save(out/'masks'/(pair+'_'+name+'.png'),mask.astype(np.uint8)*255)
                metadata=dict(pair_id=pair,source_image_id=source_id,source_path=source['image_path'],
                    source_split=source['source_split'],partition=source['partition'],duplicate_group_id=source['duplicate_group_id'],
                    variant=prior['variant'],mask_version=policy['mask_version'],transform_version=TRANSFORM_VERSION,policy_version=VERSION,
                    **{'distortion_'+key:value for key,value in params.items()},clipped_pixel_count=clipped,
                    generation_skin_pixels=int(generation_mask.sum()),input_path=input_path.relative_to(ROOT).as_posix(),
                    generation_mask_path=mask_path.relative_to(ROOT).as_posix(),reference_path=reference_path.relative_to(ROOT).as_posix(),
                    parent_pair_id=prior['pair_id'],historical_table_use=prior['table_use'],image_width=256,image_height=256,
                    intended_use='controlled_development_not_final_thesis',feature_source='saved_distorted_input_only')
                row=pair_table_row(metadata,feature,target)
                if prior['table_use']=='excluded' and row['table_use']!='excluded':
                    row.update(table_use='excluded',pair_status='held_historical_exclusion_pending_review')
                elif prior['table_use']=='stress_only' and row['table_use']!='excluded':row['table_use']='stress_only'
                rows.append(row)
                inverse=encoded.astype(float)/255
                inverse[generation_mask]=transform_rgb(inverse,**target)[generation_mask]
                residual=np.abs(np.rint(inverse*255).astype(int)-rgb.astype(int))
                check=dict(pair_id=pair,**info,correction_support_status=support_status,correction_pixels=int(support.sum()),
                           unclipped=clipped==0,source_mask_inverse_max_channel_error=int(residual[generation_mask].max()),
                           saved_input_sha256=digest(input_path),reference_sha256=digest(reference_path))
                checks.append(check)
                overlays=[]
                for label,mask in [('Estimation',estimate),('Correction support',support)]:
                    panel=saved.copy();panel[mask]=np.rint(.55*panel[mask]+.45*np.array([0,220,0])).astype(np.uint8)
                    panel=cv2.copyMakeBorder(panel,36,0,0,0,cv2.BORDER_CONSTANT)
                    cv2.putText(panel,prior['variant']+' '+label,(3,14),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
                    cv2.putText(panel,row['table_use'],(3,29),cv2.FONT_HERSHEY_SIMPLEX,.34,(255,255,255),1)
                    overlays.append(panel)
                panels.append(np.hstack(overlays))
                with (out/'attempts.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(row=row,check=check))+'\n')
                print(pair+': '+row['table_use'],flush=True)
            name=stem+'_masks.png';save(out/'review_boards'/name,np.vstack(panels));boards.append((source_id,name))
        if len(rows)!=38 or len({r['pair_id'] for r in rows})!=38:raise ValueError('Attempt accounting failed')
        fields=list(rows[0]);table(tables/'all_pairs_audit.csv',rows,fields)
        for use,name in [('train','train.csv'),('development_validation','development_validation.csv'),('stress_only','clipped_stress.csv'),('excluded','excluded_pairs.csv')]:
            table(tables/name,[r for r in rows if r['table_use']==use],fields)
        folds=source_group_folds([r for r in rows if r['table_use']=='train'])
        (tables/'source_group_folds.json').write_text(json.dumps(dict(status='plans_only_no_fitting',folds=folds),indent=2),encoding='utf-8')
        assert hashes=={str(p):digest(p) for p in tracked},'Original inputs changed'
        summary=dict(status='complete',table_version=VERSION,attempted_pairs=38,
            table_counts=dict(Counter(r['table_use'] for r in rows)),
            routing_changes=[dict(pair_id=r['pair_id'],old=r['historical_table_use'],new=r['table_use']) for r in rows if r['table_use']!=r['historical_table_use']],
            total_clipped_pixels=sum(r['clipped_pixel_count'] for r in rows),
            feature_columns=list(FEATURES),target_columns=list(TARGETS),source_checks=source_checks,pair_checks=checks,
            input_sha256=hashes,output_table_sha256={p.name:digest(p) for p in tables.iterdir() if p.is_file()},
            warning='Technical eligibility only, not mask acceptance; no model fit, no MST conditioning, no final evaluation.')
        (tables/'schema_and_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (out/'review-index.md').write_text('# Fresh 256 development pairs\n\nEstimation and experimental correction masks; not learned correction results.\n\n'+'\n'.join(f'- [{source}](review_boards/{name})' for source,name in boards),encoding='utf-8')
        status.write_text('{"state":"complete"}',encoding='utf-8')
        print(json.dumps(summary['table_counts']))
    except Exception as error:
        status.write_text(json.dumps(dict(state='failed',error=str(error),completed_attempts=len(rows))),encoding='utf-8');raise
    finally:segmenter.close()


if __name__=='__main__':main()
