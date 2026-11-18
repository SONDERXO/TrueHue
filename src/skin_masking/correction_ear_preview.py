"""Isolated ear-only preview; no measurement, alpha or runtime policy change."""
import cv2
import numpy as np

def add_associated_ears(correction,measurement,protected,categories,*,manual_removed):
    shape=correction.shape
    for mask in [correction,measurement]:
        if mask.dtype!=np.uint8 or mask.shape!=shape or mask.ndim!=2 or not set(np.unique(mask))<={0,255}:
            raise ValueError('Matching binary masks required')
    for mask in [protected,manual_removed]:
        if mask.dtype!=bool or mask.shape!=shape:raise ValueError('Matching boolean veto required')
    if categories.dtype!=np.uint8 or categories.shape!=shape or (categories>18).any():raise ValueError('Matching parser classes required')
    if np.any((correction>0)&protected):raise ValueError('Existing correction overlaps protection')
    # Association follows eight-connected adjacency to the existing selected face.
    # Ear classes only: no skin/hair/background expansion or hole filling.
    possible=np.isin(categories,[7,8])&~protected&~manual_removed
    union=(correction>0)|possible
    _,labels=cv2.connectedComponents(union.astype(np.uint8),connectivity=8)
    attached=set(np.unique(labels[correction>0]))-{0}
    additions=possible&np.isin(labels,list(attached))&~(correction>0)
    result=correction.copy();result[additions]=255
    return result,measurement.copy(),dict(added_pixels=int(additions.sum()),
        rule='parser_ear_classes_7_8_eight_connected_to_current_support_after_veto',
        forehead_added_pixels=0,measurement_unchanged=True,protections_preserved=True,
        manual_removals_preserved=True,parser_accuracy_guaranteed=False,runtime_adopted=False)
