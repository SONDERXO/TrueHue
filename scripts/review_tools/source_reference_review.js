(function(){
'use strict';
const scopes=['reference_suitability','reference_mask','displayed_stress_mask'];
const decisions=new Set(['','accept','reject','uncertain']);
function validate(value,spec){
  if(!value||value.schema_version!=='truehue_source_reference_review_v1'||value.spec_sha256!==spec.spec_sha256)throw Error('Review specification mismatch');
  if(!value.reviews||typeof value.reviews!=='object'||Array.isArray(value.reviews))throw Error('Review records required');
  const ids=new Set(spec.sources.map(r=>r.image_id));
  if(Object.keys(value.reviews).length!==ids.size)throw Error('Exact source membership required');
  for(const [id,entry] of Object.entries(value.reviews)){
    if(!ids.has(id)||!entry||Object.keys(entry).length!==scopes.length)throw Error('Unexpected source or scope');
    for(const scope of scopes){const r=entry[scope];if(!r||!decisions.has(r.decision)||typeof r.notes!=='string')throw Error('Invalid scoped judgment');}
  }
  return value;
}
function empty(spec){return Object.fromEntries(spec.sources.map(r=>[r.image_id,Object.fromEntries(scopes.map(s=>[s,{decision:'',notes:''}]))]));}
function payload(spec,reviews){return validate({schema_version:'truehue_source_reference_review_v1',spec_sha256:spec.spec_sha256,exported_at:new Date().toISOString(),reviews},spec);}
if(typeof module!=='undefined'&&module.exports){module.exports={validate,empty,payload};return;}
const spec=JSON.parse(document.getElementById('spec').textContent),key='truehue-source-reference:'+spec.spec_sha256;
let reviews=empty(spec),saved=true;
try{const stored=localStorage.getItem(key);if(stored)reviews=validate(JSON.parse(stored),spec).reviews;}catch(e){saved=false;}
function update(){
 const n=Object.values(reviews).flatMap(r=>Object.values(r)).filter(r=>r.decision).length;
 document.getElementById('status').textContent=`${n} / 9 judgments recorded. ${saved?'Saved in this browser.':'Browser saving unavailable; export a backup.'} No training admission.`;
}
function save(){try{localStorage.setItem(key,JSON.stringify(payload(spec,reviews)));saved=true;}catch(e){saved=false;}update();}
const labels={reference_suitability:'Original reference quality',reference_mask:'Exact original-reference mask',displayed_stress_mask:'Exact displayed distorted mask'};
const help={reference_suitability:'Is the original usable for reconstructing its recorded color and detail? Consider blur, lighting, filters and foreign material. This does not certify true skin color.',reference_mask:'Check facial coverage, hair, eyes, mouth, clothing and background. Acceptance applies only to this saved mask.',displayed_stress_mask:'Check this distorted mask independently. Acceptance does not remove clipping or apply to future variants.'};
for(const r of spec.sources){
 const section=document.createElement('section'),heading=document.createElement('h2'),note=document.createElement('p'),panels=document.createElement('div');
 heading.textContent='Source '+r.source_id;note.textContent=r.observation+' Clipped generation support: '+(100*r.clipping_fraction).toFixed(2)+'%.';panels.className='panels';section.append(heading,note,panels);
 ['Original','Original mask','Distorted input','Distorted mask'].forEach((name,i)=>{const fig=document.createElement('figure'),caption=document.createElement('figcaption'),view=document.createElement('div'),img=document.createElement('img');caption.textContent=name;view.className='panel';img.src=r.board_url;img.alt=r.source_id+': '+name;img.style.transform=`translateX(-${i*25}%)`;view.append(img);fig.append(caption,view);panels.append(fig);});
 const link=document.createElement('a');link.href=r.board_url;link.target='_blank';link.rel='noopener';link.textContent='Open full-size board';section.append(link);
 for(const scope of scopes){const field=document.createElement('fieldset'),legend=document.createElement('legend'),explain=document.createElement('p'),label=document.createElement('label'),select=document.createElement('select'),notesLabel=document.createElement('label'),notes=document.createElement('textarea');
 legend.textContent=labels[scope];explain.textContent=help[scope];label.textContent='Decision';select.id=r.source_id+'-'+scope;label.htmlFor=select.id;
 for(const [value,text] of [['','Not reviewed'],['accept','Accept'],['reject','Reject'],['uncertain','Uncertain']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option);}select.value=reviews[r.image_id][scope].decision;
 notes.id=select.id+'-notes';notesLabel.htmlFor=notes.id;notesLabel.textContent='Concerns or reason';notes.value=reviews[r.image_id][scope].notes;
 select.onchange=()=>{reviews[r.image_id][scope].decision=select.value;save();};notes.oninput=()=>{reviews[r.image_id][scope].notes=notes.value;save();};
 field.append(legend,explain,label,select,notesLabel,notes);section.append(field);
 }
 document.getElementById('cases').append(section);
}
document.getElementById('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(payload(spec,reviews),null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='truehue_additional_source3_judgments.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
update();
})();
