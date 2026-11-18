import numpy as np
from src.skin_masking.detector_appearance_fallback import detect_with_appearance_fallback

def test_existing_detections_are_not_retried():
    image=np.zeros((256,256,3),np.uint8)
    for boxes in [[[1,2,30,40]],[[1,2,30,40],[4,5,10,20]]]:
        calls=[]
        def detect(a):calls.append(a);return boxes
        result,trace=detect_with_appearance_fallback(image,detect)
        assert result==boxes and len(calls)==1 and not trace['fallback_attempted']

def test_zero_face_retry_preserves_input_and_requires_one_box():
    image=np.random.default_rng(42).integers(0,256,(256,256,3),dtype=np.uint8);before=image.copy()
    for retry in [[],[[1,2,30,40]],[[1,2,30,40],[4,5,10,20]]]:
        calls=[]
        def detect(a):calls.append(a.copy());return [] if len(calls)==1 else retry
        result,trace=detect_with_appearance_fallback(image,detect)
        assert np.array_equal(image,before) and len(calls)==2 and not np.array_equal(calls[0],calls[1])
        assert result==(retry if len(retry)==1 else []) and trace['accepted']==(len(retry)==1)
