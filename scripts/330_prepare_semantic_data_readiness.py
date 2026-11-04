"""Bind six new exact masks to a small review; inventory saved support only."""
import csv
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.data_preparation.redesign_access import training_candidate
from src.ita_estimation.semantic_measurement import contract
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage


def main():
    out = ROOT / 'outputs/semantic_reference_readiness_v1'
    if out.exists():
        raise FileExistsError(out)
    hashes = {}
    def digest(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()
    def read(relative):
        p = ROOT / relative; hashes[relative] = digest(p)
        return json.loads(p.read_text(encoding='utf-8'))
    semantic = read('outputs/semantic_face_coverage_v1/records.json')
    candidates = [r for r in semantic if r['case_id'].endswith('_reference')]
    assert len(candidates) == 6
    allocation = read('outputs/correction_data_redesign_v1/selection.json')
    policy = read('outputs/correction_data_redesign_v1/access_policy.json')
    dispositions = {r['image_id']: r for r in read('outputs/correction_duplicate_audit_v1/candidate_dispositions.json')}
    registry = read('outputs/reviewed_source_evidence32_v1/registry.json')
    inventory = read('outputs/independent_source_inventory_v1/fairface_inventory.json')
    scin = read('outputs/independent_source_inventory_v1/scin_inventory.json')
    oldgroups = {r['source_image_id'] for r in registry['rows']}
    assert len(oldgroups) == 32
    spec, identity = contract(ROOT)
    out.mkdir(); (out / 'boards').mkdir()
    queue = []
    for r in candidates:
        training_candidate(r['source_image_id'], allocation, policy)
        disposition = dispositions[r['source_image_id']]
        assert disposition['status'] == 'screen_clear_unreviewed', disposition
        assert r['old_judgment']['reference_suitability']['decision'] == 'accept'
        imagepath = ROOT / r['image_path']; maskpath = ROOT / 'outputs/semantic_face_coverage_v1' / r['mask_path']
        categorypath = ROOT / 'outputs/semantic_face_coverage_v1' / r['category_path']
        pointspath = ROOT / r['landmarks_path']
        assert digest(imagepath) == r['source_sha256'] and digest(maskpath) == r['mask_sha256']
        assert digest(categorypath) == r['category_sha256'] and digest(pointspath) == r['landmarks_sha256']
        image = cv2.imread(str(imagepath)); mask = cv2.imread(str(maskpath), 0)
        assert image.shape == (256, 256, 3)
        rebuilt = build_semantic_face_coverage(image, np.load(pointspath), cv2.imread(str(categorypath), 0))
        assert np.array_equal(rebuilt.mask, mask)
        overlay = np.rint(image * (1-.45*(mask > 0)[:, :, None]) + np.array([0,255,0])*.45*(mask > 0)[:, :, None]).astype(np.uint8)
        board = out / 'boards' / (r['case_id'] + '.png')
        assert cv2.imwrite(str(board), np.hstack((image, overlay, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))))
        queue.append(dict(case_id=r['case_id'], source_image_id=r['source_image_id'],
            source_path=r['image_path'], source_sha256=r['source_sha256'],
            mask_path=maskpath.relative_to(ROOT).as_posix(), mask_sha256=r['mask_sha256'],
            source_role='train', duplicate_record=disposition,
            prior_source_decision=r['old_judgment']['reference_suitability'],
            prior_old_mask_decision=r['old_judgment']['reference_mask'],
            new_mask_decision='pending', training_admitted=False,
            source_independence='Source group only; already development-exposed, person identity unverified',
            board_path=board.relative_to(out).as_posix()))
    manifest = dict(schema_version='truehue_semantic_reference_mask_review_v1',
        scope='six_exact_new_reference_masks_only_not_source_re_review',
        measurement_contract_sha256=identity, rows=queue, source_count=6,
        no_old_approvals_transferred=True, automatic_training=False,
        approval_meaning='Exact displayed mask only; not intrinsic color, MST truth or variant approval')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    mh = digest(out / 'manifest.json')
    data = json.dumps([dict(case_id=r['case_id'], source_image_id=r['source_image_id'],
                           mask_sha256=r['mask_sha256'], source_sha256=r['source_sha256']) for r in queue]).replace('<','\\u003c')
    cards = []
    for r in queue:
        key = html.escape(r['case_id'])
        cards.append(f'<section><h2>{key}</h2><p>Existing source decision: accepted. Review only the NEW mask.</p>'
            f'<img src="{r["board_path"]}" alt="Input, fuller-face overlay, binary mask">'
            f'<p><label>New mask: <select id="decision_{key}"><option value="pending">Choose</option><option value="accept">Accept</option><option value="reject">Reject</option><option value="uncertain">Uncertain</option></select></label></p>'
            f'<label>Notes (what is missing or wrongly included): <textarea id="notes_{key}" rows="2"></textarea></label></section>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Six new face masks</title>
<style>body{font:18px/1.5 system-ui;max-width:1100px;margin:25px auto;padding:20px;background:#faf8f5}img{max-width:100%}section{background:white;padding:20px;margin:25px 0;border:1px solid #ccc}select,textarea,button{font:inherit;padding:8px}textarea{width:95%}button{cursor:pointer}#bar{position:sticky;top:0;background:#fff1cb;padding:15px;border:1px solid #aa8}</style>
<h1>Six new face masks</h1><p>You already reviewed these source photographs. Those decisions are kept. Only the fuller-face masks are new.</p>
<p>Left: photo. Middle: selected skin in green. Right: selected pixels in white. Accept only if visible facial skin is sufficiently covered and eyes, eyebrows, lips/mouth, hair, glasses and background are properly excluded. If beard, an object or another problem makes the mask unsuitable, reject or mark uncertain and note it. No new beard model is enabled.</p>
<p>Acceptance does not certify true skin color, correct lighting, MST labels or any edited version. These are already exposed development photos, not new independent people.</p>
<div id="bar"><span id="count">0 / 6 decided</span> <button id="export">Download decisions</button><span id="message" role="status"></span></div>'''+''.join(cards)+f'''<script>
const rows={data}; const manifestHash="{mh}"; const storageKey="truehue_semantic6_"+manifestHash;
function collect(){{return rows.map(r=>({{...r,decision:document.getElementById('decision_'+r.case_id).value,notes:document.getElementById('notes_'+r.case_id).value}}));}}
function update(){{let v=collect();document.getElementById('count').textContent=v.filter(r=>r.decision!=='pending').length+' / 6 decided';try{{localStorage.setItem(storageKey,JSON.stringify(v));}}catch(e){{document.getElementById('message').textContent=' Download decisions to save them.';}}}}
try{{const saved=JSON.parse(localStorage.getItem(storageKey)||'[]');for(const r of saved){{if(rows.some(x=>x.case_id===r.case_id)){{document.getElementById('decision_'+r.case_id).value=r.decision;document.getElementById('notes_'+r.case_id).value=r.notes||'';}}}}}}catch(e){{}}
document.querySelectorAll('select,textarea').forEach(e=>e.addEventListener('input',update));update();
document.getElementById('export').addEventListener('click',()=>{{const payload={{schema_version:'truehue_semantic_reference_mask_decisions_v1',manifest_sha256:manifestHash,measurement_contract_sha256:'{identity}',rows:collect()}};const blob=new Blob([JSON.stringify(payload,null,2)],{{type:'application/json'}});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='truehue_semantic6_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);document.getElementById('message').textContent=' Downloaded. Save the JSON file in this review folder.';}});
</script></html>'''
    (out / 'review.html').write_text(page, encoding='utf-8')
    (out / 'review-script.js').write_text(page.split('<script>')[1].split('</script>')[0], encoding='utf-8')
    support = read('outputs/mst_limited_scope_proposal_v1/support.json')['categories']
    measured = read('outputs/semantic_mst_measurement_v1/summary.json')['records']
    supports = []
    for r in support:
        label = r['mst']; current = sorted({x['subject_id'] for x in measured if x['source_mst_label'] == label and x['status'] == 'success'})
        supports.append(dict(mst=label, current_subjects=current, official_subjects=r['official_subjects'],
            unrepresented_official_subjects=[x for x in r['official_subjects'] if x not in current],
            minimum_additional_subjects_for_two_subject_structure=max(0,2-len(current)),
            caveat='Two subjects is only structural separation, not adequate sample size or validated accuracy.'))
    remaining = [r for r in inventory if r['image_id'] not in oldgroups and r['duplicate_status'] == 'screen_clear_unreviewed']
    result = dict(status='readiness_inventory_and_six_new_masks_no_training', new_mask_decisions_needed=6,
        old_source_reviews_repeated=0, repeated_old_variant_reviews=0,
        source_groups_in_completed_comparison=len(oldgroups), remaining_screen_clear_training_groups=len(remaining),
        remaining_groups_without_new_semantic_masks=len(remaining), person_independence_not_established=True,
        scin_unallocated=sum(r['role']=='unallocated_metadata_only' for r in scin),
        mst_subject_support=supports,
        known_occlusion_hold=dict(image_id='mst_e__subject_7/PXL_20220922_201156891.jpg',
            issue='Worn face covering partly selected', scope='Exact diagnostic image; not automatic subject exclusion',
            correction_training_role=False),
        reference_quality='Retained photo-suitability decisions, not measured intrinsic skin color or lighting calibration',
        correction_fits=0, new_distortions=0, new_parser_inferences=0, reserved_pixel_access=0,
        new_mask_approvals=0, measurement_contract_sha256=identity, manifest_sha256=mh,
        missing_before_training=['Six exact original-mask decisions', 'Declared consistent generation and inverse-target protocol',
            'Explicit experimental MST packaging/admission decision; final independent validation still unfinished',
            'Exact new distorted-mask admission after generation; no inherited approvals'], input_sha256=hashes)
    assert contract(ROOT)[1] == identity
    assert all(digest(ROOT / path) == value for path, value in hashes.items())
    (out / 'readiness.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('input_sha256','mst_subject_support')}, indent=2))


if __name__ == '__main__':
    main()
