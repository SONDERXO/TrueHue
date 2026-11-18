import pytest
from src.data_preparation.stellenbosch_metadata import parse_mst_value


@pytest.mark.parametrize('value,decimal,integral',[(1,'1',True),(6.0,'6.0',True),(3.5,'3.5',False),('8','8',True),('2.588888','2.588888',False)])
def test_source_scores_are_preserved_without_rounding(value,decimal,integral):
    source={'value':value};result=parse_mst_value(source)
    assert result['raw_value']==value and result['raw_type']==type(value).__name__
    assert result['exact_decimal']==decimal and result['is_integral']==integral
    assert result['integer_category'] is None and not result['rounding_applied']
    assert source=={'value':value} and not result['training_admitted']


@pytest.mark.parametrize('record',[{'value':True},{'value':float('nan')},{'value':'Infinity'},
    {'value':0},{'value':10.1},{'value':'not labelled'},{'value':None},{'value':3,'label':3},{}])
def test_invalid_or_ambiguous_label_is_explicitly_rejected(record):
    with pytest.raises(ValueError):parse_mst_value(record)
