import numpy as np
import pytest
from src.model_training.support_shift_diagnostic import compare_masks,fit_current_support,outside_changes
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics


def test_lost_and_added_support_are_not_called_accuracy():
    a=np.zeros((6,6),np.uint8);a[1:4,1:4]=255
    b=a.copy();b[1,1]=0;b[4,4]=255
    result=compare_masks(a,b)
    assert result['lost_pixels']==result['added_pixels']==1
    assert result['consistency_iou']==.8 and not result['ground_truth_accuracy']


def test_empty_intersection_is_unavailable_not_fabricated_neutral():
    image=np.full((8,8,3),90,np.uint8);a=np.zeros((8,8),float);a[:4]=1;b=1-a
    result=fit_current_support(image,image,a,b)
    assert result['parameters'] is None and result['missed_original_scoring_pixels']==32


def test_fixed_scoring_retains_error_in_lost_regions():
    ref=np.random.default_rng(4).integers(50,210,(12,12,3),dtype=np.uint8)
    source=np.ones((12,12),float);current=source.copy();current[:6]=0
    image=render_rgb8(ref,source,[1.4,.95,1.])
    fit=fit_current_support(image,ref,source,current)
    output=render_rgb8(image,current,fit['parameters'])
    assert fit['missed_original_scoring_pixels']==72
    assert metrics(output,ref,source>0)['rgb8_mae_codes']>metrics(output,ref,current>0)['rgb8_mae_codes']
    assert np.array_equal(output[:6],image[:6])


def test_new_support_spill_is_counted_instead_of_clamped():
    image=np.full((6,6,3),90,np.uint8);output=image.copy();output[0,0]=100
    alpha=np.zeros((6,6),float);alpha[1:5,1:5]=1
    protected=np.zeros((6,6),bool);protected[0,0]=True
    report=outside_changes(output,image,alpha,protected)
    assert report['changed_pixels_outside_source']==1 and report['changed_source_protected_pixels']==1


def test_invalid_alpha_cannot_be_treated_as_missing_support():
    image=np.zeros((5,5,3),np.uint8);a=np.ones((5,5),float);b=a.copy();b[0,0]=np.nan
    with pytest.raises(ValueError):fit_current_support(image,image,a,b)
