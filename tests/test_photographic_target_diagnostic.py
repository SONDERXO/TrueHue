import numpy as np
import pytest
from src.model_training.photographic_target_diagnostic import case_matrix,distort,metrics


def test_matrix_complete_distinct_and_not_tone_assigned():
    cases=case_matrix()
    assert len(cases)==len({r['id'] for r in cases})==14
    assert [sum(r['layer']==k for r in cases) for k in ['clean','core','composite_stress_design']]==[1,8,5]
    assert all('MST' not in r for r in cases)


def test_all_cases_preserve_outside_and_clean_exact_identity():
    ref=np.random.default_rng(41).integers(30,230,(20,20,3),dtype=np.uint8)
    alpha=np.zeros((20,20),float);alpha[3:17,3:17]=1
    for case in case_matrix():
        image,recipe,role=distort(ref,alpha,case)
        assert np.array_equal(image[alpha==0],ref[alpha==0])
        assert not role['training_admitted']
        if case['layer']=='clean':assert np.array_equal(image,ref)
        if case['layer']=='core':assert recipe['clipped_channel_samples']==0


def test_metrics_score_only_declared_pixels_and_identity():
    ref=np.full((6,6,3),120,np.uint8);mask=np.zeros((6,6),bool);mask[2:4,2:4]=True
    image=ref.copy();image[~mask]=0
    assert metrics(image,ref,mask)['rgb8_mae_codes']==0
    assert metrics(image,ref,mask)['relative_deltaE00_mean']==0
    image[mask]=130
    assert metrics(image,ref,mask)['rgb8_mae_codes']==10
    assert metrics(image,ref,mask)['relative_deltaE00_mean']>0


def test_empty_scoring_is_unavailable_not_zero_error():
    ref=np.full((6,6,3),120,np.uint8)
    with pytest.raises(ValueError):metrics(ref,ref,np.zeros((6,6),bool))
