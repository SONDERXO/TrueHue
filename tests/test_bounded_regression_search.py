from copy import deepcopy
from functools import lru_cache
import math
import random
import pytest
from src.model_training.bounded_regression_search import search_tree
from src.model_training.portable_tree import PortableTree,float32


def incumbent(y,width):
    return dict(schema_version='truehue_regression_tree_v1',input_dtype='float32',threshold_dtype='float64',comparison='<=',root=0,feature_names=['x'+str(i) for i in range(width)],target_names=['gamma','red','blue'],nodes=[dict(kind='leaf',values=[sum(r[j] for r in y)/len(y) for j in range(3)])],provenance={})


def exhaustive(x,y,depth):
    # Independent full enumeration: no memoization of search bounds/incumbents.
    xx=[[float32(v) for v in row] for row in x]
    @lru_cache(None)
    def cost(ids,d):
        means=[math.fsum(y[i][j] for i in ids)/len(ids) for j in range(3)]
        best=math.fsum((y[i][j]-means[j])**2 for i in ids for j in range(3))
        if d:
            for f in range(len(xx[0])):
                values=sorted({xx[i][f] for i in ids})
                for a,b in zip(values,values[1:]):
                    if b<=a+1e-7:continue
                    t=(a+b)/2;left=tuple(i for i in ids if xx[i][f]<=t);right=tuple(i for i in ids if xx[i][f]>t)
                    best=min(best,cost(left,d-1)+cost(right,d-1))
        return best
    return cost(tuple(range(len(x))),depth)


def test_zero_immediate_gain_interaction_and_no_mutation():
    x=[[0,0],[0,1],[1,0],[1,1]];y=[[1,1,1],[2,1,1],[2,1,1],[1,1,1]];seed=incumbent(y,2);before=deepcopy((x,y,seed))
    result=search_tree(x,y,seed,max_depth=2)
    assert result['search']['optimality_certified'] and result['search']['selected_SSE']==0
    assert PortableTree(result['tree']).predict(x)==y
    assert (x,y,seed)==before


@pytest.mark.parametrize('depth',[0,1,2,3])
def test_exhaustive_three_output_agreement(depth):
    x=[[0,0],[1,0],[2,1],[3,1],[4,0],[5,1]];y=[[1+(i%2)/4,1+(i%3)/7,1+(i%4)/9] for i in range(6)]
    result=search_tree(x,y,incumbent(y,2),max_depth=depth)
    assert result['search']['optimality_certified']
    assert result['search']['best_found_SSE']==pytest.approx(exhaustive(x,y,depth),abs=1e-12)


def test_state_exhaustion_keeps_feasible_incumbent_and_no_false_certificate():
    x=[[0,0],[0,1],[1,0],[1,1]];y=[[1,1,1],[2,1,1],[2,1,1],[1,1,1]];seed=incumbent(y,2)
    result=search_tree(x,y,seed,max_depth=2,max_states=1)
    assert result['search']['status']=='budget_limited' and result['search']['global_lower_bound']==0
    assert not result['search']['optimality_certified'] and result['search']['partial_states_cached']==0
    assert result['search']['expanded_states']==1 and result['tree']==seed


def test_timeout_is_deterministic_and_does_not_cache_partial_root():
    ticks=iter([0.,2.,2.]);y=[[1,1,1],[2,1,1]]
    result=search_tree([[0],[1]],y,incumbent(y,1),max_seconds=1,clock=lambda:next(ticks))
    assert result['search']['limit_reason']=='time_limit' and result['search']['partial_states_cached']==0


def test_float32_duplicate_conflict_and_constant_targets():
    y=[[1,1,1],[2,1,1]]
    result=search_tree([[1],[1+1e-10]],y,incumbent(y,1),max_depth=3)
    assert result['search']['optimality_certified'] and result['search']['selected_SSE']==.5
    constant=[[1,1,1]]*3;result=search_tree([[0],[1],[2]],constant,incumbent(constant,1))
    assert result['search']['optimality_certified'] and result['search']['expanded_states']==0


def test_equal_cost_preserves_incumbent_structure():
    y=[[1,1,1],[2,1,1]];seed=incumbent(y,1)
    seed['nodes']=[dict(kind='split',feature=0,threshold=.5,left=1,right=2),dict(kind='leaf',values=y[0]),dict(kind='leaf',values=y[1])]
    result=search_tree([[0],[1]],y,seed,max_depth=1)
    assert not result['search']['strict_improvement'] and result['tree']==seed


def test_reject_invalid_targets_or_budget():
    seed=incumbent([[1,1,1],[2,1,1]],1)
    with pytest.raises(ValueError):search_tree([[0],[1]],[[1,1,1],[0,1,1]],seed)
    with pytest.raises(ValueError):search_tree([[0],[1]],[[1,1,1],[2,1,1]],seed,max_states=True)


def test_many_generated_exhaustive_cases_and_budget_lower_bounds():
    rng=random.Random(42)
    for _ in range(24):
        x=[[rng.randrange(3) for j in range(2)] for i in range(5)]
        y=[[1+rng.randrange(4)/8 for j in range(3)] for i in range(5)]
        best=exhaustive(x,y,2);seed=incumbent(y,2)
        result=search_tree(x,y,seed,max_depth=2)
        assert result['search']['optimality_certified']
        assert result['search']['best_found_SSE']==pytest.approx(best,abs=1e-12)
        capped=search_tree(x,y,seed,max_depth=2,max_states=1)
        assert capped['search']['global_lower_bound']<=best+1e-12
        assert capped['search']['best_found_SSE']>=best-1e-12
        assert capped['search']['partial_states_cached']==0


def test_tiny_improvement_does_not_claim_selected_tree_is_optimal():
    y=[[1.,1.,1.],[1.+1e-8,1.,1.]];seed=incumbent(y,1)
    result=search_tree([[0],[1]],y,seed,max_depth=1)
    assert result['search']['optimality_certified']
    assert not result['search']['selected_optimality_certified']
    assert not result['search']['strict_improvement'] and result['tree']==seed
