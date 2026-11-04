"""Prepare two declared gamma-only exposure controls per approved source."""
import argparse
import importlib
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.square_measurement import contract,measure,MASK_VERSION
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS
from src.model_training.facial_endpoint_features import facial_endpoint_features
from src.distortion_generation.table2_composite import SETTINGS
from src.evaluation.mask_support_quality import support_retention
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.skin_masking.landmark_exclusion import build_feature_exclusion_mask
from src.skin_masking.mouth_exclusion import exclude_complete_mouth
h=importlib.import_module('256_compare_clean_control_tree_depth');prepare=importlib.import_module('11_prepare_training_manifests')
PARENT=ROOT/'outputs/primary_training_preparation_v1';OUT=ROOT/'outputs/gamma_exposure_controls_v1'


def run():
    if OUT.exists():raise FileExistsError(OUT)
    plan=h.read(PARENT/'plan.json');assert h.read(PARENT/'verification.json')['status']=='pass'
    paths=[Path(__file__),Path(h.__file__),ROOT/'docs/gamma-control-data-specification.md',PARENT/'plan.json',PARENT/'verification.json']
    hashes=dict(plan['input_sha256']);hashes.update({p.relative_to(ROOT).as_posix():h.digest(p) for p in paths})
    for path,sha in hashes.items():assert h.digest(ROOT/path)==sha
    config=get_config();_,identity=contract(ROOT);assert identity==plan['measurement_contract_sha256']
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),identity)
    OUT.mkdir();(OUT/'images').mkdir();(OUT/'geometry').mkdir()
    h.write(OUT/'plan.json',dict(status='frozen_before_generation',sources=plan['sources'],input_sha256=hashes,
        recipe='supplemental_gamma_only_two_directions_v1',not_complete_table2_recipe=True,attempts=52,
        measurement_contract_sha256=identity,correction_tree_fits=0))
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    provider=prepare.detect_landmarks_with_margin;captured=[]
    def capture(*args,**kwargs):
        result=provider(*args,**kwargs)
        if result[0] is not None:captured.append(result[0].copy())
        return result
    prepare.detect_landmarks_with_margin=capture;records=[]
    try:
        for source in plan['sources']:
            reference=cv2.imread(str(ROOT/source['reference_path']));rgb=cv2.cvtColor(reference,cv2.COLOR_BGR2RGB)
            ref_mask=cv2.imread(str(ROOT/source['reference_mask_path']),0)>0;g=SETTINGS[source['severity']]['gamma']
            assert 0<g<1
            for variant,exponent in (('gamma_lighten',g),('gamma_darken',1/g)):
                name=source['source_id'];stem=name+'_'+variant;captured.clear()
                floating=(rgb.astype(float)/255)**exponent
                assert np.all((floating>=0)&(floating<=1))
                generated=rgb.copy();generated[ref_mask]=np.rint(floating[ref_mask]*255).astype(np.uint8)
                bgr=cv2.cvtColor(generated,cv2.COLOR_RGB2BGR)
                def masker(square,box):
                    x,y,w,height=box
                    return prepare.compute_versioned_skin_mask(square[y:y+height,x:x+w],square,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH,MASK_VERSION)
                measured=measure(bgr,detector,masker);mask=measured.mask if measured.mask is not None else np.zeros(ref_mask.shape,np.uint8)
                input_path=OUT/'images'/(stem+'.png');mask_path=OUT/'images'/(stem+'_mask.png')
                assert cv2.imwrite(str(input_path),bgr) and cv2.imwrite(str(mask_path),mask)
                if captured:np.save(OUT/'geometry'/(stem+'_landmarks.npy'),captured[-1])
                row=dict(source_image_id=source['source_image_id'],source_id=name,duplicate_group_id=source['duplicate_group_id'],
                    reference_path=source['reference_path'],reference_mask_path=source['reference_mask_path'],recorded_reference_concerns=source['recorded_reference_concerns'],
                    severity=source['severity'],pair_id=name+'__'+variant,variant=variant,exponent=exponent,
                    paper_target=[1/exponent,1.,1.],target_semantics='algebraic_float_inverse_not_exact_after_uint8',clipped_pixels=0,
                    newly_zero_channel_samples=int(((generated==0)&(rgb>0))[ref_mask].sum()),
                    input_path=input_path.relative_to(ROOT).as_posix(),input_mask_path=mask_path.relative_to(ROOT).as_posix(),
                    input_sha256=h.digest(input_path),input_mask_sha256=h.digest(mask_path),measurement=measured.report,
                    lane='input_failure_hold',training_eligible=False,exact_input_mask_review='pending')
                if measured.report['status']=='success':
                    features=dict(measured.report['features']);features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
                    screen=support_retention(ref_mask,mask>0,mask>0)
                    corrected=np.rint((generated.astype(float)/255)**(1/exponent)*255).astype(np.uint8)
                    row.update(features=features,endpoint_features=facial_endpoint_features(measured.image,mask>0)['features'],support_screen=screen,
                        inverse_rgb_mae_on_generation_support=float(np.abs(corrected.astype(float)-rgb)[ref_mask].mean()/255),
                        lane='primary_pending_exact_mask_review' if screen['screen_pass'] else 'mask_screen_hold')
                records.append(row)
            h.write(OUT/'attempts.json',records);print(source['source_id'],'gamma controls prepared',flush=True)
    finally:prepare.detect_landmarks_with_margin=provider
    assert len(records)==52
    primary=[r for r in records if r['lane']=='primary_pending_exact_mask_review']
    h.write(OUT/'primary_review_queue.json',primary)
    h.write(OUT/'summary.json',dict(status='prepared_not_admitted',sources=26,attempts=52,
        lanes={lane:sum(r['lane']==lane for r in records) for lane in sorted({r['lane'] for r in records})},
        primary_candidate_sources=len({r['source_image_id'] for r in primary}),
        primary_directions={v:sum(r['variant']==v for r in primary) for v in ('gamma_lighten','gamma_darken')},
        new_distorted_admissions=0,correction_tree_fits=0,active_demo_changed=False))


