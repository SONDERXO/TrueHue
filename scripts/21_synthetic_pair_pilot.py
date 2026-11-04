"""Local five-source/three-variant operator pilot; no model or final data split."""
import csv
import importlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.distortion_generation.generate_distortions import transform_rgb,inverse_parameters,TRANSFORM_VERSION
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

MASK_VERSION='v2_complete_mouth_v1'
# Fixed technical probes, identical for each source; not tone-dependent severity.
VARIANTS={'dark':(.7,.85,.95),'bright_warm':(1.25,1.08,.95),'color_shift':(1.,.85,1.15)}


def write_csv(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)


def encode(image):
    return np.rint(np.clip(image,0,1)*255).astype(np.uint8)


def write_rgb(path,image):
    if not cv2.imwrite(str(path),cv2.cvtColor(image,cv2.COLOR_RGB2BGR)):
        raise OSError(path)


def main():
    common=importlib.import_module('16_compare_face_outline')
    prepare=importlib.import_module('11_prepare_training_manifests')
    check=importlib.import_module('15_prepare_fairface_mask_review')
    output=ROOT/'outputs/synthetic_pair_pilot_v1'
    if output.exists():
        raise FileExistsError('Pilot exists; refusing overwrite')
    audit_path=ROOT/'outputs/accepted_exclusion_audit/audit.csv'
    manifest_path=ROOT/'data/manifests'/MASK_VERSION/'fairface_candidate_processed_manifest.csv'
    manifest={r['image_id']:r for r in common.read(manifest_path)}
    pool=sorted(r['image_id'] for r in common.read(audit_path)
                if r['exclusion_audit']=='no_obvious_gross_misalignment'
                and manifest[r['image_id']]['processing_status']=='success')
    selected=sorted(random.Random(42).sample(pool,5))
    config=get_config()
    yunet,model=ROOT/config.FACE_MODEL_PATH,ROOT/config.FACE_LANDMARKER_MODEL_PATH
    inputs=[audit_path,manifest_path,yunet,model,Path(__file__),
        ROOT/'src/distortion_generation/generate_distortions.py',ROOT/'src/skin_masking/mouth_exclusion.py',
        ROOT/'scripts/11_prepare_training_manifests.py']
    inputs += [Path(manifest[k]['image_path']) for k in selected]
    hashes={str(p):check.digest(p) for p in inputs}
    output.mkdir()
    rows=[]
    input_features=[]
    tiles=[]
    for image_id in selected:
        record=manifest[image_id]
        image=cv2.imread(record['image_path'])
        if image is None:
            raise ValueError(image_id)
        boxes=prepare._detect_face_boxes(image,yunet,.85)
        if len(boxes)!=1:
            raise ValueError('Expected one source face: '+image_id)
        x,y,w,h=boxes[0]
        crop=image[y:y+h,x:x+w].copy()
        result=prepare.compute_versioned_skin_mask(crop,image,boxes[0],model,MASK_VERSION)
        stats=compute_masked_lab_statistics(crop,result.mask,1000)
        stats['skin_ratio_percent']=round(np.count_nonzero(result.mask)/(w*h)*100,2)
        if check.measurement_differences(record,stats):
            raise ValueError('Versioned baseline drift: '+image_id)
        mask=np.zeros(image.shape[:2],np.uint8)
        mask[y:y+h,x:x+w]=result.mask
        pixels=mask>0
        reference=cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(np.float64)/255
        stem=image_id.replace('/','_')
        mask_path=output/(stem+'_generation_mask.png')
        if not cv2.imwrite(str(mask_path),mask):
            raise OSError(mask_path)
        for name,params in VARIANTS.items():
            inverse=inverse_parameters(*params)
            raw=transform_rgb(reference,*params,clip=False)
            distorted=reference.copy()
            distorted[pixels]=np.clip(raw[pixels],0,1)
            clipped=(raw>1).any(axis=2)&pixels
            # Oracle uses the source mask and known parameters, never a trained prediction.
            float_corrected=reference.copy()
            float_corrected[pixels]=transform_rgb(distorted,**inverse)[pixels]
            encoded_input=encode(distorted)
            quantized=encoded_input.astype(np.float64)/255
            oracle=quantized.copy()
            oracle[pixels]=transform_rgb(quantized,**inverse)[pixels]
            encoded_oracle=encode(oracle)
            input_path=output/(stem+'_'+name+'_input.png')
            oracle_path=output/(stem+'_'+name+'_oracle.png')
            write_rgb(input_path,encoded_input)
            write_rgb(oracle_path,encoded_oracle)
            assert np.array_equal(encoded_input[~pixels],cv2.cvtColor(image,cv2.COLOR_BGR2RGB)[~pixels])
            assert np.array_equal(encoded_oracle[~pixels],encoded_input[~pixels])
            unclipped=pixels&~clipped
            err=np.abs(float_corrected-reference)
            quant_error=np.abs(encoded_oracle.astype(float)/255-reference)
            probe_id=stem+'_'+name
            row=dict(source_image_id=image_id,pilot_id=probe_id,source_path=record['image_path'],
                source_split=image_id.split('__')[1].split('/')[0],variant=name,
                mask_version=MASK_VERSION,transform_version=TRANSFORM_VERSION,
                distortion_gamma=params[0],distortion_red_gain=params[1],distortion_blue_gain=params[2],
                correction_gamma=float(inverse['gamma']),correction_red_gain=float(inverse['red_gain']),
                correction_blue_gain=float(inverse['blue_gain']),skin_pixels=int(pixels.sum()),
                clipped_pixel_count=int(clipped.sum()),clipped_pixel_fraction=float(clipped.sum()/pixels.sum()),
                float_unclipped_max_error=float(err[unclipped].max()) if unclipped.any() else '',
                distorted_mae_skin=float(np.abs(quantized-reference)[pixels].mean()),
                oracle_mae_skin=float(quant_error[pixels].mean()),
                oracle_mae_clipped=float(quant_error[clipped].mean()) if clipped.any() else '',
                input_path=input_path.relative_to(ROOT).as_posix(),oracle_path=oracle_path.relative_to(ROOT).as_posix(),
                generation_mask_path=mask_path.relative_to(ROOT).as_posix(),
                intended_use='technical_pilot_only')
            if row['float_unclipped_max_error']>1e-12:
                raise ValueError('Analytic inverse check failed')
            rows.append(row)
            feature=prepare.process_record(dict(image_id=probe_id,image_path=str(input_path),intended_use='technical_pilot_only'),
                dataset_name='FairFace',source_mst_label=None,source_label='',dataset_root=output,
                yunet_model=yunet,landmarker_model=model,minimum_skin_pixels=1000,score_threshold=.85,
                estimated_rule=None,mask_version=MASK_VERSION)
            feature.update(source_image_id=image_id,mask_version=MASK_VERSION,feature_source='distorted_input_only')
            input_features.append(feature)
            panels=[cv2.cvtColor(encode(reference),cv2.COLOR_RGB2BGR),cv2.cvtColor(encoded_input,cv2.COLOR_RGB2BGR),
                    cv2.cvtColor(encoded_oracle,cv2.COLOR_RGB2BGR)]
            strip=np.hstack([cv2.resize(p,(224,224)) for p in panels])
            cv2.putText(strip,stem+' / '+name,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
            cv2.imwrite(str(output/(probe_id+'_comparison.png')),strip)
            tiles.append(strip)
    for start in range(0,len(tiles),3):
        cv2.imwrite(str(output/f'source_sheet_{start//3+1:02d}.png'),np.vstack(tiles[start:start+3]))
    write_csv(output/'pairs.csv',rows)
    write_csv(output/'distorted_input_features.csv',input_features)
    assert all(check.digest(Path(p))==h for p,h in hashes.items())
    summary=dict(source_count=len(selected),source_ids=selected,variants_per_source=3,pair_count=len(rows),
        selection_seed=42,selection_pool_size=len(pool),mask_version=MASK_VERSION,transform_version=TRANSFORM_VERSION,
        probes_with_clipping=sum(r['clipped_pixel_count']>0 for r in rows),
        max_float_unclipped_error=max(r['float_unclipped_max_error'] for r in rows),
        mean_distorted_mae_skin=float(np.mean([r['distorted_mae_skin'] for r in rows])),
        mean_oracle_mae_skin=float(np.mean([r['oracle_mae_skin'] for r in rows])),
        distorted_pipeline_successes=sum(r['processing_status']=='success' for r in input_features),
        hashes=hashes,note='Known-parameter oracle, fixed source mask for generation/scoring; not learned performance or final evaluation.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='hashes'},indent=2))


if __name__=='__main__':
    main()
