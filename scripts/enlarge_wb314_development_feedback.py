"""Export larger scientific viewing copies by exact integer pixel repetition.

This presentation-only export preserves every native RGB value. It never loads
the predictor, source portraits or masks and does not infer high-resolution skin
detail. Native releases and prior receipts remain unchanged.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import shutil
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/wb314-expert-development-round1-2026-11-19'
PARENT = ROOT / 'outputs/wb314_mste_development_round1_release_v1'
OUT = ROOT / 'outputs/wb314_development_feedback_large_v1'
DELIVERY = ROOT / 'output/wb314-expert-development-round1-large-2026-11-19'
SCALE = 4


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)
def embedded(p): return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode('ascii')


def main():
    if OUT.exists() or DELIVERY.exists(): raise FileExistsError('Preserve previous presentation exports')
    parent = read(PARENT / 'verification.json'); assert parent['passed']
    for path, digest in parent['artifacts'].items(): assert sha(SOURCE / path) == digest
    rows = read(PARENT / 'release_manifest_PRIVATE.json')['cases']; assert len(rows) == 20
    status = read(SOURCE / 'ROUND_STATUS.json')
    OUT.mkdir(); DELIVERY.mkdir(); (DELIVERY / 'pairs').mkdir(); (DELIVERY / 'native-pairs').mkdir()
    records = []; sections = []; shapes = []
    for i, row in enumerate(rows, 1):
        assert row['pair'] == i and row['MST'] == (i+1)//2
        path = SOURCE / row['filename']; assert sha(path) == row['sha256']
        with Image.open(path) as im:
            assert im.mode == 'RGB'; native = np.asarray(im).copy()
        assert native.ndim == 3 and native.shape[1] % 2 == 0
        # Exact block replication: no interpolation, sharpening or synthesis.
        large = np.repeat(np.repeat(native, SCALE, axis=0), SCALE, axis=1)
        target = DELIVERY / 'pairs' / path.name
        Image.fromarray(large).save(target)
        copied = DELIVERY / 'native-pairs' / path.name
        shutil.copyfile(path, copied); assert copied.read_bytes() == path.read_bytes()
        with Image.open(target) as im:
            pixels = np.asarray(im)
            assert np.array_equal(pixels, large)
            assert np.array_equal(pixels[::SCALE, ::SCALE], native)
            for dy in range(SCALE):
                for dx in range(SCALE): assert np.array_equal(pixels[dy::SCALE, dx::SCALE], native)
        h, w = native.shape[:2]; shapes.append((w//2, h))
        records.append(dict(**row, native_filename='native-pairs/'+path.name,
            enlarged_filename='pairs/'+path.name, native_size=[w,h], enlarged_size=[w*SCALE,h*SCALE],
            enlarged_sha256=sha(target), native_sha256=sha(copied), exact_all16_pixel_offsets=True))
        sections.append(f'<section><h2>{html.escape(row["Form_section"])}</h2>'
            '<p><strong>Original reference (left) | Model-corrected result (right)</strong></p>'
            '<p>4× viewing copy. Each original pixel is shown as a4×4block; no new detail is added.</p>'
            f'<p>Form upload: <code>pairs/{path.name}</code></p><div class="viewport">'
            f'<img width="{w*SCALE}" height="{h*SCALE}" src="{embedded(target)}" alt="Enlarged reference and corrected face"></div>'
            '<details><summary>Show unchanged native-size comparison</summary>'
            f'<img width="{w}" height="{h}" src="{embedded(copied)}" alt="Native reference and corrected face"></details></section>')
    note = ('These are larger viewing copies of the same released V2 results. The original output uses256px whole-frame analysis; '
        'its cropped faces are70–128pixels wide. Enlargement makes existing pixels easier to inspect but cannot recover missing skin texture. '
        'Both sides receive the same exact4×pixel repetition. No interpolation, sharpening, smoothing, AI enhancement or new correction was applied. '
        'Original reference means the normalized/cropped dataset photograph before our synthetic distortion. The right side is the correction of its distorted copy.')
    context = ('Initial development feedback:20pairs,13previously exposed people, two pairs per publisher MST1–10. '
        'Existing questions, consent, evaluator fields, overall1–5scale and comments stay unchanged. '
        'Keep this presentation fixed during the round. Record the4×viewing scale and native256px analysis limitation. '
        'Known approximate masks and preserved full-frame backgrounds remain limitations; this enlargement does not repair them. '
        'There are no supplied professional ratings or final independent validation.')
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>WB314 V2: larger expert comparisons</title><style>'
        'body{font:18px system-ui;max-width:1150px;margin:24px auto;padding:0 20px;color:#222}'
        'section{border-top:1px solid #aaa;margin:32px 0;padding:12px 0}.viewport{overflow-x:auto}'
        'img{display:block;max-width:none;image-rendering:pixelated}details{margin:16px 0}summary{cursor:pointer}'
        '.note{background:#edf3f7;padding:16px}code{overflow-wrap:anywhere}</style>'
        '<h1>Larger expert comparisons — WB314 V2</h1><div class="note"><p>' + html.escape(note) + '</p></div>'
        '<p>Each pair comes from one dataset photograph. Left: original photographic target. '
        'Right: the model’s repair of a synthetically exposure/colour-distorted copy. The distorted input is not shown in these pairs.</p>'
        '<p>Use the20PNGs in <code>pairs/</code> for the existing Form sections listed below. '
        'The Form has not been updated automatically. On narrow screens, scroll each image sideways to keep it large.</p>'
        '<p>' + html.escape(context) + '</p>' + ''.join(sections))
    (DELIVERY / 'START_HERE.html').write_text(page, encoding='utf-8')
    (DELIVERY / 'README.txt').write_text('WB314 V2 — larger expert viewing copies\n\n'+note+'\n\n'+context+
        '\n\nOpen START_HERE.html to inspect the enlarged pairs and expand the native comparisons. '
        'Upload only the20PNGs from pairs/ to matching existing Google Form sections; native-pairs/ preserves original size for inspection. '
        'Use UPLOAD_MAP.txt for section matching. Preview the Form after insertion. Its layout may scale images to fit the screen. '
        'Do not mix native and enlarged presentation versions during this round. If responses have already been collected, '
        'keep them under their actual presentation version. No existing responses were accessed or changed.\n\n'
        'Live Form insertion remains manual: editor/browser control was unavailable at the preceding checkpoint. '
        'No upload, question edit, invitation or response submission occurred in this export.\n', encoding='utf-8')
    shutil.copyfile(SOURCE / 'UPLOAD_MAP.txt', DELIVERY / 'UPLOAD_MAP.txt')
    summary = dict(round_id=status['round_id'], presentation_version='V2_exact_pixel_repeat_4x',
        parent_model_sha256=status['model_sha256'], pairs=20, subjects=13, MST_categories=10, scale=SCALE,
        native_face_width_range=[min(w for w,h in shapes),max(w for w,h in shapes)],
        large_face_width_range=[min(w for w,h in shapes)*SCALE,max(w for w,h in shapes)*SCALE],
        exact_pixel_repeat_checks=20, native_PNG_byte_copies=20, all16_offsets_checked_per_pair=True,
        invented_high_resolution_detail=False, sharpening=False, interpolation=False,
        new_model_calls=0, new_fits=0, source_portrait_decodes=0, masks_changed=False,
        questions_changed=False, model_changed=False, live_Form_updated=False, expert_responses_created=0,
        prior_packages_preserved=True, presentation_user_requested=True)
    write(DELIVERY / 'PRESENTATION_STATUS.json', summary); write(OUT / 'summary.json', summary)
    write(OUT / 'manifest_PRIVATE.json', dict(records=records,parent_verification_sha256=sha(PARENT/'verification.json'),
        script_sha256=sha(Path(__file__))))
    archive = DELIVERY / 'WB314-V2-large-expert-comparisons.zip'
    members = sorted(p for p in DELIVERY.rglob('*') if p.is_file())
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in members: z.write(p,p.relative_to(DELIVERY).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.startswith('pairs/') and n.endswith('.png')])==20
        for r in records:
            assert hashlib.sha256(z.read(r['enlarged_filename'])).hexdigest()==r['enlarged_sha256']
            assert hashlib.sha256(z.read(r['native_filename'])).hexdigest()==r['native_sha256']
    for path,digest in parent['artifacts'].items(): assert sha(SOURCE/path)==digest
    write(OUT/'verification.json',dict(passed=True,**summary,zip_CRC_pass=True,
        artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
    print('PASS20exact4xviewing copies/all16offsets+20nativebytecopies/ZIPCRC;0modelcalls/fits/sourceportraitreads.')


if __name__ == '__main__': main()
