import numpy as np
import pytest
from tests.test_complete_brow_area import example
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import build_full_face_support,nostril_guard


def setup():
    image,base,cats,points=example()
    for index,value in {98:(39,57),97:(43,59),2:(50,61),94:(50,56),19:(50,54),64:(39,54),
                       327:(61,57),326:(57,59),294:(61,54)}.items():points[index]=value
    return image,base,cats,points


def test_whole_outline_is_corrected_including_eye_hair_and_mouth():
    image,base,cats,points=setup();cats[20:24,30:50]=17
    r=build_full_face_support(image,base.measurement_mask,cats,points,face_count=1)
    outline=build_face_coverage(image,points).face_outline>0
    assert r.correction_mask[outline].all()
    assert r.correction_mask[45,35] and r.correction_mask[70,50]
    assert not r.measurement_mask[45,35] and not r.measurement_mask[70,50]
    assert not r.measurement_mask[20:24,30:50].any()
    assert not r.measurement_mask[nostril_guard(cats.shape,points)].any()


def test_protected_pixels_override_whole_face_without_changing_input():
    image,base,cats,points=setup();before=base.measurement_mask.copy()
    veto=np.zeros(cats.shape,bool);veto[45,35]=True
    r=build_full_face_support(image,base.measurement_mask,cats,points,face_count=1,protected=veto)
    assert not r.correction_mask[veto].any() and np.array_equal(before,base.measurement_mask)


def test_invalid_nasal_geometry_fails_explicitly():
    with pytest.raises(ValueError):nostril_guard((100,100),np.zeros((468,2)))
