import numpy as np
import pytest
from src.evaluation.feature_target_diagnostic import neighbor_diagnostic

def test_scale_uses_only_fitting_data_and_no_target_or_probe_information():
    x=[[0,0],[2,4],[4,8]];y=[[1,1,1],[.8,1,1],[1.2,1,1]]
    first=neighbor_diagnostic(['a','b','c'],x,y,[1,2],[1,1,1],[0,1])
    second=neighbor_diagnostic(['a','b','c'],x,list(reversed(y)),[1000,2000],[.9,1,1],[0,1])
    assert first['fit_population_std']==second['fit_population_std'] and first['fit_mean']==second['fit_mean']
    np.testing.assert_allclose(first['fit_population_std'],np.std(x,axis=0,ddof=0))

def test_ties_are_deterministic_and_conflicting_targets_are_reported_not_classified():
    result=neighbor_diagnostic(['z','a','b'],[[0],[0],[2]],[[1,1,1],[.8,1,1],[1,1,1]],[0],[1,1,1],[0])
    assert [r['pair_id'] for r in result['ranking']]==['a','z','b']
    assert result['nearest_matching_target']['distance']==result['nearest_different_target']['distance']==0
    assert result['different_target_strictly_closer'] is False

def test_constant_axes_are_explicitly_dropped_and_query_shift_not_hidden():
    result=neighbor_diagnostic(['a','b'],[[1,0],[1,2]],[[1,1,1],[.8,1,1]],[5,1],[1,1,1],[0,1])
    assert result['constant_axes']==[0] and result['active_axes']==[1] and result['query_differs_on_constant_axes']

def test_absent_matching_target_is_unavailable_not_evidence_of_conflict():
    result=neighbor_diagnostic(['a'],[[0]],[[.8,1,1]],[0],[1,1,1],[0])
    assert result['nearest_matching_target'] is None and result['different_target_strictly_closer'] is None

@pytest.mark.parametrize('ids,x,y,q,t,axes',[
    (['a','a'],[[0],[1]],[[1,1,1],[1,1,1]],[0],[1,1,1],[0]),
    (['a'],[[float('nan')]],[[1,1,1]],[0],[1,1,1],[0]),
    (['a'],[[0]],[[0,1,1]],[0],[1,1,1],[0]),
    (['a'],[[0]],[[1,1,1]],[0],[1,1,1],[2]),
    (['a'],[[0]],[[1,1,1]],[0],[1,1,1],[0,0])])
def test_invalid_diagnostic_input_is_rejected(ids,x,y,q,t,axes):
    with pytest.raises(ValueError):neighbor_diagnostic(ids,x,y,q,t,axes)
