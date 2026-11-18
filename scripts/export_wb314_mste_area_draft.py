"""Audit cached V2 predictions and export native face-box crops for inspection.

No source-image decoding, feature extraction, fitting or correction inference.
Both panels use one reference-derived box, after whole-frame prediction. Full
frames and support boards remain inspectable; this is not a mask repair.
"""
from pathlib import Path
import base64
import csv
import hashlib
import html
import json
import zipfile

import cv2
import numpy as np
from PIL import Image, ImageDraw

from repair_wb314_mste_packet_preparation import OLD, OUT, DELIVERY, MODEL, read, sha, write, recheck
from wb314_research_predictor import MODEL_SHA256
from prepare_wb314_mste_development_packet import route, replay, generate

ROOT = Path(__file__).resolve().parents[1]
FLAGGED = {1, 2, 6, 10, 11, 12, 14, 17, 18, 19, 20}


def embedded(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def main():
    if (OUT / 'presentation_audit.json').exists():
        raise FileExistsError('Preserve previous presentation audit')
    proof = read(DELIVERY / 'verification.json')
    assert proof['passed'] and proof['pairs'] == 20 and sha(MODEL) == MODEL_SHA256
    recheck(read(OUT / 'bindings.json'))
    for path, digest in proof['artifacts'].items():
        assert sha(DELIVERY / path) == digest
    old_rows = {r['pair_id']: r for r in read(OLD / 'selected_references.json')}
    old_predictions = {r['pair_id']: r for r in read(OLD / 'predictions_sealed.json')['records']}
    rows = read(OUT / 'predictions_sealed.json')['records']
    assert len(rows) == 20 and len({r['pair_id'] for r in rows}) == 20
    slots = read(OLD / 'form_slot_check.json'); assert slots['passed']
    catalog_path = ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv'
    assert sha(catalog_path) == '1813993f7efba82ec0eca145520eb41cb9355f91d9e9a650bfb0c69870fc5ae8'
    with catalog_path.open(encoding='utf-8-sig', newline='') as f:
        catalog = {'mst_e__' + r['subject_name'] + '/' + r['image_ID']: r for r in csv.DictReader(f)}
    model = read(MODEL)
    visual = read(OUT / 'reference_visual_check.json')
    observations = {r['candidate_id']: r for r in visual['records']}
    assert visual['cases_viewed'] == 20 and visual['distribution_ready'] is False
    face_dir = DELIVERY / 'face-pairs'; face_dir.mkdir()
    sections = []; manifest = []; face_images = []; changed_controls = 0
    for i, r in enumerate(rows, 1):
        old = old_rows[r['pair_id']]; slot = slots['slots'][i-1]; official = catalog[r['case_id']]
        assert int(r['pair_id'].split('_')[-1]) == i == slot['slot']
        assert all(r[k] == old[k] for k in ['case_id', 'subject_id', 'MST', 'candidate_id', 'condition'])
        assert r['subject_id'] == official['subject_name']
        assert r['MST'] == slot['MST'] == int(official['MST'])
        assert r['original_source_sha256'] == old['source_sha256'] == sha(Path(r['original_source_path']))
        folder = OUT / 'references' / r['candidate_id']
        assert sha(folder / 'reference_support.npz') == r['pack_sha256']
        assert sha(OUT / 'evaluation' / (r['pair_id'] + '.npz')) == r['evaluation_sha256']
        with np.load(OUT / 'evaluation' / (r['pair_id'] + '.npz'), allow_pickle=False) as z:
            ref, image, candidate, measurement, alpha, protected = [z[k].copy() for k in
                ['reference', 'input', 'candidate', 'measurement', 'alpha', 'protected']]
        with np.load(folder / 'reference_support.npz', allow_pickle=False) as z:
            assert all(np.array_equal(a, z[k]) for a, k in
                [(ref, 'reference'), (measurement, 'measurement'), (alpha, 'alpha'), (protected, 'protected')])
        assert np.array_equal(ref, cv2.imread(r['source_path'])[:, :, ::-1])
        assert sha(Path(r['source_path'])) == r['source_sha256']
        assert np.array_equal(generate(ref, r['condition'])[0], image)
        leaf, controls = route(model, r['features'])
        assert leaf == r['leaf'] and controls == r['controls']
        scalar, _ = replay(image, image, alpha, protected, controls)
        assert np.array_equal(scalar, candidate)
        assert np.array_equal(candidate[alpha == 0], image[alpha == 0])
        assert np.array_equal(candidate[protected], image[protected])
        changed_controls += controls != old_predictions[r['pair_id']]['controls']
        x, y, w, h = read(folder / 'parent_report.json')['face_box']
        assert all(isinstance(n, int) for n in [x, y, w, h])
        assert x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= 256 and y+h <= 256
        full = DELIVERY / 'pairs' / (r['pair_id'] + f'_mst{r["MST"]:02d}.png')
        with Image.open(full) as im:
            assert np.array_equal(np.asarray(im), np.concatenate([ref, candidate], axis=1))
        crop = np.concatenate([ref[y:y+h, x:x+w], candidate[y:y+h, x:x+w]], axis=1)
        path = face_dir / full.name; Image.fromarray(crop).save(path)
        with Image.open(path) as im:
            assert np.array_equal(np.asarray(im), crop)
            face_images.append(im.copy())
        observation = observations[r['candidate_id']]
        assert sha(folder / 'qa.png') == observation['board_sha256']
        manifest.append(dict(pair_id=r['pair_id'], MST=r['MST'], Form_heading=slot['existing_heading'],
            face_box_xywh=[x,y,w,h], full_frame_sha256=sha(full), face_pair_sha256=sha(path),
            face_pair=path.relative_to(DELIVERY).as_posix(), prior_user_appearance_concern=i in FLAGGED,
            condition=r['condition'], controls_changed_from_v1=controls != old_predictions[r['pair_id']]['controls']))
        label = '<p>Previously flagged appearance concern.</p>' if i in FLAGGED else ''
        sections.append(f'<section id="pair{i:02d}"><h2>{html.escape(slot["existing_heading"])}</h2>{label}'
            '<p>Photographic reference (left) | Frozen WB314 correction (right)</p>'
            f'<img width="{w*2}" height="{h}" src="{embedded(path)}" alt="Identical native face-box crops">'
            '<details><summary>Full frame and support inspection</summary>'
            '<p>The synthetic exposure/colour remains outside facial correction support. Cropping does not repair it.</p>'
            f'<img width="512" height="256" src="{embedded(full)}" alt="Full reference and correction frames">'
            f'<p>{html.escape(observation["observation"])}</p>'
            f'<img width="1024" height="280" src="{embedded(folder / "qa.png")}" alt="Reference and support overlays">'
            '</details></section>')
    for start in range(0, 20, 4):
        sheet = Image.new('RGB', (512, 4*280), 'white'); draw = ImageDraw.Draw(sheet)
        for j, im in enumerate(face_images[start:start+4]):
            draw.text((4,j*280+4), f'Pair {start+j+1:02d} | MST {(start+j)//2+1:02d} | reference / correction', fill='black')
            sheet.paste(im, (0,j*280+25))
        sheet.save(OUT / f'face_contact_{start//4+1:02d}.png')
    links = ' '.join(f'<a href="#pair{i:02d}">{i:02d}</a>' for i in sorted(FLAGGED))
    page = ('<!doctype html><meta charset="utf-8"><title>WB314 V2 appearance review</title>'
        '<style>body{font:17px system-ui;max-width:1100px;margin:24px auto;padding:0 20px}'
        'section{border-top:1px solid #aaa;margin:28px 0}img{max-width:100%;height:auto}'
        '.hold{padding:16px;background:#fff0cc;border:2px solid #8a5700}details{margin:12px 0}summary{cursor:pointer}</style>'
        '<h1>WB314 V2: appearance-review draft</h1><div class="hold"><strong>Not released for collection.</strong>'
        '<p>Same20photos and frozen predictor. Whole-frame area downsampling replaces bilinear shrinking before masking and prediction. '
        'Both panels now show the same native face-box crop. No sharpening, smoothing, exposure boost or post-correction retouch.</p>'
        '<p>Full frames and masks remain available below every pair. Beard, hair, jewellery and some neck/collar/foreground boundaries remain approximate. '
        'This preparation repair does not establish that the earlier overexposure concern is resolved.</p></div>'
        '<p>Previously flagged pairs: ' + links + '.</p>'
        '<p>Reference left, correction right. Face crops retain original pixels; their sizes vary with reference geometry. '
        'Two pairs per official MST category;13previously exposed people. Existing questions, overall1–5rating and comments remain unchanged. '
        'During-development feedback only; no new user ratings or expert responses are assumed.</p>' + ''.join(sections))
    (DELIVERY / 'DRAFT_REVIEW.html').write_text(page, encoding='utf-8')
    hold = ('DRAFT: NOT RELEASED FOR COLLECTION\n\nV2 repairs whole-frame downsampling consistently before masks/features/prediction. '
        'Face crops are presentation only. Full frames and support boards are retained in DRAFT_REVIEW.html. '
        'The model, questions, scale, official labels,20sources and conditions remain fixed. '
        'No brightness-strength change, masking repair or acceptance is implied. Await appearance/release decision before collection.\n')
    (DELIVERY / 'RELEASE_HOLD.txt').write_text(hold, encoding='utf-8')
    archive = DELIVERY / 'expert-images.zip'
    archive.rename(DELIVERY / 'full-frame-pairs-DRAFT-NOT-FOR-COLLECTION.zip')
    guide = hold + ('\nIf later released, match all20face-pairs PNGs to existing numbered MST sections. '
        'Do not mix V1andV2images or transfer ratings. Record V2normalisation and face-crop presentation. '
        'Preserve consent, evaluator information, overall1–5scale and comments. No Form edit/upload has occurred.\n')
    (DELIVERY / 'face-pair-instructions.txt').write_text(guide, encoding='utf-8')
    with zipfile.ZipFile(DELIVERY / 'face-pairs-DRAFT-NOT-FOR-COLLECTION.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(face_dir.glob('*.png')): z.write(path, path.relative_to(DELIVERY).as_posix())
        z.write(DELIVERY / 'face-pair-instructions.txt', 'face-pair-instructions.txt')
    write(DELIVERY / 'presentation_manifest_PRIVATE.json', dict(cases=manifest,model_sha256=MODEL_SHA256))
    status = dict(passed=True, pairs=20, subjects=13, publisher_MST_categories=10,
        condition_counts=proof['condition_counts'], official_label_Form_slot_source_joins=20,
        independently_replayed_routes=20, independently_replayed_RGB8=20, protected_outside_checks=20,
        full_frame_PNG_checks=20, exact_native_face_crop_checks=20, original_source_hash_checks=20,
        changed_controls_from_v1=changed_controls, new_fits=0, new_predictions_in_export=0,
        model_sha256=MODEL_SHA256, normalization='256 whole-frame INTER_AREA before masks and prediction',
        presentation='same saved reference face_box both panels, native pixels, post-inference',
        distribution_ready=False, appearance_concern_resolved=False, questions_changed=False,
        Form_edits=0, uploads=0, expert_responses=0, new_user_ratings=0,
        independent_final_evaluation=False, known_support_limitations_retained=True,
        reference_attempts=20, reference_failures=0, replacements=0,
        reference_process_exit_code=0, prediction_process_exit_code=0)
    write(OUT / 'packet_status.json', status); write(DELIVERY / 'release_status.json', status)
    write(OUT / 'presentation_audit.json', dict(**status, script_sha256=sha(Path(__file__)),
        review_page_sha256=sha(DELIVERY / 'DRAFT_REVIEW.html'),
        artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
    print(f'PASS20label/source/slot/route/scalar/full-frame/crop joins;{changed_controls}controls changed with input preparation;0fits. Draft held.')


if __name__ == '__main__': main()
