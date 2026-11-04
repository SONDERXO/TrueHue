/* Local-only review annotations; never changes scientific eligibility. */
'use strict';
const spec=JSON.parse(document.getElementById('review-data').textContent);
const $=id=>document.getElementById(id);
const key=`truehue-training-review:${spec.manifest_sha256}:batch${spec.batch}`;
const validDecisions=new Set(['accept','reject','uncertain','']);
let reviews={},current=spec.records[0]?.image_id,storageAvailable=true;
function validate(payload){
  if(payload.manifest_sha256!==spec.manifest_sha256||payload.batch!==spec.batch||payload.schema_version!=='truehue_training_review_v1')throw Error('This backup belongs to a different batch or image manifest.');
  const ids=new Set(spec.records.map(r=>r.image_id));
  if(!payload.reviews||typeof payload.reviews!=='object'||Array.isArray(payload.reviews))throw Error('Invalid review backup.');
  for(const [id,r] of Object.entries(payload.reviews))if(!ids.has(id)||!r||!validDecisions.has(r.decision)||typeof r.notes!=='string')throw Error('Invalid image ID, decision or notes.');
  return payload.reviews;
}
function payload(){return {schema_version:'truehue_training_review_v1',batch:spec.batch,manifest_sha256:spec.manifest_sha256,review_scope:spec.review_scope||'reference_and_distorted_processing',exported_at:new Date().toISOString(),reviews};}
try{const saved=localStorage.getItem(key);if(saved)reviews=validate(JSON.parse(saved));}catch(e){storageAvailable=false;$('storage').textContent='Saved progress could not be loaded. Export a backup to keep this session.';}
function save(){
  try{localStorage.setItem(key,JSON.stringify(payload()));storageAvailable=true;$('storage').textContent='Progress saved in this browser. Export reviews to keep a portable backup.';}
  catch(e){storageAvailable=false;$('storage').textContent='Browser saving unavailable. Your decisions are in this session only — export before closing.';}
}
function filtered(){const query=$('search').value.trim().toLowerCase(),filter=$('filter').value;return spec.records.filter(r=>{
  const decision=reviews[r.image_id]?.decision||'';
  return r.source_id.toLowerCase().includes(query)&&(filter==='all'||(filter==='unreviewed'&&!decision)||(filter==='pending_review'&&r.status==='pending_review')||(filter==='failed'&&r.status!=='pending_review')||(decision&&filter===decision));
});}
function refreshList(){
  const rows=filtered();$('cases').replaceChildren();
  for(const r of rows){const b=document.createElement('button');b.textContent=`${r.source_id} · ${reviews[r.image_id]?.decision||'not reviewed'}`;b.setAttribute('aria-current',String(r.image_id===current));b.onclick=()=>{current=r.image_id;render();};$('cases').append(b);}
  const n=spec.records.filter(r=>reviews[r.image_id]?.decision).length;$('progress').textContent=`${n} / ${spec.records.length} reviewed · ${rows.length} shown`;
  return rows;
}
function panel(r,index,label){
  const figure=document.createElement('figure'),caption=document.createElement('figcaption'),viewport=document.createElement('div'),img=document.createElement('img');
  caption.textContent=label;viewport.className='viewport';img.src=`${spec.board_base||'boards'}/${r.source_id}.png`;img.alt=`${r.source_id}: ${label}`;
  img.style.width=`${r.panel_count*100}%`;img.style.transform=`translateX(-${index*100/r.panel_count}%)`;viewport.append(img);figure.append(caption,viewport);
  viewport.tabIndex=0;viewport.setAttribute('role','button');viewport.setAttribute('aria-label',`Enlarge ${label}`);
  function zoom(){const copy=figure.cloneNode(true);copy.style.width='min(85vw,700px)';copy.style.margin='20px auto';$('zoom-content').replaceChildren(copy);$('zoomed').hidden=false;$('close-zoom').focus();}
  viewport.onclick=zoom;viewport.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();zoom();}};return figure;
}
function render(){
  const rows=refreshList();if(!rows.some(r=>r.image_id===current))current=rows[0]?.image_id;
  const r=spec.records.find(r=>r.image_id===current),article=document.querySelector('article');
  article.hidden=!r;if(!r){$('position').textContent='No matching images';return;}
  refreshList();$('case-title').textContent=`Image ${r.source_id}`;
  $('metadata').textContent=r.comparison_note|| (spec.reference_only?`Image ${r.source_id} · Reference/mask review only · ${r.selection_reason}`:`${r.status.replaceAll('_',' ')} · Experimental MST: ${r.reference_mst_estimate??'unavailable'} · Severity: ${r.assigned_severity??'unavailable'} · Clipped support: ${r.clipping_fraction==null?'unavailable':(r.clipping_fraction*100).toFixed(1)+'%'}`);
  $('warning').textContent=spec.reference_only?`Review ONLY the reference photo and its mask. Selection: ${r.selection_reason}. ${r.failure_reason?'Reference issue: '+r.failure_reason+'. ':''}Accept means reference/mask suitability only; no distorted-image approval or training admission.`:(r.status==='pending_review'?'Reference and input are measurable. Review image and mask suitability before admission.':`Processing excluded: ${r.failure_reason||r.status.replaceAll('_',' ')}. A review decision does not override this failure.`);
  if(spec.review_instructions)$('warning').textContent=spec.review_instructions+(r.failure_reason?' Unavailable: '+r.failure_reason:'');
  $('panels').replaceChildren(...(spec.panel_labels||['Reference','Reference mask','Distorted input','Input mask']).slice(0,spec.reference_only?2:r.panel_count).map((s,i)=>panel(r,i,s)));
  $('board').href=`${spec.board_base||'boards'}/${r.source_id}.png`;$('notes').value=reviews[current]?.notes||'';
  for(const b of document.querySelectorAll('[data-decision]'))b.setAttribute('aria-pressed',String(reviews[current]?.decision===b.dataset.decision));
  const index=rows.findIndex(r=>r.image_id===current);$('position').textContent=`${index+1} of ${rows.length}`;$('previous').disabled=index===0;$('next').disabled=index===rows.length-1;
}
function move(delta){const rows=filtered(),index=rows.findIndex(r=>r.image_id===current),row=rows[index+delta];if(row){current=row.image_id;render();}}
function decide(decision){if(!current)return;const next=filtered()[filtered().findIndex(r=>r.image_id===current)+1]?.image_id;
  reviews[current]={decision,notes:$('notes').value,updated_at:new Date().toISOString()};save();if($('advance').checked&&next)current=next;render();}
