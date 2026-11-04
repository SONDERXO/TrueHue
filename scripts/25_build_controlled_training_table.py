"""Generate 24 attempted controlled pairs and input-only development tables.

Run from project root. No fitting, final testing, or original-data edits.
"""
import csv
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters,TRANSFORM_VERSION
from src.data_preparation.controlled_training_table import FEATURES,TARGETS,pair_table_row


def write_table(path,rows,fields):
    with path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def main():
    common=importlib.import_module('16_compare_face_outline')
    prepare=importlib.import_module('11_prepare_training_manifests')
    pilot=importlib.import_module('21_synthetic_pair_pilot')
    check=importlib.import_module('15_prepare_fairface_mask_review')
    source_dir=ROOT/'data/manifests/controlled_development_v1'
    source_path=source_dir/'selected_sources.csv'
    policy_path=source_dir/'distortion_policy.json'
    records=sorted(common.read(source_path),key=lambda r:r['image_id'])
    policy=json.loads(policy_path.read_text(encoding='utf-8'))
    if policy['policy_version']!='controlled_skin_mask_v1' or policy['transform_version']!=TRANSFORM_VERSION:
        raise ValueError('Unsupported transform policy')
    if policy['generation_scope']!='binary_source_skin_mask_only' or policy['generation_boundary_blending']!='none':
        raise ValueError('Unsupported generation scope')
    if len(records)!=8 or len({r['image_id'] for r in records})!=8 or len(policy['variants'])!=3:
        raise ValueError('Expected fixed eight-source, three-variant configuration')
    if any(r['controlled_development_eligible']!='True' for r in records):
        raise ValueError('Ineligible source')
    for key in ('source_image_id','duplicate_group_id'):
        values={}
        for r in records:
            group=r['image_id'] if key=='source_image_id' else r[key]
            if group in values and values[group]!=r['partition']:
                raise ValueError('Source/group partition leakage')
            values[group]=r['partition']
    output=ROOT/'outputs/controlled_training_v1'
    tables=ROOT/'data/manifests/controlled_training_v1'
    if output.exists() or tables.exists():
        raise FileExistsError('Controlled training outputs exist; refusing overwrite')
    config=get_config()
    yunet,model=ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH
    inputs=[source_path,policy_path,yunet,model,Path(__file__),
        ROOT/'src/data_preparation/controlled_training_table.py',
        ROOT/'src/distortion_generation/generate_distortions.py',ROOT/'src/skin_masking/mouth_exclusion.py',
        ROOT/'scripts/11_prepare_training_manifests.py']+[Path(r['image_path']) for r in records]
    hashes={str(p):check.digest(p) for p in inputs}
    output.mkdir();tables.mkdir()
    rows=[]
    for record in records:
        image_id=record['image_id'];stem=image_id.replace('/','_')
        image=cv2.imread(record['image_path'])
        if image is None:
            raise ValueError('Unreadable source: '+image_id)
        boxes=prepare._detect_face_boxes(image,yunet,.85)
        if len(boxes)!=1:
            raise ValueError('Source face count changed: '+image_id)
        x,y,w,h=boxes[0];crop=image[y:y+h,x:x+w].copy()
        mask_result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],model,policy['mask_version'])
        stats=prepare.compute_masked_lab_statistics(crop,mask_result.mask,1000)
        stats['skin_ratio_percent']=round(np.count_nonzero(mask_result.mask)/(w*h)*100,2)
        if check.measurement_differences(record,stats):
            raise ValueError('Source baseline drift: '+image_id)
        mask=np.zeros(image.shape[:2],np.uint8);mask[y:y+h,x:x+w]=mask_result.mask
        pixels=mask>0
        mask_path=output/(stem+'_generation_mask.png')
        if not cv2.imwrite(str(mask_path),mask):
            raise OSError(mask_path)
        reference_rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        reference=reference_rgb.astype(np.float64)/255
        strips=[]
        for variant,params in policy['variants'].items():
            correction=inverse_parameters(**params)
            raw=transform_rgb(reference,**params,clip=False)
            distorted=reference.copy();distorted[pixels]=np.clip(raw[pixels],0,1)
            encoded=pilot.encode(distorted)
            if not np.array_equal(encoded[~pixels],reference_rgb[~pixels]):
                raise ValueError('Outside-mask mutation')
            clipped=(raw>1).any(axis=2)&pixels
            pair_id=stem+'__'+variant
            input_path=output/(pair_id+'_input.png');pilot.write_rgb(input_path,encoded)
            try:
                feature=prepare.process_record(dict(image_id=pair_id,image_path=str(input_path),intended_use='controlled_development'),
                    dataset_name='FairFace',source_mst_label=None,source_label='',dataset_root=output,
                    yunet_model=yunet,landmarker_model=model,minimum_skin_pixels=1000,
                    score_threshold=.85,estimated_rule=None,mask_version=policy['mask_version'])
            except Exception as error:
                feature=dict(processing_status='excluded',exclusion_reason='unexpected_input_error: '+str(error))
            metadata=dict(pair_id=pair_id,source_image_id=image_id,source_path=record['image_path'],
                source_split=record['source_split'],partition=record['partition'],duplicate_group_id=record['duplicate_group_id'],
                variant=variant,mask_version=policy['mask_version'],transform_version=TRANSFORM_VERSION,
                policy_version=policy['policy_version'],distortion_gamma=params['gamma'],
                distortion_red_gain=params['red_gain'],distortion_blue_gain=params['blue_gain'],
                clipped_pixel_count=int(clipped.sum()),generation_skin_pixels=int(pixels.sum()),
                input_path=input_path.relative_to(ROOT).as_posix(),
                generation_mask_path=mask_path.relative_to(ROOT).as_posix(),
                intended_use='controlled_development_not_final_thesis',feature_source='saved_distorted_input_only')
            rows.append(pair_table_row(metadata,feature,correction))
            oracle=encoded.astype(np.float64)/255
            oracle[pixels]=transform_rgb(oracle,**correction)[pixels]
            panels=[image,cv2.cvtColor(encoded,cv2.COLOR_RGB2BGR),cv2.cvtColor(pilot.encode(oracle),cv2.COLOR_RGB2BGR)]
            strip=np.hstack([cv2.resize(p,(224,224)) for p in panels])
            cv2.putText(strip,stem+' / '+variant,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
            strips.append(strip)
        if not cv2.imwrite(str(output/(stem+'_comparison.png')),np.vstack(strips)):
            raise OSError('Comparison image write failed')
    fields=list(rows[0])
    write_table(tables/'all_pairs_audit.csv',rows,fields)
    for use,name in (('train','train.csv'),('development_validation','development_validation.csv'),
                     ('stress_only','clipped_stress.csv'),('excluded','excluded_pairs.csv')):
        write_table(tables/name,[r for r in rows if r['table_use']==use],fields)
    assert all(check.digest(Path(p))==h for p,h in hashes.items())
    from collections import Counter
    summary=dict(attempted_sources=len(records),attempted_pairs=len(rows),
        table_counts=dict(Counter(r['table_use'] for r in rows)),
        pair_status_counts=dict(Counter(r['pair_status'] for r in rows)),
        failures=dict(Counter(r['input_exclusion_reason'] for r in rows if r['table_use']=='excluded')),
        primary_sources_by_partition={use:len({r['source_image_id'] for r in rows if r['table_use']==use})
                                    for use in ('train','development_validation')},
        model_feature_columns=list(FEATURES),model_target_columns=list(TARGETS),
        feature_source='distorted input measurements only; never consume other CSV columns as model features',
        input_sha256=hashes,note='Small technical table only; no model or final test evaluation.')
    (tables/'schema_and_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
