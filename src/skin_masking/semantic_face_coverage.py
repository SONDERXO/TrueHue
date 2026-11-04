"""User-authorized parser coverage with hard anatomical/non-skin exclusions.

The face outline associates parser components with the selected face; it does
not crop the forehead/chin to either the detector rectangle or landmark oval.
This changes the masking method and is not compatible with the old MST lookup.
"""
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import FaceCoverage,build_face_coverage
from src.skin_masking.face_parsing_experiment import facial_skin

VERSION='semantic_anatomical_face_coverage_v1'


def select_face_skin(categories,face_seed,exclusions):
    """Retain predicted skin/nose components associated with the selected face.

    Association is done before removing anatomical features, so glasses/feature
    exclusions cannot cause a largest-component filter to discard the chin or
    forehead. Separate forehead/nose components are retained if they intersect
    the selected face. Never fill holes across a predicted forbidden class.
    """
    allowed=facial_skin(categories)
    for mask in [face_seed,exclusions]:
        if not isinstance(mask,np.ndarray) or mask.dtype!=bool or mask.shape!=allowed.shape:
            raise ValueError('Matching boolean face seed and exclusions required')
    if not face_seed.any():raise ValueError('Nonempty selected face seed required')
    count,labels=cv2.connectedComponents(allowed.astype(np.uint8),connectivity=8)
    associated=set(np.unique(labels[face_seed&allowed]).tolist())-{0}
    if not associated:raise ValueError('No predicted facial skin overlaps the selected face')
    selected=np.isin(labels,sorted(associated)) & allowed & ~exclusions
    if not selected.any():raise ValueError('No skin remains after required exclusions')
    return selected.astype(np.uint8)*255,dict(associated_components=len(associated),
        rejected_unassociated_components=count-1-len(associated),
        selected_forbidden_class_pixels=int((selected&~allowed).sum()))


def build_semantic_face_coverage(image_bgr,landmarks,categories,*,non_skin_veto=None):
    geometry=build_face_coverage(image_bgr,landmarks,non_skin_veto=non_skin_veto)
    if np.asarray(categories).shape!=geometry.mask.shape:
        raise ValueError('Parser categories must share the full-image coordinate frame')
    mask,report=select_face_skin(categories,geometry.face_outline>0,geometry.exclusion_mask>0)
    # Feather inward only: no opacity can leak into hair, eyes, lips or other
    # excluded classes, and the binary measurement candidate remains explicit.
    alpha=cv2.GaussianBlur(mask,(3,3),0)
    alpha[mask==0]=0
    report.update(version=VERSION,selected_pixels=int((mask>0).sum()),
        selected_outside_geometric_outline=int(((mask>0)&(geometry.face_outline==0)).sum()),
        selected_in_anatomical_exclusions=int(((mask>0)&(geometry.exclusion_mask>0)).sum()),
        included_parser_classes=['skin','nose'],measurement_compatible_with_existing_lookup=False,
        mask_method='existing_local19class_parser_plus_landmark_exclusions',
        requires_occlusion_review=True,
        limitation='Predicted classes are imperfect; there is no separate beard/paint class and same-class touching occluders can remain. No final mask accuracy is claimed.')
    forbidden=(~facial_skin(categories))|(geometry.exclusion_mask>0)
    assert not mask[forbidden].any() and not alpha[forbidden].any()
    return FaceCoverage(mask=mask,alpha=alpha,face_outline=geometry.face_outline,
        exclusion_mask=(forbidden.astype(np.uint8)*255),report=report)
