'use strict';
// Offline annotation only. Never infer labels or modify pipeline masks.
const spec = JSON.parse(document.getElementById('review-data').textContent);
const canvas = document.getElementById('drawing');
const ctx = canvas.getContext('2d');
const colors = {skin: '#16854b', exclude: '#df3434', uncertain: '#dc9a08'};
const storageKey = 'truehue-boundary-review-' + spec.manifest_sha256;
let state = Object.fromEntries(spec.images.map(im => [im.image_id, {polygons: [], notes: '', complete: false}]));
let index = 0, label = 'skin', draft = [], zoom = 3, background = null;
const current = () => spec.images[index];
const annotations = () => state[current().image_id];
const message = text => { document.getElementById('message').textContent = text; };

function validState(candidate) {
  if (!candidate || typeof candidate !== 'object') return false;
  return spec.images.every(im => {
    const a = candidate[im.image_id];
    return a && Array.isArray(a.polygons) && typeof a.notes === 'string' && typeof a.complete === 'boolean' &&
      a.polygons.every(p => Object.hasOwn(colors, p.label) && Array.isArray(p.points) && p.points.length >= 3 &&
        p.points.every(v => Array.isArray(v) && v.length === 2 && Number.isFinite(v[0]) && Number.isFinite(v[1]) &&
          v[0] >= 0 && v[1] >= 0 && v[0] <= im.width - 1 && v[1] <= im.height - 1));
  });
}

function persist() {
  try { localStorage.setItem(storageKey, JSON.stringify(state)); }
  catch (_) { document.getElementById('storage-status').textContent = 'Browser storage unavailable. Download a draft to save.'; }
  document.getElementById('progress').textContent = spec.images.filter(im => state[im.image_id].complete).length + ' / ' + spec.images.length + ' marked complete';
}

function render() {
  const im = current();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (background) ctx.drawImage(background, 0, 0, im.width, im.height);
  function polygon(points, color, closed) {
    if (!points.length) return;
    ctx.beginPath(); ctx.moveTo(...points[0]);
    for (const p of points.slice(1)) ctx.lineTo(...p);
    if (closed) { ctx.closePath(); ctx.fillStyle = color + '38'; ctx.fill(); }
    ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
    for (const p of points) { ctx.beginPath(); ctx.arc(p[0], p[1], 1.2, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); }
  }
  if (document.getElementById('show-polygons').checked) {
    for (const p of annotations().polygons) polygon(p.points, colors[p.label], true);
  }
  polygon(draft, colors[label], false);
  canvas.style.width = im.width * zoom + 'px';
  canvas.style.height = im.height * zoom + 'px';
  document.getElementById('polygon-count').textContent = annotations().polygons.length + ' saved polygons; ' + draft.length + ' draft points';
  const list = document.getElementById('polygon-list'); list.replaceChildren();
  annotations().polygons.forEach((p, i) => {
    const item = document.createElement('li');
    item.textContent = (i + 1) + '. ' + p.label + ' (' + p.points.length + ' vertices) ';
    const button = document.createElement('button'); button.type = 'button'; button.textContent = 'Delete';
    button.addEventListener('click', () => { annotations().polygons.splice(i, 1); annotations().complete = false; sync(); persist(); render(); });
    item.append(button); list.append(item);
  });
}

function sync() {
  document.getElementById('notes').value = annotations().notes;
  document.getElementById('complete').checked = annotations().complete;
}

function selectImage(next) {
  if (draft.length) { message('Finish or cancel the current polygon before switching images.'); return; }
  index = next;
  const im = current(); canvas.width = im.width; canvas.height = im.height; background = null;
  document.getElementById('image-select').value = String(index);
  document.getElementById('image-title').textContent = im.title;
  document.getElementById('image-hint').textContent = im.hint;
  document.getElementById('image-size').textContent = im.width + ' x ' + im.height + ' original pixels';
  sync(); render();
  const selectedId = im.image_id;
  const loaded = new Image(); loaded.onload = () => { if (current().image_id === selectedId) { background = loaded; render(); } };
  loaded.onerror = () => message('Image could not load. Do not annotate a blank canvas.'); loaded.src = im.data_url;
  message('Click around the visible facial skin, then choose Finish polygon.');
}

function intersects(a, b, c, d) {
  const cross = (p, q, r) => (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);
  return cross(a,b,c)*cross(a,b,d) < 0 && cross(c,d,a)*cross(c,d,b) < 0;
}

function finishPolygon() {
  // A final click on the starting vertex closes the outline; it is not a
  // second vertex. Small mouse offsets otherwise create a crossing edge.
  if (draft.length > 3 && Math.hypot(draft[0][0]-draft[draft.length-1][0], draft[0][1]-draft[draft.length-1][1]) <= 6/zoom) draft.pop();
  if (draft.length < 3) { message('Add at least three points.'); return; }
  let area = 0;
  for (let i=0; i<draft.length; i++) {
    const a=draft[i], b=draft[(i+1)%draft.length]; area += a[0]*b[1]-a[1]*b[0];
    for (let j=i+2; j<draft.length; j++) {
      if ((j+1)%draft.length===i) continue;
      if (intersects(a,b,draft[j],draft[(j+1)%draft.length])) { message('Polygon crosses itself. Undo points or cancel and redraw.'); return; }
    }
  }
  if (Math.abs(area) < 2) { message('Polygon is too small or flat.'); return; }
  annotations().polygons.push({label, points: draft.map(p => p.slice())});
  draft=[]; annotations().complete=false; sync(); persist(); render(); message('Polygon saved. Add exclusions or another skin region as needed.');
}

