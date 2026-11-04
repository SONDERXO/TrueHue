import hashlib
import json
import cv2
import numpy as np
import pytest
from src.demo.mask_editor import MaskEditSession
from src.skin_masking.facial_hair_exclusion import paint_exclusions,apply_exclusions


def setup_preview(tmp_path):
    image=np.full((40,40,3),[40,80,120],np.uint8);mask=np.zeros((40,40),np.uint8);mask[5:35,5:35]=255;mask[12:16,12:16]=0
    cv2.imwrite(str(tmp_path/'input.png'),image);cv2.imwrite(str(tmp_path/'mask.png'),mask)
    return image,mask


def test_save_preserves_preferred_mask_and_replays_exact_user_strokes(tmp_path):
    image,base=setup_preview(tmp_path);original=(tmp_path/'mask.png').read_bytes()
    session=MaskEditSession(image,base);session.add(dict(mode='exclude',radius=3,points=[[10,26],[30,26]]))
    saved=session.save(tmp_path);record=json.loads((saved/'edit.json').read_text())
    assert (tmp_path/'mask.png').read_bytes()==original and record['added_pixels']==0
    assert record['base_mask_sha256']==hashlib.sha256(original).hexdigest() and record['training_admitted'] is False
    replay,_=apply_exclusions(base,paint_exclusions(base.shape,record['strokes']))
    assert np.array_equal(cv2.imread(str(saved/'mask.png'),0),replay)
    assert saved!=session.save(tmp_path)


def test_undo_reset_restore_and_no_automatic_suggestion(tmp_path):
    image,base=setup_preview(tmp_path);suggestion=np.ones(base.shape,bool)
    session=MaskEditSession(image,base,suggestion=suggestion)
    assert np.array_equal(session.current()[0],base)
    session.add(dict(mode='exclude',radius=4,points=[[20,25]]));assert session.current()[0][25,20]==0
    session.undo();assert np.array_equal(session.current()[0],base)
    session.use_suggestion=True;assert not session.current()[0].any()
    session.add(dict(mode='restore',radius=6,points=[[14,14]]))
    assert not session.current()[0][base==0].any()
    session.reset();assert np.array_equal(session.current()[0],base) and not session.use_suggestion


def test_changed_underlying_image_or_mask_blocks_saving(tmp_path):
    image,base=setup_preview(tmp_path);session=MaskEditSession(image,base)
    base[0,0]=255;cv2.imwrite(str(tmp_path/'mask.png'),base)
    with pytest.raises(ValueError):session.save(tmp_path)


def test_suggestion_source_is_saved_when_explicitly_enabled(tmp_path):
    image,base=setup_preview(tmp_path);veto=np.zeros_like(base,bool);veto[25:30,10:30]=True
    session=MaskEditSession(image,base,suggestion=veto);session.use_suggestion=True
    folder=session.save(tmp_path);record=json.loads((folder/'edit.json').read_text())
    saved=cv2.imread(str(folder/'suggestion_used.png'),0)>0
    assert np.array_equal(saved,veto) and record['auxiliary_suggestion_enabled'] is True


def test_invalid_stroke_does_not_pollute_undo_history(tmp_path):
    image,base=setup_preview(tmp_path);session=MaskEditSession(image,base)
    with pytest.raises(ValueError):session.add(dict(mode='exclude',radius=0,points=[[5,5]]))
    assert not session.strokes and np.array_equal(session.current()[0],base)
