"""Assemble a local walkthrough from recorded emulator evidence; no fitting."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/android_demonstration_20261031_v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'index.html').exists(), 'Preserve the existing demonstration.'
    entries = [
        ('01_home.png', 'outputs/android_reliability_20261031_v1/home.png',
         '1. Select one photo', 'The home screen labels this an experimental model that failed quality checks. The system picker grants access to the selected photo.'),
        ('02_selected.png', 'outputs/android_reliability_20261031_v1/photo_selected.png',
         '2. Process the selected photo', 'Face detection, the original rule-based skin mask, ITA, experimental MST mapping and the decision tree run locally. This exposed development example was already used for software checks.'),
        ('03_mask.png', 'outputs/android_emulator_check_20261031_v1/app_run/skin_mask.png',
         '3. Inspect the selected pixels', 'White pixels enter facial measurements and correction. This is the original mask, not the newer parser preview. Coverage and exclusions remain limitations; beard/mustache work is on hold.'),
        ('04_result.png', 'outputs/android_reliability_20261031_v1/result_actions.png',
         '4. Inspect the experimental result', 'The result has visible uneven color and hard mask boundaries. This demonstrates the pipeline running, not reliable skin-tone correction. The older baseline5/fold1 remains unchanged.'),
        ('05_save.png', 'outputs/android_emulator_check_20261031_v1/save_image_dialog.png',
         '5. Save the trial image and report', 'The Android document picker saves a PNG and a separate JSON report. Both exports were checked in the earlier emulator run. The original photo stays unchanged.'),
        ('06_failure.png', 'outputs/android_demonstration_20261031_v1/failure_ready.png',
         '6. Handle a photo with no face', 'This newly captured screen uses a synthetic gray square. The app reports that no clear face was found and offers a failure report. It does not present a correction result.'),
    ]
    manifest = {'purpose': 'Local experimental Android walkthrough',
                'published': False, 'new_training': False,
                'capture_note': 'Screenshots from separate recorded emulator runs; not a continuous video.',
                'model': 'baseline5/fold1; failed quality gate',
                'mst': 'Experimental development lookup; not validated',
                'screens': []}
    cards = []
    for name, source, title, caption in entries:
        src, dst = ROOT / source, OUT / name
        assert src.is_file() and not dst.exists()
        shutil.copyfile(src, dst)
        assert digest(src) == digest(dst)
        manifest['screens'].append({'file': name, 'source': source, 'sha256': digest(dst)})
        cards.append(f'<article><div><h2>{html.escape(title)}</h2><p>{html.escape(caption)}</p></div>'
                     f'<img src="{name}" alt="{html.escape(title)}"></article>')
    apk = ROOT / 'android-app/app/build/outputs/apk/debug/app-debug.apk'
    manifest['apk_sha256'] = digest(apk)
    assert manifest['apk_sha256'] == '3720f08a0b1c343ae421163837a09a79655265fa172512a0ed290173abff9780'
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrueHue — experimental Android walkthrough</title>
<style>body{font:18px/1.6 system-ui,sans-serif;background:#f7f4ef;color:#292421;margin:0}
main{max-width:980px;margin:auto;padding:32px}h1{line-height:1.2}header,article,footer{background:white;padding:28px;border-radius:16px;margin:24px 0}
.notice{background:#fff0cd;padding:16px;border-left:5px solid #986400}article{display:flex;gap:32px;align-items:flex-start}article div{flex:1}img{width:280px;max-width:100%;height:auto;border:1px solid #ddd}h2{font-size:24px}small{color:#635950}@media(max-width:650px){article{display:block}img{display:block;margin:24px auto}}</style>
<main><header><h1>TrueHue Android walkthrough</h1>
<p class="notice"><strong>Experimental emulator demonstration.</strong> The software runs; the correction model is unfinished and failed its quality gate.</p>
<p>31 October 2026 · Android 15 / API 35 · x86_64 emulator</p>
<small>Recorded screenshots from separate runs, arranged as a walkthrough. Images remain local. This is not a continuous recording or a new model comparison.</small></header>'''
    page += ''.join(cards)
    page += '''<footer><h2>What this establishes</h2><p>Photo selection, local processing, result display, saving and explicit failure handling work in the checked emulator configuration. Earlier checks passed six native emulator tests and eighteen JVM tests. One fixed development example matched Python pixels exactly.</p>
<p>The screen’s general device-parity warning remains appropriate: one emulator example does not establish agreement on every photo or physical phone. Reliable correction, final MST validation, neck coverage and physical-phone checks remain unfinished. No model, mask rule or demo preset was changed for this walkthrough.</p>
<p>Beard/mustache exclusions and the proposed masking change await the adviser discussion. Professional feedback and refinement follow a good initial correction model. This walkthrough is for local review; it has not been sent or published.</p></footer></main></html>'''
    (OUT / 'index.html').write_text(page, encoding='utf-8')
    assert all((OUT / item['file']).is_file() for item in manifest['screens'])
    assert 'https://' not in page and 'http://' not in page
    manifest['verification'] = {'all_six_images_exist': True, 'copied_bytes_match': True,
                                'external_assets': False, 'apk_unchanged': True}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (OUT / 'README.txt').write_text('Open index.html in a browser. Local walkthrough, not a video.\n'
                                  'Contains an exposed dataset example: keep local; do not upload raw images.\n'
                                  'Narration: docs/android-demonstration-script-2026-10-31.md\n', encoding='utf-8')
    print(json.dumps(manifest['verification']))


if __name__ == '__main__':
    main()
