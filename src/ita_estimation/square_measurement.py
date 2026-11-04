"""One fixed input frame for measurement and future MST/correction features."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.controlled_training_table import FEATURES,FEATURE_KEYS

MASK_VERSION='v2_complete_mouth_v1'
MIN_SKIN_PIXELS=1000


def contract(root):
    root=Path(root);config=get_config()
    if config.IMAGE_SIZE!=256:raise ValueError('The declared proposal contract requires configured256')
    files=[Path(__file__),root/'src/ita_estimation/compute_ita.py',root/'src/face_detection/detect_faces.py',
           root/'scripts/11_prepare_training_manifests.py',root/'src/skin_masking/skin_mask.py',
           root/'src/skin_masking/landmark_exclusion.py',root/'src/skin_masking/mouth_exclusion.py',
           root/config.FACE_MODEL_PATH,root/config.FACE_LANDMARKER_MODEL_PATH]
    payload=dict(version='truehue_square256_measurement_v1',size=config.IMAGE_SIZE,
        decode='opencv_IMREAD_COLOR_default_orientation',resize='whole_frame_INTER_LINEAR_square_stretch_before_detection',
        detector_input='same256measurementframe',detector_confidence=.85,required_faces=1,
        mask_version=MASK_VERSION,landmarks_required=True,min_skin_pixels=MIN_SKIN_PIXELS,
        pixel_count_units='selected_pixels_in256_frame_native_face_crop',
        ita='atan((mean_L-50)/mean_b)_degrees_existing_four_decimal_statistics',
        opencv_version=cv2.__version__,numpy_version=np.__version__,
        color='OpenCV8bitLab_conversion; assumed_sRGB_no_ICC_or_camera_calibration',
        dependency_sha256={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    identity=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return payload,identity


@dataclass
class SquareMeasurement:
    report:dict
    image:object=None
    mask:object=None


def measure(image,detector,mask_estimator):
    """Injected stages operate only on square pixels; failures never reuse ITA."""
    report=dict(status='failed',stage='input',features=None,mask_version=MASK_VERSION)
    square=None;full_mask=None
    try:
        if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
            raise ValueError('Nonempty uint8 BGR image required')
        size=get_config().IMAGE_SIZE
        if size!=256:raise ValueError('Configured256required')
        report['source_decoded_shape']=list(image.shape)
        square=cv2.resize(image,(size,size),interpolation=cv2.INTER_LINEAR)
        report.update(stage='face_detection',measurement_shape=list(square.shape))
        boxes=detector(square);report['face_count']=len(boxes)
        if len(boxes)!=1:raise ValueError('Exactly one square-frame face required')
        box=boxes[0]
        if len(box)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,np.integer)) for v in box):
            raise ValueError('Integer square-frame face box required')
        x,y,w,h=map(int,box)
        if min(x,y)<0 or min(w,h)<=0 or x+w>size or y+h>size:raise ValueError('Face box outside measurement frame')
        report.update(stage='skin_mask',face_box=[x,y,w,h])
        result=mask_estimator(square,(x,y,w,h))
        mask=np.asarray(result.mask);exclusions=np.asarray(result.exclusion_mask)
        if mask.shape!=(h,w) or mask.dtype!=np.uint8 or not set(np.unique(mask))<={0,255}:raise ValueError('Native crop binary mask required')
        if exclusions.shape!=mask.shape or exclusions.dtype!=np.uint8 or not set(np.unique(exclusions))<={0,255}:raise ValueError('Native anatomical exclusions required')
        if np.any((mask>0)&(exclusions>0)):raise ValueError('Mask overlaps excluded anatomy')
        full_mask=np.zeros((size,size),np.uint8);full_mask[y:y+h,x:x+w]=mask
        report['skin_pixels']=int(np.count_nonzero(mask))
        if not result.landmarks_available:raise ValueError('Required landmarks unavailable')
        report['stage']='measurement'
        stats=compute_masked_lab_statistics(square[y:y+h,x:x+w],mask,MIN_SKIN_PIXELS)
        report['statistics']=stats
        if not stats['valid']:raise ValueError(stats['reason'])
        report.update(status='success',features={name:float(stats[key]) for name,key in zip(FEATURES,FEATURE_KEYS)})
    except (ValueError,TypeError,RuntimeError,cv2.error) as error:
        report['reason']=str(error)
    return SquareMeasurement(report,square,full_mask)
