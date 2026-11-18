from copy import deepcopy
import numpy as np,pytest
from src.model_training.reference_prior_stability_audit import summarize,table_for_fold,residual

def stats(mu):return dict(total=10,positive=10,bins=[dict(count=10,mean=mu.copy())]+[dict(count=0,mean=None) for _ in range(7)])
class Poison:
    def __getitem__(self,k):raise RuntimeError('Held statistics read into prior')

def test_exclusion_order_weighting_and_nulls():
    s=dict(A=stats([.1,-.1]),B=stats([.3,-.1]),H=Poison())
    t=table_for_fold(s,['B','A'],'H');assert np.allclose(t[0]['mean'],[.2,-.1]) and t[1]['mean'] is None
    assert t==table_for_fold(s,['A','B'],'H')
    s['B']['bins'][0]['count']=100000
    assert table_for_fold(s,['A','B'],'H')==t
    own=stats([.2,-.1]);d=residual(own,t);assert d['red_residual']==d['blue_residual']==0
    own['bins'][0]['count']=0;own['bins'][1]=dict(count=10,mean=[.2,-.1]);d=residual(own,t)
    assert not d['available'] and d['red_residual'] is None

@pytest.mark.parametrize('ids',[['A','H'],['A','A'],['A'],[]])
def test_bad_rosters_rejected(ids):
    with pytest.raises(ValueError):table_for_fold(dict(A=stats([0,0]),B=stats([0,0]),H=Poison()),ids,'H')

def test_known_rgb_constant_and_no_mutation():
    rgb=np.full((256,256,3),[64,64,64],np.uint8);before=rgb.copy();s=summarize(rgb)
    assert np.array_equal(rgb,before) and s['positive']==65536 and s['bins'][2]['mean']==[0.,0.]
    t=table_for_fold(dict(A=s,B=deepcopy(s)),['A'],'B');assert residual(s,t)['red_residual']==0
