"""Six fixed native originals, predictions hidden, actual responses pending."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/stellenbosch_reference_points_v1'
CASES=('case_04','case_21','case_25','case_30','case_16','case_29')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for rel in ['scripts/459_prepare_stellenbosch_reference_points.py','scripts/460_import_stellenbosch_reference_points.py',
        'src/evaluation/reference_point_review.py','scripts/review_tools/native_reference_points.js',
        'tests/test_reference_point_review.py','docs/stellenbosch-reference-point-review-protocol-2026-11-06.md']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(p)==h for p,h in bound.items())
    source={r['case_id']:r for r in read(PARENT/'results_PRIVATE.json')['records']}
    # Header dimensions only; no new prediction or selection based on results.
    from PIL import Image
    OUT.mkdir();(OUT/'images').mkdir();rows=[];bindings={}
    for i,case in enumerate(CASES,1):
        row=source[case];folder=PARENT/case;review_id=f'review_{i:02d}'
        native=folder/'native_crop.png';context=folder/'source.jpeg'
        width,height=Image.open(native).size
        image_path=f'images/{review_id}_native.png';context_path=f'images/{review_id}_context.jpeg'
        (OUT/image_path).write_bytes(native.read_bytes());(OUT/context_path).write_bytes(context.read_bytes())
        rows.append(dict(review_id=review_id,width=width,height=height,image_path=image_path,context_path=context_path,image_sha256=sha(native)))
        grid=folder/'native_grid.png'
        bindings[review_id]=dict(case_id=case,parent_status=row['status'],source_sha256=row['source_sha256'],
            source_path=row['source_path'],native_crop_path=str(native),native_bounds=row['input_bridge']['native_bounds'],
            native_grid_path=str(grid) if grid.exists() else None,native_grid_sha256=sha(grid) if grid.exists() else None)
    manifest=dict(schema_version='truehue_native_reference_plan_v1',rows=rows,predictions_hidden=True,actual_responses_pending=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');identity=sha(OUT/'manifest.json')
    (OUT/'prediction_bindings_PRIVATE.json').write_text(json.dumps(bindings,indent=2),encoding='utf-8')
    data=dict(manifest_sha256=identity,rows=rows)
    html='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrueHue · six-photo skin reference review</title>
<style>body{font:17px system-ui;max-width:1100px;margin:auto;padding:20px;background:#faf9f6;color:#222}button,select,input,textarea{font:inherit;padding:9px;margin:5px}button{cursor:pointer}canvas{width:min(100%,512px);height:auto;image-rendering:pixelated;touch-action:none;border:1px solid #777}img{width:224px;height:224px;object-fit:contain}section{display:flex;gap:24px;flex-wrap:wrap}textarea{display:block;width:90%;min-height:55px}#message{font-weight:600;color:#7a3300}</style>
<h1>Six-photo skin reference review</h1>
<p>1. Choose a label and click a few clearly visible points on the enlarged face. Use cheek/forehead/chin skin; avoid eyes, lips, nostrils and mixed edges. Mark hair/beard or frames/objects only when clear.</p>
<p>2. Choose “Points marked” or “Cannot judge”. For a very dark/blurred photo, “Cannot judge” with a reason is a valid answer. No need to draw whole masks or find every label.</p>
<p>The zoom shows original pixel blocks, not added detail. Predictions and skin-tone scores are hidden. This is a local research review; do not share these photos. Nothing is uploaded.</p>
<label>Your name or reviewer code <input id="reviewer" autocomplete="off"></label>
<h2 id="title"></h2><section><div><p>Original scene</p><img id="context" alt="Original scene for context"></div><div><p>Original face · nearest-neighbour zoom</p><canvas id="canvas" width="512" height="512" aria-label="Click native face pixels to label reference points"></canvas></div></section>
<label>Point label <select id="label"><option value="skin">Skin · green</option><option value="hair_or_beard">Hair / beard · yellow</option><option value="object_or_other">Glasses / object / other non-skin · pink</option><option value="uncertain">Not sure · blue</option></select></label><button id="undo">Undo last point</button><p id="pointcount"></p>
<label>Photo status <select id="status"><option value="">Choose…</option><option value="marked">Points marked</option><option value="cannot_judge">Cannot judge</option></select></label>
<label>Notes / reason<textarea id="notes"></textarea></label>
<button id="prev">Previous</button><button id="next">Next</button><button id="export">Export my six responses</button><p id="message" role="status"></p>
<p>Drafts stay in this browser where storage is available. Export the JSON to keep a response file. Clicking an existing pixel replaces its label. Each image allows up to 50 points; you do not need 50.</p>
'''
    html+='<script id="data" type="application/json">'+json.dumps(data).replace('<','\\u003c')+'</script><script src="review.js"></script>'
    (OUT/'review.html').write_text(html,encoding='utf-8')
    (OUT/'review.js').write_bytes((ROOT/'scripts/review_tools/native_reference_points.js').read_bytes())
    assert len(rows)==6 and all(sha(p)==h for p,h in bound.items())
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()},indent=2),encoding='utf-8')
    print('Six fixed originals ready; no responses created. '+str(OUT/'review.html'))

if __name__=='__main__':main()
