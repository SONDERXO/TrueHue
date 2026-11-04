import numpy as np
import pytest
from src.skin_masking.faceocc_mediapipe_bridge import five_anchors,template_five,align_input


def test_fixed_anchor_order_and_template_reduction():
    points=np.zeros((478,2));points[33]=[20,30];points[133]=[30,30]
    points[362]=[60,30];points[263]=[70,30];points[1]=[45,45]
    points[61]=[30,65];points[291]=[60,65]
    assert np.array_equal(five_anchors(points),[[25,30],[65,30],[45,45],[30,65],[60,65]])
    template=np.arange(204).reshape(68,3)
    reduced=template_five(template)
    assert np.array_equal(reduced[0],template[[36,39]].mean(axis=0))
    assert np.array_equal(reduced[2],template[30])


def test_invalid_landmarks_fail_without_invented_correspondence():
    with pytest.raises(ValueError): five_anchors(np.zeros((478,2)))
    with pytest.raises(ValueError): template_five(np.zeros((5,3)))
