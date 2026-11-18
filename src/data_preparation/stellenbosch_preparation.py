"""Deterministic bounded sampling; strata are not integer MST labels."""
from decimal import Decimal
import hashlib

CONDITIONS=('F_cool_600','H_warm_600','L_warm_600')
BANDS=((1,3),(3,5),(5,7),(7,9),(9,10))


def select_subjects(subjects):
    if len({r['subject_key'] for r in subjects})!=len(subjects):
        raise ValueError('Unique source subject keys required')
    selected=[]
    for low,high in BANDS:
        eligible=[]
        for row in subjects:
            value=Decimal(row['exact_decimal'])
            if not value.is_finite() or not 1<=value<=10:raise ValueError('Finite source score1..10 required')
            if Decimal(low)<=value and (value<Decimal(high) or high==10 and value==10):
                eligible.append(row)
        if len(eligible)<2:raise ValueError('Insufficient subjects in predeclared sampling stratum')
        eligible.sort(key=lambda r:hashlib.sha256(('TrueHue-Stellenbosch-preparation-v1:'+r['subject_key']).encode()).hexdigest())
        selected.extend(dict(row,sampling_stratum=f'[{low},{high}'+(']' if high==10 else ')'),
            stratum_is_category=False) for row in eligible[:2])
    return selected
