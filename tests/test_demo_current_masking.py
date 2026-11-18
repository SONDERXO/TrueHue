"""Verify mask integration boundaries and legacy measurement provenance."""
from types import SimpleNamespace
import cv2
import numpy as np
import pytest

from src.demo import current_masking as module


def fixture_result(monkeypatch):
    image=np.full((8,8,3),100,np.uint8)
    mask=np.zeros((8,8),np.uint8);mask[2:6,2:6]=255
    protected=np.zeros((8,8),bool);protected[0]=True
    legacy=SimpleNamespace(image=image,corrected=image.copy(),report=dict(
        status='development_experimental_mst',measurement=dict(status='success',version='old'),
        features=dict(input_ita_degrees=12),mst=dict(label=4),parameters=[2.,1.1,.9]))
    seen={}
    def render(image,facial,categories,points,visible,**kwargs):
        seen.update(kwargs)
        alpha=(mask>0).astype(float)
        output=image.copy();output[mask>0]=120
        return SimpleNamespace(output=output,alpha=alpha,protected=protected,
            support=SimpleNamespace(correction_mask=mask),report={})
    monkeypatch.setattr(module,'render_preview',render)
    metadata=dict(measurement_report=dict(status='success',features=dict(input_ita_degrees=35)),measurement_mask=mask.copy())
    return image,mask,legacy,metadata,seen


def test_new_masks_preserve_separate_legacy_features_and_convert_gamma(monkeypatch):
    image,mask,legacy,metadata,seen=fixture_result(monkeypatch)
    result=module.compose_result(legacy,image,mask,mask,None,mask,metadata,glasses='clear')
    assert seen['parameters']==(.5,1.1,.9)
    assert seen['glasses']=='clear'
    assert result.report['features']['input_ita_degrees']==12
    assert result.report['display_features']['input_ita_degrees']==35
    assert result.report['mst']['measurement_source']=='historical_mask'
    assert legacy.report['mst']==dict(label=4)
    assert result.report['quality_gate_passed'] is False
    np.testing.assert_array_equal(result.corrected[result.alpha==0],image[result.alpha==0])


def test_current_masks_cannot_use_mismatched_image_or_missing_controls(monkeypatch):
    image,mask,legacy,metadata,_=fixture_result(monkeypatch)
    with pytest.raises(ValueError,match='match exactly'):
        module.compose_result(legacy,image+1,mask,mask,None,mask,metadata,glasses='uncertain')
    legacy.corrected=None
    with pytest.raises(ValueError,match='controls unavailable'):
        module.compose_result(legacy,image,mask,mask,None,mask,metadata,glasses='opaque')


def test_failed_current_masks_do_not_fall_back_to_legacy(tmp_path,monkeypatch):
    monkeypatch.setattr(module,'ROOT',tmp_path)
    helper=SimpleNamespace(dependencies=lambda:({},'test'),sha=lambda p:'hash')
    def failed(*args):raise ValueError('Mask unavailable')
    helper.prepare_photo=failed
    monkeypatch.setattr(module,'import_module',lambda name:helper)
    legacy=SimpleNamespace(run=lambda image:pytest.fail('No fallback allowed'))
    result=module.CurrentMaskDemoPipeline(legacy).run(np.full((8,8,3),100,np.uint8))
    assert result.corrected is None and result.mask is None
    assert result.report['status']=='failed'
    assert result.report['reason']=='Mask unavailable'


def test_gamma_conversion_preserves_old_curve_inside_blended_support():
    from src.correction.seamless_blend import apply_blended
    from src.evaluation.correction_prototype import apply_correction
    image=np.arange(32*32*3,dtype=np.uint16).reshape(32,32,3).astype(np.uint8)
    mask=np.zeros((32,32),np.uint8);mask[3:29,3:29]=255
    parameters=(1.7,1.12,.89)
    mapped=module.legacy_to_paper_parameters(*parameters)
    output,alpha,_=apply_blended(image,mask,tuple(mapped.values()),face_width=26)
    old=cv2.cvtColor(apply_correction(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),mask>0,parameters),cv2.COLOR_RGB2BGR)
    np.testing.assert_array_equal(output[alpha==1],old[alpha==1])
    np.testing.assert_array_equal(output[alpha==0],image[alpha==0])
