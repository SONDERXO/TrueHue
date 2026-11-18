import numpy as np
import pytest
from src.skin_masking.correction_ear_preview import add_associated_ears

def test_association_and_protections_without_measurement_change():
    c=np.zeros((9,12),np.uint8);c[2:7,4:7]=255;m=c.copy();cat=np.zeros_like(c)
    cat[3:6,3]=7;cat[3:6,7]=8;cat[0,0]=7;cat[1,4:7]=17;cat[7,4:7]=1
    p=np.zeros(c.shape,bool);p[4,3]=True;removed=np.zeros_like(p);removed[4,7]=True
    before=c.copy();result,measurement,report=add_associated_ears(c,m,p,cat,manual_removed=removed)
    assert report['added_pixels']==4
    assert not result[p].any() and not result[removed].any()
    assert not result[0,0] and not result[1].any() and not result[7].any()
    assert np.array_equal(measurement,m) and np.array_equal(c,before)

def test_invalid_or_conflicting_support_rejected():
    c=np.full((3,3),255,np.uint8);p=np.ones((3,3),bool)
    with pytest.raises(ValueError):add_associated_ears(c,c,p,np.zeros_like(c),manual_removed=~p)

def test_approved_adapter_preserves_measurement_neck_and_manual_veto():
    from src.skin_masking.approved_ear_support import extend_support,VERSION
    from src.skin_masking.face_neck_support import FaceNeckSupport
    c=np.zeros((8,8),np.uint8);c[2:6,3:5]=255;cat=np.zeros_like(c);cat[3:5,2]=7
    p=np.zeros(c.shape,bool);removed=np.zeros_like(p);removed[3,2]=True
    base=FaceNeckSupport(c.copy(),np.zeros_like(c),c.copy(),{'version':'parent'})
    result=extend_support(base,cat,protected=p,manual_removed=removed)
    assert np.array_equal(result.measurement_mask,base.measurement_mask)
    assert np.array_equal(result.neck_mask,base.neck_mask)
    assert not result.correction_mask[3,2] and result.correction_mask[4,2]
    assert result.report['ear_coverage']['version']==VERSION
