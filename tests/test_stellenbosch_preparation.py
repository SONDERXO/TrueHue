from decimal import Decimal
import pytest
from src.data_preparation.stellenbosch_preparation import select_subjects


def rows():
    return [dict(subject_key=str(i),exact_decimal=str(v)) for i,v in enumerate([1,1.5,2.5,3,3.2,4.5,5,5.7,6.5,7,7.8,8.9,9,9.5,10])]


def test_sample_is_order_independent_preserves_scores_and_not_category_assignment():
    a=select_subjects(rows());b=select_subjects(list(reversed(rows())))
    assert a==b and len(a)==10 and len({r['subject_key'] for r in a})==10
    assert all(not r['stratum_is_category'] for r in a)
    assert any(Decimal(r['exact_decimal'])%1 for r in a)
    assert len({r['sampling_stratum'] for r in a})==5


def test_missing_stratum_fails_without_replacement():
    with pytest.raises(ValueError):select_subjects(rows()[:-2])


def test_duplicate_subject_cannot_become_two_people():
    source=rows();source.append(source[0])
    with pytest.raises(ValueError):select_subjects(source)
