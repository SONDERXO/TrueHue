"""Offline safety checks for inspecting external checkpoints without execution."""
import importlib.util
from pathlib import Path
import zipfile
import pickle
import pytest

spec=importlib.util.spec_from_file_location('cpm_preflight',Path(__file__).parents[1]/'scripts/110_preflight_cpm_pattern.py')
preflight=importlib.util.module_from_spec(spec);spec.loader.exec_module(preflight)

def test_pickle_reduce_is_described_without_being_executed(tmp_path):
    # Evaluating this pickle would raise ZeroDivisionError. Opcode inspection must not.
    path=tmp_path/'model.pth'
    with zipfile.ZipFile(path,'w') as archive:archive.writestr('archive/data.pkl',b"cbuiltins\neval\n(V1/0\ntR.")
    result=preflight.static_archive(path)
    assert result['status']=='static_archive_inspected_no_model_load'
    assert result['serialized_globals']==['builtins eval']
    assert result['model_deserialized'] is False and result['tensor_inference'] is False

def test_non_zip_is_retained_without_pickle_loading(tmp_path):
    path=tmp_path/'legacy.pth';path.write_bytes(b"cbuiltins\neval\n(V1/0\ntR.")
    assert preflight.static_archive(path)['status']=='unsupported_non_zip_no_unpickling_attempted'

@pytest.mark.parametrize('members',[['a/data.pkl','b/data.pkl'],['tensor_only']])
def test_ambiguous_or_absent_pickle_member_is_rejected(tmp_path,members):
    path=tmp_path/'model.pth'
    with zipfile.ZipFile(path,'w') as archive:
        for name in members:archive.writestr(name,b'N.')
    with pytest.raises(ValueError,match='one bounded'):preflight.static_archive(path)

class Response:
    def __init__(self,kind='application/octet-stream',length=None,body=b'x'*2048):
        self.headers={'Content-Type':kind};self.body=body
        if length is not None:self.headers['Content-Length']=str(length)
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):chunk=self.body[:n];self.body=self.body[n:];return chunk
    def geturl(self):return 'https://example.invalid/public-checkpoint'

@pytest.mark.parametrize('response,reason',[
    (Response(kind='text/html',body=b'<html>confirmation</html>'),'HTML'),
    (Response(length=preflight.MAX_BYTES+1),'exceeds256MiB')])
def test_interstitial_and_oversized_header_never_create_model(tmp_path,monkeypatch,response,reason):
    monkeypatch.setattr(preflight.urllib.request,'urlopen',lambda *args,**kwargs:response)
    target=tmp_path/'pattern.pth'
    with pytest.raises(ValueError,match=reason):preflight.download(target)
    assert not target.exists() and not target.with_suffix('.part').exists()

def test_unannounced_stream_overflow_never_promotes_partial(tmp_path,monkeypatch):
    monkeypatch.setattr(preflight,'MAX_BYTES',1024)
    monkeypatch.setattr(preflight.urllib.request,'urlopen',lambda *args,**kwargs:Response())
    target=tmp_path/'pattern.pth'
    with pytest.raises(ValueError,match='Stream exceeds'):preflight.download(target)
    assert not target.exists() and target.with_suffix('.part').exists()

def test_existing_partial_is_not_overwritten(tmp_path):
    target=tmp_path/'pattern.pth';partial=target.with_suffix('.part');partial.write_bytes(b'prior attempt')
    with pytest.raises(FileExistsError):preflight.download(target)
    assert partial.read_bytes()==b'prior attempt'

legacy_spec=importlib.util.spec_from_file_location('cpm_legacy',Path(__file__).parents[1]/'scripts/111_inspect_cpm_legacy_metadata.py')
legacy=importlib.util.module_from_spec(legacy_spec);legacy_spec.loader.exec_module(legacy)

def legacy_bytes(magic=legacy.MAGIC):
    headers=b''.join(pickle.dumps(v,protocol=2) for v in [magic,1001,{'protocol_version':1001}])
    return headers+b"cbuiltins\neval\n(V1/0\ntR."+pickle.dumps([],protocol=2)

def test_legacy_metadata_stops_before_opaque_storage_and_does_not_execute_reduce(tmp_path):
    metadata=legacy_bytes();path=tmp_path/'old.pth';path.write_bytes(metadata+b'opaque-storage-not-pickle')
    result=legacy.inspect_metadata(path)
    assert result['metadata_end']==len(metadata)
    assert result['opaque_remaining_bytes']==len(b'opaque-storage-not-pickle')
    assert result['streams'][3]['serialized_globals']==['builtins eval']
    assert not result['model_deserialized'] and not result['serialized_globals_imported']

def test_legacy_invalid_magic_and_truncated_metadata_fail_closed(tmp_path):
    path=tmp_path/'old.pth';path.write_bytes(legacy_bytes(magic=1))
    with pytest.raises(ValueError,match='expected torch legacy header'):legacy.inspect_metadata(path)
    path.write_bytes(legacy_bytes()[:20])
    with pytest.raises(ValueError):legacy.inspect_metadata(path)
