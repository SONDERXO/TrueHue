"""Hand-computed safeguards for interpreting channel clipping/detail counts."""
import importlib.util
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location('detail_check',Path(__file__).resolve().parents[1]/'scripts/397_ppr10k_clipping_detail_check.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


def test_single_channel_clipping_is_not_all_rgb_white():
    source=np.full((1,1,3),.5);target=source.copy();raw=np.array([[[1.2,.5,.5]]])
    result,*_=audit.analyse(source,target,np.ones((1,1),bool),raw)
    assert result['high_channel_samples']==1
    assert result['all_RGB_white_pixels']==0
    assert result['target_two_codes_away_samples']==1


def test_mask_and_target_endpoint_are_respected():
    source=np.full((1,2,3),.5);target=np.ones((1,2,3));raw=np.full((1,2,3),1.2)
    result,*_=audit.analyse(source,target,np.array([[True,False]]),raw)
    assert result['clipped_channel_samples']==3
    assert result['all_RGB_white_pixels']==1
    assert result['target_two_codes_away_samples']==0


def test_adjacent_source_and_target_variation_can_collapse_in_one_channel():
    source=np.array([[[.6,.5,.5],[.7,.5,.5]]]);target=np.array([[[.8,.5,.5],[.9,.5,.5]]])
    raw=np.array([[[1.1,.5,.5],[1.2,.5,.5]]])
    result,*_=audit.analyse(source,target,np.ones((1,2),bool),raw)
    assert result['adjacent_pairs']['horizontal']['source_and_target_variation']==1
    assert result['adjacent_pairs']['vertical']['same_endpoint_pairs']==0
