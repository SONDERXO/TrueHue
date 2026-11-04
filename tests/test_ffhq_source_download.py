"""Downloader integrity checks use fake responses; no dataset/network access."""
import hashlib
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('ffhq_source_prepare',
    Path(__file__).resolve().parents[1]/'scripts/408_prepare_ffhq_sources.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Response:
    def __init__(self, data, content_type='application/octet-stream'):
        self.data = data
        self.headers = {'Content-Type': content_type}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def raise_for_status(self): pass
    def iter_content(self, chunk_size):
        yield self.data[:2]
        yield self.data[2:]


class Session:
    def __init__(self, response): self.response = response
    def get(self, *args, **kwargs): return self.response


def test_verified_bytes_are_atomically_published(tmp_path):
    data = b'fixture-bytes'; target = tmp_path/'source.png'
    result = module.download(Session(Response(data)), 'https://example.invalid/file',
        target, len(data), hashlib.md5(data).hexdigest())
    assert result['success'] and target.read_bytes() == data
    assert result['sha256'] == hashlib.sha256(data).hexdigest()
    assert not target.with_suffix('.png.partial').exists()


@pytest.mark.parametrize('kind', ['oversize', 'short', 'checksum', 'html'])
def test_invalid_download_never_becomes_source_file(tmp_path, kind):
    data = b'fixture-bytes'; target = tmp_path/'source.png'
    size = len(data) + (1 if kind == 'short' else -1 if kind == 'oversize' else 0)
    md5 = '0'*32 if kind == 'checksum' else hashlib.md5(data).hexdigest()
    response = Response(data, 'text/html' if kind == 'html' else 'application/octet-stream')
    result = module.download(Session(response), 'https://example.invalid/file', target, size, md5)
    assert not result['success']
    assert not target.exists() and not target.with_suffix('.png.partial').exists()
