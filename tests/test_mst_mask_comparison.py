"""Detector-scale geometry for the explicitly separate MST comparison run."""
import importlib
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
comparison=importlib.import_module('27_compare_mst_mapping_mask_versions')


def test_detector_resize_maps_boxes_to_original_measurement_pixels():
    image=np.zeros((200,100,3),np.uint8)
    original=image.copy()
    def detector(probe,model,threshold):
        assert probe.shape==(100,50,3) and threshold==.85
        return [(5,10,20,30)]
    boxes,size=comparison.detect_comparison_boxes(image,detector,None,100)
    assert boxes==[(10,20,40,60)] and size==(50,100)
    assert np.array_equal(image,original)


def test_native_images_are_not_upsampled():
    image=np.zeros((20,10,3),np.uint8)
    def detector(probe,model,threshold):
        assert probe is image
        return [(1,2,3,4)]
    for maximum in (0,1024):
        assert comparison.detect_comparison_boxes(image,detector,None,maximum)==([(1,2,3,4)],(10,20))


def test_scaled_coordinates_clamp_right_and_bottom_bounds():
    image=np.zeros((201,101,3),np.uint8)
    boxes,_=comparison.detect_comparison_boxes(image,lambda *args:[(49,99,10,10)],None,100)
    assert boxes==[(98,198,3,3)]
