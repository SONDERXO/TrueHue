"""Generated API guarantees: no trained assets or photographic inference."""
from pathlib import Path
import sys
import math
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from wb314_headroom_advisory import WB314WithHeadroomAdvisory
from src.model_training.luminance_chroma_operator import render_rgb8


class GeneratedBase:
    def __init__(self):self.calls=0;self.controls=[1,math.sqrt(2),1,1,1]
    def correct(self,rgb,m,a,p):
        self.calls+=1
        return dict(output=render_rgb8(rgb,a,p,self.controls),controls=self.controls.copy(),
                    features=[0.]*314,leaf=7,qualification_complete=False)


def fixture():
    obj=WB314WithHeadroomAdvisory.__new__(WB314WithHeadroomAdvisory);obj.base=GeneratedBase()
    return obj,np.full((256,256,3),250,np.uint8),np.full((256,256),255,np.uint8),np.ones((256,256),float),np.zeros((256,256),bool)


def test_bright_primary_is_not_replaced_by_protected_candidate():
    obj,rgb,m,a,p=fixture()
    # Include midtones: uniform near-white RGB can quantize to255under both
    # controls, even though the computed exposure gains differ.
    rgb[128:]=128
    expected=render_rgb8(rgb,a,p,obj.base.controls)
    result=obj.correct(rgb,m,a,p)
    assert np.array_equal(result['output'],expected)
    assert result['controls']==obj.base.controls and result['features']==[0.]*314
    assert not np.array_equal(result['output'],result['headroom_candidate'])
    assert result['headroom_candidate_controls'][1]<result['controls'][1]
    assert result['headroom_advisory']['candidate_controls_changed']
    assert result['headroom_applied_to_primary'] is False and result['automatic_overcorrection_fix'] is False


def test_alternative_does_not_alias_or_mutate_primary_or_input():
    obj,rgb,m,a,p=fixture();rgb[:]=100;before=[v.tobytes() for v in [rgb,m,a,p]]
    result=obj.correct(rgb,m,a,p);primary=result['output'].copy()
    assert not np.shares_memory(result['output'],result['headroom_candidate'])
    result['headroom_candidate'][:]=0
    assert np.array_equal(result['output'],primary)
    assert [v.tobytes() for v in [rgb,m,a,p]]==before


def test_unavailable_advisory_is_explicit_not_a_safe_result():
    obj,rgb,m,a,p=fixture();m[:]=0;m[:,:20]=255;a[:]=0;a[:,200:]=1
    result=obj.correct(rgb,m,a,p)
    assert result['headroom_advisory']['available'] is False
    assert result['headroom_advisory']['not_a_safety_pass']
    assert result['headroom_candidate'] is None
    assert np.array_equal(result['output'],render_rgb8(rgb,a,p,obj.base.controls))


@pytest.mark.parametrize('kind',['rgb','measurement','alpha','protection'])
def test_invalid_inputs_fail_before_base_is_called(kind):
    obj,rgb,m,a,p=fixture()
    if kind=='rgb':rgb=rgb[:20]
    if kind=='measurement':m[0,0]=123
    if kind=='alpha':a[0,0]=np.nan
    if kind=='protection':p[0,0]=True
    with pytest.raises(ValueError):obj.correct(rgb,m,a,p)
    assert obj.base.calls==0
