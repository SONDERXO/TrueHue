"""Generated context/weight/fold proof; no photographic inference or real fits."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from assess_wb314_background_balance import context_view, weighted_fit
from wb_feature_direct_verify import route


def test_context_replacement_preserves_measurement_and_every_application_pixel():
    image=np.full((256,256,3),50,np.uint8);reference=np.full_like(image,200)
    alpha=np.zeros((256,256));alpha[50:120,50:120]=.1
    measurement=np.zeros((256,256),np.uint8);measurement[120:150,120:150]=255
    before=image.tobytes(),reference.tobytes(),alpha.tobytes(),measurement.tobytes()
    result,retained=context_view(image,reference,alpha,measurement)
    assert np.all(result[retained]==50) and np.all(result[~retained]==200)
    assert before==(image.tobytes(),reference.tobytes(),alpha.tobytes(),measurement.tobytes())


def test_duplicate_identity_context_does_not_create_another_view():
    image=np.full((256,256,3),80,np.uint8)
    result,_=context_view(image,image.copy(),np.ones((256,256)),np.zeros((256,256),np.uint8))
    assert np.array_equal(result,image)


def test_source_held_fit_excludes_both_views_and_weighted_leaf_means_are_verified():
    rows=[]
    for source in ['a','b','held']:
        for view in ['original','context']:
            rows.append(dict(source_id=source,x=[0.]*314,weight=.5,
                y=[1.,2. if source=='a' else 1. if source=='b' else 4.,1.,1.,1.]))
    model=weighted_fit(rows,'held')
    assert route(model,[0.]*314)[1]==[1.,1.5,1.,1.,1.]


def test_invalid_features_rejected_before_fit():
    with pytest.raises(ValueError):
        weighted_fit([dict(source_id='a',x=[float('nan')]*314,y=[1.]*5,weight=1.)])
