from copy import deepcopy
import numpy as np
import pytest
from src.model_training.split_control_candidate import fit_split_predictors,predict_split
from src.model_training.gamma_scene_chroma_restriction import fit_restricted_gamma,EXCLUDED

def test_restricted_gamma_ignores_scene_chroma_and_freezes_gains():
    names=['x',*EXCLUDED];x=np.array([[i%3,i,i%2] for i in range(24)],float);y=np.array([[1+.1*(i%3),.8+.01*i,1.2-.01*i] for i in range(24)])
    baseline,_=fit_split_predictors(x,y,names);before=deepcopy(baseline);candidate=fit_restricted_gamma(baseline,x,y)
    assert baseline==before and candidate['heads']['gains']==baseline['heads']['gains']
    assert all(n['feature']==0 for n in candidate['heads']['gamma']['tree']['nodes'] if n['kind']=='split')
    assert predict_split(candidate,[1,-1e5,1e5])[0]==predict_split(candidate,[1,1e5,-1e5])[0]
    for row in x:assert predict_split(candidate,row)[1:]==predict_split(baseline,row)[1:]

def test_restricted_gamma_rejects_invalid_targets_and_missing_columns():
    base,_=fit_split_predictors([[0,0,0]],[[1,1,1]],['x',*EXCLUDED])
    with pytest.raises(ValueError):fit_restricted_gamma(base,[[0,0,0]],[[0,1,1]])
    base['feature_names']=['x','y','z']
    with pytest.raises(ValueError):fit_restricted_gamma(base,[[0,0,0]],[[1,1,1]])
