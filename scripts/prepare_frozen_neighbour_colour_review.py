"""Bind all11colour-only cases for usefulness, without new correction renders."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from src.model_training.reiqa_frozen_features import sha
from prepare_frozen_neighbour_identity_review import TEMPLATE as IDENTITY_TEMPLATE
RUN=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
OUT=ROOT/'outputs/frozen_neighbour_colour_review_v2'

SCRIPT=r'''const CONFIG=__CONFIG__;
const key='truehue_colour_'+CONFIG.manifest_sha256;
const prefs=['candidate','input','no_useful_difference','uncertain'],looks=['acceptable','unwanted','uncertain'];
let answers={},events=[],cursor=0;const el=id=>document.getElementById(id);
function valid(d){if(d.schema!=='truehue_colour_usefulness_review_v1'||d.review_kind!=='colour_usefulness_and_appearance'||d.manifest_sha256!==CONFIG.manifest_sha256||d.qa_fixture!==CONFIG.qa_fixture)throw Error('This file belongs to another review.');for(const [id,a] of Object.entries(d.answers||{})){if(!CONFIG.cases.some(c=>c.review_id===id)||(a.preference!==null&&!prefs.includes(a.preference))||(a.appearance!==null&&!looks.includes(a.appearance))||typeof a.note!=='string')throw Error('Invalid saved answer.');}return d;}
function stopped(){return CONFIG.cases.findIndex(c=>answers[c.review_id]?.appearance&&answers[c.review_id].appearance!=='acceptable');}
function complete(a){return a&&prefs.includes(a.preference)&&looks.includes(a.appearance);}
function payload(){const s=stopped(),done=CONFIG.cases.every(c=>complete(answers[c.review_id]));return {schema:'truehue_colour_usefulness_review_v1',review_kind:'colour_usefulness_and_appearance',manifest_sha256:CONFIG.manifest_sha256,qa_fixture:CONFIG.qa_fixture,status:s>=0?'stopped_'+answers[CONFIG.cases[s].review_id].appearance:done?'complete_recorded':'partial',answers,events,saved_at:new Date().toISOString()};}
function persist(){try{localStorage.setItem(key,JSON.stringify(payload()));}catch(e){el('status').textContent='Browser saving unavailable. Use Save review.';}}
function show(){const s=stopped();if(s>=0&&cursor>s)cursor=s;const c=CONFIG.cases[cursor],a=answers[c.review_id];for(const name of ['input','candidate','reference'])el(name).src=c[name];el('progress').textContent='Case '+(cursor+1)+' of '+CONFIG.cases.length;el('note').value=a?.note||'';for(const b of document.querySelectorAll('[data-field]'))b.setAttribute('aria-pressed',String(a?.[b.dataset.field]===b.dataset.value));el('back').disabled=cursor===0;el('next').disabled=!complete(a)||s>=0||cursor===CONFIG.cases.length-1;el('stop').hidden=s<0;el('status').textContent=s>=0?'Stopped: save your result.':payload().status==='complete_recorded'?'All 11 cases recorded. Save your review.':CONFIG.cases.filter(c=>complete(answers[c.review_id])).length+' of '+CONFIG.cases.length+' recorded.';}
for(const b of document.querySelectorAll('[data-field]'))b.onclick=()=>{const id=CONFIG.cases[cursor].review_id,a=answers[id]||{preference:null,appearance:null,note:''};a[b.dataset.field]=b.dataset.value;a.note=el('note').value;answers[id]=a;events.push({review_id:id,field:b.dataset.field,value:b.dataset.value,at:new Date().toISOString()});persist();show();};
el('note').oninput=()=>{const a=answers[CONFIG.cases[cursor].review_id];if(a){a.note=el('note').value;persist();}};
el('next').onclick=()=>{if(!el('next').disabled){cursor++;show();}};el('back').onclick=()=>{if(cursor>0){cursor--;show();}};
el('clear').onclick=()=>{const id=CONFIG.cases[cursor].review_id;delete answers[id];events.push({review_id:id,field:'all',value:'cleared',at:new Date().toISOString()});persist();show();};
el('save').onclick=()=>{const blob=new Blob([JSON.stringify(payload(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=CONFIG.qa_fixture?'colour-review-QA.json':'truehue-colour-usefulness-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);el('status').textContent='Review downloaded. Keep the saved file.';};
function restore(d){answers=d.answers;events=d.events||[];cursor=stopped()>=0?stopped():Math.max(0,CONFIG.cases.findIndex(c=>!complete(answers[c.review_id])));persist();show();}
el('load').onchange=async e=>{try{restore(valid(JSON.parse(await e.target.files[0].text())));}catch(err){el('status').textContent='Could not load: '+err.message;}};
try{const raw=localStorage.getItem(key);if(raw){const d=valid(JSON.parse(raw));answers=d.answers;events=d.events||[];cursor=stopped()>=0?stopped():Math.max(0,CONFIG.cases.findIndex(c=>!complete(answers[c.review_id])));}}catch(e){}
show();'''

def template():
    style=IDENTITY_TEMPLATE[IDENTITY_TEMPLATE.index('<style>'):IDENTITY_TEMPLATE.index('</style>')+8]
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Colour correction usefulness</title>'''+style+'''
<h1>Colour correction: is the improvement useful?</h1><p>Use the photographic reference to compare the input and candidate. Judge the skin's colour and overall appearance. A difference that is too small to prefer belongs under <strong>No useful difference</strong>.</p>
<p id="progress"></p><div class="pair"><figure><figcaption>Input</figcaption><img id="input" alt="Input photograph"></figure><figure><figcaption>Candidate</figcaption><img id="candidate" alt="Candidate photograph"></figure><figure><figcaption>Photographic reference</figcaption><img id="reference" alt="Photographic reference"></figure></div>
<p><strong>1. Which result is more useful toward the reference?</strong></p><div>
<button data-field="preference" data-value="candidate" aria-pressed="false">Candidate: visible, useful improvement</button><button data-field="preference" data-value="input" aria-pressed="false">Input is preferable</button><button data-field="preference" data-value="no_useful_difference" aria-pressed="false">No useful difference</button><button data-field="preference" data-value="uncertain" aria-pressed="false">Unsure</button></div>
<p><strong>2. Does the candidate introduce an unwanted change?</strong></p><div><button data-field="appearance" data-value="acceptable" aria-pressed="false">Acceptable, including a slight acceptable difference</button><button data-field="appearance" data-value="unwanted" aria-pressed="false">Unwanted change</button><button data-field="appearance" data-value="uncertain" aria-pressed="false">Unsure</button></div>
<label>Optional explanation<br><textarea id="note" aria-label="Optional explanation"></textarea></label><div id="stop" hidden>Review stopped. Save the result, including any explanation. Leave the remaining cases unrated.</div>
<button id="back">Previous</button><button id="next">Next</button><button id="clear">Clear current answer</button><p id="status" aria-live="polite"></p><hr><button id="save">Save review</button><label class="small">Load a previously saved review <input id="load" type="file" accept="application/json"></label><p class="small">Selections save in this browser. Download before closing. Use your usual viewing setup. This page contains 11 colour cases; exposure correction is assessed separately.</p><script>'''+SCRIPT+'''</script></html>'''

def main():
    if OUT.exists():raise FileExistsError(OUT)
    identity=ROOT/'outputs/frozen_neighbour_identity_ratings_v1/assessment_PRIVATE.json'
    assert json.loads(identity.read_text())['status']=='complete_acceptable'
    proof=json.loads((RUN/'verification_PRIVATE.json').read_text());assert proof['passed'] and proof['numeric_status']=='NUMERIC_PREDICTION_ELIGIBLE_ONLY'
    hashes={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    rows=[r for r in json.loads((RUN/'models/held_controls_sealed.json').read_text()) if r['role']=='colour_only']
    rows.sort(key=lambda r:r['source_id']);assert len(rows)==11 and len({r['source_id'] for r in rows})==11
    OUT.mkdir();(OUT/'images').mkdir();manifest=[]
    for i,r in enumerate(rows,1):
        relative='evaluation/'+r['case_id']+'.npz';assert sha(RUN/relative)==hashes[relative]
        with np.load(RUN/relative,allow_pickle=False) as pack:images={k:pack[k].copy() for k in ['input','tree','reference']}
        record=dict(review_id=f'colour_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],cached_pack_sha256=hashes[relative],pixel_identical=bool(np.array_equal(images['input'],images['tree'])))
        for field,arraykey in [('input','input'),('candidate','tree'),('reference','reference')]:
            p=OUT/'images'/f'{i:02d}_{field}.png';Image.fromarray(images[arraykey]).save(p)
            np.testing.assert_array_equal(np.asarray(Image.open(p)),images[arraykey]);record[field]=p.relative_to(OUT).as_posix();record[field+'_sha256']=sha(p)
        manifest.append(record)
    assert sum(r['pixel_identical'] for r in manifest)==1
    binding=dict(ui_version=2,cases=manifest,review_kind='colour_usefulness_and_appearance',identity_assessment_sha256=sha(identity),
        run_verification_sha256=sha(RUN/'verification_PRIVATE.json'),protocol_sha256=sha(ROOT/'docs/frozen-neighbour-colour-usefulness-protocol-2026-11-15.md'))
    (OUT/'manifest_PRIVATE.json').write_text(json.dumps(binding,indent=2),encoding='utf-8')
    config=dict(manifest_sha256=sha(OUT/'manifest_PRIVATE.json'),qa_fixture=False,cases=[{k:r[k] for k in ['review_id','input','candidate','reference']} for r in manifest])
    html=template().replace('__CONFIG__',json.dumps(config));(OUT/'index.html').write_text(html,encoding='utf-8')
    (OUT/'script_syntax.js').write_text(SCRIPT.replace('__CONFIG__',json.dumps(config)),encoding='utf-8')
    (OUT/'preparation_PRIVATE.json').write_text(json.dumps(dict(cases=11,images=33,unchanged_included=1,ratings_collected=0,
        manifest_sha256=config['manifest_sha256'],code_sha256=sha(Path(__file__)),html_sha256=sha(OUT/'index.html')),indent=2),encoding='utf-8')
    print('Prepared11full-roster colour cases/33losslessimages;0newratings or correctionrenders.')
if __name__=='__main__':main()
