"""Local, presentation-blinded source review pages; no scores or network use."""
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/photographer_reference_review_v1'


def main():
    if OUT.exists():raise FileExistsError(OUT)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/table2_reviewed_ten_source_evaluation_v1'
    plan=read(parent/'fit_plan.json');verify=read(parent/'verification.json')
    assert digest(parent/'fit_plan.json')==verify['fit_plan_sha256']
    rows=sorted([r for r in plan['rows'] if r['variant']=='identity'],key=lambda r:hashlib.sha256(('reference_review42/'+r['source_image_id']).encode()).hexdigest())
    assert len(rows)==10
    OUT.mkdir();(OUT/'images').mkdir()
    key=[];cases=[]
    for i,r in enumerate(rows,1):
        code=f'R{i:02d}';path=ROOT/r['reference_path'];dest=OUT/'images'/(code+'.png')
        shutil.copyfile(path,dest);assert digest(path)==digest(dest)
        cases.append(dict(case_id=code,image_path='images/'+code+'.png',image_sha256=digest(dest)))
        key.append(dict(case_id=code,source_image_id=r['source_image_id'],reference_path=r['reference_path'],image_sha256=digest(path)))
    orders={reviewer:sorted([c['case_id'] for c in cases],key=lambda c:hashlib.sha256((reviewer+'/reference_review42/'+c).encode()).hexdigest()) for reviewer in ['P1','P2']}
    manifest=dict(schema_version='truehue_reference_suitability_review_v1',purpose='Development reference suitability; not final MOS',cases=cases,reviewer_orders=orders,
        allowed=dict(detail=['adequate','limited','cannot_judge'],illumination=['usable','strong_cast_or_uneven','cannot_judge'],
                     occlusion=['low','substantial','cannot_judge'],decision=['suitable','uncertain','unsuitable']))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');identity=digest(OUT/'manifest.json')
    (OUT/'researcher_key.json').write_text(json.dumps(dict(status='researcher_only_not_reviewer_material',case_sources=key,original_fit_plan_sha256=digest(parent/'fit_plan.json')),indent=2),encoding='utf-8')
    js=r'''
function validateReview(value) {
  const errors=[];
  if(value.schema_version!==manifest.schema_version||value.manifest_sha256!==manifestHash)errors.push('Review version mismatch');
  if(value.reviewer_code!==reviewer||value.photographer_self_declaration!==true)errors.push('Photographer declaration required');
  const ratings=value.ratings||[];
  if(ratings.length!==order.length||new Set(ratings.map(r=>r.case_id)).size!==order.length)errors.push('All ten unique cases required');
  for(const c of order){const r=ratings.find(r=>r.case_id===c);if(!r){errors.push(c+' missing');continue;}
    for(const field of Object.keys(manifest.allowed))if(!manifest.allowed[field].includes(r[field]))errors.push(c+' '+field+' required');
    if(['uncertain','unsuitable'].includes(r.decision)&&!String(r.notes||'').trim())errors.push(c+' reason required');
  }
  return errors;
}
function collect(){return {schema_version:manifest.schema_version,manifest_sha256:manifestHash,reviewer_code:reviewer,
  photographer_self_declaration:document.getElementById('photographer').checked,session_notes:document.getElementById('session-notes').value,
  ratings:order.map(c=>{const r={case_id:c};for(const f of Object.keys(manifest.allowed))r[f]=document.getElementById(c+'-'+f).value;r.notes=document.getElementById(c+'-notes').value;return r;})};}
function saveDraft(){try{localStorage.setItem(storageKey,JSON.stringify(collect()));}catch(e){document.getElementById('status').textContent='Browser draft storage unavailable. Export before closing.';}}
function exportReview(){const value=collect();const errors=validateReview(value);document.getElementById('status').textContent=errors.join('; ');if(errors.length)return;
  value.exported_at_utc=new Date().toISOString();const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='reference-review-'+reviewer+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  document.getElementById('status').textContent='Export created. Keep this original JSON file.';}
function init(){for(const c of order){const meta=manifest.cases.find(r=>r.case_id===c);const section=document.createElement('section');
  const h=document.createElement('h2');h.textContent=c;section.appendChild(h);const img=document.createElement('img');img.src=meta.image_path;img.alt='Reference '+c;section.appendChild(img);
  for(const f of Object.keys(manifest.allowed)){const label=document.createElement('label');label.textContent=f+' ';const select=document.createElement('select');select.id=c+'-'+f;
    const blank=document.createElement('option');blank.value='';blank.textContent='Choose';select.appendChild(blank);
    for(const v of manifest.allowed[f]){const o=document.createElement('option');o.value=v;o.textContent=v.replaceAll('_',' ');select.appendChild(o);}label.appendChild(select);section.appendChild(label);}
  const label=document.createElement('label');label.textContent='Reason / observations ';const notes=document.createElement('textarea');notes.id=c+'-notes';label.appendChild(notes);section.appendChild(label);document.getElementById('cases').appendChild(section);}
  try{const saved=JSON.parse(localStorage.getItem(storageKey)||'null');if(saved&&saved.manifest_sha256===manifestHash&&saved.reviewer_code===reviewer){document.getElementById('photographer').checked=saved.photographer_self_declaration===true;document.getElementById('session-notes').value=saved.session_notes||'';
    for(const r of saved.ratings||[]){for(const f of [...Object.keys(manifest.allowed),'notes']){const el=document.getElementById(r.case_id+'-'+f);if(el)el.value=r[f]||'';}}}}catch(e){}
  document.addEventListener('change',saveDraft);document.addEventListener('input',saveDraft);document.getElementById('export').addEventListener('click',exportReview);}
if(typeof document!=='undefined')init();
'''
    (OUT/'review.js').write_text(js,encoding='utf-8')
    for reviewer in ['P1','P2']:
        setup='const manifest='+json.dumps(manifest)+';const manifestHash='+json.dumps(identity)+';const reviewer='+json.dumps(reviewer)+';const order=manifest.reviewer_orders[reviewer];const storageKey="truehue-reference/"+manifestHash+"/"+reviewer+"/"+location.pathname;'
        html='<!doctype html><html lang="en"><meta charset="utf-8"><title>Reference suitability '+reviewer+'</title><style>body{font:17px system-ui;max-width:800px;margin:25px auto;padding:15px}section{border-top:1px solid #aaa;margin:25px 0;padding:12px}img{width:256px;height:256px;image-rendering:auto}label{display:block;margin:12px 0}select,textarea{font:inherit}textarea{display:block;width:95%;min-height:60px}button{font:inherit;padding:10px}#status{white-space:pre-wrap}</style><h1>Photographic reference suitability — '+reviewer+'</h1><p>Judge these ten processing-frame photos as possible synthetic reconstruction references. Assess visible detail, illumination and occlusion. Do not infer true skin color or assign skin-tone categories. This is development screening, not final correction MOS.</p><p>Review independently; use consistent display/viewing conditions. Record uncertainty, display limitations or recognition in session notes. No model outputs are shown. Nothing is sent over the network. Drafts stay in this browser where storage is available; export the JSON before closing.</p><label><input id="photographer" type="checkbox">I am the photographer reviewing these images independently.</label><label>Session notes / display or recognition limitations<textarea id="session-notes"></textarea></label><main id="cases"></main><button id="export" type="button">Validate and export review</button><p id="status" role="status" aria-live="polite"></p><script>'+setup+'</script><script src="review.js"></script></html>'
        (OUT/(reviewer+'.html')).write_text(html,encoding='utf-8')
    (OUT/'README.md').write_text('# Local photographer reference review\n\nResearcher: keep researcher_key.json private. Have two actual photographers independently open P1.html and P2.html locally. These are reference-suitability judgments, not final MOS. Do not upload images. Each reviewer exports their own completed JSON; no labels are prefilled. Preserve originals and disagreements. No automatic cohort change or fit follows. Browser drafts are convenience only; exported originals are the review evidence.\n',encoding='utf-8')
    print('Prepared two blank local photographer pages; ten references; no ratings collected.')


if __name__=='__main__':main()
