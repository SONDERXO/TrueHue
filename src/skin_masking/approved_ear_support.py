"""User-approved correction-only ear extension, separate from measurement."""
import numpy as np
from src.skin_masking.correction_ear_preview import add_associated_ears
from src.skin_masking.face_neck_support import FaceNeckSupport

VERSION='associated_ear_correction_support_v1'

def extend_support(support,categories,*,protected,manual_removed=None):
    if manual_removed is None:manual_removed=np.zeros(support.correction_mask.shape,bool)
    correction,measurement,details=add_associated_ears(support.correction_mask,
        support.measurement_mask,protected,categories,manual_removed=manual_removed)
    return FaceNeckSupport(measurement,support.neck_mask.copy(),correction,
        dict(support.report,ear_coverage=dict(details,version=VERSION,
            user_approved=True,pipeline_integrated=True,scientifically_validated=False,
            runtime_adopted=True,approval_scope='ear coverage only; not correction-control model')))
