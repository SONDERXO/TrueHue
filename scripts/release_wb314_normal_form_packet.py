"""Copy the existing normal-photo primary pairs for development feedback.

Offline export only: no model calls, photo rendering, Form edits or submissions.
The cached public instrument must match its earlier sections and rating items.
"""
from pathlib import Path
import base64
import csv
import hashlib
import html
import io
import json
import re
import shutil
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/wb314-headroom-advisory-2026-11-19'
OUT = ROOT / 'outputs/wb314_normal_photo_expert_form_release_v1'
DELIVERY = ROOT / 'output/wb314-normal-photo-expert-form-2026-11-19'
ROUND = 'wb314_mste_normal_primary_development_round1_2026_11_19'
MODEL = '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)


INTRO = '''Please compare the original, uncorrected photograph on the LEFT with the main TrueHue model result on the RIGHT. No synthetic exposure or colour distortion was added to these photographs for this round.

Some original photographs may already look adequate. An unchanged result can be appropriate; a visible change is not automatically an improvement. The left image is the starting photograph, not a calibrated skin-colour ground truth.

Focus on the face and skin region. Use the existing overall 1-5 rating to assess the corrected result, considering exposure, colour and texture together. In the optional comments, describe useful changes, remaining problems or unwanted changes. Backgrounds may remain unchanged by the facial correction.

These are development-feedback materials. The face views are enlarged from 256-pixel whole-frame processing using exact pixel repetition; enlargement does not add detail. Please keep the same display settings while reviewing the pairs.
'''