for(const b of document.querySelectorAll('[data-decision]'))b.onclick=()=>decide(b.dataset.decision);
$('clear').onclick=()=>decide('');
$('notes').oninput=()=>{if(!current)return;reviews[current]={decision:reviews[current]?.decision||'',notes:$('notes').value,updated_at:new Date().toISOString()};save();};
$('previous').onclick=()=>move(-1);$('next').onclick=()=>move(1);
$('search').oninput=render;$('filter').onchange=render;$('large').onchange=()=>document.body.classList.toggle('large',$('large').checked);
$('close-zoom').onclick=()=>{$('zoomed').hidden=true;};
document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('zoomed').hidden=true;return;}if(!$('zoomed').hidden||['INPUT','TEXTAREA','SELECT','BUTTON'].includes(e.target.tagName)||e.target.isContentEditable)return;
  if(e.key==='ArrowLeft'){e.preventDefault();move(-1);}if(e.key==='ArrowRight'){e.preventDefault();move(1);}if(['1','2','3'].includes(e.key)){e.preventDefault();decide({1:'accept',2:'reject',3:'uncertain'}[e.key]);}});
$('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(payload(),null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=`truehue_batch_${spec.batch}_reviews.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
$('copy').onclick=async()=>{const lines=spec.records.filter(r=>reviews[r.image_id]?.decision).map(r=>`${r.source_id}: ${reviews[r.image_id].decision}${reviews[r.image_id].notes?' — '+reviews[r.image_id].notes:''}`);try{await navigator.clipboard.writeText(lines.join('\n'));$('storage').textContent='Decisions copied.';}catch(e){$('storage').textContent='Clipboard unavailable for this local page. Use Export reviews instead.';}};
$('import').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;const incoming=validate(JSON.parse(await file.text()));if(!confirm('Merge this backup? Incoming entries replace matching image decisions and notes.'))return;reviews={...reviews,...incoming};save();render();}catch(error){$('storage').textContent=`Import failed: ${error.message}`;}finally{e.target.value='';}};
render();if(storageAvailable)$('storage').textContent='Decisions save in this browser. Export reviews for a portable backup.';
