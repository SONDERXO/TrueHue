import cv2
import numpy as np
import pytest

from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.face_outline_experiment import FACE_OVAL
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
from src.skin_masking.mouth_exclusion import OUTER_LIPS


def points():
    p = np.full((478, 2), 50., dtype=float)
    t = np.linspace(-np.pi/2, 3*np.pi/2, len(FACE_OVAL), endpoint=False)
    p[list(FACE_OVAL)] = np.column_stack([50+35*np.cos(t), 50+44*np.sin(t)])
    for name, center, radius in [('left_eye', (65,40), (8,3)), ('right_eye',(35,40),(8,3)),
            ('left_eyebrow',(35,30),(9,2)), ('right_eyebrow',(65,30),(9,2))]:
        indices = FEATURE_INDICES[name]
        a = np.linspace(0, 2*np.pi, len(indices), endpoint=False)
        p[indices] = np.column_stack([center[0]+radius[0]*np.cos(a),center[1]+radius[1]*np.sin(a)])
    a = np.linspace(0, 2*np.pi, len(OUTER_LIPS), endpoint=False)
    p[list(OUTER_LIPS)] = np.column_stack([50+12*np.cos(a),68+5*np.sin(a)])
    return p


def test_covers_entire_geometric_surface_except_explicit_features():
    image = np.zeros((100,100,3),np.uint8)
    result = build_face_coverage(image,points())
    assert np.array_equal(result.mask>0,(result.face_outline>0)&~(result.exclusion_mask>0))
    assert result.mask[55,35] == result.mask[82,50] == result.mask[17,50] == 255
    assert result.mask[40,35] == result.mask[30,35] == result.mask[68,50] == result.mask[0,0] == 0
    assert not (result.alpha[result.exclusion_mask>0]).any()
    assert set(np.unique(result.mask)) == {0,255}
    assert not result.report['measurement_compatible_with_existing_lookup']


def test_geometry_is_independent_of_skin_hue_shadow_and_fragmented_old_masks():
    a = np.zeros((100,100,3),np.uint8);b = np.full_like(a,255)
    b[20:60,20:60] = [255,0,0]
    assert np.array_equal(build_face_coverage(a,points()).mask,build_face_coverage(b,points()).mask)


def test_explicit_occlusion_veto_cannot_be_filled_back_in():
    veto = np.zeros((100,100),bool);veto[45:65,30:40] = True
    result=build_face_coverage(np.zeros((100,100,3),np.uint8),points(),non_skin_veto=veto)
    assert not result.mask[veto].any() and not result.alpha[veto].any()
    assert result.report['non_skin_veto_supplied']


def test_supersampled_edges_have_alpha_without_modifying_images_or_landmarks():
    image=np.full((100,100,3),100,np.uint8);p=points()+.3
    before_image=image.copy();before_points=p.copy()
    result=build_face_coverage(image,p)
    assert ((result.alpha>0)&(result.alpha<255)).any()
    assert np.array_equal(image,before_image) and np.array_equal(p,before_points)
    assert not result.alpha[result.mask==0].any()


@pytest.mark.parametrize('bad',[np.zeros((10,2)),np.zeros((478,2)),np.full((478,2),np.nan)])
def test_invalid_geometry_has_no_silent_color_mask_fallback(bad):
    with pytest.raises(ValueError):build_face_coverage(np.zeros((100,100,3),np.uint8),bad)


def test_veto_type_and_shape_are_checked():
    for veto in [np.zeros((100,100),np.uint8),np.zeros((10,10),bool)]:
        with pytest.raises(ValueError):build_face_coverage(np.zeros((100,100,3),np.uint8),points(),non_skin_veto=veto)


def test_visible_face_is_raster_clipped_without_moving_vertices():
    p=points();p[:,0]-=20
    result=build_face_coverage(np.zeros((100,100,3),np.uint8),p)
    assert result.mask[:,0].any()
    p[:,0]-=200
    with pytest.raises(ValueError):build_face_coverage(np.zeros((100,100,3),np.uint8),p)
