"""Experimental additions-only boundary; existing support is never removed."""
import numpy as np
from src.skin_masking.lower_face_boundary_experiment import lower_face_boundary


def restrict_new_support(baseline, proposal, landmarks):
    """Apply the existing guarded lower boundary before union with baseline.

    Geometry is checked on the proposal first: baseline preservation must not
    hide a rejected boundary. Baseline errors remain; this is not a skin oracle.
    """
    base=np.asarray(baseline);candidate=np.asarray(proposal)
    if base.dtype!=bool or candidate.dtype!=bool or base.ndim!=2 or base.shape!=candidate.shape:
        raise ValueError('Expected matching2D boolean supports')
    bounded,metadata=lower_face_boundary(candidate,landmarks)
    result=base|bounded
    return result,dict(**metadata,baseline_pixels=int(base.sum()),
                       proposed_additions=int((candidate&~base).sum()),
                       retained_additions=int((result&~base).sum()),
                       rejected_additions=int((candidate&~base&~bounded).sum()),
                       baseline_only_pixels_preserved=int((base&~candidate).sum()))
