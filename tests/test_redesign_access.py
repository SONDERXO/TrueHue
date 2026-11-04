from copy import deepcopy
import pytest
from src.data_preparation.redesign_access import training_candidate


def example():
    manifest={'selected':[dict(image_id=role,role=role,original_split='train' if role!='final_test' else 'validation',relative_image_path='data/raw/example.jpg',eligibility='unreviewed_candidate') for role in ['train','development_validation','final_test']]}
    policy=dict(permitted_current_role='train',locked_roles=['development_validation','final_test'],automatic_unlock=False)
    return manifest,policy


def test_training_copy_does_not_change_frozen_manifest():
    manifest,policy=example();before=deepcopy(manifest)
    selected=training_candidate('train',manifest,policy);selected['role']='final_test'
    assert manifest==before


@pytest.mark.parametrize('role',['development_validation','final_test'])
def test_locked_candidates_never_authorized_for_preparation(role):
    manifest,policy=example()
    with pytest.raises(PermissionError):training_candidate(role,manifest,policy)


@pytest.mark.parametrize('path',['../outside.jpg','C:/outside.jpg','C:outside.jpg','//server/share/image.jpg'])
def test_nonworkspace_paths_rejected(path):
    manifest,policy=example();manifest['selected'][0]['relative_image_path']=path
    with pytest.raises(ValueError):training_candidate('train',manifest,policy)


def test_unknown_duplicate_and_original_validation_rows_rejected():
    manifest,policy=example()
    with pytest.raises(ValueError):training_candidate('unknown',manifest,policy)
    manifest['selected'][0]['original_split']='validation'
    with pytest.raises(ValueError):training_candidate('train',manifest,policy)
    manifest['selected'].append(deepcopy(manifest['selected'][0]))
    with pytest.raises(ValueError):training_candidate('train',manifest,policy)


def test_policy_cannot_silently_open_validation_phase():
    manifest,policy=example();policy['permitted_current_role']='development_validation'
    with pytest.raises(ValueError):training_candidate('development_validation',manifest,policy)