def verify():
    target=OUT/'verification.json'
    if target.exists():raise FileExistsError(target)
    plan=h.read(OUT/'plan.json');rows=h.read(OUT/'attempts.json');assert len(rows)==52 and len({r['pair_id'] for r in rows})==52
    for path,sha in plan['input_sha256'].items():assert h.digest(ROOT/path)==sha
    lookup=DevelopmentMonotoneLookup(h.read(ROOT/'outputs/mst_monotone_square256_v1/development_lookup.json'),plan['measurement_contract_sha256'])
    measurements=0
    for r in rows:
        ref=cv2.cvtColor(cv2.imread(str(ROOT/r['reference_path'])),cv2.COLOR_BGR2RGB);support=cv2.imread(str(ROOT/r['reference_mask_path']),0)>0
        exponent=SETTINGS[r['severity']]['gamma'] if r['variant']=='gamma_lighten' else 1/SETTINGS[r['severity']]['gamma']
        assert exponent==r['exponent'] and r['paper_target']==[1/exponent,1.,1.] and not r['training_eligible']
        # Independent channel-wise power/quantization, including untouched pixels.
        expected=ref.copy()
        for c in range(3):expected[:,:,c][support]=np.rint(np.power(ref[:,:,c][support].astype(float)/255,exponent)*255).astype(np.uint8)
        image=cv2.imread(str(ROOT/r['input_path']));np.testing.assert_array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),expected)
        assert h.digest(ROOT/r['input_path'])==r['input_sha256'] and h.digest(ROOT/r['input_mask_path'])==r['input_mask_sha256']
        assert int(((expected==0)&(ref>0))[support].sum())==r['newly_zero_channel_samples']
        if r['measurement']['status']!='success':continue
        mask=cv2.imread(str(ROOT/r['input_mask_path']),0);x,y,w,height=r['measurement']['face_box'];crop=image[y:y+height,x:x+w]
        points=np.load(OUT/'geometry'/(r['source_id']+'_'+r['variant']+'_landmarks.npy'))
        excluded=build_feature_exclusion_mask(crop,points,dilation=0)
        local,_=exclude_complete_mouth(cv2.bitwise_and(keep_largest_connected_component(create_candidate_mask_bgr(crop)),cv2.bitwise_not(excluded)),points)
        full=np.zeros_like(mask);full[y:y+height,x:x+w]=local;np.testing.assert_array_equal(mask,full)
        stats=compute_masked_lab_statistics(crop,local,1000);assert stats==r['measurement']['statistics']
        features={f:float(stats[k]) for f,k in zip(FEATURES,FEATURE_KEYS)};features['input_mst_index']=lookup.label(features['input_ita_degrees'])-1
        assert features==r['features'] and facial_endpoint_features(image,mask>0)['features']==r['endpoint_features']
        screen=support_retention(support,mask>0,mask>0);assert screen==r['support_screen']
        assert r['lane']==('primary_pending_exact_mask_review' if screen['screen_pass'] else 'mask_screen_hold')
        restored=np.rint(np.power(expected.astype(float)/255,1/exponent)*255).astype(np.uint8)
        assert abs(float(np.abs(restored.astype(float)-ref)[support].mean()/255)-r['inverse_rgb_mae_on_generation_support'])<1e-12
        measurements+=1
    queue=h.read(OUT/'primary_review_queue.json');assert queue==[r for r in rows if r['lane']=='primary_pending_exact_mask_review']
    h.write(target,dict(status='pass',independent_power_and_inverse_targets=52,reconstructed_masks_and_features=measurements,
        new_training_admissions=0,correction_tree_fits=0,
        evidence_sha256={p.relative_to(OUT).as_posix():h.digest(p) for p in OUT.rglob('*') if p.is_file()}))
    print('PASS: 52 generated power curves/targets;',measurements,'mask and feature reconstructions; no admissions.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    verify() if args.verify else run()
