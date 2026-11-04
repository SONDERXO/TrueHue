"""Fixed 19-person eligibility page: reuse parents, one frozen FaceOcc pass, no fits."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.ita_estimation.faceocc_development import contract, evaluate_parent
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

OUT = ROOT / 'outputs/mst_subject_skin_study_v1'
PARENT = ROOT / 'outputs/nostril_mst_measurement_v4'
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    selection_path = ROOT / 'outputs/mst_subject_skin_study_plan_v1/plan.json'
    selection = read(selection_path)
    assert len(selection['rows']) == 19
    assert sum(r['new_review_needed'] for r in selection['rows']) == 15
    parents = {r['image_id']: r for r in map(json.loads, (PARENT / 'records.jsonl').read_text().splitlines())}
    human_path = ROOT / 'outputs/mst_skin_check_four_import_v1/decisions.json'
    human = {r['image_id']: r for r in read(human_path)['human_judgments']['rows']}
    spec, identity = contract(ROOT)
    assert identity == read(ROOT / 'outputs/faceocc_development_service_v1/contract.json')['sha256']
    hashes = {str(p): digest(p) for p in [selection_path, human_path, PARENT / 'records.jsonl', Path(__file__), ROOT / 'scripts/387_run_subject_skin_logits.py', ROOT / 'scripts/369_run_faceocc_logits.py']}
    hashes.update({str(ROOT / p): h for p, h in spec['dependency_sha256'].items()})
    template_path = ROOT / 'models/faceocc_candidate_v1/similarity_Lm3D_all.mat'
    hashes[str(template_path)] = digest(template_path)
    for r in selection['rows']:
        if not r['new_review_needed']:
            for key in ['input_source', 'mask_source']:
                p = ROOT / r[key]; hashes[str(p)] = digest(p)
        else:
            parent = parents[r['image_id']]
            if parent['status'] == 'success':
                for path, checksum in [('source_path', 'source_sha256'), ('mask_path', 'mask_sha256'), ('landmarks_path', 'landmarks_sha256')]:
                    p = Path(parent[path]) if path == 'source_path' else PARENT / parent[path]
                    assert digest(p) == parent[checksum]
                    hashes[str(p)] = parent[checksum]
    OUT.mkdir(); (OUT / 'logits').mkdir()
    (OUT / 'plan.json').write_text(json.dumps(dict(selection=selection, contract=spec, contract_sha256=identity, input_sha256=hashes,
        authorization='User explicitly accepted preparation of up to15 additional checks; no fitting', fits=0), indent=2))
    template = loadmat(template_path)['lm']
    records, attempts = [], []
    for i, row in enumerate(selection['rows'], 1):
        folder = OUT / f'case_{i}'; folder.mkdir()
        rec = dict(row, case_index=i, training_admitted=False, calibration_admitted=False)
        if not row['new_review_needed']:
            prior = human[row['image_id']]
            assert row['human_decisions'] == prior['decisions']
            assert digest(ROOT / row['input_source']) == prior['input_sha256']
            assert digest(ROOT / row['mask_source']) == prior['mask_sha256']
            (folder / 'input.png').write_bytes((ROOT / row['input_source']).read_bytes())
            (folder / 'candidate_mask.png').write_bytes((ROOT / row['mask_source']).read_bytes())
            rec.update(status='prior_review_complete', human_decisions=prior['decisions'], human_notes=prior['notes'])
        else:
            parent = parents[row['image_id']]
            rec['parent_report'] = parent
            if parent['status'] != 'success':
                rec.update(status='parent_failed', reason=parent.get('reason', parent.get('stage')))
            else:
                image = cv2.imread(parent['source_path'])
                if image is None:
                    rec.update(status='source_decode_failed', reason='Source failed to decode; no replacement')
                else:
                    image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)
                    mask = cv2.imread(str(PARENT / parent['mask_path']), 0)
                    points = np.load(PARENT / parent['landmarks_path'], allow_pickle=False)
                    statistics = compute_masked_lab_statistics(image, mask, 1000)
                    assert statistics['mean_l_star'] == parent['statistics']['mean_l_star']
                    assert statistics['mean_a_star'] == parent['statistics']['mean_a_star']
                    assert statistics['mean_b_star'] == parent['statistics']['mean_b_star']
                    assert cv2.imwrite(str(folder / 'input.png'), image)
                    assert cv2.imwrite(str(folder / 'baseline_mask.png'), mask)
                    np.save(folder / 'landmarks.npy', points)
                    try:
                        aligned, matrix, bridge = align_input(image, points, template)
                        assert cv2.imwrite(str(folder / 'aligned.png'), aligned)
                        rec.update(status='inference_ready', matrix=matrix.tolist(), bridge=bridge)
                        attempts.append(dict(image_id=row['image_id'], case_index=i, aligned_path=str(folder / 'aligned.png')))
                    except ValueError as error:
                        rec.update(status='alignment_failed', reason=str(error))
        records.append(rec)
        print(f'{i}/19 {rec["status"]}', flush=True)
    assert all(digest(p) == h for p, h in hashes.items())
    (OUT / 'baseline.json').write_text(json.dumps(dict(records=records), indent=2))
    inference_hashes = dict(hashes)
    for p in OUT.glob('case_*/*'):
        if p.is_file(): inference_hashes[str(p)] = digest(p)
    (OUT / 'inference_plan.json').write_text(json.dumps(dict(attempts=attempts, input_sha256=inference_hashes), indent=2))


def finalize():
    if (OUT / 'manifest.json').exists():
        raise FileExistsError('Already finalized')
    plan = read(OUT / 'plan.json'); ip = read(OUT / 'inference_plan.json'); run = read(OUT / 'inference.json')
    assert run['plan_sha256'] == digest(OUT / 'inference_plan.json')
    assert all(digest(p) == h for p, h in ip['input_sha256'].items())
    predictions = {r['image_id']: r for r in run['records']}
    template = loadmat(ROOT / 'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records, replays = [], 0
    for rec in read(OUT / 'baseline.json')['records']:
        folder = OUT / f'case_{rec["case_index"]}'
        if rec['status'] == 'inference_ready':
            pred = predictions[rec['image_id']]
            if pred['status'] != 'success':
                rec.update(status='model_failed', reason=pred['reason'])
            else:
                lp = OUT / pred['logits_path']; assert digest(lp) == pred['logits_sha256']
                image = cv2.imread(str(folder / 'input.png')); mask = cv2.imread(str(folder / 'baseline_mask.png'), 0)
                logits = np.load(lp, allow_pickle=False)
                candidate, _, report = combine_saved(image, mask, logits, np.array(rec['matrix']))
                service = evaluate_parent(SimpleNamespace(report=rec['parent_report'], image=image, mask=mask),
                    np.load(folder / 'landmarks.npy', allow_pickle=False), template, lambda _: logits)
                assert np.array_equal(service.mask, candidate)
                assert service.report['features'] == report['features']
                assert np.array_equal(service.aligned, cv2.imread(str(folder / 'aligned.png')))
                assert not candidate[mask == 0].any()
                assert service.report['mst'] is None and not service.report['training_admitted']
                assert cv2.imwrite(str(folder / 'candidate_mask.png'), candidate)
                rec.update(status='ready_for_human_review' if report['status'] == 'success' else 'candidate_failed', candidate_report=report)
                replays += 1
        if rec['status'] in {'ready_for_human_review', 'prior_review_complete'}:
            image = cv2.imread(str(folder / 'input.png')); mask = cv2.imread(str(folder / 'candidate_mask.png'), 0) > 0
            overlay = image.copy(); overlay[mask] = np.rint(.7 * image[mask] + .3 * np.array([0, 255, 0])).astype(np.uint8)
            selected = image.copy(); selected[~mask] = 35
            assert cv2.imwrite(str(folder / 'overlay.png'), overlay)
            assert cv2.imwrite(str(folder / 'selected.png'), selected)
        rec['file_sha256'] = {p.name: digest(p) for p in folder.iterdir() if p.is_file()}
        records.append(rec)
    assert len(records) == 19 and sum(r['status'] == 'prior_review_complete' for r in records) == 4
    manifest = dict(schema='truehue_mst_subject_skin_study_v1', rows=records, contract_sha256=plan['contract_sha256'],
        input_sha256=ip['input_sha256'], plan_sha256=digest(OUT / 'plan.json'), calibration_admitted=False, training_admitted=False)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    make_page(manifest)
    assert contract(ROOT)[1] == plan['contract_sha256']
    assert all(digest(p) == h for p, h in ip['input_sha256'].items())
    result = dict(total_subjects=19, preserved_reviews=4, new_attempts=15,
        new_reviewable=sum(r['status'] == 'ready_for_human_review' for r in records),
        failed_new_attempts=sum(r['status'] not in {'ready_for_human_review', 'prior_review_complete'} for r in records),
        new_forwards=run['forwards'], saved_service_replays=replays, calibration_fits=0, tree_fits=0,
        all_source_hashes_unchanged=True, no_added_parent_pixels=True)
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2)); print(json.dumps(result, indent=2))


def make_page(manifest):
    cards = []
    for r in manifest['rows']:
        key = f'case_{r["case_index"]}'
        card = '<section><h2>' + html.escape(r['subject_id']) + '</h2><p>' + html.escape(r['image_id']) + '</p>'
        if r['status'] in {'ready_for_human_review', 'prior_review_complete'}:
            card += '<div class="images">' + ''.join(f'<figure><img src="{key}/{name}.png"><figcaption>{label}</figcaption></figure>' for name, label in [('input','Original saved input'),('overlay','Green = measured area'),('selected','Selected pixels only')]) + '</div>'
        if r['status'] == 'prior_review_complete':
            card += '<p><b>Already reviewed — no action needed.</b></p><p>' + html.escape(str(r['human_decisions'])) + '</p><p>' + html.escape(r['human_notes']) + '</p>'
        elif r['status'] == 'ready_for_human_review':
            for field, question in [('non_skin','Does the selected area include hair, glasses, covering, clothing or background?'),('skin_loss','Does it leave out obvious useful facial skin?'),('judgeable','Is this image clear enough to judge the selected pixels?')]:
                card += f'<label>{question} <select id="{key}_{field}"><option value="">Choose</option><option value="yes">Yes</option><option value="no">No</option><option value="unsure">Cannot tell</option></select></label>'
            card += f'<label>Optional note<textarea id="{key}_notes"></textarea></label>'
        else:
            card += '<p><b>Processing failed — no review needed; retained, not replaced.</b> ' + html.escape(str(r.get('reason', r.get('candidate_report',{}).get('reason','Candidate unavailable')))) + '</p>'
        cards.append(card + '</section>')
    pending = [dict(case_id=f'case_{r["case_index"]}', image_id=r['image_id'], input_sha256=r['file_sha256']['input.png'], mask_sha256=r['file_sha256']['candidate_mask.png']) for r in manifest['rows'] if r['status'] == 'ready_for_human_review']
    script = '''const pending=PENDING,binding=BINDING,key='truehue_mst_subject_skin_study_v1_'+binding;
function collect(){return pending.map(r=>({...r,decisions:Object.fromEntries(['non_skin','skin_loss','judgeable'].map(f=>[f,document.getElementById(r.case_id+'_'+f).value])),notes:document.getElementById(r.case_id+'_notes').value}));}
try{const old=JSON.parse(localStorage.getItem(key)||'null');if(old)for(const r of old){for(const f of ['non_skin','skin_loss','judgeable'])document.getElementById(r.case_id+'_'+f).value=r.decisions[f]||'';document.getElementById(r.case_id+'_notes').value=r.notes||'';}}catch(e){}
document.addEventListener('input',()=>{try{localStorage.setItem(key,JSON.stringify(collect()));document.getElementById('status').textContent='Progress saved in this browser.';}catch(e){document.getElementById('status').textContent='Browser save unavailable; export a progress copy before closing.';}});
function save(complete){const rows=collect();if(complete&&rows.some(r=>Object.values(r.decisions).some(v=>!v))){document.getElementById('status').textContent='Please answer all three questions for each new photo. Cannot tell is valid.';return;}const blob=new Blob([JSON.stringify({schema:'truehue_mst_subject_skin_study_v1',manifest_sha256:binding,complete,rows},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=complete?'truehue_mst_subject_skin_decisions.json':'truehue_mst_subject_skin_progress.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);document.getElementById('status').textContent=complete?'Answers exported. Tell me when done.':'Progress copy exported; keep reviewing in this page.';}
document.getElementById('export').onclick=()=>save(true);document.getElementById('progress').onclick=()=>save(false);
'''.replace('PENDING', json.dumps(pending)).replace('BINDING', json.dumps(digest(OUT / 'manifest.json')))
    (OUT / 'review.js').write_text(script, encoding='utf-8')
    (OUT / 'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Existing-subject skin check</title><style>body{font:18px/1.5 system-ui;max-width:1250px;margin:auto;padding:20px}section{border-top:2px solid #aaa;padding:20px 0}.images{display:flex;flex-wrap:wrap}figure{flex:1;min-width:240px;margin:8px}img{width:100%}label{display:block;margin:16px 0}select,textarea,button{font:inherit}textarea{display:block;width:95%}</style><h1>Skin check: 19 existing people</h1><p>'+str(len(pending))+' new photos need answers. Your four completed reviews are preserved. Failed cases need no answers. No drawing or training.</p><p>Check the selected pixels, not whether someone has a beard elsewhere. Eyes, eyebrows, lips, nostrils, hair and neck are intentionally excluded. Choose Cannot tell if uncertain. These saved 256-pixel inputs cannot prove true skin colour.</p><p>You can take breaks. Browser saving may depend on your browser; export a progress copy as a backup. Only a complete answers export can be imported.</p>'+''.join(cards)+'<button id="progress">Export progress copy</button> <button id="export">Export completed answers</button><p id="status" role="status"></p><script src="review.js"></script></html>', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--finalize', action='store_true')
    args = parser.parse_args(); finalize() if args.finalize else prepare()
