import numpy as np
import pytest
from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.lower_face_boundary_experiment import lower_face_boundary


def landmarks():
    points=np.full((478,2),50.)
    theta=np.linspace(0,2*np.pi,len(FACE_OVAL),endpoint=False)
    points[list(FACE_OVAL)]=np.column_stack([50+30*np.cos(theta),50+40*np.sin(theta)])
    points[168]=[50,30]
    return points


def test_forehead_unchanged_and_lower_outer_pixels_removed():
    original=np.ones((100,100),bool)
    candidate,metadata=lower_face_boundary(original,landmarks(),minimum_retained_fraction=.1)
    np.testing.assert_array_equal(candidate[:30],original[:30])
    assert not candidate[90,5]
    assert candidate[60,50]
    assert not np.any(candidate&~original)
    assert metadata['removed_pixels']>0
    assert original.all()


def test_does_not_fill_anatomical_holes():
    original=np.ones((100,100),bool);original[40:60,40:60]=False
    candidate,_=lower_face_boundary(original,landmarks(),minimum_retained_fraction=.1)
    assert not candidate[40:60,40:60].any()


def test_large_loss_rejected_instead_of_silent_fallback():
    support=np.zeros((100,100),bool);support[85:95,:10]=True
    with pytest.raises(ValueError,match='Unsafe boundary retention'):
        lower_face_boundary(support,landmarks())


@pytest.mark.parametrize('invalid_y',[-1,100,float('nan')])
def test_invalid_landmarks_fail(invalid_y):
    points=landmarks();points[168,1]=invalid_y
    with pytest.raises(ValueError):lower_face_boundary(np.ones((100,100),bool),points)
