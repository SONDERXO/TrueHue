"""Inspect all publisher DAST examples; no image features, inference or fitting."""
import csv
import hashlib
import html
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/dast_sample_readiness_v1'
BASE = OUT / 'example/example-data'
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if (OUT / 'sample_audit.json').exists(): raise FileExistsError('Audit already saved')
    csvrows = list(csv.reader((BASE / 'example_overview.csv').open(), delimiter=';'))
    byname = {Path(r[3]).name: r for r in csvrows}
    assert len(csvrows) == len(byname) == 36
    images, measurements, cards = [], [], []
    for subject in ['001', '002', '036']:
        folder = BASE / subject
        files = sorted((folder / 'Pictures/cropped').glob('*.jpg')); assert len(files) == 12
        board = Image.new('RGB', (1200, 1080), '#eeeeee'); draw = ImageDraw.Draw(board)
        for i, path in enumerate(files):
            with Image.open(path) as im:
                im.load(); size = im.size; icc = bool(im.info.get('icc_profile')); exif = len(im.getexif())
                tile = ImageOps.contain(im.convert('RGB'), (285, 270))
            board.paste(tile, ((i % 4) * 300 + 5, (i // 4) * 360 + 40))
            row = byname.get(path.name)
            proposed = byname.get(path.name.replace('-0.jpg', '.jpg')) if row is None else None
            label = ' / '.join(row[8:11]) if row else 'CSV filename mismatch'
            draw.text(((i % 4) * 300 + 5, (i // 4) * 360 + 8), path.name, fill='black')
            draw.text(((i % 4) * 300 + 5, (i // 4) * 360 + 322), label, fill='black')
            images.append(dict(subject=subject, file=path.relative_to(OUT).as_posix(), sha256=digest(path),
                size=list(size), embedded_icc=icc, exif_entries=exif, exact_csv_match=row is not None,
                camera=row[8] if row else None, exposure=row[9] if row else None,
                proposed_minus0_filename_match=Path(proposed[3]).name if proposed else None,
                proposed_mapping_applied=False))
            cards.append('<article><h3>'+html.escape(path.name)+'</h3><img loading="lazy" src="'+path.relative_to(OUT).as_posix()+'"><p>'+html.escape(label)+'</p></article>')
        board.save(OUT / (subject + '_contact.png'))
        cmf = folder / 'Colorimeter' / (subject + '.cmf')
        lines = cmf.read_text(encoding='utf-8-sig').splitlines()
        start = next(i for i, line in enumerate(lines) if line.split('\t')[0].strip() == 'Label')
        table = csv.DictReader(io.StringIO('\n'.join(lines[start:])), delimiter='\t')
        rows = [{str(k).strip(): v for k, v in row.items() if k is not None} for row in table]
        rows = [r for r in rows if r.get('Label', '').strip()]
        assert len(rows) == 5
        for row in rows:
            lab = np.array([float(row[k]) for k in ['CIE-L*', 'CIE-a*', 'CIE-b*']])
            xyz = np.array([float(row[k]) for k in ['X', 'Y', 'Z']])
            def residual(white):
                values = xyz / np.array(white); delta = 6 / 29
                values = np.where(values > delta**3, np.cbrt(values), values / (3*delta**2) + 4/29)
                rebuilt = np.array([116*values[1]-16, 500*(values[0]-values[1]), 200*(values[1]-values[2])])
                return float(np.max(np.abs(rebuilt-lab)))
            measurements.append(dict(subject=subject, raw_label=row['Label'], Lab=lab.tolist(), XYZ=xyz.tolist(),
                D65_2degree_max_abs_Lab_residual=residual([95.047, 100, 108.883]),
                D65_10degree_max_abs_Lab_residual=residual([94.811, 100, 107.304]),
                observer_independently_verified=False, target_admitted=False))
    assert len(images) == 36 and len(measurements) == 15
    report = dict(images=images, measurements=measurements,
        counts=dict(subjects=3, images=36, measurement_rows=15, exact_csv_matches=sum(r['exact_csv_match'] for r in images),
                    csv_rows_with_blank_camera_or_exposure=sum(not r[8] or not r[9] for r in csvrows)),
        caution='Instrument consistency is not observer certification or skin-image colour accuracy; no silent filename repairs',
        mst_available=False, inference=0, calibration_fits=0, tree_fits=0, training_admitted=False)
    (OUT / 'sample_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (OUT / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>DAST public sample inspection</title><style>body{font:17px/1.5 system-ui;max-width:1300px;margin:auto;padding:20px}article{display:inline-block;vertical-align:top;width:30%;margin:1%}img{max-width:100%}</style><h1>DAST: all 36 publisher example portraits</h1><p>Three people, twelve examples each. Inspection only; no training admission, MST labels or true-colour guarantee. JPEG examples lack embedded ICC/EXIF. Filename mismatches are shown without applying repairs.</p><p>Source: <a href="https://github.com/dasec/DAST-SkinTone-database">Busch, Kibler, Stockhardt and Rathgeb, DAST</a>. Full release/recipient permissions need clarification. All archive portraits retained; no selection by appearance.</p>'+''.join(cards), encoding='utf-8')
    print(json.dumps(report['counts'], indent=2))
    print('Maximum Lab component residual for D65/2degree and D65/10degree:',
          max(r['D65_2degree_max_abs_Lab_residual'] for r in measurements),
          max(r['D65_10degree_max_abs_Lab_residual'] for r in measurements))


if __name__ == '__main__': main()
