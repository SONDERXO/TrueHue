"""Freeze candidate lanes and a source-grouped review; never train or infer labels."""
import hashlib
import html
import json
import os
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/primary_training_review_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    preparations=[ROOT/'outputs/primary_training_preparation_v1',ROOT/'outputs/gamma_exposure_controls_v1']
    attempts=[]
    for folder in preparations:
        verification=read(folder/'verification.json');assert verification['status']=='pass'
        for path,digest in verification['evidence_sha256'].items():assert sha(folder/path)==digest
        attempts.extend(read(folder/'attempts.json'))
    assert len(attempts)==156 and len({r['pair_id'] for r in attempts})==156
    primary=[r for r in attempts if r['lane']=='primary_pending_exact_mask_review'];assert len(primary)==61
    endpoint=ROOT/'outputs/endpoint_feature_tree_v1';parent=read(endpoint/'plan.json')
    known={}
    for row in parent['rows']:
        if row['variant']=='identity':continue
        key=(sha(ROOT/row['input_path']),sha(ROOT/row['input_mask_path']),parent['measurement_contract_sha256'])
        known[key]=dict(decision='accept',notes=row.get('exact_review_notes',row.get('review_concern','')),pair_id=row['pair_id'])
    review_parent=ROOT/'outputs/distorted_mask_review11_v1'
    old_reviews=read(review_parent/'truehue_distorted_mask_review11_decisions.json')['reviews']
    for row in read(review_parent/'manifest.json')['rows']:
        entry=old_reviews[row['image_id']]
        known[(row['input_sha256'],row['input_mask_sha256'],parent['measurement_contract_sha256'])]=dict(entry)
    matches=[]
    for r in primary:
        match=known.get((r['input_sha256'],r['input_mask_sha256'],parent['measurement_contract_sha256']))
        if match:matches.append(dict(pair_id=r['pair_id'],exact_previous_evidence=match))
    # No derived-mask acceptance is inferred. Unexpected exact matches need an
    # explicit import provenance path instead of silently preselecting the UI.
    assert not matches
    out.mkdir();(out/'boards').mkdir();queue=[]
    for r in primary:
        image=cv2.imread(str(ROOT/r['input_path']));mask=cv2.imread(str(ROOT/r['input_mask_path']),0)>0
        shown=image.copy();shown[mask]=(.5*shown[mask]+np.array([0,150,0])).astype(np.uint8)
        path=out/'boards'/(r['pair_id']+'.png');assert cv2.imwrite(str(path),np.hstack((image,shown)))
        queue.append(dict(pair_id=r['pair_id'],source_image_id=r['source_image_id'],source_id=r['source_id'],variant=r['variant'],
            severity=r['severity'],duplicate_group_id=r['duplicate_group_id'],reference_concerns=r['recorded_reference_concerns'],
            reference_path=r['reference_path'],input_sha256=r['input_sha256'],input_mask_sha256=r['input_mask_sha256'],
            board_path=path.relative_to(out).as_posix(),paper_target=r['paper_target'],training_eligible=False))
    manifest=dict(schema_version='truehue_primary_mask_review_v1',scope='exact_new_primary_candidate_input_masks_only',
        measurement_contract_sha256=parent['measurement_contract_sha256'],rows=queue,source_count=26,mask_count=61,
        source_groups_exposed_development=True,new_mask_approvals=0)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');identity=sha(out/'manifest.json')
    groups=[]
    for source in dict.fromkeys(r['source_image_id'] for r in queue):
        items=[r for r in queue if r['source_image_id']==source]
        ref=(ROOT/items[0]['reference_path']).resolve()
        groups.append(dict(source_id=items[0]['source_id'],reference_url=os.path.relpath(ref,out).replace('\\','/'),rows=items))
    payload=json.dumps(groups).replace('<','\\u003c')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TrueHue — normal-case masks</title>
