"""Bounded byte-range metadata and one exact official model member; no images."""
import io, json, re, zipfile, hashlib, argparse
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/ppr_parameter_access_v1'
ARCHIVE_ID = '1OIxGfPGMTXB_j1zeos15ZzSMeTr56bAG'
MEMBER = 'pretrained_models/mask_noglc_a/classifier_-1.pth'
CAP = 64 * 1024 * 1024


class Ranges(io.RawIOBase):
    def __init__(self):
        self.session = requests.Session(); self.params = {'id': ARCHIVE_ID, 'export': 'download'}
        self.pos = self.transferred = 0; self.size = None
        first, meta = self.request('bytes=-65536', allow_form=True)
        if meta['status'] == 200:
            params = dict(re.findall(r'name="([^"]+)" value="([^"]*)"', first.decode('utf-8')))
            if params.get('id') != ARCHIVE_ID or 'confirm' not in params:
                raise ValueError('Expected official public download confirmation')
            self.params = params
            first, meta = self.request('bytes=-65536')
        self.size = int(meta['content_range'].split('/')[-1])
        self.initial_metadata = meta

    def request(self, byte_range, allow_form=False):
        r = self.session.get('https://drive.usercontent.google.com/download', params=self.params,
                             headers={'Range': byte_range}, timeout=(8, 20), stream=True)
        try:
            if r.status_code == 200 and allow_form and 'text/html' in r.headers.get('content-type', ''):
                r.raw.decode_content = True; data = r.raw.read(65537)
                if len(data) > 65536: raise ValueError('Confirmation page exceeds cap')
            elif r.status_code == 206:
                expected = int(r.headers['Content-Length'])
                if expected > CAP - self.transferred: raise ValueError('Transfer cap exceeded')
                data = r.raw.read(expected + 1)
                if len(data) != expected: raise ValueError('Incomplete/oversized byte range')
            else:
                raise ValueError('Range unavailable or ignored: HTTP' + str(r.status_code))
            self.transferred += len(data)
            if self.transferred > CAP: raise ValueError('Transfer cap exceeded')
            return data, {'status': r.status_code, 'content_range': r.headers.get('Content-Range'),
                          'content_type': r.headers.get('Content-Type'), 'bytes': len(data)}
        finally:
            r.close()

    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos
    def read(self, size=-1):
        if size < 0: size = self.size - self.pos
        size = min(size, self.size - self.pos)
        if size <= 0: return b''
        start = self.pos; data, meta = self.request(f'bytes={start}-{start+size-1}')
        if meta['content_range'] != f'bytes {start}-{start+size-1}/{self.size}':
            raise ValueError('Unexpected range binding')
        self.pos += size
        return data


def main(retrieve=False):
    receipt = OUT / ('checkpoint_receipt.json' if retrieve else 'archive_metadata.json')
    if receipt.exists() or (retrieve and (OUT / 'classifier_-1.pth').exists()):
        raise FileExistsError('Refusing existing attempt')
    remote = Ranges()
    with zipfile.ZipFile(remote) as archive:
        listing = [dict(name=i.filename, size=i.file_size, compressed=i.compress_size, crc=i.CRC)
                   for i in archive.infolist()]
        if remote.transferred > 1024 * 1024: raise ValueError('Metadata exceeds1MiB')
        matches = [i for i in archive.infolist() if i.filename == MEMBER]
        if len(matches) != 1: raise ValueError('Exact default member absent/ambiguous')
        selected = matches[0]
        if selected.file_size > CAP or selected.compress_size + remote.transferred > CAP:
            raise ValueError('Selected checkpoint exceeds cap')
        payload = archive.read(selected) if retrieve else None  # ZIP CRC verified by stdlib.
    record = dict(official_archive_id=ARCHIVE_ID, archive_bytes=remote.size, transferred=remote.transferred,
                  selected_member=MEMBER, entries=listing, metadata_only=not retrieve, models_executed=0,
                  images=0, trained_models=0, checkpoint_bytes=None if payload is None else len(payload),
                  checkpoint_sha256=None if payload is None else hashlib.sha256(payload).hexdigest())
    if payload is not None:
        with (OUT / 'classifier_-1.pth').open('xb') as f: f.write(payload)
    with receipt.open('x', encoding='utf-8') as f: json.dump(record, f, indent=2); f.write('\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--retrieve', action='store_true')
    try:
        main(parser.parse_args().retrieve)
    except Exception as exc:
        p = OUT / 'archive_attempt_failure.json'
        if not p.exists(): p.write_text(json.dumps({'error': repr(exc), 'models_executed': 0, 'trained_models': 0}) + '\n')
        raise
