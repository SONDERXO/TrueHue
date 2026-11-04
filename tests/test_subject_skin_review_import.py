"""Synthetic-only guards against stale, partial or altered human review imports."""
import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('subject_skin_review', Path(__file__).resolve().parents[1] / 'scripts/388_import_subject_skin_review.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    row = dict(case_index=1, image_id='synthetic_image', status='ready_for_human_review', file_sha256={'input.png': 'input_hash', 'candidate_mask.png': 'mask_hash'})
    preserved = dict(case_index=2, image_id='synthetic_prior', status='prior_review_complete')
    failed = dict(case_index=3, image_id='synthetic_failure', status='parent_failed')
    manifest = dict(schema='synthetic', rows=[row, preserved, failed])
    answer = dict(case_id='case_1', image_id='synthetic_image', input_sha256='input_hash', mask_sha256='mask_hash', decisions=dict(non_skin='no', skin_loss='no', judgeable='yes'), notes='synthetic only')
    payload = dict(schema='synthetic', manifest_sha256='binding', complete=True, rows=[answer])
    return payload, manifest


def test_only_new_reviewable_rows_required():
    payload, manifest = fixture()
    original = copy.deepcopy(manifest)
    result = module.validate(payload, manifest, 'binding', verify_files=False)
    assert len(result) == 1
    assert manifest == original


@pytest.mark.parametrize('change', ['binding', 'incomplete', 'duplicate', 'mask', 'answer', 'prior_as_new'])
def test_invalid_human_evidence_rejected(change):
    payload, manifest = fixture()
    if change == 'binding': payload['manifest_sha256'] = 'old'
    elif change == 'incomplete': payload['complete'] = False
    elif change == 'duplicate': payload['rows'] *= 2
    elif change == 'mask': payload['rows'][0]['mask_sha256'] = 'other_mask'
    elif change == 'answer': payload['rows'][0]['decisions']['non_skin'] = ''
    elif change == 'prior_as_new': payload['rows'][0]['image_id'] = 'synthetic_prior'
    with pytest.raises(AssertionError):
        module.validate(payload, manifest, 'binding', verify_files=False)
