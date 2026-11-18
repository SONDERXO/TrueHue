"""Isolated continuous-score correction schema; not a runtime/category adapter."""
import math
from numbers import Real
import re
from src.data_preparation.controlled_training_table import FEATURES

VERSION = 'truehue_continuous_mst_correction_candidate_v1'
CONTINUOUS_FEATURES = FEATURES + ('input_mst_score',)


def _finite(value):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError('Finite numeric value required')
    return float(value)


def continuous_model_features(input_features, prediction, *, measurement_contract_sha256,
                              estimator_measurement_contract_sha256):
    """Join actual input statistics and clipped contextual prediction, without rounding.

    Contract equality checks declarations only. The caller must bind prediction
    to this exact image and establish estimator eligibility and fold isolation.
    This function neither fits nor validates an estimator scientifically.
    """
    if (not isinstance(measurement_contract_sha256, str)
            or not re.fullmatch('[0-9a-f]{64}', measurement_contract_sha256)
            or estimator_measurement_contract_sha256 != measurement_contract_sha256):
        raise ValueError('Matching measurement contracts required')
    if not isinstance(input_features, dict) or set(input_features) != set(FEATURES):
        raise ValueError('Exact input-only Lab/ITA schema required')
    values = {k: _finite(input_features[k]) for k in FEATURES}
    if not 0 <= values['input_mean_l_star'] <= 100 or not -90 <= values['input_ita_degrees'] <= 90:
        raise ValueError('Invalid L/ITA range')
    if any(not -128 <= values[k] <= 127 for k in ('input_mean_a_star', 'input_mean_b_star')):
        raise ValueError('Invalid chroma range')
    if not isinstance(prediction, dict) or set(prediction) != {'raw', 'score'}:
        raise ValueError('Contextual raw and clipped score required; no fallback')
    raw, score = _finite(prediction['raw']), _finite(prediction['score'])
    if score != min(10., max(1., raw)):
        raise ValueError('Score must equal explicit 1–10 clipping of raw prediction')
    values['input_mst_score'] = score
    return values
