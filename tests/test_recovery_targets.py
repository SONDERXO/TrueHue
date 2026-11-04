import numpy as np
import pytest
from src.model_training.recovery_targets import fit_recovery_target
from src.distortion_generation.table2_composite import composite_rgb
from src.evaluation.correction_prototype import apply_correction


def image():return np.random.default_rng(42).integers(40,210,(20,20,3),dtype=np.uint8)
def mask():return np.ones((20,20),bool)


def test_identity_recovery_and_no_input_mutation():
    x=image();old=x.copy();r=fit_recovery_target(x,x,mask(),mask())
    assert r['status']=='available_approximate_target' and r['parameters']==[1.,1.,1.]
    assert r['float_rgb_rmse']==0;np.testing.assert_array_equal(x,old)


def test_known_in_family_recovery_with_quantization_residual():
    x=image();reference=apply_correction(x,mask(),[1.3,1.1,.9])
    r=fit_recovery_target(x,reference,mask(),mask())
    np.testing.assert_allclose(r['parameters'],[1.3,1.1,.9],atol=.004,rtol=0)
    assert r['float_rgb_rmse']<.002 and r['float_rgb_rmse']<r['identity_float_rgb_rmse']


@pytest.mark.parametrize('group',['light','medium','dark'])
def test_composite_fit_reports_residual_instead_of_exact_inverse(group):
    reference=image();distorted,info=composite_rgb(reference,group)
    r=fit_recovery_target(distorted,reference,mask(),mask())
    assert info['transform_version']=='table2_encoded_rgb_composite_v1'
    assert r['status']=='available_approximate_target'
    assert 0<r['float_rgb_rmse']<r['identity_float_rgb_rmse']


def test_clipping_accounting_on_black_pixels():
    x=np.zeros((20,20,3),np.uint8);out,info=composite_rgb(x,'dark')
    assert info['clipped_pixels']==400 and not out.any()
    r=fit_recovery_target(out,image(),mask(),mask());assert r['parameters'] is None


def test_reference_outside_intersection_has_no_effect():
    x=image();support=mask();support[:10]=False
    reference=x.copy();reference[:10]=255
    r=fit_recovery_target(x,reference,support,mask())
    assert r['selected_pixels']==200 and r['float_rgb_rmse']==0


def test_small_and_flat_inputs_are_unavailable():
    m=mask();m[1:]=False
    assert fit_recovery_target(image(),image(),m,mask())['status']=='unavailable_insufficient_pixels'
    flat=np.full((20,20,3),100,np.uint8)
    assert fit_recovery_target(flat,flat,mask(),mask())['status']=='unavailable_degenerate_input'


@pytest.mark.parametrize('change',[
 lambda x,r,a,b:(x.astype(float),r,a,b),lambda x,r,a,b:(x,r[:10],a,b),
 lambda x,r,a,b:(x,r,a.astype(np.uint8),b),lambda x,r,a,b:(x,r,a,b[:10])])
def test_invalid_data_rejected(change):
    with pytest.raises(ValueError):fit_recovery_target(*change(image(),image(),mask(),mask()))
