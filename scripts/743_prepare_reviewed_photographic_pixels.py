"""Prepare exact paired pixels and edited native supports; no costs or fits."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.demo.manual_refinement import digest,verify_export
from src.demo.labelled_measurement import write
from src.model_training.aligned_correction_support import project_alpha
from src.skin_masking.fixed_face_input_bridge import native_projection

AUDIT=ROOT/'outputs/photographic_support_review_audit_v1'
OUT=ROOT/'outputs/reviewed_photographic_pixels_v1'
BASES=dict(source=ROOT/'outputs/ppr10k_native_pipeline_diagnostic_v1',target=ROOT/'outputs/ppr10k_expert_control_readiness_v1')


def main():
    if OUT.exists():raise FileExistsError('Preserve existing or partial preparation')
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    audit=read(AUDIT/'audit_PRIVATE.json');assert audit['passed']
    assert audit['summary']['missing_roles']==[] and audit['summary']['valid_latest']==14
    bound=dict(audit['input_sha256'])
    for p,h in bound.items():assert digest(p)==h
    inventory={role:{k.replace('\\','/'):v for k,v in read(parent/'artifact_sha256_PRIVATE.json').items()} for role,parent in BASES.items()}
    full={}
    for frame in sorted({r['frame'] for r in audit['latest']}):
        for role,parent in BASES.items():
            name='source_rgb8.png' if role=='source' else 'target_rgb8.png';rel=frame+'/'+name;p=parent/rel
            assert digest(p)==inventory[role][rel];bound[str(p)]=digest(p)
            image=cv2.imread(str(p));assert image is not None and image.dtype==np.uint8
            full[(frame,role)]=image
        assert full[(frame,'source')].shape==full[(frame,'target')].shape
    OUT.mkdir();records=[]
    for row in audit['latest']:
        folder=Path(row['annotation']);verify_export(folder)
        assert digest(folder/'manifest.json')==row['manifest_sha256']
        report=read(folder/'report.json');bridge=report['input_bridge'];frame=report['frame'];role=report['role']
        original=full[(frame,role)];reference=full[(frame,'target')]
        assert list(original.shape)==bridge['source_shape']
        left,top,right,bottom=bridge['native_bounds']
        assert right-left==bottom-top==bridge['native_side']
        sliced=original[top:bottom,left:right]
        normalized=cv2.resize(sliced,(256,256),interpolation=cv2.INTER_LINEAR)
        assert np.array_equal(normalized,cv2.imread(str(folder/'photo_used.png')))
        masks={k:cv2.imread(str(folder/(k+'_mask.png')),0) for k in ['measurement','correction','protected']}
        measurement,_=native_projection(masks['measurement'],bridge)
        correction,_=native_projection(masks['correction'],bridge)
        alpha,protected=project_alpha(np.load(folder/'correction_alpha.npy',allow_pickle=False),masks['protected']>0,bridge)
        assert not alpha[protected].any()
        scoring=alpha>0;assert scoring.any()
        assert np.array_equal(measurement,cv2.imread(str(AUDIT/(row['case_id']+'__measurement_native.png')),0))
        assert np.array_equal(alpha,np.load(AUDIT/(row['case_id']+'__alpha_native.npy'),allow_pickle=False))
        dest=OUT/row['case_id'];dest.mkdir()
        np.savez_compressed(dest/'paired_pixels.npz',input_rgb8=np.ascontiguousarray(original[:,:,::-1]),
            reference_rgb8=np.ascontiguousarray(reference[:,:,::-1]),alpha=alpha,protected=protected,
            measurement_mask=measurement,correction_mask=correction,scoring_mask=scoring)
        # Same coordinates for viewing the reference of this role; no reference features are extracted.
        target_crop=cv2.resize(reference[top:bottom,left:right],(256,256),interpolation=cv2.INTER_LINEAR)
        header=np.full((30,512,3),255,np.uint8)
        cv2.putText(header,row['case_id']+' | own input / same-grid reference',(4,20),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,0,0),1)
        assert cv2.imwrite(str(dest/'coordinate_board.png'),np.vstack([header,np.hstack([normalized,target_crop])]))
        record=dict(case_id=row['case_id'],frame=frame,role=role,publisher_group=report['publisher_group'],
            annotation_manifest_sha256=row['manifest_sha256'],task_manifest_sha256=report['task_manifest_sha256'],
            support_method_sha256=report['method_sha256'],input_bridge=bridge,
            pixels_file=str(dest/'paired_pixels.npz'),pixels_sha256=digest(dest/'paired_pixels.npz'),
            own_input_exact_cached_slice=True,reference_policy='same_publisher_pixel_grid_no_warp',
            registration_verified=False,correspondence_status='declared_editor_pair_assumption_not_registration_proof',
            scoring_policy='all_positive_source_application_alpha_no_intersection_filter',scoring_pixels=int(scoring.sum()),
            measurement_native_pixels=int(np.count_nonzero(measurement)),provided_mst_label=None,
            input_measurement_statistics=report['measurement_statistics'],
            identity_reference_role=role=='target',native_adequacy_established=False,
            calibration_admitted=False,training_admitted=False,qualified_16features=False,
            target_control_fit=False,model_calls=0)
        if role=='target':assert np.array_equal(original,reference)
        write(dest/'record_PRIVATE.json',record);records.append(record)
    for p in [Path(__file__),ROOT/'docs/reviewed-photographic-pixel-preparation-protocol-2026-11-10.md',
              AUDIT/'audit_PRIVATE.json',ROOT/'src/model_training/aligned_correction_support.py',ROOT/'src/skin_masking/fixed_face_input_bridge.py']:
        bound[str(p)]=digest(p)
    assert all(digest(p)==h for p,h in bound.items())
    write(OUT/'records_PRIVATE.json',dict(records=records,blocked_roles=audit['summary']['blocked_roles']))
    write(OUT/'verification_PRIVATE.json',dict(passed=True,roles=14,pairs=7,exact_own_input_replays=14,
        target_identity_pixel_pairs=7,blocked_roles=2,qualified_16vectors=0,action_cost_evaluations=0,
        calibration_fits=0,target_fits=0,tree_fits=0,image_model_calls=0,original_TIFF_reads=0,holdout_bytes_read=0,input_sha256=bound))
    print('PASS: 14 own-input exact native slices, 7 source/reference pairs +7 target-identity pixel pairs; 2 blocked roles retained, zero fits.')


if __name__=='__main__':main()
