"""Fixed segmentation-only appearance probe; never a colour-measurement input."""
import cv2
import numpy as np

VERSION='parser_only_lab_L_CLAHE_clip2_grid8_v1'

def parser_input(image):
    """Return a separate CLAHE-L copy with fixed settings, preserving original BGR."""
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.shape!=(256,256,3):
        raise ValueError('Original square256 uint8 BGR image required')
    lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
    lab[:,:,0]=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8)).apply(lab[:,:,0])
    return cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
