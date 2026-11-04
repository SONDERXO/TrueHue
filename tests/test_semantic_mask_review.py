import hashlib
import json
import pytest
from src.data_preparation.semantic_mask_review import reconcile


def fixture(tmp_path):
    (tmp_path/'image').write_bytes(b'image'); (tmp_path/'mask').write_bytes(b'mask')
    row = dict(case_id='case', source_image_id='train/example', source_role='train', source_path='image', mask_path='mask',
        source_sha256=hashlib.sha256(b'image').hexdigest(), mask_sha256=hashlib.sha256(b'mask').hexdigest(),
        prior_source_decision={'decision':'accept','notes':'retained'})
    raw = json.dumps(dict(rows=[row], measurement_contract_sha256='contract')).encode()
    review = {k:row[k] for k in ('case_id','source_image_id','source_sha256','mask_sha256')}
    review.update(decision='accept',notes='only exact mask')
    export = dict(schema_version='truehue_semantic_reference_mask_decisions_v1',
        manifest_sha256=hashlib.sha256(raw).hexdigest(),measurement_contract_sha256='contract',rows=[review])
    return raw, export


def test_acceptance_does_not_approve_training_lighting_or_variants(tmp_path):
    raw, export = fixture(tmp_path)
    result = reconcile(raw, export, tmp_path, 'contract')[0]
    assert result['exact_reference_mask_accepted']
    assert not any(result[k] for k in ('training_admitted','distorted_mask_approval','reference_lighting_validated'))


@pytest.mark.parametrize('mutation', ['contract','duplicate','pending','tampered_file'])
def test_stale_incomplete_or_mismatched_review_cannot_be_imported(tmp_path, mutation):
    raw, export = fixture(tmp_path)
    if mutation == 'contract': export['measurement_contract_sha256']='old'
    elif mutation == 'duplicate': export['rows']*=2
    elif mutation == 'pending': export['rows'][0]['decision']='pending'
    else: (tmp_path/'mask').write_bytes(b'changed')
    with pytest.raises(ValueError): reconcile(raw, export, tmp_path, 'contract')
