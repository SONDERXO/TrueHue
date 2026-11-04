import pytest
from src.data_preparation.table2_stress_contract import validate_stress_rows,POLICY
from src.data_preparation.mst_training_contract import validate_mst_training_rows
from src.data_preparation.controlled_training_table import FEATURES,TARGETS


def row():
    r=dict(pair_id='a',source_image_id='s',duplicate_group_id='g',dataset_name='FairFace',partition='train',
        training_eligible=True,input_processing_status='success',measurement_shape=[256,256,3],
        mask_version='v2_complete_mouth_v1',measurement_contract_sha256='a'*64,lookup_sha256='b'*64,
        mst_feature_source='distorted_input_ita_lookup',input_mst_index=5,admission_policy=POLICY,
        clipped_pixel_count=20,clipped_channel_samples=30,generation_skin_pixels=1000,clipped_pixel_fraction=.02,
        mask_review_status='approved',scene_review_status='approved',mask_review_report_sha256='c'*64,input_sha256='d'*64,
        input_mask_sha256='e'*64,reference_mask_sha256='f'*64,variant='table2',severity_probe='medium',
        reference_mst_estimate=4,group_assignment_source='experimental_reference_ita_lookup',reference_lookup_sha256='b'*64,
        transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',target_fit_report_sha256='c'*64)
    r.update(zip(FEATURES,[50.,10.,20.,0.]));r.update(zip(TARGETS,[1.2,1.1,.9]))
    r['target_fit']=dict(status='available_approximate_target',target_method=r['target_method'],jacobian_rank=3,
        converged=True,parameters=[1.2,1.1,.9],selected_pixels=200,float_rgb_rmse=.02,identity_float_rgb_rmse=.1,quantized_rgb_mae=.01)
    return r


def validate(r,validator=validate_stress_rows):
    return validator([r],measurement_contract_sha256='a'*64,lookup_sha256='b'*64,eligible_pair_ids=['a'])


def test_clipped_row_requires_separate_policy_preserves_actual_counts():
    r=row();assert validate(r)[0]['clipped_pixel_count']==20;assert r['clipped_pixel_count']==20
    with pytest.raises(ValueError):validate(r,validate_mst_training_rows)


@pytest.mark.parametrize('key,value',[
    ('admission_policy','ordinary'),('mask_review_status','pending'),('scene_review_status','pending'),('mask_review_report_sha256','missing'),
    ('clipped_pixel_count',-1),('clipped_pixel_count',True),('clipped_channel_samples',61),
    ('clipped_channel_samples',19),('clipped_pixel_fraction',float('nan')),('clipped_pixel_fraction',.1),
    ('severity_probe','dark'),('reference_mst_estimate',True),('group_assignment_source','official_fairface'),
    ('reference_lookup_sha256','a'*64),('input_mask_sha256',''),('dataset_name','MST-E'),('training_eligible',False),
    ('mst_feature_source','reference_ita_lookup'),('input_processing_status','failed')])
def test_stress_exception_never_overrides_other_requirements(key,value):
    r=row();r[key]=value
    with pytest.raises(ValueError):validate(r)


def test_identity_cannot_disguise_clipped_composite():
    r=row();r['variant']='identity'
    with pytest.raises(ValueError):validate(r)
