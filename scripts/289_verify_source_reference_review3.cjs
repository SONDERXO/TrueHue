/* Annotation integrity and DOM smoke checks; synthetic decisions stay in memory. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),out=path.join(root,'outputs/additional_source_reference_review3_v1');
const spec=JSON.parse(fs.readFileSync(path.join(out,'spec.json'),'utf8'));
const {validate,empty,payload}=require('./review_tools/source_reference_review.js');
const initial=payload(spec,empty(spec));
assert.equal(Object.values(initial.reviews).flatMap(Object.values).filter(r=>r.decision).length,0);
assert.deepEqual(validate(JSON.parse(JSON.stringify(initial)),spec),initial);
for(const change of [p=>p.spec_sha256='wrong',p=>p.reviews.unknown={},p=>delete p.reviews[spec.sources[0].image_id].reference_mask,p=>p.reviews[spec.sources[0].image_id].reference_mask.decision='approved',p=>p.reviews[spec.sources[0].image_id].reference_mask.notes=null]){
 const altered=structuredClone(initial);change(altered);assert.throws(()=>validate(altered,spec));
}
class Element{constructor(tag){this.tag=tag;this.children=[];this.style={};this.value='';this.textContent='';}append(...items){this.children.push(...items);}click(){if(this.onclick)this.onclick();}}
const elements=Object.fromEntries(['spec','cases','status','export'].map(id=>[id,new Element(id)]));elements.spec.textContent=JSON.stringify(spec);
const document={getElementById:id=>elements[id],createElement:tag=>new Element(tag)};
const storage=new Map();let exported;
const context={document,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},Blob,
 URL:{createObjectURL:b=>{exported=b;return 'test:download';},revokeObjectURL:()=>{}},setTimeout:f=>f()};
vm.runInNewContext(fs.readFileSync(path.join(out,'source_reference_review.js'),'utf8'),context);
const all=[];function walk(e){all.push(e);e.children.forEach(walk);}walk(elements.cases);
const selects=all.filter(e=>e.tag==='select'),notes=all.filter(e=>e.tag==='textarea'),imgs=all.filter(e=>e.tag==='img');
assert.equal(selects.length,9);assert.equal(notes.length,9);assert.equal(imgs.length,12);
assert.ok(selects.every(e=>e.value===''));
assert.match(elements.status.textContent,/0 \/ 9/);
selects[0].value='uncertain';selects[0].onchange();notes[0].value='Synthetic check only';notes[0].oninput();
assert.match(elements.status.textContent,/1 \/ 9/);assert.ok(selects.slice(1).every(e=>e.value===''));
elements.export.click();
(async()=>{
 const p=JSON.parse(await exported.text());validate(p,spec);
 assert.equal(Object.values(p.reviews).flatMap(Object.values).filter(r=>r.decision).length,1);
 assert.equal(p.reviews[spec.sources[0].image_id].reference_mask.decision,'');
 for(const r of spec.sources){const board=path.resolve(out,r.board_url);assert.equal(crypto.createHash('sha256').update(fs.readFileSync(board)).digest('hex'),r.board_sha256);}
 const html=fs.readFileSync(path.join(out,'review.html'),'utf8');assert.ok(!html.includes('__SPEC__'));
 const embedded=JSON.parse(html.match(/<script id="spec" type="application\/json">([\s\S]*?)<\/script>/)[1]);assert.deepEqual(embedded,spec);
 const report={status:'pass',blank_default_judgments:9,independent_scope_updates:true,export_roundtrip:true,invalid_payloads_rejected:5,board_hashes_verified:3,dom_smoke_pass:true,real_browser_visual_check:'unavailable_no_connected_browser',synthetic_decisions_persisted_to_disk:false};
 fs.writeFileSync(path.join(out,'interaction_verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})();
