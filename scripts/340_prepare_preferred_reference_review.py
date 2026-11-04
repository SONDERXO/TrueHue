"""Review new source/region judgments only, with exact file bindings."""
import hashlib
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main(parent=None,out=None):
    parent=parent or ROOT/'outputs/preferred_support_cohort_v1';out=out or ROOT/'outputs/preferred_reference_review_v1'
    if out.exists():raise FileExistsError(out)
    rows=json.loads((parent/'records.json').read_text());out.mkdir()
    manifest=[];cards=[];failures=[]
    for row in rows:
        if row['measurement']['status']!='success':
            failures.append(dict(image_id=row['image_id'],reason=row['measurement'].get('reason'),stage=row['measurement']['stage']))
            continue
        required=['correction_mask'] if row['kind']=='anchor' else ['source','measurement_mask','correction_mask']
        item=dict(image_id=row['image_id'],kind=row['kind'],required=required,
            input_path=row['input_path'],input_sha256=hashlib.sha256((ROOT/row['input_path']).read_bytes()).hexdigest(),
            mask_paths=row['mask_paths'],mask_sha256=row['mask_sha256'],original_source_decision=row['original_source_decision'])
        manifest.append(item);key=Path(row['image_id']).stem
        link='../'+parent.name+'/'+row['board_path']
        controls=''
        for field,label in [('source','Photo suitable as a photographic reference'),('measurement_mask','Facial measurement mask'),('correction_mask','Face + neck + brows + lips correction mask')]:
            if field in required:
                controls+=f'<p><label>{label}: <select id="{key}_{field}"><option value="pending">Choose</option><option value="accept">Accept</option><option value="reject">Reject</option><option value="uncertain">Uncertain</option></select></label></p>'
        cards.append('<section><h2>'+html.escape(row['image_id'])+'</h2><p>'+('Source and facial-mask decisions retained; only the NEW combined correction region needs review.' if row['kind']=='anchor' else 'Additional training-role source; prior development processing exposure, no collected source decision. Distinct person identity is not verified.')+'</p><img src="'+link+'">'+controls+f'<label>Notes: <textarea id="{key}_notes" rows="2"></textarea></label></section>')
    payload=dict(schema_version='truehue_preferred_reference_review_v1',rows=manifest,failures=failures,
        measurement_contract_sha256=json.loads((parent/'plan.json').read_text())['measurement_contract_sha256'],
        automatic_training=False,scope='exact_reference_judgments_only_not_variant_approval')
    raw=json.dumps(payload,indent=2).encode();(out/'manifest.json').write_bytes(raw)
    identity=hashlib.sha256(raw).hexdigest()
    data=json.dumps([dict(image_id=r['image_id'],key=Path(r['image_id']).stem,required=r['required']) for r in manifest]).replace('<','\\u003c')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Preferred-support reference review</title>
<style>body{font:18px/1.5 system-ui;max-width:1300px;margin:25px auto;padding:20px;background:#faf8f5}img{width:100%}section{background:white;padding:20px;margin:25px 0;border:1px solid #ccc}select,textarea,button{font:inherit;padding:8px}textarea{width:95%}#bar{position:sticky;top:0;background:#fff0c8;padding:15px}</style>
<h1>References for the preferred correction regions</h1><p>Panels: original; green face / cyan neck / pink brows and lips; facial measurement mask; combined correction mask.</p>
<p>For new sources, reject or mark uncertain if blur, heavy color casts, lighting, occlusion or filtering makes the photo unsuitable as a reconstruction reference. Visual suitability is not calibrated true color. Check measurement-mask exclusions separately from correction coverage. Correction intentionally includes brows/lips and visible neck; eyes, mouth interior/teeth, hair, clothing, jewelry and background should stay out. If a source is rejected or uncertain, its mask judgments may stay unchosen.</p>
<p>For the six anchor photos, your accepted source/facial-mask decisions are kept. Only the newly expanded correction support needs judgment. No variant approvals or training admission follow automatically.</p>
<div id="bar"><span id="count"></span> <button id="export">Download decisions</button><span id="message"></span></div>'''+''.join(cards)+'<h2>Technical holds — no review requested</h2>'+''.join('<p>'+html.escape(r['image_id'])+': '+html.escape(str(r['reason']))+'</p>' for r in failures)+f'''<script>
const rows={data};const mh='{identity}';const sk='truehue_preferred_refs_'+mh;
function collect(){{return rows.map(r=>({{image_id:r.image_id,decisions:Object.fromEntries(r.required.map(k=>[k,document.getElementById(r.key+'_'+k).value])),notes:document.getElementById(r.key+'_notes').value}}));}}
function done(r){{const d=r.decisions;if(d.source==='reject'||d.source==='uncertain')return true;return Object.values(d).every(v=>v!=='pending');}}
function update(){{const v=collect();document.getElementById('count').textContent=v.filter(done).length+' / '+rows.length+' photos complete';try{{localStorage.setItem(sk,JSON.stringify(v));}}catch(e){{}}}}
try{{for(const saved of JSON.parse(localStorage.getItem(sk)||'[]')){{const r=rows.find(x=>x.image_id===saved.image_id);if(r){{for(const k of r.required)document.getElementById(r.key+'_'+k).value=saved.decisions[k]||'pending';document.getElementById(r.key+'_notes').value=saved.notes||'';}}}}}}catch(e){{}}
document.querySelectorAll('select,textarea').forEach(e=>e.addEventListener('input',update));update();
document.getElementById('export').addEventListener('click',()=>{{const b=new Blob([JSON.stringify({{schema_version:'truehue_preferred_reference_decisions_v1',manifest_sha256:mh,rows:collect()}},null,2)],{{type:'application/json'}});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='truehue_preferred_reference_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);document.getElementById('message').textContent=' Save the JSON in this review folder.';}});
</script></html>'''
    (out/'review.html').write_text(page,encoding='utf-8');(out/'review-script.js').write_text(page.split('<script>')[1].split('</script>')[0],encoding='utf-8')
    print(json.dumps(dict(reference_rows=len(manifest),new_sources=sum(r['kind']=='new_candidate' for r in manifest),
        retained_anchor_sources=6,maximum_decisions=sum(len(r['required']) for r in manifest),technical_holds=len(failures),manifest_sha256=identity),indent=2))


if __name__=='__main__':main()
