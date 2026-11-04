"""Bounded publisher PPR10K inspection, using ZIP byte ranges; no model fitting."""
import hashlib
import html
import io
import json
from pathlib import Path
import re
import sys
import zipfile

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/ppr10k_inspection_v1'
IDS = {'source': '1Bt_ishGRgIMSQVCCED4XfeTNI0KAQFU4',
       'target_a': '1Yqtop2r4yyE09u9PCijYR4URwYkp8hof'}
REV = '239490b8a8e917f2c29e3016ee2f6543c3c1bfba'


class RemoteZip(io.RawIOBase):
    def __init__(self, key):
        response = requests.get('https://drive.usercontent.google.com/download',
            params={'id': IDS[key], 'export': 'download'},
            headers={'Range': 'bytes=-128'}, timeout=45)
        response.raise_for_status()
        page = response.text
        if 'name="confirm"' not in page:
            raise ValueError('Expected publisher download confirmation form')
        (OUT / (key + '-access.bin')).write_text(page, encoding='utf8')
        self.params = dict(re.findall(r'name="([^"]+)" value="([^"]*)"', page))
        self.session = requests.Session()
        self.pos = 0
        response = self.session.get('https://drive.usercontent.google.com/download',
            params=self.params, headers={'Range': 'bytes=-128'}, timeout=45)
        response.raise_for_status()
        assert response.status_code == 206
        self.size = int(response.headers['Content-Range'].split('/')[-1])
        self.transferred = len(response.content)

    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def read(self, size=-1):
        if size < 0: size = self.size - self.pos
        size = min(size, self.size - self.pos)
        if size <= 0: return b''
        if size > 4_000_000: raise ValueError('Bounded transfer exceeded')
        start, end = self.pos, self.pos + size - 1
        response = self.session.get('https://drive.usercontent.google.com/download',
            params=self.params, headers={'Range': f'bytes={start}-{end}'}, timeout=45)
        response.raise_for_status()
        assert response.status_code == 206
        assert response.headers['Content-Range'].startswith(f'bytes {start}-{end}/')
        assert len(response.content) == size
        self.pos += size
        self.transferred += size
        return response.content


def inventory():
    if (OUT / 'inventory.json').exists(): raise FileExistsError('Inventory already frozen')
    inventories = {}
    for key in IDS:
        remote = RemoteZip(key)
        with zipfile.ZipFile(remote) as archive:
            rows = [dict(name=x.filename, size=x.file_size, compressed=x.compress_size,
                         crc=x.CRC) for x in archive.infolist() if x.filename.endswith('.tif')]
        inventories[key] = dict(archive_id=IDS[key], archive_bytes=remote.size,
                                entries=rows, transferred=remote.transferred)
    path = OUT / 'inventory.json'
    if path.exists(): raise FileExistsError(path)
    path.write_text(json.dumps(inventories, indent=2), encoding='utf8')
    sources = {Path(x['name']).stem for x in inventories['source']['entries']}
    targets = {Path(x['name']).stem for x in inventories['target_a']['entries']}
    common = sources & targets
    groups = sorted({x.split('_')[0] for x in common},
                    key=lambda x: hashlib.sha256(('TrueHue-PPR10K-v1:' + x).encode()).hexdigest())
    # Two groups, first three numeric frame IDs each, fixed before any pixel decoding.
    selected = []
    for group in groups[:2]:
        frames = sorted((x for x in common if x.split('_')[0] == group),
                        key=lambda x: int(x.split('_')[1]))[:3]
        selected.extend(frames)
    plan = dict(revision=REV, editor='a', groups=groups[:2], frames=selected,
        rule='Two SHA256-ranked common group IDs; first three numeric frame IDs per group; no replacements',
        source='unaugmented source.zip', common_frames=len(common),
        notes='Development feasibility only. No subject independence, MST, skin masks or true colour assumed.',
        training=False, calibration=False, operator_fitting=False)
    (OUT / 'frozen_sample.json').write_text(json.dumps(plan, indent=2), encoding='utf8')
    print(json.dumps(plan, indent=2))


def acquire():
    from PIL import Image, ImageDraw, ImageOps
    import tifffile
    import numpy as np
    if (OUT / 'image_audit.json').exists(): raise FileExistsError('Image audit already saved')
    plan = json.loads((OUT / 'frozen_sample.json').read_text())
    report = []
    for key in IDS:
        remote = RemoteZip(key)
        with zipfile.ZipFile(remote) as archive:
            names = {Path(x).stem: x for x in archive.namelist() if x.endswith('.tif')}
            for frame in plan['frames']:
                relative = Path('originals') / key / (frame + '.tif')
                path = OUT / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists(): data = path.read_bytes()
                else:
                    data = archive.read(names[frame])  # zipfile verifies CRC
                    path.write_bytes(data)
                with tifffile.TiffFile(io.BytesIO(data)) as tif:
                    page = tif.pages[0]
                    arr = page.asarray()
                    icc = page.tags.get(34675)
                    profile = icc.value if icc else b''
                    record = dict(frame=frame, role=key, file=relative.as_posix(),
                        sha256=hashlib.sha256(data).hexdigest(), archive_member=names[frame],
                        shape=list(arr.shape), dtype=str(arr.dtype),
                        photometric=str(page.photometric), embedded_icc_bytes=len(profile),
                        icc_sha256=hashlib.sha256(profile).hexdigest() if profile else None,
                        bits_per_sample=page.bitspersample)
                assert arr.ndim == 3 and arr.shape[2] == 3
                # Viewing copies only; retain original RGB16 data unchanged.
                view = (arr.astype(np.float64) / 257).round().astype('uint8') if arr.dtype == np.uint16 else arr
                image = Image.fromarray(view)
                preview = OUT / f'{key}_{frame}.png'
                image.save(preview)
                record['preview'] = preview.name
                report.append(record)
        print(key, 'bytes transferred', remote.transferred)
    for frame in plan['frames']:
        board = Image.new('RGB', (1100, 620), 'white')
        draw = ImageDraw.Draw(board)
        for index, key in enumerate(IDS):
            image = Image.open(OUT / f'{key}_{frame}.png')
            image = ImageOps.contain(image, (540, 570))
            board.paste(image, (index * 550, 40))
            draw.text((index * 550 + 8, 10), key + ' / ' + frame, fill='black')
        board.save(OUT / f'pair_{frame}.png')
    (OUT / 'image_audit.json').write_text(json.dumps(report, indent=2), encoding='utf8')
    cards = ''.join(f'<h2>{html.escape(f)}</h2><img src="pair_{f}.png">' for f in plan['frames'])
    (OUT / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>PPR10K fixed sample</title>'
        '<style>body{font:18px system-ui;max-width:1120px;margin:30px auto}img{width:100%}</style>'
        '<h1>PPR10K fixed sample — assistant inspection</h1><p>Left: source; right: editor a. '
        'Viewing copies only. Two groups are not verified different people. No skin masks, MST, '
        'training, fitting or true-colour claims.</p>' + cards, encoding='utf8')


if __name__ == '__main__':
    {'inventory': inventory, 'acquire': acquire}[sys.argv[1]]()
