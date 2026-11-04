import pytest
from src.data_preparation.mst_training_contract import validate_mst_training_rows
from src.data_preparation.controlled_training_table import FEATURES,TARGETS
from src.distortion_generation.generate_distortions import inverse_parameters


def row():
    r=dict(pair_id='a',source_image_id='sourceA',duplicate_group_id='groupA',dataset_name='FairFace',partition='train',
        training_eligible=True,input_processing_status='success',clipped_pixel_count=0,measurement_shape=[256,256,3],
        mask_version='v2_complete_mouth_v1',measurement_contract_sha256='a'*64,lookup_sha256='b'*64,
        mst_feature_source='distorted_input_ita_lookup',input_mst_index=4,
        transform_version='encoded_rgb_gamma_then_gain_v1',target_method='exact_gamma_gain_inverse',
        distortion_gamma=.7,distortion_red_gain=.85,distortion_blue_gain=.95)
    r.update(zip(FEATURES,[50.,10.,20.,0.]));r.update(zip(TARGETS,inverse_parameters(.7,.85,.95).values()));return r


def validate(r):return validate_mst_training_rows([r],measurement_contract_sha256='a'*64,lookup_sha256='b'*64,eligible_pair_ids=['a'])


def test_valid_row_is_copied_not_promoted():
    r=row();out=validate(r);assert out[0]==r and out[0] is not r


def fitted_row():
    r=row();r.update(transform_version='table2_encoded_rgb_composite_v1',target_method='bounded_rgb_recovery_target_v1',target_fit_report_sha256='c'*64)
    r['target_fit']=dict(status='available_approximate_target',target_method=r['target_method'],jacobian_rank=3,converged=True,
        parameters=[r[k] for k in TARGETS],selected_pixels=100,float_rgb_rmse=.01,identity_float_rgb_rmse=.1,quantized_rgb_mae=.01)
    return r


def test_approximate_composite_targets_require_explicit_report():
    r=fitted_row();assert validate(r)[0]['target_method']=='bounded_rgb_recovery_target_v1'


@pytest.mark.parametrize('change',[
 lambda r:r.pop('target_fit'),lambda r:r.update(target_fit_report_sha256='missing'),
 lambda r:r['target_fit'].update(converged=False),lambda r:r['target_fit'].update(jacobian_rank=2),
 lambda r:r['target_fit'].update(float_rgb_rmse=float('nan')),
 lambda r:r['target_fit'].update(parameters=[1,1,1])])
def test_incomplete_composite_evidence_fails(change):
    r=fitted_row();change(r)
    with pytest.raises(ValueError):validate(r)


@pytest.mark.parametrize('key,value',[
 ('training_eligible',False),('dataset_name','MST-E'),('partition','reserved_test'),
 ('measurement_shape',[224,224,3]),('lookup_sha256','c'*64),
 ('measurement_contract_sha256','c'*64),('mst_feature_source','source_official_label'),
 ('input_mst_index',True),('input_mst_index',10),('clipped_pixel_count',1),
 ('input_processing_status','failed'),('brightness_offset',-20),('contrast_multiplier',1.05),
 ('transform_version','table2_composite'),('target_gamma',2.),('input_ita_degrees',float('nan'))])
def test_wrong_policy_labels_admission_and_inverse_targets_rejected(key,value):
    r=row();r[key]=value
    with pytest.raises(ValueError):validate(r)
