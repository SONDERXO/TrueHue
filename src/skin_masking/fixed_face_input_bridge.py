"""One declared face ROI with native-resolution accounting; not added detail."""
import math
import cv2
import numpy as np

VERSION='fixed_native_face_square_1p5_from_saved256_box_v1'


def crop_face(image,box):
    if not isinstance(image,np.ndarray) or image.dtype!=np.uint8 or image.ndim!=3 or image.shape[2]!=3 or not image.size:
        raise ValueError('Nonempty native uint8 BGR image required')
    if len(box)!=4 or any(isinstance(v,bool) or not isinstance(v,(int,np.integer)) for v in box):
        raise ValueError('Integer source-box coordinates on the saved256 frame required')
    x,y,w,h=map(int,box)
    if min(x,y)<0 or min(w,h)<1 or x+w>256 or y+h>256:
        raise ValueError('Saved box must be inside source256 frame')
    height,width=image.shape[:2];sx=width/256;sy=height/256
    side=int(math.ceil(1.5*max(w*sx,h*sy)))
    if side<1 or side>min(height,width):raise ValueError('Fixed square context cannot fit native image')
    left=int(math.floor((x+w/2)*sx-side/2));top=int(math.floor((y+h/2)*sy-side/2))
    original=[left,top];left=max(0,min(width-side,left));top=max(0,min(height-side,top))
    crop=image[top:top+side,left:left+side].copy()
    report=dict(version=VERSION,source_shape=list(image.shape),source256_face_box=[x,y,w,h],
        native_face_box_float=[x*sx,y*sy,w*sx,h*sy],native_bounds=[left,top,left+side,top+side],
        native_side=side,context_scale=1.5,edge_shift=[left-original[0],top-original[1]],
        source_to_normalized_linear_scale=256/side,exact_native_slice=True,padding_added=False,
        new_detail_created=False,old_wholeframe_lookup_compatible=False)
    return crop,report


def native_projection(mask,report):
    if not isinstance(mask,np.ndarray) or mask.dtype!=np.uint8 or mask.shape!=(256,256) or not set(np.unique(mask))<={0,255}:
        raise ValueError('Binary256 normalized mask required')
    side=report['native_side'];left,top,right,bottom=report['native_bounds']
    native=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
    result=np.zeros(tuple(report['source_shape'][:2]),np.uint8);result[top:bottom,left:right]=native
    return result,dict(normalized_selected_pixels=int(np.count_nonzero(mask)),
        selected_native_grid_locations=int(np.count_nonzero(native)),
        source_area_equivalent_pixels=float(np.count_nonzero(mask)*(side/256)**2),
        effective_independent_sample_size=None,native_adequacy_established=False,
        calibration_admitted=False,training_admitted=False)
