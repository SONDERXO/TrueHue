'use strict';
const spec=JSON.parse(document.getElementById('data').textContent);
const el=id=>document.getElementById(id), canvas=el('canvas'),ctx=canvas.getContext('2d');
const key='truehue-skin-patches-'+spec.manifest_sha256;
let state={reviewer:'',rows:spec.rows.map(r=>({review_id:r.review_id,image_sha256:r.image_sha256,status:'',notes:'',polygons:[]}))};
let index=0,draft=[],loaded=false;
const current=()=>state.rows[index], source=()=>spec.rows[index];
function validPolygon(p,w,h){
  if(!Array.isArray(p)||p.length<3||p.length>200)return false;
  if(p.some(v=>!Array.isArray(v)||v.length!==2||!v.every(Number.isInteger)||v[0]<0||v[1]<0||v[0]>=w||v[1]>=h))return false;
  if(new Set(p.map(v=>v.join(','))).size!==p.length)return false;
  const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const on=(a,b,c)=>cross(a,b,c)===0&&Math.min(a[0],b[0])<=c[0]&&c[0]<=Math.max(a[0],b[0])&&Math.min(a[1],b[1])<=c[1]&&c[1]<=Math.max(a[1],b[1]);
  for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++){
    if(j===i+1||(i===0&&j===p.length-1))continue;
    const a=p[i],b=p[(i+1)%p.length],c=p[j],d=p[(j+1)%p.length];
    if((cross(a,b,c)*cross(a,b,d)<0&&cross(c,d,a)*cross(c,d,b)<0)||on(a,b,c)||on(a,b,d)||on(c,d,a)||on(c,d,b))return false;
  }
  return Math.abs(p.reduce((s,a,i)=>{const b=p[(i+1)%p.length];return s+a[0]*b[1]-a[1]*b[0];},0))>0;
}
function validState(s){return s&&typeof s.reviewer==='string'&&Array.isArray(s.rows)&&s.rows.length===spec.rows.length&&s.rows.every((r,i)=>{
  const b=spec.rows[i];return r.review_id===b.review_id&&r.image_sha256===b.image_sha256&&['','marked','unavailable'].includes(r.status)&&typeof r.notes==='string'&&Array.isArray(r.polygons)&&r.polygons.every(p=>validPolygon(p,b.width,b.height));
});}
try{const saved=JSON.parse(localStorage.getItem(key));if(validState(saved))state=saved;}catch(_){}
let picture=null;
function message(s){el('message').textContent=s;}
function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch(_){message('Storage unavailable. Download a draft before closing.');}}
function paint(){
 ctx.clearRect(0,0,512,512);ctx.imageSmoothingEnabled=false;if(picture)ctx.drawImage(picture,0,0,512,512);
 const draw=(points,closed)=>{if(!points.length)return;ctx.beginPath();points.forEach((p,i)=>{const x=(p[0]+.5)*512/source().width,y=(p[1]+.5)*512/source().height;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});if(closed){ctx.closePath();ctx.fillStyle='#00d98b30';ctx.fill();}ctx.strokeStyle=closed?'#00ff9a':'#ffdc00';ctx.lineWidth=2;ctx.stroke();};
 if(el('show').checked)current().polygons.forEach(p=>draw(p,true));draw(draft,false);
 el('count').textContent=current().polygons.length+' saved patches; '+draft.length+' draft vertices';
}
function show(){
 loaded=false;picture=null;el('title').textContent='Photo '+(index+1)+' of '+spec.rows.length;
 el('context').src=source().context_path;el('notes').value=current().notes;el('status').value=current().status;
 el('reviewer').value=state.reviewer;paint();const chosen=index,img=new Image();
 img.onload=()=>{if(index!==chosen)return;picture=img;loaded=true;paint();};img.onerror=()=>message('Image failed to load; do not mark a blank image.');img.src=source().image_path;
}
canvas.addEventListener('pointerdown',e=>{
 if(!loaded)return;const b=canvas.getBoundingClientRect(),x=e.clientX-b.left,y=e.clientY-b.top;
 if(x<0||y<0||x>=b.width||y>=b.height)return;
 if(current().status==='unavailable'){message('Change status before drawing patches.');return;}
 const p=[Math.floor(x*source().width/b.width),Math.floor(y*source().height/b.height)];
 if(!draft.some(v=>v[0]===p[0]&&v[1]===p[1]))draft.push(p);paint();
});
el('finish').onclick=()=>{if(!validPolygon(draft,source().width,source().height)){message('Use at least three distinct vertices forming a non-crossing patch.');return;}current().polygons.push(draft);draft=[];current().status='marked';el('status').value='marked';save();paint();message('Patch saved. Add another only if clearly visible.');};
el('undo').onclick=()=>{draft.pop();paint();};el('cancel').onclick=()=>{draft=[];paint();};
el('remove').onclick=()=>{current().polygons.pop();if(!current().polygons.length){current().status='';el('status').value='';}save();paint();};
for(const [id,step] of [['prev',-1],['next',1]])el(id).onclick=()=>{if(draft.length){message('Finish or cancel the draft first.');return;}index=Math.max(0,Math.min(spec.rows.length-1,index+step));show();};
el('status').onchange=()=>{if(el('status').value==='unavailable'&&(draft.length||current().polygons.length)){el('status').value=current().status;message('Remove saved patches and cancel the draft before marking unavailable.');return;}current().status=el('status').value;save();};
el('notes').oninput=()=>{current().notes=el('notes').value;save();};el('reviewer').oninput=()=>{state.reviewer=el('reviewer').value;save();};el('show').onchange=paint;
function download(final){
 if(draft.length){message('Finish or cancel the draft first.');return;}
 if(final&&(!state.reviewer.trim()||state.rows.some(r=>!(r.status==='marked'&&r.polygons.length||r.status==='unavailable'&&!r.polygons.length&&r.notes.trim())))){message('Enter reviewer name/code and complete all six: patches marked, or unavailable with a reason.');return;}
 const value={schema_version:'truehue_skin_patch_review_v1',manifest_sha256:spec.manifest_sha256,reviewer:state.reviewer,draft:!final,rows:state.rows};
 const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=final?'truehue_skin_patch_review.json':'truehue_skin_patch_draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message(final?'Review exported. Keep this file private.':'Draft downloaded.');
}
el('export').onclick=()=>download(true);el('draft').onclick=()=>download(false);
el('import').onchange=async e=>{try{const v=JSON.parse(await e.target.files[0].text());if(v.schema_version!=='truehue_skin_patch_review_v1'||v.manifest_sha256!==spec.manifest_sha256||!validState(v))throw Error('Wrong set or invalid patches');state={reviewer:v.reviewer,rows:v.rows};draft=[];save();show();message('Draft imported.');}catch(err){message('Import failed: '+err.message);}e.target.value='';};
show();
