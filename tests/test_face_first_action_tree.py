import numpy as np
from src.model_training.face_first_action_tree import fit_face_first_tree,ROOT_FEATURES
from src.model_training.portable_tree import PortableTree
A=[[1.,1.,1.],[.7,1.,1.],[1.4,1.,1.]]

def test_facial_root_learns_clean_identity_and_distortion_correction():
    names=['input_mean_l_star','scene_l_p50']
    m=fit_face_first_tree([[0,2],[1,1]],[[0,10,12],[20,0,30]],[True,False],A,names)
    tree=PortableTree(m['tree']);assert m['tree']['nodes'][0]['feature']==0
    assert tree.predict_one([0,2])==A[0] and tree.predict_one([1,1])==A[1]

def test_scene_only_root_shortcut_is_not_available():
    m=fit_face_first_tree([[1,0],[1,1]],[[0,10,12],[20,0,30]],[True,False],A,['input_mean_l_star','scene_l_p50'])
    assert len(m['tree']['nodes'])==1 and m['tree']['nodes'][0]['values']==A[0]

def test_descendants_can_use_context_after_facial_root():
    x=[[0,0],[1,0],[1,1]];costs=[[0,50,50],[20,0,10],[20,10,0]]
    m=fit_face_first_tree(x,costs,[True,False,False],A,['input_mean_l_star','scene_l_p50'])
    assert m['tree']['nodes'][0]['feature']==0
    assert any(n['kind']=='split' and n['feature']==1 for n in m['tree']['nodes'][1:])
    assert PortableTree(m['tree']).predict(x)==A
