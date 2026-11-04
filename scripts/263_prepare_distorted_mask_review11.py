"""Review only missing distorted-mask approvals for eleven accepted references."""
import hashlib
import html
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/distorted_mask_review11_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/correction_training_preparation_v1'
    admitted=read(ROOT/'outputs/accepted_clean_control_comparison_v1/plan.json')
    ids={r['source_image_id'] for r in admitted['rows'] if r['cohort']=='new_clean'}
    sources=[json.loads(line) for line in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    selected=[r for r in sources if r['image_id'] in ids];assert len(selected)==11
    hashes=read(parent/'verification.json')['evidence_sha256'];rows=[]
    out.mkdir();(out/'boards').mkdir()
    for r in selected:
        name=r['source_id'];paths={k:f'images/{name}_{k}.png' for k in ('reference','reference_mask','input','input_mask')}
        for path in paths.values():assert sha(parent/path)==hashes[path]
        assert r['input_measurement']['status']=='success' and r['target_fit']['status']=='available_approximate_target'
        reference=cv2.imread(str(parent/paths['reference']));image=cv2.imread(str(parent/paths['input']))
        mask=cv2.imread(str(parent/paths['input_mask']),0)>0
        overlay=image.copy();overlay[mask]=(.5*overlay[mask]+np.array([0,150,0])).astype(np.uint8)
        cv2.imwrite(str(out/'boards'/f'{name}.png'),np.hstack((reference,image,overlay)))
        rows.append(dict(image_id=r['image_id'],source_id=name,duplicate_group_id=r['duplicate_group_id'],
            review_scope='exact_original_rule_distorted_input_mask_only',reference_review='previously_accepted_no_notes',
            input_sha256=sha(parent/paths['input']),input_mask_sha256=sha(parent/paths['input_mask']),
            clipping_fraction=r['clipping_fraction'],existing_target_available=True,training_eligible=False))
    manifest=dict(schema_version='truehue_distorted_mask_review11_v1',rows=rows,measurement_contract_sha256=admitted['measurement_contract_sha256'],
        rule='Review input facial coverage and hair/eyes/mouth/clothing/background exclusion. No automatic training admission.',
        original_recipe='existing_table2_encoded_rgb_composite_v1_not_new_three_variant_recipe')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');identity=sha(out/'manifest.json')
    data=json.dumps(rows).replace('<','\\u003c')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TrueHue — 11 distorted masks</title><style>
body{font:18px system-ui;margin:24px auto;padding:0 16px;max-width:1100px;background:#f5f6f8;color:#17202a}button,textarea{font:inherit}button{padding:12px;margin:5px;border:1px solid #8b96a1;border-radius:8px;background:white;cursor:pointer}button[aria-pressed=true]{background:#173d6b;color:white}img{width:100%;image-rendering:auto;background:white}textarea{box-sizing:border-box;width:100%;height:80px}nav{display:flex;justify-content:space-between;flex-wrap:wrap}.labels{display:grid;grid-template-columns:repeat(3,1fr);text-align:center;font-weight:600}#notice{color:#8b2300}h1{font-size:27px}</style>
<h1>Check 11 distorted face masks</h1><p>The original photos were already accepted. Check only the green mask on the right. Does it cover facial skin while leaving out hair, eyes, lips, clothes and background?</p>
<p>Accept minor imperfections only if you would still use the mask. Reject clear contamination or badly missing facial coverage. Choose Unsure if needed. Your choice does not automatically train the model.</p>
<nav><button id="prev">Previous</button><strong id="count"></strong><button id="next">Next</button></nav>
<h2 id="name"></h2><div class="labels"><span>Original photo</span><span>Distorted photo</span><span>Mask to review</span></div><img id="board" alt="Original photo, distorted photo, and green overlay of the distorted face mask">
<div id="choices"><button data-choice="accept">Accept</button><button data-choice="reject">Reject</button><button data-choice="uncertain">Unsure</button></div>
<label for="notes">Notes (for example: hair included, missing cheek, holes)</label><textarea id="notes"></textarea>
<p id="notice" role="status"></p><button id="export">Download decisions</button><p>Choices are saved in this browser when available. Download your decisions when finished and save the JSON file in this review folder.</p>
<script>const rows=__DATA__, manifest='__HASH__', key='truehue_distorted11_'+manifest;
let index=0, decisions={};const byId=id=>document.getElementById(id);
try{const saved=JSON.parse(localStorage.getItem(key)||'{}');for(const r of rows){const d=saved[r.image_id];if(d&&['accept','reject','uncertain'].includes(d.decision)&&typeof d.notes==='string')decisions[r.image_id]=d;}}catch(e){byId('notice').textContent='Browser saving is unavailable. Download decisions before closing.';}
function store(){try{localStorage.setItem(key,JSON.stringify(decisions));}catch(e){byId('notice').textContent='Browser saving is unavailable. Download decisions before closing.';}}
function draw(){const r=rows[index],d=decisions[r.image_id]||{};byId('name').textContent='Image '+r.source_id;byId('board').src='boards/'+r.source_id+'.png';byId('notes').value=d.notes||'';byId('count').textContent=(index+1)+' / 11 — '+Object.values(decisions).filter(x=>x.decision).length+' reviewed';byId('prev').disabled=index===0;byId('next').disabled=index===rows.length-1;document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.choice===d.decision)));}
function update(choice){const r=rows[index],old=decisions[r.image_id]||{};decisions[r.image_id]={decision:choice===undefined?(old.decision||''):choice,notes:byId('notes').value,updated_at:new Date().toISOString()};store();draw();}
document.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>update(b.dataset.choice));
byId('notes').oninput=()=>{const r=rows[index],old=decisions[r.image_id]||{};decisions[r.image_id]={decision:old.decision||'',notes:byId('notes').value,updated_at:new Date().toISOString()};store();};
byId('prev').onclick=()=>{index--;draw();};byId('next').onclick=()=>{index++;draw();};
byId('export').onclick=()=>{const reviews=Object.fromEntries(rows.map(r=>[r.image_id,decisions[r.image_id]||{decision:'',notes:''}]));const blob=new Blob([JSON.stringify({schema_version:'truehue_distorted_mask_review11_v1',manifest_sha256:manifest,review_scope:'exact_original_rule_distorted_input_mask_only',reviews},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='truehue_distorted_mask_review11_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};draw();</script></html>'''
    (out/'review.html').write_text(page.replace('__DATA__',data).replace('__HASH__',identity),encoding='utf-8')
    (out/'verification.json').write_text(json.dumps(dict(status='pass',review_items=11,exact_original_image_and_mask_hashes_verified=True,
        inherited_acceptance_of_distorted_masks=False,manifest_sha256=identity,
        evidence_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('Prepared 11 exact distorted-mask checks; no new training approvals inferred.')


if __name__=='__main__':main()
