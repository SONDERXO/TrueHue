"""Release exact approved V2 image bytes for the first development-feedback round.

Copies cached PNGs only. No inference, source-image decode, resampling, fitting,
Form edit, upload, invitation or response submission occurs here.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/wb314-mst-development-feedback-2026-11-19-v2'
EVIDENCE = ROOT / 'outputs/wb314_mste_development_packet_v2_area'
OUT = ROOT / 'outputs/wb314_mste_development_round1_release_v1'
DELIVERY = ROOT / 'output/wb314-expert-development-round1-2026-11-19'
MODEL_SHA = '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'
ROUND = 'wb314_mste_v2_area_development_round1_2026_11_19'


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False)


def main():
    if OUT.exists() or DELIVERY.exists():
        raise FileExistsError('Preserve earlier release; do not silently replace a round')
    audit = read(EVIDENCE / 'presentation_audit.json')
    assert audit['passed'] and audit['pairs'] == 20 and audit['model_sha256'] == MODEL_SHA
    assert sha(ROOT / 'outputs/wb314_final_training_v1/model.json') == MODEL_SHA
    for name, digest in audit['artifacts'].items(): assert sha(SOURCE / name) == digest
    assert read(EVIDENCE / 'final_embedded_byte_check.json')['passed']
    rows = read(SOURCE / 'presentation_manifest_PRIVATE.json')['cases']
    slots = read(ROOT / 'outputs/wb314_mste_development_packet_v1/form_slot_check.json')
    assert slots['passed'] and slots['scale_unchanged'] and len(rows) == len(slots['slots']) == 20
    feedback = ROOT / 'outputs/wb314_mste_v2_appearance_reply_v1'
    assert read(feedback / 'interpretation.json')['user_reports_batch_improvement']
    OUT.mkdir(); DELIVERY.mkdir(); (DELIVERY / 'pairs').mkdir()
    (OUT / 'user_authorization.txt').write_text('okay lets do that', encoding='utf-8')
    write(OUT / 'authorization_context.json', dict(
        exact_user_reply='okay lets do that',
        preceding_recommendation='Place exact V2 images into the existing Form with MST labels, questions, scale and comments unchanged; keep model fixed during development feedback.',
        prior_batch_improvement_reply_sha256=sha(feedback / 'user_reply.txt'),
        meaning='Authorizes this V2 initial-development round and Form image placement, not final model adoption or invented ratings.',
        external_invitations_sent=0))
    sections = []; mapping = []; copied = []
    for number, (row, slot) in enumerate(zip(rows, slots['slots']), 1):
        assert int(row['pair_id'].split('_')[-1]) == number == slot['slot']
        assert row['MST'] == slot['MST'] and row['Form_heading'] == slot['existing_heading']
        src = SOURCE / row['face_pair']; assert sha(src) == row['face_pair_sha256']
        target = DELIVERY / 'pairs' / src.name
        shutil.copyfile(src, target); assert src.read_bytes() == target.read_bytes()
        copied.append(dict(pair=number, MST=row['MST'], Form_section=slot['existing_heading'],
            filename='pairs/' + target.name, sha256=sha(target)))
        mapping.append(f'{number:02d} | {slot["existing_heading"].strip()} | pairs/{target.name}')
        x, y, w, h = row['face_box_xywh']
        encoded = base64.b64encode(target.read_bytes()).decode('ascii')
        assert base64.b64decode(encoded) == src.read_bytes()
        sections.append(f'<section><h2>{html.escape(slot["existing_heading"])}</h2>'
            f'<p>Upload: <code>pairs/{target.name}</code></p>'
            '<p>Photographic reference (left) | WB314 correction (right)</p>'
            f'<img width="{2*w}" height="{h}" alt="Reference left and correction right" '
            f'src="data:image/png;base64,{encoded}"></section>')
    note = ('Initial development-feedback round using the frozen WB314 V2 images. '
        '20photographic pairs cover all10publisher MST categories and13previously exposed people. '
        'Images use256px whole-frame analysis with native face-box presentation and reference-derived supports. '
        'Prototype masks can include facial hair and imperfect hair, jewellery, neck/collar or foreground boundaries. '
        'This round gathers professional feedback for development; it is not final independent appraisal. '
        'No expert ratings or participation are assumed.')
    guide = ('WB314 V2 — initial expert development-feedback upload\n\n'
        '1. Open your existing Google Form in Edit mode.\n'
        '2. Insert each PNG in pairs/ under its matching Image Pair/MST section. Use UPLOAD_MAP.txt or START_HERE.html. '
        'Keep the existing questions, consent, evaluator fields, overall1–5scale and optional comments unchanged.\n'
        '3. Preview the respondent Form. Check all20image sections: photographic reference left, WB314 correction right, '
        'two pairs per MST1–10. The upload itself has not been performed by this package.\n\n'
        'Use this one fixed image/model version throughout the round. Preserve returned ratings/comments separately '
        'under round ID ' + ROUND + '. Earlier user reviews are not expert responses.\n\n'
        'Development-stage context to accompany the review:\n' + note + '\n\n'
        'The folder dated2026-11-18 is the older V1 draft. Use only this package for the new round. '
        'Historical V1/V2 preparation drafts and their original hold notices are preserved as records; '
        'the user subsequently reported improvement and authorized this round. '
        'Full frames/support boards remain in the original V2 preparation folder for inspection.\n\n'
        'Live Form status: no connected document editor and native browser control unavailable. '
        'Images have not been uploaded and Form content has not been edited. No invitations were sent.\n')
    (DELIVERY / 'README.txt').write_text(guide, encoding='utf-8')
    (DELIVERY / 'UPLOAD_MAP.txt').write_text('\n'.join(mapping)+'\n', encoding='utf-8')
    page = ('<!doctype html><meta charset="utf-8"><title>WB314 V2 development round 1</title>'
        '<style>body{font:17px system-ui;max-width:900px;margin:24px auto;padding:0 20px}'
        'section{border-top:1px solid #aaa;margin:24px 0}img{max-width:100%;height:auto}'
        '.status{padding:16px;background:#eaf4ed}code{overflow-wrap:anywhere}</style>'
        '<h1>WB314 V2: expert development round 1</h1>'
        '<div class="status"><strong>Local materials released for initial development feedback.</strong>'
        '<p>The20images below are exact copies of the approved V2 files. The live Google Form still needs image insertion.</p></div>'
        '<p>Open your existing Form in Edit mode. Insert the named PNG into its matching existing section. '
        'Keep questions, consent, MST categories, overall1–5scale and comments unchanged. Preview all20sections after insertion.</p>'
        '<p>' + html.escape(note) + '</p>' + ''.join(sections))
    (DELIVERY / 'START_HERE.html').write_text(page, encoding='utf-8')
    status = dict(round_id=ROUND, model_sha256=MODEL_SHA, local_materials_released=True,
        user_authorized_initial_development_round=True, pairs=20, subjects=13, publisher_MST_categories=10,
        byte_identical_V2_PNG_copies=20, exact_Form_slot_joins=20, questions_changed=False,
        live_Form_updated=False, Form_images_inserted=0, connected_document_sessions=0,
        browser_control_available=False, live_Form_step_pending=True, expert_responses=0,
        invitations_sent=0, new_fits=0, new_predictions=0, resampling=False,
        independent_final_appraisal=False, final_model_adoption=False,
        known_support_limitations_disclosed=True, old_drafts_and_feedback_preserved=True)
    write(DELIVERY / 'ROUND_STATUS.json', status); write(OUT / 'summary.json', status)
    write(OUT / 'release_manifest_PRIVATE.json', dict(status=status, cases=copied,
        original_presentation_audit_sha256=sha(EVIDENCE / 'presentation_audit.json'),
        source_script_sha256=sha(Path(__file__))))
    archive = DELIVERY / 'WB314-V2-expert-development-round1.zip'
    members = sorted(p for p in DELIVERY.rglob('*') if p.is_file())
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for p in members: z.write(p, p.relative_to(DELIVERY).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len([n for n in z.namelist() if n.endswith('.png')]) == 20
        for row in copied:
            assert hashlib.sha256(z.read(row['filename'])).hexdigest() == row['sha256']
    write(OUT / 'verification.json', dict(passed=True, **status, zip_CRC_pass=True,
        archive_sha256=sha(archive), artifacts={p.relative_to(DELIVERY).as_posix():sha(p)
            for p in DELIVERY.rglob('*') if p.is_file()}))
    print('PASS20exact V2 PNG copies/20existing MST-Form joins/ZIP CRC;local release ready;live Form insertion pending;0fits/inference.')


if __name__ == '__main__': main()
