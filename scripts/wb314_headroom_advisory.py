"""Frozen WB314 primary correction with a separately labelled headroom candidate.

The primary image/controls are never replaced by the cap. This is a research API,
not an automatic highlight repair, new-photo qualification or Android adoption.
"""
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from wb314_research_predictor import FrozenWB314, validate_inputs
from src.model_training.facial_exposure_headroom import cap_facial_exposure_headroom
from src.model_training.luminance_chroma_operator import render_rgb8


class WB314WithHeadroomAdvisory:
    """Return the unchanged primary result and an explicit research alternative."""

    def __init__(self):
        self.base=FrozenWB314()

    def correct(self,rgb,measurement,alpha,protected):
        validate_inputs(rgb,measurement,alpha,protected)
        raw=self.base.correct(rgb,measurement,alpha,protected)
        result=dict(raw)
        result['output']=raw['output'].copy()
        result['controls']=list(raw['controls'])
        result['pipeline_version']='wb314_headroom_advisory_v1'
        result['primary_control_policy']='unchanged_frozen_tree'
        result['headroom_applied_to_primary']=False
        result['automatic_overcorrection_fix']=False
        result['qualification_complete']=False
        selected=(measurement>0)&(alpha>0)&~protected
        if not selected.any():
            result['headroom_advisory']=dict(available=False,reason='no_measured_unprotected_application_pixels',
                applied_to_primary=False,not_a_safety_pass=True)
            result['headroom_candidate']=None
            result['headroom_candidate_controls']=None
            return result
        decision=cap_facial_exposure_headroom(rgb,measurement,alpha,protected,raw['controls'])
        candidate_controls=decision['effective_controls']
        candidate=(render_rgb8(rgb,alpha,protected,candidate_controls)
                   if decision['applied'] else raw['output'].copy())
        if (not np.array_equal(candidate[protected],rgb[protected])
                or not np.array_equal(candidate[alpha==0],rgb[alpha==0])):
            raise RuntimeError('Headroom candidate protection invariant failed')
        result['headroom_advisory']=dict(available=True,applied_to_primary=False,
            candidate_controls_changed=decision['applied'],policy=decision['policy'],
            reason=decision['reason'],decision_region=decision['decision_region'],
            decision_pixels=decision['decision_pixels'],application_pixels=decision['application_pixels'],
            automatically_validated_as_preferred=False)
        result['headroom_candidate']=candidate
        result['headroom_candidate_controls']=candidate_controls
        return result
