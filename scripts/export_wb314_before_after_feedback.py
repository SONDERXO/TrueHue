"""Fix development-feedback pairing: actual distorted input left, saved output right.

Uses only the20sealed V2 evaluation arrays and existing reference-derived crop
boxes. No correction inference, source-photo decode, fitting or mask change.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'outputs/wb314_mste_development_packet_v2_area'
OLD_NATIVE = ROOT / 'output/wb314-expert-development-round1-2026-11-19'
OLD_LARGE = ROOT / 'output/wb314-expert-development-round1-large-2026-11-19'
OUT = ROOT / 'outputs/wb314_before_after_feedback_v1'
DELIVERY = ROOT / 'output/wb314-expert-before-after-2026-11-19'
MODEL_SHA = '7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f'
ROUND = 'wb314_mste_v2_before_after_development_round1_2026_11_19'


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, data):
    with p.open('x', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False, allow_nan=False)
def embedded(p): return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode('ascii')


def main():
    if OUT.exists() or DELIVERY.exists(): raise FileExistsError('Preserve earlier pairing exports')
    predictions = read(PARENT / 'predictions_sealed.json')
    assert predictions['model_sha256'] == MODEL_SHA
    assert sha(ROOT / 'outputs/wb314_final_training_v1/model.json') == MODEL_SHA
    rows = predictions['records']; assert len(rows) == 20
    old = read(ROOT / 'outputs/wb314_development_feedback_large_v1/verification.json')
    assert old['passed']
    for name, digest in old['artifacts'].items(): assert sha(OLD_LARGE / name) == digest
    crops = {r['pair_id']:r for r in read(ROOT / 'output/wb314-mst-development-feedback-2026-11-19-v2/presentation_manifest_PRIVATE.json')['cases']}
    slots = read(ROOT / 'outputs/wb314_mste_development_packet_v1/form_slot_check.json'); assert slots['passed']
    OUT.mkdir(); DELIVERY.mkdir(); (DELIVERY / 'pairs').mkdir(); (DELIVERY / 'native-pairs').mkdir()
    records = []; sections = []; mapping = []
    for i, (r, slot) in enumerate(zip(rows, slots['slots']), 1):
        assert int(r['pair_id'].split('_')[-1]) == i == slot['slot']
        assert r['MST'] == slot['MST'] == crops[r['pair_id']]['MST']
        source = PARENT / 'evaluation' / (r['pair_id']+'.npz')
        assert sha(source) == r['evaluation_sha256']
        with np.load(source, allow_pickle=False) as z:
            image, candidate, reference = [z[k].copy() for k in ['input','candidate','reference']]
        x,y,w,h = crops[r['pair_id']]['face_box_xywh']
        before = image[y:y+h,x:x+w]; after = candidate[y:y+h,x:x+w]
        assert before.shape == after.shape == (h,w,3)
        assert not np.array_equal(before,reference[y:y+h,x:x+w])
        native = np.concatenate([before,after],axis=1)
        large = np.repeat(np.repeat(native,4,axis=0),4,axis=1)
        name = r['pair_id']+f'_mst{r["MST"]:02d}.png'
        p = DELIVERY/'native-pairs'/name; q = DELIVERY/'pairs'/name
        Image.fromarray(native).save(p); Image.fromarray(large).save(q)
        with Image.open(p) as im: assert np.array_equal(np.asarray(im),native)
        with Image.open(q) as im:
            pixels = np.asarray(im)
            for dy in range(4):
                for dx in range(4): assert np.array_equal(pixels[dy::4,dx::4],native)
        with Image.open(OLD_NATIVE/'pairs'/name) as im:
            assert np.array_equal(np.asarray(im)[:,w:],after)
        with Image.open(OLD_LARGE/'pairs'/name) as im:
            assert np.array_equal(np.asarray(im)[:,w*4:],large[:,w*4:])
        records.append(dict(pair=i,MST=r['MST'],Form_section=slot['existing_heading'],
            evaluation_sha256=sha(source),face_box=[x,y,w,h],native_path='native-pairs/'+name,
            large_path='pairs/'+name,native_sha256=sha(p),large_sha256=sha(q),
            left_exact_cached_distorted_input=True,right_exact_previously_released_candidate=True))
        mapping.append(f'{i:02d} | {slot["existing_heading"].strip()} | pairs/{name}')
        sections.append(f'<section><h2>{html.escape(slot["existing_heading"])}</h2>'
            '<p><strong>BEFORE: uncorrected input (left) | AFTER: model correction (right)</strong></p>'
            f'<p>Form file: <code>pairs/{name}</code></p><div class="viewport">'
            f'<img width="{w*8}" height="{h*4}" src="{embedded(q)}" alt="Uncorrected input left, corrected result right"></div>'
            '<details><summary>Native-size comparison</summary>'
            f'<img width="{w*2}" height="{h}" src="{embedded(p)}" alt="Native before and after"></details></section>')
    intro = ('You are invited to participate as an expert evaluator in a study on smartphone-based skin tone correction. '
        'You will be shown pairs of facial images: the uncorrected input photo before correction (left) and the corrected version produced by the system (right). '
        'The left image contains the exposure and colour problems supplied to the system; it is not a colour-accuracy reference.\n\n'
        'Please focus on the face and skin region, disregarding background elements. Use the left image to understand the starting condition. '
        'Give the existing overall1–5rating for the corrected image, considering skin exposure, colour appearance, texture naturalness and overall skin-region quality. '
        'Use the comments to describe improvements, remaining problems or new artifacts; a visible change is not automatically an improvement.\n\n'
        'This is development-stage feedback on a prototype. Images are4×viewing copies of256px processed outputs and do not contain added detail. '
        'Colour-restoration error against the clean dataset photograph is evaluated separately using quantitative metrics. '
        'Professional scores/comments and quantitative results will be reported under their actual model and presentation versions.\n\n'
        'By proceeding, you confirm that you understand the purpose of this evaluation and agree to participate as an expert evaluator.')
    (DELIVERY/'FORM_INTRO_CLARIFICATION.txt').write_text(intro+'\n',encoding='utf-8')
    (DELIVERY/'UPLOAD_MAP.txt').write_text('\n'.join(mapping)+'\n',encoding='utf-8')
    guide = ('WB314 V2 — BEFORE/AFTER expert development feedback\n\n'
        'This is the corrected pairing requested by the user. LEFT is the actual uncorrected input supplied to the model. '
        'RIGHT is exactly the previously saved model output. The clean dataset target is retained internally for restoration-error metrics; it is not the left panel here.\n\n'
        'Upload the20PNGs from pairs/ to the existing matching Image Pair/MST sections, using UPLOAD_MAP.txt. '
        'Keep consent, evaluator fields, all rating questions, MST headings, overall1–5scale and comments unchanged. '
        'Clarify the Form introduction using FORM_INTRO_CLARIFICATION.txt so that reference/accuracy wording does not contradict before/after pairing. '
        'The clarification is introductory guidance; it adds no rating items. Preview all20sections before collection.\n\n'
        'Use this before/after package instead of the earlier target-versus-output packages for the requested development round. '
        'They serve different evaluation purposes. Keep any actual earlier answers under their actual image/instruction version; do not relabel or transfer them. '
        'No responses have been supplied or accessed during this export.\n\n'
        '20pairs represent13previously exposed people, two per official MST1–10; ten fixed combined-under and ten combined-over conditions. '
        'The4×pixel repetition is for viewing only; native face detail is limited to70–128pixels wide. '
        'Reference-derived masks have known hair, beard, jewellery, neck/collar and possible foreground limitations. '
        'This is initial development feedback, not final independent evaluation or proof of physical colour accuracy.\n\n'
        'Round: '+ROUND+'\nLive Form status: no image insertion, introduction edit, upload, invitation or response submission has occurred here; '
        'the known editor/browser connection limitation remains.\n')
    (DELIVERY/'README.txt').write_text(guide,encoding='utf-8')
    page = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>WB314: before and after expert feedback</title><style>'
        'body{font:18px system-ui;max-width:1150px;margin:24px auto;padding:0 20px;color:#222}'
        'section{border-top:1px solid #aaa;margin:32px 0}.viewport{overflow-x:auto}'
        'img{max-width:none;display:block;image-rendering:pixelated}.note{background:#edf3f7;padding:16px}'
        'details{margin:16px 0}summary{cursor:pointer}code{overflow-wrap:anywhere}</style>'
        '<h1>Before and after — WB314 development feedback</h1><div class="note">'
        '<p><strong>Left: photo before correction. Right: the same photo after model correction.</strong></p>'
        '<p>These are the existing V2 inputs and outputs. The model has not been rerun or strengthened. '
        'The clean target photograph is kept separately for quantitative restoration checks.</p></div>'
        '<p>Use the20PNGs in pairs/ for the existing Form sections. Clarify the introduction using '
        'FORM_INTRO_CLARIFICATION.txt; rating questions, scale, MST headings and comments remain unchanged. '
        'The live Form has not been edited or uploaded to.</p>'
        '<p>4×viewing copies: larger pixels, not additional detail.13previously exposed people; prototype mask and native256px processing limitations remain. '
        'Use the same presentation/instructions throughout this development round.</p>'+''.join(sections))
    (DELIVERY/'START_HERE.html').write_text(page,encoding='utf-8')
    summary = dict(round_id=ROUND,presentation='before_input_after_output_4x',model_sha256=MODEL_SHA,
        pairs=20,subjects=13,publisher_MST_categories=10,unchanged_Form_slot_joins=20,
        exact_input_left_checks=20,exact_saved_candidate_right_checks=20,exact_4x_repeat_checks=20,
        left_is_clean_reference=False,clean_reference_kept_for_quantitative_restoration=True,
        questions_changed=False,scale_changed=False,intro_clarification_prepared=True,live_Form_updated=False,
        new_fits=0,new_model_calls=0,new_source_portrait_decodes=0,new_human_ratings=0,
        model_changed=False,masks_changed=False,previous_outputs_and_packages_preserved=True,
        rating_transfer=False,independent_final_evaluation=False)
    write(OUT/'summary.json',summary); write(DELIVERY/'PRESENTATION_STATUS.json',summary)
    write(OUT/'manifest_PRIVATE.json',dict(records=records,parent_predictions_sha256=sha(PARENT/'predictions_sealed.json'),
        script_sha256=sha(Path(__file__))))
    archive = DELIVERY/'WB314-before-after-expert-feedback.zip'
    files = sorted(p for p in DELIVERY.rglob('*') if p.is_file())
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,p.relative_to(DELIVERY).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for r in records:
            assert hashlib.sha256(z.read(r['large_path'])).hexdigest()==r['large_sha256']
            assert hashlib.sha256(z.read(r['native_path'])).hexdigest()==r['native_sha256']
    for name,digest in old['artifacts'].items():assert sha(OLD_LARGE/name)==digest
    write(OUT/'verification.json',dict(passed=True,**summary,zip_CRC_pass=True,
        artifacts={p.relative_to(DELIVERY).as_posix():sha(p) for p in DELIVERY.rglob('*') if p.is_file()}))
    print('PASS20cached-input-left/20unchanged-output-right/20existing MST-slots/4xrepeat+ZIPCRC;0modelcalls/fits.')


if __name__ == '__main__': main()
