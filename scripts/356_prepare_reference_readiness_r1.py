"""Bind existing R1 artifacts and build a review; no inference or fitting."""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/reference_readiness_r1'


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    hashes = {}

    def bind(relative):
        hashes[relative] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        return hashes[relative]

    def read(relative):
        bind(relative)
        return json.loads((ROOT / relative).read_text(encoding='utf-8'))

    records = read('outputs/preferred_support_cohort_v1/records.json')
    soft = {r['case_id']: r for r in read('outputs/seamless_support_v5/records.json')}
    plan = read('outputs/seamless_support_v5/plan.json')
    inventory = read('outputs/independent_source_inventory_v1/fairface_inventory.json')
    subjects = read('outputs/next_cycle_data_plan_v1/mst_subject_inventory.json')
    by_id = {r['image_id']: r for r in inventory}
    rows, holds = [], []
    for r in records:
        if r['measurement']['status'] != 'success':
            holds.append(dict(image_id=r['image_id'], reason=r['measurement'].get('reason'),
                              stage=r['measurement'].get('stage'), decision='technical_hold'))
            continue
        sid = Path(r['image_id']).stem
        folder = 'outputs/seamless_support_v5/cases/' + sid + '/'
        files = {name: folder + name + '.png' for name in
                 ['input', 'measurement_mask', 'correction_mask', 'alpha', 'soft']}
        files['overlay'] = 'outputs/whole_face_support_v4/cases/' + sid + '/overlay.png'
        file_hashes = {k: bind(v) for k, v in files.items()}
        assert file_hashes['measurement_mask'] == soft[sid]['measurement_mask_sha256']
        assert file_hashes['correction_mask'] == soft[sid]['binary_correction_mask_sha256']
        old_path = r.get('input_path', r.get('path'))
        assert old_path and bind(old_path) == file_hashes['input']
        prior = r['original_source_decision']
        retained = r['kind'] == 'anchor' and prior['decision'] == 'accept'
        evidence = by_id[r['image_id']]
        rows.append(dict(image_id=r['image_id'], key=sid, kind=r['kind'], files=files,
            file_sha256=file_hashes, original_source_decision=prior,
            source_retained=retained, required=([] if retained else ['source']) +
            ['lighting', 'measurement', 'correction', 'facial_hair', 'covering', 'contamination'],
            role=evidence['role'], duplicate_group=evidence['duplicate_group'],
            person_identity='not_verified', official_mst=None,
            exposure_evidence=evidence['exposure_evidence'],
            historical_review_evidence=evidence['scoped_review_evidence'],
            lighting_provenance='not_established_in_checked_records',
            decisions='pending', training_admitted=False))
    assert len(rows) == 16 and len(holds) == 2
    assert sum(r['source_retained'] for r in rows) == 6
    manifest = dict(schema_version='truehue_reference_readiness_r1', rows=rows, holds=holds,
        subject_metadata=[r for r in subjects if not r['in_completed_cycle']],
        measurement_contract_sha256=plan['measurement_contract_sha256'],
        correction='whole_face_plus_neck_inward_union_smoothstep_3percent',
        alpha_display='saved_8bit_preview_not_float_operator_target',
        input_sha256=hashes, automatic_training=False)
    raw = json.dumps(manifest, indent=2).encode()
    identity = hashlib.sha256(raw).hexdigest()
    OUT.mkdir()
    (OUT / 'manifest.json').write_bytes(raw)
    labels = dict(source='Photographic reconstruction reference',
        lighting='Independent lighting / true-colour evidence', measurement='Actual-skin measurement mask',
        correction='Whole-face + visible-neck coverage and inward blending',
        facial_hair='Visible facial hair', covering='Visible face covering / other occluder',
        contamination='Hair or covering selected as measurement skin')
    choices = dict(lighting=[('unknown', 'Unknown / no independent evidence'), ('documented', 'Documented: describe evidence below')],
        facial_hair=[('absent', 'Not apparent'), ('present', 'Present'), ('uncertain', 'Uncertain')],
        covering=[('absent', 'Not apparent'), ('present', 'Present'), ('uncertain', 'Uncertain')],
        contamination=[('absent', 'None apparent'), ('present', 'Present — hold'), ('uncertain', 'Uncertain — hold')])
    cards = []
    for r in rows:
        controls = ''
        for field in r['required']:
            options = choices.get(field, [('accept', 'Accept'), ('reject', 'Reject'), ('uncertain', 'Uncertain / hold')])
            controls += '<label>' + labels[field] + ': <select id="' + r['key'] + '_' + field + '"><option value="pending">Choose</option>' + ''.join(
                '<option value="' + v + '">' + html.escape(label) + '</option>' for v, label in options) + '</select></label>'
        images = ''.join('<figure><img src="../../' + path + '"><figcaption>' + label + '</figcaption></figure>' for path, label in [
            (r['files']['input'], 'Original photographic reference'),
            (r['files']['overlay'], 'Correction overlay: whole face and visible neck'),
            (r['files']['measurement_mask'], 'Measurement only: white pixels supply ITA/MST'),
            (r['files']['alpha'], 'Correction strength: black outside, grey inward boundary'),
            (r['files']['soft'], 'Illustrative correction only — NOT model prediction')])
        retained = 'Source acceptance retained. Notes: ' + str(r['original_source_decision'].get('notes', '')) if r['source_retained'] else 'Source suitability still needs a decision.'
        cards.append('<section><h2>' + html.escape(r['image_id']) + '</h2><p>' + html.escape(retained) + '</p><div class="images">' + images + '</div>' + controls + '<label>Notes / evidence / hold reason<textarea id="' + r['key'] + '_notes"></textarea></label></section>')
    js = '''const rows=ROWS, mh=HASH;const key='truehue_r1_'+mh;
function collect(){return rows.map(r=>({image_id:r.image_id,decisions:Object.fromEntries(r.required.map(f=>[f,document.getElementById(r.key+'_'+f).value])),notes:document.getElementById(r.key+'_notes').value}));}
function complete(r){const d=r.decisions;if(d.source==='reject'||d.source==='uncertain')return true;return Object.values(d).every(v=>v!=='pending')&&(d.lighting!=='documented'||r.notes.trim().length>0);}
function update(){const v=collect();document.getElementById('count').textContent=v.filter(complete).length+' / 16 complete';try{localStorage.setItem(key,JSON.stringify(v));}catch(e){}}
try{for(const s of JSON.parse(localStorage.getItem(key)||'[]')){const r=rows.find(r=>r.image_id===s.image_id);if(r){for(const f of r.required)document.getElementById(r.key+'_'+f).value=s.decisions[f]||'pending';document.getElementById(r.key+'_notes').value=s.notes||'';}}}catch(e){}
document.querySelectorAll('select,textarea').forEach(e=>e.addEventListener('input',update));update();
document.getElementById('export').onclick=()=>{if(!collect().every(complete)){document.getElementById('message').textContent=' Finish all decisions, or reject/hold an unsuitable source. Documented lighting needs evidence notes.';return;}const b=new Blob([JSON.stringify({schema_version:'truehue_reference_readiness_r1_decisions',manifest_sha256:mh,rows:collect()},null,2)],{type:'application/json'});const u=URL.createObjectURL(b),a=document.createElement('a');a.href=u;a.download='truehue_reference_readiness_r1_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};'''.replace('ROWS', json.dumps([dict(image_id=r['image_id'],key=r['key'],required=r['required']) for r in rows])).replace('HASH', json.dumps(identity))
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrueHue reference readiness R1</title>
<style>body{font:17px/1.5 system-ui;max-width:1450px;margin:auto;padding:24px;background:#f7f6f2}section{padding:20px;background:white;margin:24px 0;border:1px solid #ccc}.images{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;width:256px}img{width:256px;image-rendering:auto}figcaption{font-size:14px}label{display:block;margin:15px 0}select,textarea,button{font:inherit;padding:8px}textarea{width:95%;height:70px}#bar{position:sticky;top:0;background:#fff0bf;padding:15px;z-index:1}</style>
<h1>Reference readiness — 16 existing photos</h1>
<p>Keep six accepted source decisions. Judge current masks separately. White measurement pixels must be actual facial skin, excluding eyes, brows, lips/mouth, hair, nostrils and neck. Beard or covering contamination means hold. Whole-face correction intentionally includes internal features and hair inside the outline, plus visible neck; inspect outer coverage and blending.</p>
<p>For photographic suitability inspect detail, casts, mixed light, clipping, filtering and occlusions. Acceptance is a photographic reconstruction target, not true skin colour. Choose unknown for lighting unless independent evidence is available; an attractive photo or mask approval is not that evidence. Preserve uncertainty. No automatic training or MST adoption follows.</p>
<p>If rejecting or holding a source, its other judgments may stay unchosen. Decisions are saved in this browser; download the JSON to preserve them.</p>
<div id="bar"><span id="count"></span> <button id="export">Download decisions</button><span id="message"></span></div>'''
    page += ''.join(cards) + '<h2>Two technical holds — retained, no replacement</h2>' + ''.join('<p>' + html.escape(str(r)) + '</p>' for r in holds) + '<script>' + js + '</script></html>'
    (OUT / 'review.html').write_text(page, encoding='utf-8')
    (OUT / 'review-script.js').write_text(js, encoding='utf-8')
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in hashes.items())
    (OUT / 'verification.json').write_text(json.dumps(dict(status='artifact_binding_pass', available=16,
        technical_holds=2, retained_source_decisions=6, new_mask_approvals=0, fits=0,
        manifest_sha256=identity), indent=2))
    print(str(OUT / 'review.html'))


if __name__ == '__main__':
    main()
