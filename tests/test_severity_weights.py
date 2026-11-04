import numpy as np
import pytest
from src.model_training.severity_weights import control_severity_weights


def test_imbalanced_fitting_severities_share_distorted_weight():
    variants=['identity','identity','table2_light','table2_medium','table2_medium','table2_medium']
    weights=control_severity_weights([dict(variant=v) for v in variants])
    np.testing.assert_allclose(weights,[.25,.25,.25,1/12,1/12,1/12])
    assert weights[:2].sum()==.5 and abs(weights.sum()-1)<1e-12


def test_missing_severity_is_not_fabricated_and_input_unmodified():
    rows=[dict(variant='identity'),dict(variant='table2_medium')]
    assert control_severity_weights(rows).tolist()==[.5,.5]
    assert rows==[dict(variant='identity'),dict(variant='table2_medium')]


@pytest.mark.parametrize('variants',[[],['identity'],['table2_medium'],['identity','unknown']])
def test_missing_groups_or_unknown_variants_rejected(variants):
    with pytest.raises(ValueError):control_severity_weights([dict(variant=v) for v in variants])
