import numpy as np
import pytest
from src.ita_estimation.faceocc_veto_candidate import combine_saved


def test_veto_is_removal_only_and_threshold_is_strict():
    image=np.full((256,256,3),[80,110,150],np.uint8)
    mask=np.zeros((256,256),np.uint8);mask[40:210,40:210]=255
    before=mask.copy();logits=np.ones((256,256));logits[60:80,60:80]=0
    candidate,_,report=combine_saved(image,mask,logits,np.array([[1,0,0],[0,1,0]]))
    assert not candidate[60:80,60:80].any() and not candidate[mask==0].any()
    assert report['removed_pixels']==400 and report['status']=='success'
    assert np.array_equal(mask,before)


def test_unavailable_features_and_nonfinite_outputs_fail():
    image=np.full((256,256,3),[80,110,150],np.uint8);mask=np.full((256,256),255,np.uint8)
    matrix=np.array([[1,0,0],[0,1,0]])
    _,_,report=combine_saved(image,mask,np.zeros((256,256)),matrix)
    assert report['features'] is None and report['status']=='failed'
    with pytest.raises(ValueError):combine_saved(image,mask,np.full((256,256),np.nan),matrix)
