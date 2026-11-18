"""Prepare six fixed private original crops; never generate reviewer answers."""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_reference_points_v1'
OUT=ROOT/'outputs/stellenbosch_skin_patch_review_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    bindings=json.loads((PARENT/'prediction_bindings_PRIVATE.json').read_text())
    rows=[];bound={str(PARENT/'prediction_bindings_PRIVATE.json'):sha(PARENT/'prediction_bindings_PRIVATE.json')}
    for key,b in bindings.items():
        crop=Path(b['native_crop_path']);source=Path(b['source_path'])
        assert sha(source)==b['source_sha256']
        with Image.open(source) as im,Image.open(crop) as face:
            assert im.crop(tuple(b['native_bounds'])).convert('RGB').tobytes()==face.convert('RGB').tobytes()
            w,h=face.size
        bound[str(crop)]=sha(crop);bound[str(source)]=sha(source)
        rows.append(dict(review_id=key,width=w,height=h,image_path=key+'.png',context_path=key+'.jpeg',image_sha256=sha(crop)))
    assert len(rows)==6
    for rel in ['scripts/472_prepare_skin_patch_review.py','scripts/review_tools/skin_patch_review.js',
                'docs/skin-patch-review-protocol-2026-11-06.md']:
        bound[rel]=sha(ROOT/rel)
    OUT.mkdir(parents=True)
    for r in rows:
        b=bindings[r['review_id']];shutil.copyfile(b['native_crop_path'],OUT/r['image_path']);shutil.copyfile(b['source_path'],OUT/r['context_path'])
    manifest=dict(schema_version='truehue_skin_patch_manifest_v1',rows=rows)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    data=dict(manifest_sha256=sha(OUT/'manifest.json'),rows=rows)
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrueHue skin patches</title>
<style>body{font:17px system-ui;max-width:1150px;margin:24px auto;padding:0 16px;background:#f4f6f8;color:#182b39}button,input,select{font:inherit;padding:8px;margin:4px}textarea{width:95%;min-height:60px;font:inherit}section{display:flex;gap:24px;flex-wrap:wrap}canvas{width:512px;max-width:100%;height:auto;image-rendering:pixelated;touch-action:none;border:1px solid #666}img{width:224px;image-rendering:pixelated}#message{font-weight:bold}li{margin:8px 0}</style>
<h1>Mark clearly visible facial skin patches</h1><p>Six previously reviewed photos. Select a few skin patches you can judge confidently; you do not need to outline the whole face. No model masks or scores are shown.</p>
<ol><li>Click around a clearly visible facial-skin patch, then <b>Save patch</b>. More than one patch is allowed; no fixed size or number is required.</li><li>Avoid beard/stubble, hair, eyes/brows, lips/mouth, nostrils, glasses frames, reflections and unclear edges. Leave the neck unmarked. A patch need not match another photo's location.</li><li>If no facial patch is reliable, choose <b>No reliable patch</b> and explain why. Do not guess.</li><li>Review all six and export. This is a development measurement reference, not a manual step in the app or a training approval.</li></ol>
<label>Your name/code <input id="reviewer"></label><button id="draft">Download draft</button><label>Resume draft <input id="import" type="file" accept=".json"></label>
<h2 id="title"></h2><section><div>Original scene<br><img id="context" alt="Original scene"></div><div>Original face at nearest-neighbour zoom<br><canvas id="canvas" width="512" height="512" aria-label="Click vertices around visible facial skin"></canvas></div></section>
<p>Zoom enlarges original pixels; it does not restore detail. Yellow is your unfinished outline; green is saved.</p><button id="finish">Save patch</button><button id="undo">Undo vertex</button><button id="cancel">Cancel unfinished patch</button><button id="remove">Delete last saved patch</button><label><input id="show" type="checkbox" checked>Show saved patches</label><p id="count"></p>
<label>Photo status <select id="status"><option value="">Choose…</option><option value="marked">Patches marked</option><option value="unavailable">No reliable patch</option></select></label><p>Notes / reason</p><textarea id="notes"></textarea>
<p><button id="prev">Previous</button><button id="next">Next</button><button id="export">Export completed review</button></p><p id="message" role="status"></p><p>Saved patches are kept in this browser where available. Download a draft before closing. Keep the images and exported review private.</p>
'''
    html+='<script id="data" type="application/json">'+json.dumps(data).replace('<','\\u003c')+'</script><script src="review.js"></script></html>'
    (OUT/'review.html').write_text(html,encoding='utf-8')
    shutil.copyfile(ROOT/'scripts/review_tools/skin_patch_review.js',OUT/'review.js')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    assert all(sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print('Prepared six original native crops, prediction-hidden UI; no actual responses created.')


if __name__=='__main__':main()
