import cv2
import numpy as np
import pytest
from src.skin_masking.faceocc_coordinates import alignment_matrix, map_visible_mask


def test_source_pos_matrix_matches_known_camera_without_half_pixel_repair():
    template = np.array([[-1,1,0],[1,1,0],[0,0,1],[-.7,-1,0],[.7,-1,0]],float)
    # Known source POS projection: s=58, tx=120, ty=130, image height=256.
    points = np.column_stack((58*template[:,0]+120,255-(58*template[:,1]+130)))
    matrix=alignment_matrix(points,template,256)
    assert np.allclose(matrix,[[2,0,-112],[0,2,-124]],atol=1e-10)


def test_inverse_mapping_preserves_integer_translation_and_excludes_padding():
    source=np.zeros((80,90),np.uint8);source[20:40,30:50]=255
    matrix=np.array([[1,0,11],[0,1,19]],float)
    aligned=cv2.warpAffine(source,matrix,(256,256),flags=cv2.INTER_NEAREST)
    aligned[180:210,180:210]=255  # entirely outside original image validity
    restored=map_visible_mask(aligned,source.shape,matrix)
    assert np.array_equal(restored,source)


def test_degenerate_correspondence_and_mapping_fail_explicitly():
    with pytest.raises(ValueError): alignment_matrix(np.zeros((5,2)),np.zeros((5,3)),256)
    with pytest.raises(ValueError): map_visible_mask(np.zeros((256,256),np.uint8),(10,10),np.zeros((2,3)))
