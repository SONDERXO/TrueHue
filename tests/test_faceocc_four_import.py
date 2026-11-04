import importlib.util
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('four',Path(__file__).resolve().parents[1]/'scripts/379_import_faceocc_four_review.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_exact_four_bindings_and_valid_qualitative_values():
    manifest={'rows':[{'image_id':str(i)} for i in range(4)]}
    export=dict(schema_version='truehue_faceocc_four_decisions_v1',manifest_sha256='bound',
        rows=[dict(image_id=str(i),decisions=dict(old_unwanted='yes',new_unwanted='uncertain',useful_skin_lost='no',preference='similar'),notes='synthetic') for i in range(4)])
    assert len(module.validate(manifest,export,'bound'))==4
    with pytest.raises(ValueError):module.validate(manifest,export,'wrong')
    export['rows'][3]['image_id']='0'
    with pytest.raises(ValueError):module.validate(manifest,export,'bound')


def test_unfinished_judgments_rejected():
    manifest={'rows':[{'image_id':str(i)} for i in range(4)]}
    export=dict(schema_version='truehue_faceocc_four_decisions_v1',manifest_sha256='bound',rows=[dict(image_id=str(i),decisions=dict(old_unwanted='pending',new_unwanted='no',useful_skin_lost='no',preference='faceocc'),notes='') for i in range(4)])
    with pytest.raises(ValueError):module.validate(manifest,export,'bound')
