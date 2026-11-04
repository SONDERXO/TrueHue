"""Four fixed user judgments; preserve full comparison and old polygon page."""
import hashlib
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    parent=ROOT/'outputs/faceocc_light_comparison_v1';out=ROOT/'outputs/faceocc_four_review_v1'
    if out.exists():raise FileExistsError(out)
    summary=json.loads((parent/'summary.json').read_text());plan=json.loads((parent/'plan.json').read_text())
    ids=plan['user_review_ids'];assert len(ids)==4
    rows=[];cards=[]
    for row in summary['records']:
        if row['image_id'] not in ids:continue
        board=parent/row['board_path'] if row.get('board_path') else None
        item=dict(image_id=row['image_id'],key=str(row['case_index']),status=row['status'],
            board_path=None if board is None else str(board.relative_to(ROOT)),
            board_sha256=None if board is None else hashlib.sha256(board.read_bytes()).hexdigest())
        rows.append(item)
        fields=[('old_unwanted','Previous method includes unwanted pixels?'),('new_unwanted','With FaceOcc includes unwanted pixels?'),
            ('useful_skin_lost','Does FaceOcc remove useful skin compared with the previous method?')]
        controls=''
        for field,label in fields:
            controls+='<label>'+label+' <select id="'+item['key']+'_'+field+'"><option value="pending">Choose</option><option value="yes">Yes</option><option value="no">No obvious problem</option><option value="uncertain">Uncertain</option><option value="unavailable">Unavailable</option></select></label>'
        controls+='<label>Better overall measurement mask? <select id="'+item['key']+'_preference"><option value="pending">Choose</option><option value="previous">Previous</option><option value="faceocc">With FaceOcc</option><option value="similar">Similar</option><option value="uncertain">Uncertain</option><option value="unavailable">Unavailable</option></select></label>'
        image='<img src="../../'+item['board_path']+'">' if board else '<p>No paired output: '+html.escape(str(row.get('reason',row['status'])))+'</p>'
        cards.append('<section><h2>'+html.escape(row['image_id'])+'</h2>'+image+controls+'<label>Optional notes<textarea id="'+item['key']+'_notes"></textarea></label></section>')
    manifest=dict(schema_version='truehue_faceocc_four_review_v1',rows=rows,subset_selected_before_predictions=True,
        full_attempts=24,scope='qualitative_four_exposed_challenges_not_pixel_accuracy',automatic_adoption=False)
    raw=json.dumps(manifest,indent=2).encode();identity=hashlib.sha256(raw).hexdigest()
    out.mkdir();(out/'manifest.json').write_bytes(raw)
    js='''const rows=ROWS,hash=HASH,fields=['old_unwanted','new_unwanted','useful_skin_lost','preference'];const key='truehue_faceocc_four_'+hash;
function collect(){return rows.map(r=>({image_id:r.image_id,decisions:Object.fromEntries(fields.map(f=>[f,document.getElementById(r.key+'_'+f).value])),notes:document.getElementById(r.key+'_notes').value}));}
function complete(r){return Object.values(r.decisions).every(v=>v!=='pending');}
function update(){const v=collect();document.getElementById('count').textContent=v.filter(complete).length+' / 4 complete';try{localStorage.setItem(key,JSON.stringify(v));}catch(e){}}
try{for(const s of JSON.parse(localStorage.getItem(key)||'[]')){const r=rows.find(r=>r.image_id===s.image_id);if(r){for(const f of fields)document.getElementById(r.key+'_'+f).value=s.decisions[f]||'pending';document.getElementById(r.key+'_notes').value=s.notes||'';}}}catch(e){}
document.querySelectorAll('select,textarea').forEach(e=>e.addEventListener('input',update));update();
document.getElementById('export').onclick=()=>{const values=collect();if(!values.every(complete)){document.getElementById('message').textContent=' Finish the four cases; uncertain is allowed.';return;}const value={schema_version:'truehue_faceocc_four_decisions_v1',manifest_sha256:hash,rows:values};const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='truehue_faceocc_four_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);document.getElementById('message').textContent=' Save the JSON in this review folder.';};'''.replace('ROWS',json.dumps(rows)).replace('HASH',json.dumps(identity))
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Four FaceOcc judgments</title><style>body{font:18px/1.5 system-ui;max-width:1200px;margin:auto;padding:24px;background:#faf8f4}section{background:white;border:1px solid #ccc;padding:20px;margin:24px 0}img{width:100%}label{display:block;margin:16px 0}select,textarea,button{font:inherit;padding:8px}textarea{width:95%;height:65px}#bar{position:sticky;top:0;background:#fff0bf;padding:12px}</style><h1>Four cases — no drawing</h1><p>Panels: original; previous measurement mask; previous mask with FaceOcc veto. Green means pixels used for measurement, NOT correction coverage. Excluding eyes, brows, lips, hair and neck is intentional. Look for unwanted pixels and loss of actual facial skin. FaceOcc is not yet adopted.</p><p>These four known challenge cases were selected before predictions. Your judgments are separate from assistant observations; uncertainty is welcome. The full24attempts, including all failures, remain saved.</p><div id="bar"><span id="count"></span> <button id="export">Download decisions</button><span id="message"></span></div>'+''.join(cards)+'<script>'+js+'</script></html>'
    (out/'review.html').write_text(page,encoding='utf-8');(out/'review.js').write_text(js,encoding='utf-8')
    print('Four fixed cases ready: '+str(out/'review.html'))


if __name__=='__main__':main()
