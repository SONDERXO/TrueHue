"""Version dispatch preserves baseline behavior and fails closed on drift."""
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
pipeline=importlib.import_module('11_prepare_training_manifests')


def test_baseline_and_unavailable_landmarks_return_original(monkeypatch):
    baseline=SimpleNamespace(landmarks_available=False)
    monkeypatch.setattr(pipeline,'compute_v2_skin_mask_with_margin',lambda *args:baseline)
    for version in ('v2','v2_complete_mouth_v1'):
        assert pipeline.compute_versioned_skin_mask(None,None,None,None,version) is baseline


def test_version_rejects_unmatched_geometry(monkeypatch):
    baseline=SimpleNamespace(landmarks_available=True,exclusion_mask=np.zeros((10,10),np.uint8))
    monkeypatch.setattr(pipeline,'detect_landmarks_with_margin',lambda *args:(None,None,'missing'))
    with pytest.raises(ValueError,match='geometry'):
        pipeline.compute_versioned_skin_mask(None,None,None,None,'v2_complete_mouth_v1',baseline)


def test_unknown_version_rejected_before_processing():
    with pytest.raises(ValueError,match='Unsupported mask version'):
        pipeline.compute_versioned_skin_mask(None,None,None,None,'unrecorded')
