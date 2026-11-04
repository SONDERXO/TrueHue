"""Static source-only gallery; no new photo processing, models or review requests."""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT/'outputs/ffhq_source_preparation_v1'
OUT = ROOT/'outputs/ffhq_source_visual_assessment_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def esc(value):
    return html.escape(str(value),quote=True)


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes=json.loads((PARENT/'sha256.json').read_text())
    assert all(sha(PARENT/k)==v for k,v in hashes.items())
    selected=json.loads((PARENT/'selected_before_pixels.json').read_text())['sources']
    attempts=json.loads((PARENT/'attempts.json').read_text())
    assert [r['id'] for r in selected]==[r['id'] for r in attempts]
    cards=[]
    for row,result in zip(selected,attempts):
        meta=row['metadata']
        if result['access']['success']:
            image=ROOT/result['path']
            assert sha(image)==result['access']['sha256']
            relative='../../'+result['path']
            picture=f'<a href="{esc(relative)}"><img src="{esc(relative)}" alt="FFHQ {esc(row["id"])} source"></a>'
        else:
            picture='<p class="failure">Unavailable. Failure retained; no replacement.</p>'
        cards.append(f'<article><h2>FFHQ {esc(row["id"])}</h2>{picture}'
            f'<p>Photographer: {esc(meta.get("author","unknown"))}</p>'
            f'<p><a href="{esc(meta["photo_url"])}">Original photo attribution</a> · '
            f'<a href="{esc(meta["license_url"])}">{esc(meta["license"])}</a></p>'
            '<p>Aligned/cropped FFHQ source. Display scaled only; no TrueHue colour correction.</p>'
            '<p>Development candidate only. MST unavailable; person independence and masks unverified.</p></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrueHue FFHQ source candidates</title>
<style>body{font:16px/1.5 system-ui,sans-serif;background:#f3f4f5;color:#222;margin:24px}
header{max-width:1000px;margin:auto auto 24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
article{background:white;border:1px solid #ddd;border-radius:10px;padding:16px}h2{margin-top:0;font-size:20px}
img{width:100%;height:auto;display:block}p{margin:10px 0}a{color:#145daf}.failure{padding:40px;background:#fee}</style>
<header><h1>FFHQ: photographic source candidates</h1>
<p>Fixed 12-source development sample. These are original aligned FFHQ photos, not corrected outputs or measured true-colour references.
Acquisition makes them development-exposed, not unseen final evaluation.</p>
<p>ITA-to-MST work is deferred. No MST labels, mask approvals, person-disjoint split, new correction model or training admission are claimed.
This gallery does not request annotations. Click an image to inspect its full resolution.</p>
<p>FFHQ: Karras, Laine and Aila, <em>A Style-Based Generator Architecture for Generative Adversarial Networks</em>.
<a href="https://github.com/NVlabs/ffhq-dataset">Official dataset and terms</a>.
Per-photo authors and licence links are retained below; original publisher alignment/cropping is distinct from TrueHue colour correction.</p></header>
<main class="grid">'''+''.join(cards)+'</main></html>'
    OUT.mkdir()
    (OUT/'review.html').write_text(page,encoding='utf-8')
    (OUT/'input_sha256.json').write_text(json.dumps(dict(parent_manifest=sha(PARENT/'sha256.json'),
        script=sha(Path(__file__)),gallery=sha(OUT/'review.html'),attempts=len(attempts),
        verified_images=sum(r['access']['success'] for r in attempts)),indent=2),encoding='utf-8')
    print(str(OUT/'review.html'))


if __name__=='__main__':
    main()
