"""All11identity human check, only after independent numerical eligibility."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.reiqa_frozen_features import sha
RUN=ROOT/'outputs/frozen_block_neighbour_prediction_v1'
OUT=ROOT/'outputs/frozen_neighbour_identity_review_v1'

TEMPLATE='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Identity preservation review</title><style>
body{font:17px system-ui,sans-serif;margin:24px auto;padding:0 18px;max-width:1000px;background:#fff;color:#171717}h1{font-size:24px;margin-bottom:8px}p{line-height:1.45}.pair{display:flex;gap:24px;flex-wrap:wrap}figure{margin:0}figcaption{margin:8px 0;font-weight:600}img{width:256px;height:256px;object-fit:contain}button{font:inherit;padding:10px 14px;margin:6px 8px 6px 0;cursor:pointer}button:disabled{cursor:default;opacity:.5}button[aria-pressed=true]{outline:3px solid #1657a8}textarea{font:inherit;width:min(95%,650px);height:62px}#stop{background:#fff0db;padding:14px;border:2px solid #9a5c00}#status{min-height:26px;font-weight:600}.small{font-size:14px}label{display:block;margin:12px 0}input[type=file]{max-width:100%}hr{border:0;border-top:1px solid #ddd;margin:18px 0}
</style><h1>Check that acceptable photographs stay acceptable</h1>
<p>Compare the input and candidate. Does the candidate introduce an <strong>unwanted change</strong>? A slight difference can still be acceptable. Use your usual review display and settings.</p>
<p id="progress"></p><div class="pair"><figure><figcaption>Input</figcaption><img id="input" alt="Input photograph"></figure><figure><figcaption>Candidate</figcaption><img id="candidate" alt="Candidate photograph"></figure></div>
<p>Is the candidate acceptable for this already acceptable input?</p>
<div id="answers"><button data-value="acceptable" aria-pressed="false">Acceptable, including a slight acceptable difference</button><button data-value="unwanted" aria-pressed="false">Unwanted change</button><button data-value="uncertain" aria-pressed="false">Unsure</button></div>
<label>Optional note<br><textarea id="note" aria-label="Optional note"></textarea></label>
<div id="stop" hidden>Review stopped. Save this result. Leave the remaining cases unrated.</div>
<div><button id="back">Previous</button><button id="next">Next</button><button id="clear">Clear current answer</button></div><p id="status" aria-live="polite"></p><hr>
<button id="save">Save review</button><label class="small">Load a previously saved review <input id="load" type="file" accept="application/json"></label>
<p class="small">Your selections are saved in this browser as you work. Download the review before closing. This check is about preserving acceptable appearance; correction usefulness is assessed separately.</p>
<script>const CONFIG=__CONFIG__;
const key='truehue_identity_'+CONFIG.manifest_sha256;
const allowed=['acceptable','unwanted','uncertain'];
let answers={},events=[],cursor=0;
const el=id=>document.getElementById(id);
function valid(data){if(data.schema!=='truehue_identity_review_v1'||data.manifest_sha256!==CONFIG.manifest_sha256||data.qa_fixture!==CONFIG.qa_fixture)throw Error('This file belongs to another review.');for(const [id,a] of Object.entries(data.answers||{})){if(!CONFIG.cases.some(c=>c.review_id===id)||!allowed.includes(a.value)||typeof a.note!=='string')throw Error('Invalid saved answer.');}return data;}
function stopped(){return CONFIG.cases.findIndex(c=>answers[c.review_id]&&answers[c.review_id].value!=='acceptable');}
function payload(){const s=stopped(),complete=CONFIG.cases.every(c=>answers[c.review_id]?.value==='acceptable');return {schema:'truehue_identity_review_v1',manifest_sha256:CONFIG.manifest_sha256,qa_fixture:CONFIG.qa_fixture,review_kind:'identity_no_unwanted_change',status:s>=0?'stopped_'+answers[CONFIG.cases[s].review_id].value:complete?'complete_acceptable':'partial',answers,events,saved_at:new Date().toISOString()};}
function persist(){try{localStorage.setItem(key,JSON.stringify(payload()));}catch(e){el('status').textContent='Browser saving unavailable. Use Save review.';}}
function show(){let stop=stopped();if(stop>=0&&cursor>stop)cursor=stop;const c=CONFIG.cases[cursor],a=answers[c.review_id];el('input').src=c.input;el('candidate').src=c.candidate;el('progress').textContent='Case '+(cursor+1)+' of '+CONFIG.cases.length;el('note').value=a?.note||'';for(const b of document.querySelectorAll('[data-value]'))b.setAttribute('aria-pressed',String(a?.value===b.dataset.value));el('back').disabled=cursor===0;el('next').disabled=!a||stop>=0||cursor===CONFIG.cases.length-1;el('stop').hidden=stop<0;el('status').textContent=stop>=0?'Stopped: save your result.':payload().status==='complete_acceptable'?'All 11 cases checked. Save your review.':Object.keys(answers).length+' of '+CONFIG.cases.length+' answered.';}
for(const b of document.querySelectorAll('[data-value]'))b.addEventListener('click',()=>{let c=CONFIG.cases[cursor];answers[c.review_id]={value:b.dataset.value,note:el('note').value};events.push({review_id:c.review_id,value:b.dataset.value,at:new Date().toISOString()});persist();show();});
el('note').addEventListener('input',()=>{let a=answers[CONFIG.cases[cursor].review_id];if(a){a.note=el('note').value;persist();}});
el('next').onclick=()=>{if(!el('next').disabled){cursor++;show();}};
el('back').onclick=()=>{if(cursor>0){cursor--;show();}};
el('clear').onclick=()=>{const id=CONFIG.cases[cursor].review_id;delete answers[id];events.push({review_id:id,value:'cleared',at:new Date().toISOString()});persist();show();};
el('save').onclick=()=>{const blob=new Blob([JSON.stringify(payload(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=CONFIG.qa_fixture?'identity-review-QA.json':'truehue-identity-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);el('status').textContent='Review downloaded. Keep the saved file.';};
el('load').onchange=async e=>{try{const d=valid(JSON.parse(await e.target.files[0].text()));answers=d.answers;events=d.events||[];cursor=stopped()>=0?stopped():Math.max(0,CONFIG.cases.findIndex(c=>!answers[c.review_id]));persist();show();}catch(err){el('status').textContent='Could not load: '+err.message;}};
try{const raw=localStorage.getItem(key);if(raw){const d=valid(JSON.parse(raw));answers=d.answers;events=d.events||[];cursor=stopped()>=0?stopped():Math.max(0,CONFIG.cases.findIndex(c=>!answers[c.review_id]));}}catch(e){}
show();</script></html>'''

def main():
    if OUT.exists():raise FileExistsError(OUT)
    proof=json.loads((RUN/'verification_PRIVATE.json').read_text())
    summary=json.loads((RUN/'evaluation/summary.json').read_text())
    assert proof['passed'] and proof['numeric_status']==summary['status']=='NUMERIC_PREDICTION_ELIGIBLE_ONLY'
    hashes={Path(k).as_posix():v for k,v in proof['artifact_sha256'].items()}
    held=json.loads((RUN/'models/held_controls_sealed.json').read_text())
    identities=[r for r in held if r['role']=='identity'];assert len(identities)==11
    # Prioritize changed outputs for early-stop efficiency; all11 remain in review.
    def change(r):
        return json.loads((RUN/'evaluation'/(r['case_id']+'.json')).read_text())['identity_changed_pixels']
    identities.sort(key=lambda r:(change(r)==0,r['source_id']))
    OUT.mkdir();(OUT/'images').mkdir()
    manifest=[]
    for i,r in enumerate(identities,1):
        relative='evaluation/'+r['case_id']+'.npz';assert sha(RUN/relative)==hashes[relative]
        with np.load(RUN/relative,allow_pickle=False) as pack:images={k:pack[k].copy() for k in ['input','tree']}
        record=dict(review_id=f'identity_{i:02d}',case_id=r['case_id'],source_id=r['source_id'],cached_pack_sha256=hashes[relative])
        for field,keyname in [('input','input'),('candidate','tree')]:
            path=OUT/'images'/f'{i:02d}_{field}.png';Image.fromarray(images[keyname]).save(path)
            np.testing.assert_array_equal(np.asarray(Image.open(path)),images[keyname])
            record[field]=str(path.relative_to(OUT)).replace('\\','/')
            record[field+'_sha256']=sha(path)
        record['pixel_identical']=bool(np.array_equal(images['input'],images['tree']))
        manifest.append(record)
    body=dict(review_kind='identity_no_unwanted_change',cases=manifest,source_verification_sha256=sha(RUN/'verification_PRIVATE.json'),
              policy='all11; slight acceptable permitted; stop unwanted/uncertain; no automatic reuse or generated human ratings')
    (OUT/'manifest_PRIVATE.json').write_text(json.dumps(body,indent=2),encoding='utf-8')
    digest=sha(OUT/'manifest_PRIVATE.json')
    config=dict(manifest_sha256=digest,qa_fixture=False,cases=[{k:r[k] for k in ['review_id','input','candidate']} for r in manifest])
    (OUT/'index.html').write_text(TEMPLATE.replace('__CONFIG__',json.dumps(config)),encoding='utf-8')
    # Functional QA has synthetic image pairs and separate bindings/storage/download names.
    qa=OUT/'qa';qa.mkdir()
    Image.fromarray(np.full((256,256,3),128,np.uint8)).save(qa/'fixture.png')
    fixture=dict(manifest_sha256='generated_ui_fixture_not_scientific_ratings',qa_fixture=True,
                 cases=[dict(review_id=f'qa_{i:02d}',input='fixture.png',candidate='fixture.png') for i in range(1,12)])
    (qa/'index.html').write_text(TEMPLATE.replace('__CONFIG__',json.dumps(fixture)),encoding='utf-8')
    (OUT/'preparation_PRIVATE.json').write_text(json.dumps(dict(cases=11,pixel_identical=sum(r['pixel_identical'] for r in manifest),
        changed=2,manifest_sha256=digest,ratings_collected=0,qa_fixture_separate=True,
        code_sha256=sha(Path(__file__)),index_sha256=sha(OUT/'index.html')),indent=2),encoding='utf-8')
    print('Prepared11identity cases,9pixelidentical/2changed; no human ratings or corrections generated.')
if __name__=='__main__':main()
