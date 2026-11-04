const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict'),crypto=require('crypto');
const folder=process.argv[2]?path.resolve(process.argv[2]):path.resolve(__dirname,'../outputs/preferred_reference_review_v1');
const raw=fs.readFileSync(path.join(folder,'manifest.json')),manifest=JSON.parse(raw),elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:'',textContent:'',handlers:{},addEventListener(n,f){this.handlers[n]=f;}});return elements.get(id);}
for(const r of manifest.rows){for(const field of r.required)element(path.basename(r.image_id,'.jpg')+'_'+field).value='pending';element(path.basename(r.image_id,'.jpg')+'_notes');}
let exported;
const memory=new Map();const context=vm.createContext({document:{getElementById:element,
 querySelectorAll:()=>[...elements.values()],createElement:()=>({click(){}})},
 localStorage:{getItem:k=>memory.get(k)||null,setItem:(k,v)=>memory.set(k,v)},
 Blob:class{constructor(parts){exported=JSON.parse(parts.join(''));}},URL:{createObjectURL:()=> 'mock:',revokeObjectURL(){}},setTimeout:f=>f()});
vm.runInContext(fs.readFileSync(path.join(folder,'review-script.js'),'utf8'),context);
assert.equal(element('count').textContent,'0 / 16 photos complete');
for(const r of manifest.rows){const key=path.basename(r.image_id,'.jpg');for(const field of r.required)element(key+'_'+field).value=field==='source'?'reject':r.kind==='anchor'?'accept':'pending';element(key+'_notes').value='HARNESS ONLY';}
vm.runInContext('update()',context);assert.equal(element('count').textContent,'16 / 16 photos complete');
element('export').handlers.click();assert.equal(exported.rows.length,16);
assert.equal(exported.manifest_sha256,crypto.createHash('sha256').update(raw).digest('hex'));
assert(exported.rows.every(r=>r.notes==='HARNESS ONLY'));
let priorCarryChecked=false;
if(typeof context.importPrevious==='function'){
 const previous=fs.readFileSync(path.resolve(folder,'../preferred_reference_review_v1/manifest.json'));
 for(const r of manifest.rows){const key=path.basename(r.image_id,'.jpg');for(const field of r.required)element(key+'_'+field).value='pending';element(key+'_notes').value='';}
 const prior={schema_version:'truehue_preferred_reference_decisions_v1',manifest_sha256:crypto.createHash('sha256').update(previous).digest('hex'),
  rows:manifest.rows.map(r=>({image_id:r.image_id,decisions:Object.fromEntries(r.required.map(k=>[k,'accept'])),notes:'Earlier note'}))};
 assert.equal(context.importPrevious(prior),20);
 for(const r of manifest.rows){const key=path.basename(r.image_id,'.jpg');assert.equal(element(key+'_correction_mask').value,'pending');}
 assert.throws(()=>context.importPrevious({...prior,manifest_sha256:'wrong'}));
 priorCarryChecked=true;
}
for(const r of manifest.rows){assert(fs.existsSync(path.resolve(folder,'../../',r.input_path)));for(const p of Object.values(r.mask_paths))assert(fs.existsSync(path.resolve(folder,'../../',p)));}
const result={status:'passed',rows:16,initial_pending:true,source_reject_skips_unneeded_mask_judgments:true,
 exact_export_binding:true,notes_preserved:true,all_image_mask_links_exist:true,prior_source_face_only_carry_checked:priorCarryChecked,live_browser_tested:false,simulated_decisions_saved:false};
fs.writeFileSync(path.join(folder,'page_verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
