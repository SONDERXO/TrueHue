"""Full input-stage stress of frozen endpoint trees; preserve every failure."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import measure,contract,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.model_training.portable_tree import PortableTree
from src.distortion_generation.paper_gamma import transform_rgb
from src.evaluation.correction_prototype import image_errors
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
h=importlib.import_module('256_compare_clean_control_tree_depth')
prepare=importlib.import_module('11_prepare_training_manifests')
PARENT=ROOT/'outputs/endpoint_jpeg_sensitivity_v1';MODELS=ROOT/'outputs/endpoint_feature_tree_v1'
OUT=ROOT/'outputs/endpoint_full_path_jpeg_v1';ENCODINGS=('lossless','jpeg95','jpeg85')


def setup():
    config=get_config();_,identity=contract(ROOT)
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    def detector(image):return prepare._detect_face_boxes(image,ROOT/config.FACE_MODEL_PATH,.85)
    return config,identity,lookup,detector


def summarize(records):
    aggregates=[]
    for encoding in ENCODINGS:
        for scope in ('all','clean','distorted'):
            attempted=[r for r in records if r['encoding']==encoding and (scope=='all' or (r['variant']=='identity')==(scope=='clean'))]
            part=[r for r in attempted if r['status']=='success']
            aggregates.append(dict(encoding=encoding,scope=scope,attempts=len(attempted),successful=len(part),failed=len(attempted)-len(part),
                mean_ciede2000=float(np.mean([r['metrics']['ciede2000_source_mask'] for r in part])) if part else None,
                unchanged_on_success_subset=float(np.mean([r['no_correction']['ciede2000_source_mask'] for r in part])) if part else None,
                corrected_pairs=sum(r['changed_input_pixels']>0 for r in part),
                changed_parameters_vs_fixed_support=sum(r['parameters_changed_vs_fixed'] for r in part),
                changed_masks_vs_original=sum(not r['mask_matches_original'] for r in attempted)))
    clean_failures={e:[r['pair_id'] for r in records if r['encoding']==e and r['variant']=='identity' and r['status']=='success' and r['changed_input_pixels']] for e in ENCODINGS}
    return dict(aggregates=aggregates,clean_overcorrection_ids=clean_failures,
        measurement_failures=[dict(pair_id=r['pair_id'],encoding=r['encoding'],stage=r['measurement']['stage'],reason=r['measurement'].get('reason')) for r in records if r['status']!='success'],
        attempts=141,models_fitted=0,active_demo_changed=False,new_human_approvals=0)


def run():
    if OUT.exists():raise FileExistsError(OUT)
    assert h.read(PARENT/'verification.json')['status']=='pass'
    parent=h.read(PARENT/'plan.json');model_plan=h.read(MODELS/'plan.json');rows={r['pair_id']:r for r in parent['parent_rows']}
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/endpoint-full-path-jpeg-protocol.md',PARENT/'verification.json']
    paths.extend(PARENT/p for p in h.read(PARENT/'verification.json')['evidence_sha256'])
    hashes=dict(parent['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    config,identity,lookup,detector=setup();assert identity==parent['measurement_contract_sha256']
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'geometry').mkdir()
    h.write(OUT/'plan.json',dict(status='frozen_before_full_path',input_sha256=hashes,rows=parent['parent_rows'],
        features=model_plan['features'],measurement_contract_sha256=identity,encodings=ENCODINGS))
    original_provider=prepare.detect_landmarks_with_margin;captured=[]
    def provider(*args,**kwargs):
        result=original_provider(*args,**kwargs)
        if result[0] is not None:captured.append(result[0].copy())
        return result
    prepare.detect_landmarks_with_margin=provider
    records=[]
    try:
        for old in h.read(PARENT/'predictions.json'):
            pair=old['pair_id'];encoding=old['encoding'];row=rows[pair];stem=pair+'_'+encoding
            image=cv2.imread(str(PARENT/old['encoded_input_path']));captured.clear()
            def masker(square,box):
                x,y,w,height=box
                return prepare.compute_versioned_skin_mask(square[y:y+height,x:x+w],square,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
            measured=measure(image,detector,masker)
            mask=measured.mask if measured.mask is not None else np.zeros(image.shape[:2],np.uint8)
            path=OUT/'images'/(stem+'_mask.png');assert cv2.imwrite(str(path),mask)
            if captured:np.save(OUT/'geometry'/(stem+'_landmarks.npy'),captured[-1])
            original_mask=cv2.imread(str(ROOT/row['input_mask_path']),0)>0;selected=mask>0
            union=int((selected|original_mask).sum())
            record=dict(pair_id=pair,encoding=encoding,variant=row['variant'],cohort=row['cohort'],fold_id=old['fold_id'],
                status='failed',measurement=measured.report,mask_sha256=h.digest(path),
                mask_matches_original=bool(np.array_equal(selected,original_mask)),
                original_mask_iou=float((selected&original_mask).sum()/union) if union else None)
            if measured.report['status']=='success':
                features=dict(measured.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
                extra=facial_endpoint_features(measured.image,selected);assert extra['valid'];features.update(extra['features'])
                tree=PortableTree(h.read(MODELS/f'fold_{old["fold_id"]}'/'candidate.json'))
                params=tree.predict_one([features[k] for k in model_plan['features']])
                rgb=cv2.cvtColor(measured.image,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
                score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0;output=rgb.copy()
                output[selected]=np.rint(transform_rgb(rgb.astype(float)/255,*params)[selected]*255).astype(np.uint8)
                assert np.array_equal(output[~selected],rgb[~selected])
                result_path=OUT/'images'/(stem+'_result.png');assert cv2.imwrite(str(result_path),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
                record.update(status='success',features=features,parameters=params,parameters_changed_vs_fixed=params!=old['parameters'],
                    changed_input_pixels=int(np.count_nonzero(np.any(output!=rgb,axis=2))),metrics=image_errors(reference,output,score),
                    no_correction=image_errors(reference,rgb,score),output_sha256=h.digest(result_path))
            records.append(record);print(stem,record['status'],flush=True)
    finally:prepare.detect_landmarks_with_margin=original_provider
    h.write(OUT/'attempts.json',records);h.write(OUT/'summary.json',summarize(records))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');rows={r['pair_id']:r for r in plan['rows']}
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    config,identity,lookup,detector=setup();assert identity==plan['measurement_contract_sha256']
    old={(r['pair_id'],r['encoding']):r for r in h.read(PARENT/'predictions.json')};records=h.read(OUT/'attempts.json')
    assert len(records)==141 and len({(r['pair_id'],r['encoding']) for r in records})==141
    reconstructed=0
    for r in records:
        row=rows[r['pair_id']];prior=old[(r['pair_id'],r['encoding'])];stem=r['pair_id']+'_'+r['encoding']
        image=cv2.imread(str(PARENT/prior['encoded_input_path']));boxes=detector(image)
        assert len(boxes)==r['measurement']['face_count']
        if 'face_box' in r['measurement']:assert list(boxes[0])==r['measurement']['face_box']
        path=OUT/'images'/(stem+'_mask.png');assert h.digest(path)==r['mask_sha256'];mask=cv2.imread(str(path),0)>0
        original=cv2.imread(str(ROOT/row['input_mask_path']),0)>0
        assert bool(np.array_equal(mask,original))==r['mask_matches_original']
        if r['status']!='success':
            assert r['measurement']['status']=='failed' and 'parameters' not in r
            assert not (OUT/'images'/(stem+'_result.png')).exists();continue
        x,y,w,height=r['measurement']['face_box'];crop=image[y:y+height,x:x+w]
        points=np.load(OUT/'geometry'/(stem+'_landmarks.npy'))
        colors=create_candidate_mask_bgr(crop);exclusion=build_feature_exclusion_mask(crop,points,dilation=0)
        initial=cv2.bitwise_and(keep_largest_connected_component(colors),cv2.bitwise_not(exclusion))
        expected,mouth=exclude_complete_mouth(initial,points)
        full=np.zeros(image.shape[:2],np.uint8);full[y:y+height,x:x+w]=expected
        np.testing.assert_array_equal(full>0,mask);assert not np.any((expected>0)&((exclusion>0)|(mouth>0)))
        stats=compute_masked_lab_statistics(crop,expected,1000);assert stats==r['measurement']['statistics']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        features.update(facial_endpoint_features(image,mask)['features']);assert features==r['features']
        membership=h.read(MODELS/f'fold_{r["fold_id"]}'/'membership.json');assert row['source_image_id'] not in {rows[p]['source_image_id'] for p in membership['train_pair_ids']}
        tree=PortableTree(h.read(MODELS/f'fold_{r["fold_id"]}'/'candidate.json'));params=tree.predict_one([features[k] for k in plan['features']]);assert params==r['parameters']
        assert r['parameters_changed_vs_fixed']==(params!=prior['parameters'])
        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB);reference=cv2.cvtColor(cv2.imread(str(ROOT/row['reference_path'])),cv2.COLOR_BGR2RGB)
        score=cv2.imread(str(ROOT/row['reference_mask_path']),0)>0;output=rgb.copy();output[mask]=np.rint(transform_rgb(rgb.astype(float)/255,*params)[mask]*255).astype(np.uint8)
        result_path=OUT/'images'/(stem+'_result.png');assert h.digest(result_path)==r['output_sha256'];np.testing.assert_array_equal(cv2.imread(str(result_path)),cv2.cvtColor(output,cv2.COLOR_RGB2BGR))
        np.testing.assert_array_equal(output[~mask],rgb[~mask]);assert np.count_nonzero(np.any(output!=rgb,axis=2))==r['changed_input_pixels']
        assert image_errors(reference,output,score)==r['metrics'] and image_errors(reference,rgb,score)==r['no_correction'];reconstructed+=1
    assert summarize(records)==h.read(OUT/'summary.json')
    h.write(target,dict(status='pass',face_detection_replays=141,geometry_mask_feature_output_replays=reconstructed,
        explicit_failed_attempts=141-reconstructed,source_separation_verified=True,models_fitted=0,active_demo_changed=False,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS:',141,'detections,',reconstructed,'geometry/feature/output replays;',141-reconstructed,'explicit failures.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