function exportReview() {
  if (draft.length) { message('Finish or cancel the current polygon before exporting.'); return; }
  const images = spec.images.map(im => ({image_id: im.image_id, width: im.width, height: im.height,
    image_sha256: im.image_sha256, ...state[im.image_id]}));
  const data = {version: spec.version, manifest_sha256: spec.manifest_sha256,
    exported_at: new Date().toISOString(), draft: !images.every(im => im.complete),
    coordinate_system: 'original-image pixels, x right/y down; polygons close last vertex to first',
    label_priority: ['exclude', 'uncertain', 'skin'], outside_polygons: 'unlabeled, not automatically background', images};
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'truehue_face_boundary_review.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000); message(data.draft ? 'Draft downloaded. Mark each image complete when ready.' : 'Review downloaded. Return the JSON file path to Codex.');
}

for (const [i, im] of spec.images.entries()) {
  const option=document.createElement('option'); option.value=String(i); option.textContent=im.title; document.getElementById('image-select').append(option);
}
document.getElementById('image-select').addEventListener('change', e => { const next=Number(e.target.value); e.target.value=String(index); selectImage(next); });
document.getElementById('previous').addEventListener('click', () => selectImage(Math.max(0,index-1)));
document.getElementById('next').addEventListener('click', () => selectImage(Math.min(spec.images.length-1,index+1)));
for (const button of document.querySelectorAll('[data-label]')) button.addEventListener('click', () => {
  if (draft.length) { message('Finish or cancel the draft before changing its label.'); return; }
  label=button.dataset.label; document.querySelectorAll('[data-label]').forEach(b => b.setAttribute('aria-pressed', String(b===button))); render();
});
canvas.addEventListener('click', e => {
  if (!background) { message('Wait for the image to load.'); return; }
  const rect=canvas.getBoundingClientRect(), im=current();
  const p=[Math.round(Math.max(0,Math.min(im.width-1,(e.clientX-rect.left)*im.width/rect.width))*100)/100,
    Math.round(Math.max(0,Math.min(im.height-1,(e.clientY-rect.top)*im.height/rect.height))*100)/100];
  if (draft.length && Math.hypot(p[0]-draft[draft.length-1][0],p[1]-draft[draft.length-1][1])<.5) return;
  if (draft.length >= 3 && Math.hypot(p[0]-draft[0][0],p[1]-draft[0][1]) <= 6/zoom) { finishPolygon(); return; }
  draft.push(p); render();
});
document.getElementById('finish').addEventListener('click',finishPolygon);
document.getElementById('undo-point').addEventListener('click',()=>{draft.pop();render();});
document.getElementById('cancel').addEventListener('click',()=>{draft=[];render();message('Draft canceled. Saved polygons unchanged.');});
document.getElementById('zoom').addEventListener('change',e=>{zoom=Number(e.target.value);render();});
document.getElementById('show-polygons').addEventListener('change',render);
document.getElementById('notes').addEventListener('input',e=>{annotations().notes=e.target.value;persist();});
document.getElementById('complete').addEventListener('change',e=>{
  if (e.target.checked && (draft.length || !annotations().polygons.some(p=>p.label==='skin') || !annotations().polygons.some(p=>p.label==='exclude'))) {
    e.target.checked=false;message('Finish the draft and draw skin plus eye/mouth/non-skin exclusions before marking complete.');return;
  }
  annotations().complete=e.target.checked;persist();
});
document.getElementById('download').addEventListener('click',exportReview);
document.getElementById('import').addEventListener('change',async e=>{
  const file=e.target.files[0];if(!file)return;
  try {
    const data=JSON.parse(await file.text());
    if (data.version!==spec.version || data.manifest_sha256!==spec.manifest_sha256 || !Array.isArray(data.images) || data.images.length!==spec.images.length || new Set(data.images.map(r=>r.image_id)).size!==spec.images.length) throw Error('Wrong review set');
    for (const im of spec.images) { const r=data.images.find(a=>a.image_id===im.image_id); if(!r||r.width!==im.width||r.height!==im.height||r.image_sha256!==im.image_sha256)throw Error('Image mismatch'); }
    const candidate=Object.fromEntries(data.images.map(r=>[r.image_id,{polygons:r.polygons,notes:r.notes,complete:r.complete}]));
    if(!validState(candidate))throw Error('Invalid polygons');state=candidate;draft=[];persist();selectImage(index);message('Draft imported.');
  } catch(error) { message('Import failed: '+error.message); }
  e.target.value='';
});
try { const saved=JSON.parse(localStorage.getItem(storageKey)||'null'); if(validState(saved))state=saved; } catch (_) {}
persist(); selectImage(0);
