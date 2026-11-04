import numpy as np
import pytest
from src.correction.correct_image import correct_from_estimate,LEGACY_POLICY,MATERIAL_HAIR_POLICY


class FixedModel:
    n_features_in_=4
    def predict(self,x):
        self.last=x.copy()
        return np.tile([1.4,1.,1.],(len(x),1))


class FakeSegmenter:
    def categories_bgr(self,image):
        out=np.full(image.shape[:2],3,np.uint8);out[10:20,10:20]=1
        return out


def example():
    image=np.full((80,80,3),[70,100,140],np.uint8)
    mask=np.zeros((80,80),bool);mask[5:75,5:75]=True
    exclude=np.zeros_like(mask);exclude[35:45,35:45]=True;mask[exclude]=False
    return image,mask,exclude


def test_policy_changes_application_without_changing_features_or_parameters():
    image,mask,excluded=example();old=image.copy();model=FixedModel()
    legacy=correct_from_estimate(image,(0,0,80,80),mask,excluded,model)
    selected=correct_from_estimate(image,(0,0,80,80),mask,excluded,model,MATERIAL_HAIR_POLICY,FakeSegmenter())
    assert legacy.features==selected.features and legacy.parameters==selected.parameters
    assert not selected.correction_mask[10:20,10:20].any()
    assert legacy.correction_mask[10:20,10:20].all()
    assert not selected.correction_mask[excluded].any()
    np.testing.assert_array_equal(selected.corrected_bgr[~selected.correction_mask],image[~selected.correction_mask])
    np.testing.assert_array_equal(image,old)


@pytest.mark.parametrize('policy',[LEGACY_POLICY,MATERIAL_HAIR_POLICY])
def test_explicit_paint_protection_preserves_even_baseline_selected_pixels(policy):
    image,mask,excluded=example();protected=np.zeros_like(mask);protected[20:30,20:30]=True
    image[protected]=[130,30,160]  # Existing mask includes this colored material.
    result=correct_from_estimate(image,(0,0,80,80),mask,excluded,FixedModel(),policy,FakeSegmenter(),protected)
    assert not result.correction_mask[protected].any()
    np.testing.assert_array_equal(result.corrected_bgr[protected],image[protected])
    assert result.metadata['protected_pixels_removed']==100


def test_missing_semantic_dependency_fails_without_legacy_fallback():
    image,mask,excluded=example()
    with pytest.raises(ValueError,match='no fallback'):
        correct_from_estimate(image,(0,0,80,80),mask,excluded,FixedModel(),MATERIAL_HAIR_POLICY)


def test_insufficient_estimation_and_unknown_versions_are_not_silently_accepted():
    image,mask,excluded=example()
    with pytest.raises(ValueError):correct_from_estimate(image,(0,0,80,80),mask,excluded,FixedModel(),'unknown')
    mask[:]=False
    with pytest.raises(ValueError,match='statistics'):correct_from_estimate(image,(0,0,80,80),mask,excluded,FixedModel())
