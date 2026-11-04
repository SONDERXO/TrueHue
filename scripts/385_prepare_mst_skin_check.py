"""Four exact saved MST masks for human inspection; never fits or admits rows."""
import argparse
import hashlib
import html
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/mst_skin_check_four_v1'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    evidence = ROOT / 'outputs/faceocc_mst_feasibility_v1/matching_attempts.json'
    matching = json.loads(evidence.read_text(encoding='utf-8'))
    available = [r for r in matching if r['technical_available']]
    assert len(matching) == 33 and len(available) == 23
    sources = {}
    first = ROOT / 'outputs/faceocc_diagnostic_v1'
    first_plan = json.loads((first / 'plan.json').read_text())['attempts']
    for r in first_plan:
        if not r.get('input_path'):
            continue
        sources[r['image_id']] = (Path(r['input_path']), first / f"case_{r['case_index']}" / 'candidate_mask.png')
    second = ROOT / 'outputs/faceocc_light_comparison_v1'
    for r in json.loads((second / 'summary.json').read_text())['records']:
        folder = second / f"case_{r['case_index']}"
        sources[r['image_id']] = (folder / 'input.png', folder / 'candidate_mask.png')
    subjects = sorted({r['subject_id'] for r in available})
    assert len(subjects) == 4
    selected = [min((r for r in available if r['subject_id'] == subject),
                    key=lambda r: hashlib.sha256(('truehue-mst-skin-check-v1|' + r['image_id']).encode()).hexdigest())
                for subject in subjects]
    # Freeze selection before opening any selected pixels. No concern/outcome filter.
    OUT.mkdir()
    plan = dict(rule='lowest SHA256(truehue-mst-skin-check-v1|image_id) per subject among all 23 saved technical successes',
                scope='four exact-image visual judgments only; all 33 attempts/10 failures retained in parent evidence; no replacement, batch admission or fit',
                source_sha256={str(evidence.relative_to(ROOT)): digest(evidence)}, rows=selected)
    (OUT / 'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
    rows = []
    for i, r in enumerate(selected, 1):
        source, mask_path = sources[r['image_id']]
        im = np.asarray(Image.open(source).convert('RGB'))
        mask = np.asarray(Image.open(mask_path).convert('L')) > 0
        assert im.shape[:2] == mask.shape and mask.any()
        folder = OUT / f'case_{i}'
        folder.mkdir()
        (folder / 'input.png').write_bytes(source.read_bytes())
        (folder / 'mask.png').write_bytes(mask_path.read_bytes())
        selected_only = im.copy()
        selected_only[~mask] = 35
        overlay = im.copy()
        overlay[mask] = np.round(.7 * im[mask] + .3 * np.array([0, 255, 0])).astype(np.uint8)
        Image.fromarray(selected_only).save(folder / 'selected.png')
        Image.fromarray(overlay).save(folder / 'overlay.png')
        rows.append(dict(case_id=f'case_{i}', image_id=r['image_id'], subject_id=r['subject_id'],
                         official_mst=r['official_mst'], input_sha256=digest(source), mask_sha256=digest(mask_path),
                         source_input=str(source.relative_to(ROOT)), source_mask=str(mask_path.relative_to(ROOT)),
                         display_sha256={name: digest(folder / name) for name in ['input.png', 'mask.png', 'selected.png', 'overlay.png']}))
    manifest = dict(schema='truehue_mst_skin_check_four_v1', rows=rows,
                    plan_sha256=digest(OUT / 'plan.json'), training_admitted=False, calibration_admitted=False)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    manifest_hash = digest(OUT / 'manifest.json')
    cards = []
    for r in rows:
        key = r['case_id']
        controls = ''
        questions = [('non_skin', 'Does the highlighted area include hair, glasses, a face covering, clothing or background?'),
                     ('skin_loss', 'Does the mask leave out an obvious useful area of facial skin?'),
                     ('judgeable', 'Is this saved image clear enough for you to judge the selected pixels?')]
        for field, question in questions:
            controls += f'<label>{html.escape(question)} <select id="{key}_{field}"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option><option value="unsure">Cannot tell</option></select></label>'
        cards.append(f'<section><h2>Photo {len(cards)+1} of 4</h2><p>{html.escape(r["image_id"])}</p><div class="images">' +
                     ''.join(f'<figure><img src="{key}/{name}.png"><figcaption>{label}</figcaption></figure>' for name, label in [('input', 'Original saved input'), ('overlay', 'Green = selected measurement area'), ('selected', 'Selected pixels only')]) +
                     f'</div>{controls}<label>Optional note <textarea id="{key}_notes"></textarea></label></section>')
    script = '''const manifest=MANIFEST, binding=BINDING;
const fields=['non_skin','skin_loss','judgeable','notes'];
const storageKey='truehue_mst_skin_check_four_v1_'+binding;
function collect(){return manifest.rows.map(r=>({...r,decisions:Object.fromEntries(fields.filter(f=>f!=='notes').map(f=>[f,document.getElementById(r.case_id+'_'+f).value])),notes:document.getElementById(r.case_id+'_notes').value}));}
try{const old=JSON.parse(localStorage.getItem(storageKey)||'null');if(old)for(const r of old)for(const f of fields)document.getElementById(r.case_id+'_'+f).value=f==='notes'?r.notes:(r.decisions[f]||'');}catch(e){}
document.addEventListener('input',()=>{try{localStorage.setItem(storageKey,JSON.stringify(collect()));}catch(e){document.getElementById('status').textContent='Browser save unavailable. Keep this page open and export your answers.';}});
document.getElementById('export').onclick=()=>{const rows=collect();if(rows.some(r=>Object.values(r.decisions).some(v=>!v))){document.getElementById('status').textContent='Answer all three questions for each photo; Cannot tell is a valid answer.';return;}const blob=new Blob([JSON.stringify({schema:manifest.schema,manifest_sha256:binding,rows},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='truehue_mst_skin_check_four_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);document.getElementById('status').textContent='Answers exported. Tell me when you are done.';};
'''.replace('MANIFEST', json.dumps(manifest)).replace('BINDING', json.dumps(manifest_hash))
    (OUT / 'review.js').write_text(script, encoding='utf-8')
    (OUT / 'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Four labelled skin checks</title><style>body{font:18px/1.5 system-ui;max-width:1250px;margin:auto;padding:20px}section{border-top:2px solid #bbb;padding:20px 0}.images{display:flex;flex-wrap:wrap}figure{margin:8px;flex:1;min-width:240px}img{width:100%;image-rendering:auto}label{display:block;margin:16px 0}select,textarea,button{font:inherit}textarea{display:block;width:95%}</style><h1>Check four labelled photos</h1><p>No drawing needed. Check only the highlighted measurement area. Hair elsewhere on the face is fine if it is not selected. Zooming does not add detail; choose Cannot tell when uncertain. Eyes, eyebrows, lips, nostrils, hair and neck are intentionally excluded; those gaps are expected. You are checking visible skin selection, not whether the lighting shows true skin colour.</p><p>These are saved 256-pixel inputs, not new predictions. This checks only these four exact masks. It does not approve other photographs or start training.</p>'+''.join(cards)+'<button id="export">Export my answers</button><p id="status" role="status"></p><script src="review.js"></script></html>', encoding='utf-8')
    print(OUT / 'review.html')


def import_review(path):
    manifest_path = OUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    payload = json.loads(path.read_text(encoding='utf-8-sig'))
    assert payload['schema'] == manifest['schema']
    assert payload['manifest_sha256'] == digest(manifest_path)
    assert len(payload['rows']) == 4
    assert [r['case_id'] for r in payload['rows']] == [r['case_id'] for r in manifest['rows']]
    for actual, expected in zip(payload['rows'], manifest['rows']):
        for key, value in expected.items():
            assert actual[key] == value, key
        assert set(actual['decisions']) == {'non_skin', 'skin_loss', 'judgeable'}
        assert all(v in {'yes', 'no', 'unsure'} for v in actual['decisions'].values())
        assert isinstance(actual['notes'], str)
        for name, checksum in expected['display_sha256'].items():
            assert digest(OUT / expected['case_id'] / name) == checksum
        assert digest(ROOT / expected['source_input']) == expected['input_sha256']
        assert digest(ROOT / expected['source_mask']) == expected['mask_sha256']
    target = ROOT / 'outputs/mst_skin_check_four_import_v1'
    if target.exists():
        raise FileExistsError(target)
    target.mkdir()
    (target / 'original_export.json').write_bytes(path.read_bytes())
    (target / 'decisions.json').write_text(json.dumps(dict(original_sha256=digest(path), human_judgments=payload,
                                                         calibration_admitted=False, training_admitted=False,
                                                         scope='exact-image visual evidence only; no automatic fitting or all-person approval'), indent=2), encoding='utf-8')
    print(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--import-review', type=Path)
    args = parser.parse_args()
    import_review(args.import_review) if args.import_review else prepare()
