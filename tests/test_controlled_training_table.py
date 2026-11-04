import pytest
from src.data_preparation.controlled_training_table import FEATURES,pair_table_row


def row(status='success',clip=0,**overrides):
    return pair_table_row(dict(partition='train',clipped_pixel_count=clip,source_mean_l_star=99),
        dict(processing_status=status,mean_l_star=20,mean_a_star=10,mean_b_star=5,ita_degrees=-40,**overrides),
        dict(gamma=1,red_gain=1,blue_gain=1))


def test_model_features_come_only_from_input_statistics():
    result=row()
    assert result['input_mean_l_star']==20 and result['table_use']=='train'
    assert result['source_mean_l_star']==99 and 'source_mean_l_star' not in FEATURES


def test_failed_input_cannot_reuse_reference_features_or_enter_stress_set():
    result=row('excluded',clip=3,exclusion_reason='insufficient_skin_pixels')
    assert result['table_use']=='excluded'
    assert all(result[k]=='' for k in FEATURES)


def test_clipped_valid_input_routes_to_stress():
    assert row(clip=1)['table_use']=='stress_only'


def test_nonfinite_input_is_excluded_and_no_feature_vector_is_imputed():
    bad=dict(processing_status='success',mean_l_star=float('nan'),mean_a_star=0,mean_b_star=1,ita_degrees=0)
    result=pair_table_row(dict(partition='development_validation',clipped_pixel_count=0),bad,
                          dict(gamma=1,red_gain=1,blue_gain=1))
    assert result['table_use']=='excluded' and all(result[k]=='' for k in FEATURES)


def test_metadata_cannot_inject_features():
    with pytest.raises(ValueError,match='Metadata'):
        pair_table_row(dict(partition='train',clipped_pixel_count=0,input_mean_l_star=99),
                       dict(processing_status='excluded'),dict(gamma=1,red_gain=1,blue_gain=1))
