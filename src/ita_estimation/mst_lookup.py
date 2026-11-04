"""Versioned calibrated ITA→MST interface; no built-in or guessed thresholds."""
from bisect import bisect_right
import hashlib
import json
import math
from numbers import Real
import re
from src.utilities.config import get_config
from src.data_preparation.controlled_training_table import FEATURES

MST_FEATURES = FEATURES + ('input_mst_index',)


def _sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


class CalibratedMstLookup:
    """Read-only lookup tied to a measurement contract and held-subject evidence.

    Schema validation verifies declarations, not scientific accuracy. The
    referenced validation report must itself be independently checked before
    use. This project does not currently supply a validated production artifact.
    """
    def __init__(self, payload, *, measurement_contract_sha256):
        if not _sha(measurement_contract_sha256):
            raise ValueError('Measurement contract SHA256 required')
        if payload.get('schema_version') != 'truehue_ita_mst_lookup_v1':
            raise ValueError('Unsupported lookup schema')
        labels = get_config().MST_LABELS
        if set(labels) != set(range(10)):
            raise ValueError('Ten configured MST indices required')
        bounds = payload.get('ita_thresholds_degrees')
        if not isinstance(bounds, list) or len(bounds) != len(labels)-1:
            raise ValueError('Nine calibrated thresholds required for ten categories')
        if any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) for v in bounds):
            raise ValueError('Finite numeric thresholds required')
        if any(a >= b for a,b in zip(bounds,bounds[1:])):
            raise ValueError('Strictly ascending thresholds required')
        if payload.get('boundary_rule') != 'upper_bin_at_equal':
            raise ValueError('Explicit boundary rule required')
        if payload.get('mst_labels_low_to_high_ita') != list(range(10,0,-1)):
            raise ValueError('ITA order must map to official MST10 through MST1')
        calibration=payload.get('calibration',{}); validation=payload.get('validation',{})
        if calibration.get('dataset') != 'MST-E':
            raise ValueError('Paper requires declared MST-E calibration provenance')
        if calibration.get('measurement_contract_sha256') != measurement_contract_sha256:
            raise ValueError('Calibration and input measurement contracts differ')
        def subjects(values):
            if not isinstance(values,list) or not values or any(not isinstance(v,str) or not v.strip() for v in values) or len(set(values)) != len(values):
                raise ValueError('Unique nonempty subject IDs required')
            return set(values)
        if subjects(calibration.get('subject_ids')) & subjects(validation.get('subject_ids')):
            raise ValueError('Calibration/validation subject overlap')
        if validation.get('status') != 'passed' or not _sha(validation.get('report_sha256')):
            raise ValueError('Passing validation report declaration required; no unvalidated fallback')
        # Store immutable values; caller mutation must not change routing.
        self._thresholds=tuple(float(v) for v in bounds)
        self.measurement_contract_sha256=measurement_contract_sha256
        self.validation_report_sha256=validation['report_sha256']
        self.artifact_sha256=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

    def label(self, ita_degrees):
        if isinstance(ita_degrees,bool) or not isinstance(ita_degrees,Real) or not math.isfinite(ita_degrees):
            raise ValueError('Finite measured ITA required')
        return 10-bisect_right(self._thresholds,float(ita_degrees))


def mst_model_features(input_features, lookup, *, measurement_contract_sha256):
    """Map the actual distorted-input ITA; never accept a reference MST feature."""
    if not isinstance(lookup,CalibratedMstLookup):
        raise ValueError('Calibrated MST lookup required; four-feature fallback prohibited')
    if lookup.measurement_contract_sha256 != measurement_contract_sha256:
        raise ValueError('Input measurement contract differs from calibrated lookup')
    if set(input_features) != set(FEATURES):
        raise ValueError('Exact input-only Lab/ITA features required')
    values={}
    for key in FEATURES:
        value=input_features[key]
        if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value):
            raise ValueError('Finite numeric input measurements required')
        values[key]=float(value)
    values['input_mst_index']=lookup.label(values['input_ita_degrees'])-1
    return values