def main():
    if OUT.exists() or DELIVERY.exists():
        raise FileExistsError('Preserve previous deliveries; do not replace this round')
    instrument = ROOT / 'outputs/wb314_normal_form_instrument_check_v1'
    definition = read(instrument / 'definition_PRIVATE.json')
    previous = read(ROOT / 'outputs/wb314_expert_instrument_respondent_access_v1/public_form_definition.json')
    current_items, old_items = definition[1][1], previous[1][1]
    sections = [x[1] for x in current_items if len(x) > 3 and x[3] == 8
                and str(x[1]).strip().startswith('Image Pair ')]
    expected = read(ROOT / 'outputs/wb314_expert_instrument_respondent_access_v1/instrument_summary.json')
    assert sections == expected['image_pair_sections'] and len(sections) == 20
    # Preserve full question definitions, including IDs, required flags and anchors.
    for kind in (0, 1, 2, 5):
        assert [x for x in current_items if x[3] == kind] == [x for x in old_items if x[3] == kind]
    assert sum(x[3] == 5 for x in current_items) == sum(x[3] == 1 for x in current_items) == 20
    audit = read(ROOT / 'outputs/wb314_headroom_advisory_integration_v1/verification.json')
    assert audit['passed'] and read(ROOT / 'outputs/wb314_headroom_advisory_integration_v1/finalization_verification.json')['passed']
    assert sha(ROOT / 'outputs/wb314_final_training_v1/model.json') == MODEL
    sealed = read(ROOT / 'outputs/wb314_normal_photo_preview_v1/predictions_sealed.json')
    assert sealed['model_sha256'] == MODEL and len(sealed['records']) == 20
    selected = read(ROOT / 'outputs/wb314_mste_development_packet_v2_area/selected_references.json')
    catalog_path = ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv'
    assert sha(catalog_path) == '1813993f7efba82ec0eca145520eb41cb9355f91d9e9a650bfb0c69870fc5ae8'
    with catalog_path.open(encoding='utf-8-sig', newline='') as stream:
        catalog = list(csv.DictReader(stream))
    OUT.mkdir(); DELIVERY.mkdir(); (DELIVERY / 'pairs').mkdir()
    write(OUT / 'authorization_PRIVATE.json', dict(
        selected_packet_use_authorized=True,
        source_page=str(SOURCE / 'START_HERE.html'), source_page_sha256=sha(SOURCE / 'START_HERE.html'),
        scope='Use existing main normal-photo pairs in existing Form; separate alternatives excluded; not individual ratings.'))
    write(OUT / 'instrument_encoding_correction.json', dict(
        passed=True, initial_check_preserved=True,
        initial_mismatch_cause='Default Windows text decoding of cached UTF-8 JSON; explicit UTF-8 comparison passes.',
        sections_exact_cached=20, complete_existing_question_definitions_equal=True,
        source_html_sha256=sha(instrument / 'respondent.html'),
        original_verification_sha256=sha(instrument / 'verification.json')))
    copied = []; mapping = []; panels = []
    for number, (row, reference, heading) in enumerate(zip(sealed['records'], selected, sections), 1):
        pair = f'image_pair_{number:02d}'; mst = (number + 1) // 2
        assert row['pair_id'] == reference['pair_id'] == pair
        assert row['MST'] == reference['MST'] == mst
        assert row['case_id'] == reference['case_id'] and row['subject_id'] == reference['subject_id']
        match = re.search(r'Image Pair (\d+).*MST Category:\s*(\d+)', heading)
        assert match and tuple(map(int, match.groups())) == (number, mst)
        official = [x for x in catalog if 'mst_e__' + x['subject_name'] + '/' + x['image_ID'] == row['case_id']]
        assert official and all(x['subject_name'] == row['subject_id'] and int(x['MST']) == mst for x in official)
        name = f'pairs/{pair}_mst{mst:02d}.png'; src = SOURCE / f'primary-pairs/{pair}.png'
        assert sha(src) == audit['artifacts'][f'primary-pairs/{pair}.png']
        baseline = ROOT / f'output/wb314-normal-photo-preview-2026-11-19/pairs/{pair}_mst{mst:02d}.png'
        assert src.read_bytes() == baseline.read_bytes()
        target = DELIVERY / name; shutil.copyfile(src, target)
        assert target.read_bytes() == src.read_bytes()
        encoded = base64.b64encode(target.read_bytes()).decode('ascii')
        assert base64.b64decode(encoded) == src.read_bytes()
        with Image.open(io.BytesIO(base64.b64decode(encoded))) as image:
            image.verify()
        copied.append(dict(pair=number, MST=mst, filename=name, sha256=sha(target),
                           case_id=row['case_id'], subject_id=row['subject_id'], Form_heading=heading))
        clean_heading = f'Image Pair {number:02d} - MST Category: {mst:02d}'
        mapping.append(f'{clean_heading} | {name}')
        panels.append(f'<section><h2>{clean_heading}</h2><p>Upload <code>{name}</code></p>'
                      f'<img alt="Original left; main correction right" src="data:image/png;base64,{encoded}"></section>')
    assert len({x['subject_id'] for x in copied}) == 13
    status = dict(passed=True, round_id=ROUND, model_sha256=MODEL,
        pairs=20, subjects=13, publisher_MST_categories=10, exact_primary_PNG_copies=20,
        exact_official_label_Form_slot_joins=20, embedded_PNG_byte_checks=20,
        normal_inputs_without_added_synthetic_distortion=True, protected_alternatives_included=False,
        questions_changed=False, existing_instrument_definitions_verified=True,
        intro_clarification_prepared=True, live_Form_updated=False, Form_images_inserted_by_agent=0,
        connected_document_sessions=0, live_Form_step_pending=True, expert_responses_accessed=0,
        invitations_sent=0, responses_submitted=0, new_fits=0, new_predictions=0,
        new_correction_renders=0, source_JPEG_reads=0, new_human_ratings=0,
        independent_final_validation=False, correction_model_finished=False)
    instructions = ('NORMAL-PHOTO DEVELOPMENT FEEDBACK\n\n'
        '1. Open the existing Google Form in Edit mode.\n'
        '2. Insert or replace the image under each matching Image Pair/MST section using only the 20 PNGs in pairs/. '
        'Follow UPLOAD_MAP.txt. Do not add the separate protected alternatives.\n'
        '3. Clarify the introductory instructions using FORM_INTRO_FOR_NORMAL_PHOTOS.txt. '
        'Keep consent, evaluator fields, questions, MST headings, overall 1-5 anchors and comments unchanged.\n'
        '4. Preview all 20 sections. Confirm original input LEFT and main correction RIGHT, correct order, '
        'two pairs per MST category, readable images, and unchanged rating/comment controls.\n\n'
        'The agent has not edited the live Form or uploaded images: no connected editor is available. '
        'No invitations, submissions or expert responses are included.\n\n'
        'Use this one fixed version during the round. Round ID: ' + ROUND + '\n'
        'Preserve any earlier actual responses under their original image/version; do not pool or relabel them. '
        'Earlier synthetic packets remain historical and are not this normal-photo round.\n\n'
        'Organizer context: these are 20 well-lit MST-E photos of 13 previously exposed people, '
        'not an independent final cohort or representative naturally faulty phone captures. Publisher MST labels '
        'group the evaluation; they are not predictor inputs. No model training uses this dataset. '
        'Known facial-mask, hair/beard, jewellery, neck/collar and foreground boundaries remain. '
        'The main outputs preserve their earlier highlight behaviour. The separate headroom candidates are not applied. '
        'Native processing is 256 pixels; the exact enlarged crops add no HD detail. '
        'This round gathers development feedback, not final model acceptance.\n')
    (DELIVERY / 'README.txt').write_text(instructions, encoding='utf-8')
    (DELIVERY / 'UPLOAD_MAP.txt').write_text('\n'.join(mapping) + '\n', encoding='utf-8')
    (DELIVERY / 'FORM_INTRO_FOR_NORMAL_PHOTOS.txt').write_text(INTRO, encoding='utf-8')
    page = ('<!doctype html><meta charset="utf-8"><title>Normal-photo Form upload guide</title>'
        '<style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:0 20px}'
        'img{max-width:100%;height:auto}section{border-top:1px solid #aaa;padding:20px 0}'
        'pre{white-space:pre-wrap}code{overflow-wrap:anywhere}</style>'
        '<h1>Normal-photo development feedback: upload guide</h1>'
        '<p><strong>Local package ready. Live Form insertion remains pending.</strong></p>'
        '<p>Original input left; unchanged main model result right. Separate protected alternatives are excluded.</p>'
        '<p><a href="WB314-normal-photo-expert-form.zip">Download upload ZIP</a></p>'
        '<pre>' + html.escape(instructions) + '</pre><h2>Introductory clarification</h2><pre>'
        + html.escape(INTRO) + '</pre>' + ''.join(panels))
    (DELIVERY / 'START_HERE.html').write_text(page, encoding='utf-8')
    write(DELIVERY / 'ROUND_STATUS.json', status)
    archive = DELIVERY / 'WB314-normal-photo-expert-form.zip'
    members = sorted(x for x in DELIVERY.rglob('*') if x.is_file())
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as bundle:
        for path in members:
            bundle.write(path, path.relative_to(DELIVERY).as_posix())
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert len([name for name in bundle.namelist() if name.endswith('.png')]) == 20
        assert not any('candidate' in name or 'PRIVATE' in name for name in bundle.namelist())
        for row in copied:
            assert hashlib.sha256(bundle.read(row['filename'])).hexdigest() == row['sha256']
    write(OUT / 'release_manifest_PRIVATE.json', dict(cases=copied,
        source_script_sha256=sha(Path(__file__)), instrument_definition_sha256=sha(instrument / 'definition_PRIVATE.json')))
    write(OUT / 'summary.json', status)
    write(OUT / 'verification.json', dict(passed=True, zip_CRC_pass=True, zip_PNG_hash_checks=20,
        artifacts={p.relative_to(DELIVERY).as_posix(): sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
    print('PASS: 20 exact main PNGs; 20 official MST/Form joins; unchanged questions; 20 embeds/ZIP hashes and CRC. Live insertion pending.')


if __name__ == '__main__':
    main()
