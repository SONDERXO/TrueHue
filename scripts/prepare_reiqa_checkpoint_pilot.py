"""One bounded official checkpoint transfer; never deserialize remote pickle."""
import hashlib
import json
from pathlib import Path
import time
from html.parser import HTMLParser
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / 'reiqa_checkpoint_pilot_v1'
LIMIT = 512 * 1024 * 1024
FILE_ID = '1DYMx8omn69yXUmBFL728JD3qMLNogFt8'

class Form(HTMLParser):
    def __init__(self):
        super().__init__()
        self.params = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('type') == 'hidden':
            self.params[a['name']] = a.get('value', '')

def main():
    OUT.mkdir(exist_ok=False)
    record = {'official_file_id': FILE_ID, 'limit_bytes': LIMIT,
              'checkpoint_deserialized': False, 'status': 'STARTED'}
    started = time.monotonic()
    try:
        session = requests.Session()
        response = session.get('https://drive.google.com/uc',
            params={'export': 'download', 'id': FILE_ID}, stream=True, timeout=30)
        response.raise_for_status()
        if 'text/html' in response.headers.get('Content-Type', ''):
            page = response.content
            (OUT / 'official_download_page.html').write_bytes(page)
            parser = Form()
            parser.feed(page.decode('utf-8'))
            if parser.params.get('id') != FILE_ID or parser.params.get('confirm') != 't':
                raise RuntimeError('Official download confirmation unavailable; no fallback')
            response.close()
            response = session.get('https://drive.usercontent.google.com/download',
                params=parser.params, stream=True, timeout=60)
            response.raise_for_status()
        if 'text' in response.headers.get('Content-Type', ''):
            raise RuntimeError('Download returned text, not checkpoint; no retry')
        size = int(response.headers.get('Content-Length', 0))
        if size > LIMIT:
            raise RuntimeError('Declared checkpoint exceeds transfer bound')
        sha = hashlib.sha256()
        count = 0
        target = OUT / 'quality_aware_r50.pth.partial'
        with target.open('xb') as stream:
            for block in response.iter_content(1024 * 1024):
                count += len(block)
                if count > LIMIT or time.monotonic() - started > 600:
                    raise RuntimeError('Transfer size/time bound exceeded')
                stream.write(block)
                sha.update(block)
        response.close()
        if size and size != count:
            raise RuntimeError('Incomplete declared transfer')
        target.rename(OUT / 'quality_aware_r50.pth')
        record.update(status='TRANSFERRED_NOT_DESERIALIZED', bytes=count,
                      sha256=sha.hexdigest(), declared_bytes=size)
        license_source = ROOT / 'outputs/reiqa_feature_feasibility_v1/source/LICENSE'
        (OUT / 'REIQA_LICENSE').write_bytes(license_source.read_bytes())
    except Exception as exc:
        record.update(status='STOPPED', error=f'{type(exc).__name__}: {exc}')
    record['elapsed_seconds'] = time.monotonic() - started
    (OUT / 'transfer_PRIVATE.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
