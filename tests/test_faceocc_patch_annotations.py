import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('faceocc_patches',Path(__file__).resolve().parents[1]/'scripts/373_import_faceocc_broader_patches.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_pixel_centres_and_crossed_boundary_rejected():
    assert module.polygon_mask([[0,0],[10,0],[10,10],[0,10]]).sum()==100
    with pytest.raises(ValueError):module.polygon_mask([[0,0],[20,20],[0,20],[20,0]])
    with pytest.raises(ValueError):module.polygon_mask([[0,0],[256,0],[10,10]])


def test_conflicting_labels_and_binding_fail():
    manifest={'rows':[{'image_id':'a','image_sha256':'img'}],'technical_failures':[]}
    row=dict(image_id='a',image_sha256='img',status='gradable',notes='',
        tags={'glasses':'unknown','covering':'unknown','facial_hair':'unknown','lighting':'unknown'},
        polygons=[{'label':'skin','points':[[0,0],[10,0],[10,10],[0,10]]},
                  {'label':'object','points':[[20,20],[30,20],[30,30],[20,30]]}])
    export=dict(schema_version='truehue_faceocc_broader_patch_decisions_v1',manifest_sha256='bound',
        annotator='synthetic_fixture',rows=[row],technical_failures=[])
    assert module.validate(manifest,export,'bound')[0]['class_pixel_counts']['skin']==100
    with pytest.raises(ValueError):module.validate(manifest,export,'different')
    row['polygons'][1]['points']=[[5,5],[15,5],[15,15],[5,15]]
    with pytest.raises(ValueError):module.validate(manifest,export,'bound')
