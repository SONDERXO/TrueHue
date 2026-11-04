import copy
import pytest
from src.ita_estimation.monotone_lookup import DevelopmentMonotoneLookup


def payload():return dict(schema_version='truehue_development_monotone_mst_v1',status='experimental_not_final_validated',measurement_contract_sha256='a'*64,rounding='floor_plus_half',outside_range='clip',ita_knots=[-50,0,50],mst_knots=[9,5,1])
def lookup(p=None):return DevelopmentMonotoneLookup(payload() if p is None else p,'a'*64)


def test_interpolation_boundaries_clipping_and_rounding():
    m=lookup();assert m.label(-100)==9 and m.label(100)==1
    assert m.continuous(-25)==7 and m.label(0)==5
    assert m.label(6.25)==5 and m.label(6.26)==4


def test_artifact_is_copied():
    p=payload();m=lookup(p);p['mst_knots'][0]=1;assert m.label(-100)==9


@pytest.mark.parametrize('change',[
 lambda p:p.update(status='validated'),lambda p:p.update(measurement_contract_sha256='b'*64),
 lambda p:p.update(ita_knots=[0,0,1]),lambda p:p.update(mst_knots=[1,5,9]),
 lambda p:p.update(mst_knots=[11,5,1]),lambda p:p.update(ita_knots=[float('nan'),0,50]),
 lambda p:p.update(outside_range='extrapolate'),lambda p:p.update(rounding='bankers')])
def test_invalid_or_misrepresented_artifacts_fail(change):
 p=payload();change(p)
 with pytest.raises(ValueError):lookup(p)


@pytest.mark.parametrize('v',[True,float('nan'),float('inf'),'20',None])
def test_invalid_inputs_fail(v):
 with pytest.raises(ValueError):lookup().label(v)
