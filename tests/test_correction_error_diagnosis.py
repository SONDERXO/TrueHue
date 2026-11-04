import numpy as np
import pytest
from src.evaluation.correction_error_diagnosis import region_errors,factorial_gaps
from src.evaluation.correction_prototype import apply_correction


def test_known_inverse_isolates_missed_and_extra_support_instead_of_changing_overlap():
    reference=np.full((4,4,3),100,np.uint8)
    source=np.zeros((4,4),bool);source[1:3,1:3]=True
    current=source.copy();current[1,1]=False;current[0,0]=True
    distorted=reference.copy();distorted[source]=[80,100,120]
    known=apply_correction(distorted,current,[1,1.25,1/1.2])
    oracle=apply_correction(distorted,source,[1,1.25,1/1.2])
    regions=region_errors(reference,known,source,current)
    assert sum(r['pixels'] for r in regions.values())==16
    assert regions['shared_source_and_current']['ciede2000']==0
    assert regions['source_missed_by_current']['ciede2000']>0
    assert regions['current_outside_source']['ciede2000']>0
    assert regions['neither_source_nor_current']['ciede2000']==0
    np.testing.assert_array_equal(reference,oracle)


def test_empty_regions_have_no_means_and_invalid_shapes_are_rejected():
    image=np.zeros((3,3,3),np.uint8);mask=np.ones((3,3),bool)
    result=region_errors(image,image,mask,mask)
    assert result['source_missed_by_current']['pixels']==0 and result['source_missed_by_current']['ciede2000'] is None
    with pytest.raises(ValueError):region_errors(image,image,mask,np.ones((2,3),bool))


def test_factorial_differences_preserve_sign_and_interaction():
    result=factorial_gaps(dict(tree_current_mask=4,known_current_mask=5,tree_source_mask_oracle=8,known_source_mask_oracle=1))
    assert result['parameter_gap_at_current_mask']==-1 and result['mask_gap_at_tree_parameters']==-4
    assert result['parameter_mask_interaction']==-8
    assert result['parameter_gap_at_current_mask']+result['mask_gap_at_known_parameters']==result['tree_above_source_oracle']
    with pytest.raises(ValueError):factorial_gaps({})
