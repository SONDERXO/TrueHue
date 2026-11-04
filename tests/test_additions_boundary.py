import numpy as np
import pytest
from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.additions_boundary_experiment import restrict_new_support


def points():
    result=np.full((478,2),50.)
    theta=np.linspace(0,2*np.pi,len(FACE_OVAL),endpoint=False)
    result[list(FACE_OVAL)]=np.column_stack([50+40*np.cos(theta),50+45*np.sin(theta)])
    result[168]=[50,30]
    return result


def test_preserves_baseline_outside_oval_and_excludes_new_spill():
    base=np.zeros((100,100),bool);base[40:70,35:65]=True;base[90,1]=True
    proposal=base.copy();proposal[45,65:70]=True;proposal[90,2:5]=True
    original=base.copy();result,metadata=restrict_new_support(base,proposal,points())
    assert np.all(result[base])
    assert result[45,68]
    assert not result[90,3]
    assert metadata['retained_additions']==5 and metadata['rejected_additions']==3
    np.testing.assert_array_equal(base,original)


def test_union_does_not_hide_invalid_proposal_geometry():
    baseline=np.ones((100,100),bool)
    proposal=np.zeros_like(baseline);proposal[90:95,:5]=True
    with pytest.raises(ValueError,match='Unsafe boundary retention'):
        restrict_new_support(baseline,proposal,points())


def test_preserves_old_support_missing_from_proposal():
    baseline=np.zeros((100,100),bool);baseline[20,30]=True
    proposal=np.zeros_like(baseline);proposal[45:65,40:60]=True
    result,metadata=restrict_new_support(baseline,proposal,points())
    assert result[20,30] and result[50,50]
    assert metadata['baseline_only_pixels_preserved']==1


def test_cannot_fill_holes_absent_from_both_masks():
    base=np.zeros((100,100),bool);base[40:60,40:60]=True;base[50,50]=False
    result,_=restrict_new_support(base,base,points())
    assert not result[50,50]