<style>body{font:18px system-ui;max-width:1000px;margin:24px auto;padding:0 16px;background:#f4f6f8;color:#17202a}h1{font-size:27px}button,textarea{font:inherit}button{padding:10px;margin:5px;border:1px solid #8090a0;border-radius:7px;background:white;cursor:pointer}button[aria-pressed=true]{background:#173f6b;color:white}img{max-width:100%;height:auto}.reference{width:210px}section{background:white;border-radius:10px;padding:16px;margin:20px 0}textarea{width:100%;box-sizing:border-box;height:65px}nav{display:flex;align-items:center;justify-content:space-between;gap:10px}#notice{color:#8b2300}.labels{display:grid;grid-template-columns:1fr 1fr;text-align:center;font-weight:600}</style>
<h1>Normal-case training masks</h1><p><strong>26 existing photos, 61 mask decisions.</strong> The original photos were already accepted. Only check the new masks below. These normal-case versions will supply the next planned training comparison; no model is trained from your choices automatically.</p>
<p>Check facial coverage and exclusions of hair, eyes, lips, clothes and background. Choose Accept, Reject or Unsure. Use the photo-wide button only if every mask shown for this photo is acceptable.</p>
<nav><button id="previous">Previous photo</button><strong id="progress"></strong><button id="next">Next photo</button></nav>
<h2 id="source"></h2><img id="reference" class="reference" alt="Previously accepted original photo"><p id="concerns"></p>
<button id="acceptGroup">Accept every mask on this photo</button><div id="cards"></div><p id="notice" role="status"></p>
<button id="download">Download decisions</button><p>Save the downloaded JSON in this review folder when finished. Choices are also saved in this browser when available. Original-mask approvals remain separate.</p>
<script>const groups=__DATA__,manifest='__HASH__',key='truehue_primary_masks_'+manifest;let index=0,decisions={};const el=id=>document.getElementById(id);const labels={gamma_lighten:'Lighter exposure',gamma_darken:'Darker exposure',color:'Color shift',exposure:'Table 2 exposure component'};
try{const saved=JSON.parse(localStorage.getItem(key)||'{}');for(const g of groups)for(const r of g.rows){const d=saved[r.pair_id];if(d&&['accept','reject','uncertain',''].includes(d.decision)&&typeof d.notes==='string')decisions[r.pair_id]=d;}}catch(e){el('notice').textContent='Browser saving unavailable. Download decisions before closing.';}
function save(){try{localStorage.setItem(key,JSON.stringify(decisions));}catch(e){el('notice').textContent='Browser saving unavailable. Download decisions before closing.';}}
function progress(){const done=Object.values(decisions).filter(d=>d.decision).length;el('progress').textContent='Photo '+(index+1)+' / '+groups.length+' — '+done+' / 61 masks reviewed';}
function choose(id,decision){const previous=decisions[id]||{};decisions[id]={decision,notes:previous.notes||'',updated_at:new Date().toISOString()};save();draw();}
function draw(){const g=groups[index];el('source').textContent='Photo '+g.source_id;el('reference').src=g.reference_url;el('concerns').textContent=g.rows[0].reference_concerns?'Earlier reference note: '+(typeof g.rows[0].reference_concerns==='string'?g.rows[0].reference_concerns:JSON.stringify(g.rows[0].reference_concerns)):'';el('previous').disabled=index===0;el('next').disabled=index===groups.length-1;el('cards').replaceChildren();
for(const r of g.rows){const card=document.createElement('section'),heading=document.createElement('h3');heading.textContent=labels[r.variant]||r.variant;card.append(heading);const captions=document.createElement('div');captions.className='labels';captions.innerHTML='<span>New input</span><span>Mask to check</span>';card.append(captions);const image=document.createElement('img');image.src=r.board_path;image.alt='Input and green face mask for '+heading.textContent;card.append(image);const controls=document.createElement('div');for(const [decision,label] of [['accept','Accept'],['reject','Reject'],['uncertain','Unsure']]){const button=document.createElement('button');button.textContent=label;button.setAttribute('aria-pressed',String((decisions[r.pair_id]||{}).decision===decision));button.onclick=()=>choose(r.pair_id,decision);controls.append(button);}card.append(controls);const label=document.createElement('label');label.textContent='Notes';const note=document.createElement('textarea');note.setAttribute('aria-label','Notes for '+heading.textContent);note.value=(decisions[r.pair_id]||{}).notes||'';note.oninput=()=>{const prior=decisions[r.pair_id]||{};decisions[r.pair_id]={decision:prior.decision||'',notes:note.value,updated_at:new Date().toISOString()};save();};label.append(note);card.append(label);el('cards').append(card);}progress();}
el('previous').onclick=()=>{index--;draw();window.scrollTo(0,0);};el('next').onclick=()=>{index++;draw();window.scrollTo(0,0);};
el('acceptGroup').onclick=()=>{for(const r of groups[index].rows){const prior=decisions[r.pair_id]||{};decisions[r.pair_id]={decision:'accept',notes:prior.notes||'',updated_at:new Date().toISOString()};}save();draw();};
el('download').onclick=()=>{const reviews={};for(const g of groups)for(const r of g.rows)reviews[r.pair_id]=decisions[r.pair_id]||{decision:'',notes:''};const data={schema_version:'truehue_primary_mask_review_v1',manifest_sha256:manifest,review_scope:'exact_new_primary_candidate_input_masks_only',reviews};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='truehue_primary_mask_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};draw();</script></html>'''
    page=page.replace('__DATA__',payload).replace('__HASH__',identity)
    (out/'review.html').write_text(page,encoding='utf-8')
    # Extract for syntax-only checks; no browser interaction claim is made.
    (out/'review-script.js').write_text(page.split('<script>',1)[1].split('</script>',1)[0],encoding='utf-8')
    lanes={lane:sum(r['lane']==lane for r in attempts) for lane in sorted({r['lane'] for r in attempts})}
    (out/'data_freeze.json').write_text(json.dumps(dict(status='frozen_candidates_pending_exact_mask_reviews',lanes=lanes,
        primary_pairs=61,primary_sources=26,exact_prior_mask_decision_matches=matches,new_distorted_admissions=0,
        current_mask_contract=parent['measurement_contract_sha256'],frozen_features=parent['features'],frozen_tree_settings=parent['settings'],
        next_comparison='frozen endpoint stress baseline versus primary-only fitting plus original controls; source-held; no sweeps',
        row_policy='26 original controls retained; no clipped row in proposed primary fit; authorized stress route preserved separately',
        original_stress_rows_preserved=21,independent_final_evaluation=False,MST_status='experimental_not_final_validated',
        schema='unchanged target gamma/red/blue; gamma controls algebraic before encoding, color/composite targets approximate',
        prerequisites=['Exact input masks must be reviewed before admission','Record accepted membership and source folds before the one candidate fit',
            'Report mask/target failures and clean safety; no source exceptions','Final MST validation and independent evaluation remain unresolved']),indent=2),encoding='utf-8')
    for g in groups:
        assert (out/g['reference_url']).exists()
        for r in g['rows']:
            assert (out/r['board_path']).exists() and not r['training_eligible']
    assert len(groups)==26
    (out/'verification.json').write_text(json.dumps(dict(status='static_assets_and_provenance_verified',source_cards=26,input_masks=61,
        manifest_sha256=identity,previous_decisions_not_transferred=True,live_browser_tested=False,
        preparation_verification_sha256={str(p.relative_to(ROOT)):sha(p/'verification.json') for p in preparations},
        evidence_sha256={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('Frozen 61 primary candidates on 26 source cards; 52 clipped variants and 17 screen holds kept separate; no tree fitting.')


if __name__=='__main__':main()
