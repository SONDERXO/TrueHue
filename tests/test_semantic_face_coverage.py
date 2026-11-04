import numpy as np
import pytest
from src.skin_masking.semantic_face_coverage import select_face_skin


def test_forehead_and_chin_are_not_clipped_to_seed_rectangle():
    cats=np.zeros((20,20),np.uint8);cats[1:19,5:15]=1;cats[8:12,8:12]=10
    seed=np.zeros((20,20),bool);seed[6:14,7:13]=True
    mask,report=select_face_skin(cats,seed,np.zeros_like(seed))
    assert mask[1,10]==mask[18,10]==255
    assert report['selected_forbidden_class_pixels']==0


def test_every_forbidden_class_remains_excluded_without_hole_filling():
    cats=np.ones((20,20),np.uint8)
    for i,label in enumerate([0,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18]):cats[5,i]=label
    seed=np.ones((20,20),bool);mask,_=select_face_skin(cats,seed,np.zeros_like(seed))
    assert not mask[5,:17].any() and mask[4,5]==255


def test_disconnected_forehead_and_lower_face_are_both_kept():
    cats=np.zeros((20,20),np.uint8);cats[2:7,4:16]=1;cats[12:18,4:16]=1
    cats[7:12,4:16]=6
    seed=np.zeros((20,20),bool);seed[3:17,6:14]=True
    mask,report=select_face_skin(cats,seed,np.zeros_like(seed))
    assert mask[3,10]==mask[15,10]==255 and not mask[7:12].any()
    assert report['associated_components']==2


def test_unassociated_other_face_component_is_rejected():
    cats=np.zeros((20,30),np.uint8);cats[2:18,2:10]=1;cats[2:18,20:28]=1
    seed=np.zeros(cats.shape,bool);seed[5:15,3:9]=True
    mask,report=select_face_skin(cats,seed,np.zeros_like(seed))
    assert mask[:,2:10].any() and not mask[:,20:].any()
    assert report['rejected_unassociated_components']==1


def test_exclusions_are_hard_and_inputs_unchanged():
    cats=np.ones((20,20),np.uint8);seed=np.ones((20,20),bool);exclude=np.zeros_like(seed);exclude[8:12,8:12]=True
    before=[x.copy() for x in [cats,seed,exclude]]
    mask,_=select_face_skin(cats,seed,exclude)
    assert not mask[exclude].any()
    assert all(np.array_equal(a,b) for a,b in zip([cats,seed,exclude],before))


@pytest.mark.parametrize('kind',['no_skin','empty_seed','all_excluded','wrong_type','invalid_class'])
def test_invalid_or_unavailable_skin_has_no_geometric_fallback(kind):
    cats=np.ones((20,20),np.uint8);seed=np.ones((20,20),bool);exclude=np.zeros_like(seed)
    if kind=='no_skin':cats[:]=0
    elif kind=='empty_seed':seed[:]=False
    elif kind=='all_excluded':exclude[:]=True
    elif kind=='wrong_type':seed=seed.astype(np.uint8)
    elif kind=='invalid_class':cats[0,0]=19
    with pytest.raises(ValueError):select_face_skin(cats,seed,exclude)
