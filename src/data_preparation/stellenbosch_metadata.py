"""Read release MST scores without silently creating integer category labels."""
from decimal import Decimal,InvalidOperation
import math


def parse_mst_value(record):
    if not isinstance(record,dict) or set(record)!={'value'}:
        raise ValueError('Exactly one value field required')
    raw=record['value']
    if isinstance(raw,bool) or not isinstance(raw,(int,float,str)):
        raise ValueError('Numeric MST score or numeric string required')
    if isinstance(raw,float) and not math.isfinite(raw):
        raise ValueError('Finite MST score required')
    try:
        value=Decimal(str(raw).strip())
    except InvalidOperation as error:
        raise ValueError('Invalid numeric MST score') from error
    if not value.is_finite() or not Decimal(1)<=value<=Decimal(10):
        raise ValueError('MST score must be finite within1..10')
    integral=value==value.to_integral_value()
    return dict(raw_value=raw,raw_type=type(raw).__name__,
        exact_decimal=format(value,'f'),is_integral=integral,
        integer_category=None,rounding_applied=False,
        training_admitted=False)
