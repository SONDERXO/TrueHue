from types import SimpleNamespace
import numpy as np
import pytest
from src.ita_estimation.square_measurement import measure


def estimator(image,box):
    x,y,w,h=box
    return SimpleNamespace(mask=np.full((h,w),255,np.uint8),exclusion_mask=np.zeros((h,w),np.uint8),landmarks_available=True)


def test_detection_and_measurement_share_square_frame_and_source_is_unchanged():
    image=np.full((120,300,3),(90,130,180),np.uint8);before=image.copy()
    def detect(square):
        assert square.shape==(256,256,3)
        return [(40,40,100,100)]
    result=measure(image,detect,estimator)
    assert result.report['status']=='success'
    assert result.mask.shape==(256,256) and np.count_nonzero(result.mask)==10000
    assert result.report['skin_pixels']==10000
    np.testing.assert_array_equal(image,before)


@pytest.mark.parametrize('boxes',[[],[(0,0,100,100),(100,100,100,100)],[(250,0,100,100)],[(0.,0,100,100)]])
def test_bad_detection_never_supplies_features(boxes):
    result=measure(np.zeros((100,100,3),np.uint8),lambda _:boxes,estimator)
    assert result.report['status']=='failed' and result.report['features'] is None


def test_insufficient_pixels_and_missing_landmarks_fail_without_fallback():
    image=np.full((100,100,3),120,np.uint8)
    result=measure(image,lambda _:[(0,0,20,20)],estimator)
    assert result.report['status']=='failed' and result.report['features'] is None
    def missing(image,box):
        result=estimator(image,box);result.landmarks_available=False;return result
    result=measure(image,lambda _:[(0,0,100,100)],missing)
    assert result.report['status']=='failed' and result.report['features'] is None


def test_exclusion_overlap_fails():
    def overlap(image,box):
        result=estimator(image,box);result.exclusion_mask[0,0]=255;return result
    result=measure(np.zeros((100,100,3),np.uint8),lambda _:[(0,0,100,100)],overlap)
    assert result.report['status']=='failed' and 'overlap' in result.report['reason']
