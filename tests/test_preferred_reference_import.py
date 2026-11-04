import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest


def setup_case(tmp_path,monkeypatch):
    path=Path(__file__).resolve().parents[1]/'scripts/341_import_preferred_reference_review.py'
    spec=importlib.util.spec_from_file_location('preferred_import_test',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=tmp_path;monkeypatch.setattr(module,'contract',lambda root:({},'contract'))
    folder=tmp_path/'outputs/preferred_reference_review_v1';folder.mkdir(parents=True)
    (tmp_path/'input').write_bytes(b'photo');(tmp_path/'mask').write_bytes(b'mask')
    row=dict(image_id='id',kind='new_candidate',required=['source','measurement_mask','correction_mask'],
        input_path='input',input_sha256=hashlib.sha256(b'photo').hexdigest(),mask_paths={'face':'mask'},
        mask_sha256={'face':hashlib.sha256(b'mask').hexdigest()},original_source_decision=None)
    raw=json.dumps(dict(rows=[row],measurement_contract_sha256='contract')).encode();(folder/'manifest.json').write_bytes(raw)
    export=dict(schema_version='truehue_preferred_reference_decisions_v1',manifest_sha256=hashlib.sha256(raw).hexdigest(),
        rows=[dict(image_id='id',decisions={'source':'accept','measurement_mask':'accept','correction_mask':'accept'},notes='exact notes')])
    file=tmp_path/'export.json';monkeypatch.setattr(sys,'argv',['import',str(file)])
    return module,file,export


def test_acceptance_only_admits_reference_preparation(tmp_path,monkeypatch):
    module,file,export=setup_case(tmp_path,monkeypatch);file.write_text(json.dumps(export));module.main()
    row=json.loads((tmp_path/'outputs/preferred_reference_review_import_v1/decisions.json').read_text())[0]
    assert row['reference_preparation_eligible'] and row['notes']=='exact notes'
    assert not row['training_admitted'] and not row['variant_masks_approved']


def test_source_reject_does_not_require_extra_mask_judgments(tmp_path,monkeypatch):
    module,file,export=setup_case(tmp_path,monkeypatch)
    export['rows'][0]['decisions']={'source':'reject','measurement_mask':'pending','correction_mask':'pending'}
    file.write_text(json.dumps(export));module.main()
    row=json.loads((tmp_path/'outputs/preferred_reference_review_import_v1/decisions.json').read_text())[0]
    assert not row['reference_preparation_eligible']


@pytest.mark.parametrize('fault',['duplicate','hash','incomplete','changed_mask'])
def test_invalid_exports_are_not_imported(tmp_path,monkeypatch,fault):
    module,file,export=setup_case(tmp_path,monkeypatch)
    if fault=='duplicate':export['rows']*=2
    elif fault=='hash':export['manifest_sha256']='wrong'
    elif fault=='incomplete':export['rows'][0]['decisions']['correction_mask']='pending'
    else:(tmp_path/'mask').write_bytes(b'changed')
    file.write_text(json.dumps(export))
    with pytest.raises(ValueError):module.main()
    assert not (tmp_path/'outputs/preferred_reference_review_import_v1').exists()
