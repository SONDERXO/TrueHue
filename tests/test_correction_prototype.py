import numpy as np
import pytest
from src.evaluation.correction_prototype import model_arrays,apply_correction,image_errors
from src.data_preparation.controlled_training_table import FEATURES,TARGETS


def test_matrices_use_only_declared_columns_not_numeric_provenance():
    row=dict(zip(FEATURES,[40,10,15,-30]));row.update(zip(TARGETS,[1.2,.9,1.1]))
    row.update(distortion_gamma=99,source_l_star=100,clipped_pixel_count=123)
    x,y=model_arrays([row])
    np.testing.assert_array_equal(x,[[40,10,15,-30]])
    np.testing.assert_array_equal(y,[[1.2,.9,1.1]])


def test_matrix_builder_rejects_failed_empty_vectors():
    row=dict.fromkeys(FEATURES,'');row.update(zip(TARGETS,[1,1,1]))
    with pytest.raises(ValueError):model_arrays([row])


def test_correction_uses_only_supplied_inference_mask_and_does_not_mutate():
    rgb=np.full((3,3,3),64,np.uint8);original=rgb.copy()
    mask=np.zeros((3,3),bool);mask[1,1]=True
    result=apply_correction(rgb,mask,[2,1,1])
    assert np.array_equal(rgb,original) and np.array_equal(result[~mask],original[~mask])
    assert np.all(result[mask]>original[mask])


def test_identity_and_empty_mask_leave_pixels_unchanged():
    image=np.random.default_rng(42).integers(0,256,(5,5,3),dtype=np.uint8)
    assert np.array_equal(apply_correction(image,np.ones((5,5),bool),[1,1,1]),image)
    assert np.array_equal(apply_correction(image,np.zeros((5,5),bool),[2,2,2]),image)


def test_image_metrics_use_fixed_scoring_region_and_report_outside_edits():
    reference=np.full((3,3,3),128,np.uint8);out=reference.copy()
    mask=np.zeros((3,3),bool);mask[1,1]=True
    out[~mask]=0
    metrics=image_errors(reference,out,mask)
    assert metrics['rgb_mae_source_mask']==0 and metrics['ciede2000_source_mask']==0
    assert metrics['rgb_mae_outside_source_mask']>0


def test_empty_scoring_region_rejected_instead_of_nan_metric():
    with pytest.raises(ValueError):image_errors(np.zeros((2,2,3),np.uint8),np.zeros((2,2,3),np.uint8),np.zeros((2,2),bool))
