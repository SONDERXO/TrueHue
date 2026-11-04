import copy
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('readiness_r1', Path(__file__).resolve().parents[1] / 'scripts/357_import_reference_readiness_r1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    fields = ['lighting', 'measurement', 'correction', 'facial_hair', 'covering', 'contamination']
    manifest = {'rows': [dict(image_id='a', required=fields, source_retained=True,
                             original_source_decision={'decision': 'accept', 'notes': 'retained'})]}
    export = dict(schema_version='truehue_reference_readiness_r1_decisions', manifest_sha256='bound',
        rows=[dict(image_id='a', decisions=dict(lighting='unknown', measurement='accept',
            correction='accept', facial_hair='present', covering='absent', contamination='absent'), notes='')])
    return manifest, export


def test_hair_presence_does_not_equal_contamination_or_true_colour():
    manifest, export = fixture()
    row = module.validate(manifest, export, 'bound')[0]
    assert row['photographic_candidate']
    assert not row['training_admitted'] and not row['true_skin_colour_validated']
    export['rows'][0]['decisions']['contamination'] = 'present'
    assert not module.validate(manifest, export, 'bound')[0]['photographic_candidate']


def test_wrong_binding_duplicate_and_missing_decisions_rejected():
    manifest, export = fixture()
    with pytest.raises(ValueError):
        module.validate(manifest, export, 'changed')
    duplicate = copy.deepcopy(export)
    duplicate['rows'] *= 2
    with pytest.raises(ValueError):
        module.validate(manifest, duplicate, 'bound')
    export['rows'][0]['decisions']['measurement'] = 'pending'
    with pytest.raises(ValueError):
        module.validate(manifest, export, 'bound')


def test_lighting_claim_requires_evidence_and_does_not_verify_it():
    manifest, export = fixture()
    export['rows'][0]['decisions']['lighting'] = 'documented'
    with pytest.raises(ValueError):
        module.validate(manifest, export, 'bound')
    export['rows'][0]['notes'] = 'Reference to capture record'
    row = module.validate(manifest, export, 'bound')[0]
    assert row['lighting_evidence_claimed'] and not row['independent_lighting_verified']
