import pytest
from src.correction.continuous_mst_candidate import continuous_model_features, CONTINUOUS_FEATURES


BASE = dict(input_mean_l_star=54., input_mean_a_star=9., input_mean_b_star=14., input_ita_degrees=16.)


def join(features=None, prediction=None, contract='a'*64, estimator='a'*64):
    return continuous_model_features(BASE if features is None else features,
        {'raw': 4.37, 'score': 4.37} if prediction is None else prediction,
        measurement_contract_sha256=contract, estimator_measurement_contract_sha256=estimator)


def test_fraction_retained_and_inputs_unchanged():
    before = BASE.copy()
    result = join()
    assert tuple(result) == CONTINUOUS_FEATURES
    assert result['input_mst_score'] == 4.37 and 'input_mst_index' not in result
    assert BASE == before


@pytest.mark.parametrize('raw,score', [(-2., 1.), (12., 10.), (1., 1.), (10., 10.)])
def test_explicit_clipping(raw, score):
    assert join(prediction=dict(raw=raw, score=score))['input_mst_score'] == score


@pytest.mark.parametrize('prediction', [{}, {'raw': 4.37, 'score': 4}, {'raw': None, 'score': 1},
    {'raw': float('nan'), 'score': 1}, {'raw': True, 'score': 1}, {'raw': 4, 'score': 4, 'label': 4}])
def test_no_missing_rounding_or_extra_label_fallback(prediction):
    with pytest.raises(ValueError):
        join(prediction=prediction)


@pytest.mark.parametrize('features', [dict(BASE, input_mst_index=3), dict(BASE, input_mean_l_star=101),
    dict(BASE, input_mean_a_star=float('inf')), {k:v for k,v in BASE.items() if k!='input_ita_degrees'}])
def test_reject_incompatible_features(features):
    with pytest.raises(ValueError):
        join(features=features)


def test_contract_mismatch_and_missing_contract():
    for contract, estimator in [('a'*64, 'b'*64), ('', ''), (None, None)]:
        with pytest.raises(ValueError):
            join(contract=contract, estimator=estimator)
