from copy import deepcopy
import numpy as np
import pytest
from src.evaluation.reference_point_review import validate_export,compare_points

def fixture():
    manifest={'rows':[dict(review_id='r1',image_sha256='a'*64,width=4,height=3),dict(review_id='r2',image_sha256='b'*64,width=4,height=3)]}
    value=dict(schema_version='truehue_native_reference_points_v1',manifest_sha256='c'*64,reviewer='SYNTHETIC TEST',rows=[
        dict(review_id='r1',image_sha256='a'*64,status='marked',notes='',points=[dict(x=1,y=1,label='skin'),dict(x=2,y=1,label='hair_or_beard'),dict(x=0,y=0,label='uncertain')]),
        dict(review_id='r2',image_sha256='b'*64,status='cannot_judge',notes='Synthetic dark/unjudgeable fixture',points=[])])
    return manifest,value

def test_sparse_agreement_excludes_uncertain_and_does_not_create_admission():
    manifest,value=fixture();before=deepcopy(value);rows=validate_export(value,manifest,'c'*64)
    mask=np.zeros((3,4),bool);mask[1,1]=True;mask[1,2]=True
    result=compare_points(rows,{'r1':mask,'r2':None})
    assert result['summary']['skin_point_inclusion']==1
    assert result['summary']['unwanted_point_inclusion']==1
    assert result['summary']['uncertain_excluded']==1
    assert result['summary']['calibration_admissions']==0 and not result['summary']['segmentation_accuracy']
    assert value==before

def test_failed_prediction_is_unavailable_not_negative_or_zero_error():
    manifest,value=fixture();rows=validate_export(value,manifest,'c'*64)
    result=compare_points(rows,{'r1':None,'r2':None})
    assert result['summary']['definite_unavailable']==2
    assert result['summary']['skin_point_inclusion'] is None and result['summary']['unwanted_point_inclusion'] is None
    assert all(p['predicted_selected'] is None for p in result['points'])

@pytest.mark.parametrize('change',[
    lambda v:v.update(manifest_sha256='d'*64),
    lambda v:v.update(reviewer=' '),
    lambda v:v['rows'].pop(),
    lambda v:v['rows'].__setitem__(1,deepcopy(v['rows'][0])),
    lambda v:v['rows'][0].update(image_sha256='d'*64),
    lambda v:v['rows'][0].update(review_id=['r1']),
    lambda v:v['rows'][0]['points'][0].update(x=True),
    lambda v:v['rows'][0]['points'][0].update(x=1.5),
    lambda v:v['rows'][0]['points'][0].update(x=4),
    lambda v:v['rows'][0]['points'][0].update(y=-1),
    lambda v:v['rows'][0]['points'][0].update(label=[]),
    lambda v:v['rows'][0]['points'].append(dict(x=1,y=1,label='object_or_other')),
    lambda v:v['rows'][0].update(points=[dict(x=0,y=0,label='uncertain')]),
    lambda v:v['rows'][1].update(notes=''),
    lambda v:v['rows'][1].update(points=[dict(x=0,y=0,label='skin')]),
    lambda v:v.update(source_mst=5),
])
def test_strict_import_rejects_wrong_binding_membership_native_points_and_fake_completeness(change):
    manifest,value=fixture();change(value)
    with pytest.raises(ValueError):validate_export(value,manifest,'c'*64)

def test_cannot_judge_can_preserve_uncertain_points_and_partial_labels_are_allowed():
    manifest,value=fixture()
    value['rows'][0]['points']=[dict(x=0,y=0,label='skin')]
    value['rows'][1]['points']=[dict(x=2,y=2,label='uncertain')]
    assert len(validate_export(value,manifest,'c'*64))==2
