from types import SimpleNamespace
import json
import cv2
import numpy as np
import pytest
from src.demo.service import read_photo,plain_failure,analyze_photo,save_run,skin_overlay


def test_saved_manifest_binds_images_report_and_captured_run_identity(tmp_path,monkeypatch):
    import hashlib
    import src.demo.service as service
    path=photo(tmp_path)
    result=SimpleNamespace(report=dict(status='development_experimental_mst',measurement=dict(status='success')),
        image=np.full((20,20,3),100,np.uint8),mask=np.full((20,20),255,np.uint8),corrected=np.full((20,20,3),120,np.uint8))
    provenance={'tree_sha256':'test-tree','lookup_sha256':'test-lookup','nested':{'held_fold':1}}
    run=analyze_photo(path,SimpleNamespace(run=lambda im:result),provenance)
    provenance['nested']['held_fold']=9
    monkeypatch.setitem(service.PRESET,'experiment','later-unrelated-setting')
    first=save_run(run,tmp_path);second=save_run(run,tmp_path)
    for folder in [first,second]:
        report=json.loads((folder/'report.json').read_text())
        manifest=json.loads((folder/'manifest.json').read_text())
        assert report['demo']['preset']['experiment']=='baseline5'
        assert report['provenance']['nested']['held_fold']==1
        assert manifest['run_id']==report['demo']['run_id']==run.run_id
        assert set(manifest['files'])=={p.name for p in folder.iterdir() if p.name!='manifest.json'}
        for name,evidence in manifest['files'].items():
            assert evidence=={'sha256':hashlib.sha256((folder/name).read_bytes()).hexdigest(),'bytes':(folder/name).stat().st_size}
    assert first!=second


def photo(tmp_path):
    path=tmp_path/'photo.png';assert cv2.imwrite(str(path),np.full((20,20,3),100,np.uint8))
    return path


def test_corrupt_file_rejected_before_pipeline(tmp_path):
    path=tmp_path/'bad.png';path.write_bytes(b'not an image')
    with pytest.raises(ValueError,match='could not be opened'):read_photo(path)


def test_failure_messages_distinguish_zero_and_multiple_faces():
    assert 'No clear face' in plain_failure(dict(failed_stage='face_detection',measurement=dict(face_count=0)))
    assert 'More than one' in plain_failure(dict(failed_stage='face_detection',measurement=dict(face_count=2)))
    assert 'Too little' in plain_failure(dict(failed_stage='measurement'))


def test_failed_result_cannot_export_partial_or_stale_correction(tmp_path):
    path=photo(tmp_path);original=path.read_bytes()
    result=SimpleNamespace(report=dict(status='failed',failed_stage='face_detection',measurement=dict(face_count=0)),
        image=np.full((20,20,3),100,np.uint8),mask=None,corrected=np.zeros((20,20,3),np.uint8))
    pipeline=SimpleNamespace(run=lambda im:result)
    run=analyze_photo(path,pipeline,{})
    assert not run.success and run.result.corrected is None
    folder=save_run(run,tmp_path)
    assert (folder/'report.json').is_file() and not (folder/'experimental_correction.png').exists()
    assert path.read_bytes()==original


def test_success_preserves_report_and_mask_support_in_overlay(tmp_path):
    path=photo(tmp_path);image=np.full((20,20,3),100,np.uint8);mask=np.zeros((20,20),np.uint8);mask[:5,:5]=255
    result=SimpleNamespace(report=dict(status='development_experimental_mst',experimental=True,quality_gate_passed=False,measurement=dict(status='success')),
        image=image,mask=mask,corrected=image.copy())
    run=analyze_photo(path,SimpleNamespace(run=lambda im:result),dict(experiment='test'))
    overlay=skin_overlay(run);np.testing.assert_array_equal(overlay[mask==0],image[mask==0])
    assert not np.array_equal(overlay[mask>0],image[mask>0])
    a=save_run(run,tmp_path);b=save_run(run,tmp_path)
    assert a!=b and (a/'experimental_correction.png').exists()
    report=json.loads((a/'report.json').read_text())
    assert report['experimental'] is True and report['quality_gate_passed'] is False


def test_failed_mask_is_not_shown_as_valid_green_skin(tmp_path):
    image=np.full((20,20,3),100,np.uint8)
    result=SimpleNamespace(report=dict(status='failed',measurement=dict(status='failed')),
        image=image,mask=np.full((20,20),255,np.uint8),corrected=None)
    run=analyze_photo(photo(tmp_path),SimpleNamespace(run=lambda im:result),{})
    assert skin_overlay(run) is None
