"""Audit cached packet pixels/labels and make the known-mask-issue release hold visible."""
from pathlib import Path
import base64
import csv
import hashlib
import html
import json
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/wb314_mste_development_packet_v1'
DELIVERY = ROOT / 'output/wb314-mst-development-feedback-2026-11-18'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(d, f, indent=2, allow_nan=False)
def embedded(p): return 'data:image/png;base64,' + base64.b64encode(Path(p).read_bytes()).decode('ascii')


def main():
    if (OUT / 'draft_audit.json').exists(): raise FileExistsError('Preserve earlier audit/hold')
    proof = read(DELIVERY / 'verification.json'); assert proof['passed'] and proof['pairs'] == 20
    for p, h in proof['artifacts'].items(): assert sha(DELIVERY / p) == h
    for p, h in read(OUT / 'bindings.json').items(): assert sha(p) == h
    plan = read(OUT / 'plan.json')
    for r in plan['selection']: assert sha(r['source_path']) == r['source_sha256']
    with (ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv').open(encoding='utf-8-sig', newline='') as f:
        catalogue = {'mst_e__' + r['subject_name'] + '/' + r['image_ID']: r for r in csv.DictReader(f)}
    manifest = read(DELIVERY / 'manifest_PRIVATE.json')
    slots = read(OUT / 'form_slot_check.json'); assert slots['passed']
    selected = {r['pair_id']: r for r in read(OUT / 'selected_references.json')}
    predictions = {r['pair_id']: r for r in read(OUT / 'predictions_sealed.json')['records']}
    visual = read(OUT / 'reference_visual_check.json')
    assert visual['distribution_ready'] is False and visual['cases_viewed'] == 20
    observations = {r['candidate_id']: r for r in visual['records']}
    sections = []; pair_images = []
    for i, r in enumerate(manifest['cases'], 1):
        source = selected[r['pair_id']]; official = catalogue[r['case_id']]; slot = slots['slots'][i-1]
        assert r['subject_id'] == official['subject_name'] and r['MST'] == int(official['MST']) == slot['MST']
        assert int(r['pair_id'].split('_')[-1]) == i == slot['slot']
        assert sha(OUT / 'evaluation' / (r['pair_id'] + '.npz')) == r['evaluation_sha256']
        reference_folder = OUT / 'references' / source['candidate_id']
        assert sha(reference_folder / 'reference_support.npz') == source['pack_sha256']
        with np.load(OUT / 'evaluation' / (r['pair_id'] + '.npz'), allow_pickle=False) as z:
            ref, image, candidate, m, a, p = [z[k] for k in ['reference', 'input', 'candidate', 'measurement', 'alpha', 'protected']]
        with np.load(reference_folder / 'reference_support.npz', allow_pickle=False) as z:
            assert all(np.array_equal(x, z[k]) for x, k in [(ref, 'reference'), (m, 'measurement'), (a, 'alpha'), (p, 'protected')])
        assert np.array_equal(ref, cv2.imread(str(reference_folder / 'input.png'))[:, :, ::-1])
        assert np.array_equal(candidate[p], image[p]) and np.array_equal(candidate[a == 0], image[a == 0])
        png = DELIVERY / r['png']; assert sha(png) == r['png_sha256']
        with Image.open(png) as im:
            pixels = np.asarray(im)
            assert pixels.shape == (256, 512, 3)
            assert np.array_equal(pixels[:, :256], ref) and np.array_equal(pixels[:, 256:], candidate)
            pair_images.append(im.copy())
        observation = observations[source['candidate_id']]
        assert sha(reference_folder / 'qa.png') == observation['board_sha256']
        sections.append('<section><h2>' + html.escape(slot['existing_heading']) + '</h2>'
                        '<p>Photographic reference (left) | Frozen WB314 correction (right)</p>'
                        '<img width="512" height="256" src="' + embedded(png) + '" alt="Reference and correction">'
                        '<details><summary>Reference/support inspection note</summary><p>' + html.escape(observation['observation'])
                        + '</p><img width="1024" height="280" src="' + embedded(reference_folder / 'qa.png')
                        + '" alt="Reference, measurement, application and protection overlays"></details></section>')
    assert len(selected) == len(predictions) == len(manifest['cases']) == 20
    for start in range(0, 20, 4):
        sheet = Image.new('RGB', (512, 280 * 4), 'white'); draw = ImageDraw.Draw(sheet)
        for j, im in enumerate(pair_images[start:start+4]):
            row = manifest['cases'][start+j]
            draw.text((4, j*280+5), f'{row["pair_id"]} | MST {row["MST"]} | reference / frozen correction', fill='black')
            sheet.paste(im, (0, j*280+24))
        sheet.save(OUT / f'correction_contact_{start//4+1:02d}.png')
    page = ('<!doctype html><meta charset="utf-8"><title>Review MST-labelled WB314 draft</title>'
            '<style>body{font:17px system-ui;max-width:1100px;margin:24px auto;padding:0 20px}section{border-top:1px solid #aaa;margin:25px 0}img{max-width:100%;height:auto}.hold{padding:16px;background:#fff0cc;border:2px solid #8a5700}details{margin:12px 0}summary{cursor:pointer}</style>'
            '<h1>MST-labelled development-feedback draft</h1><div class="hold"><strong>Draft: release decision pending.</strong>'
            '<p>The20corrections and publisher labels passed technical checks. Visual inspection found prototype masking issues, including facial-hair selection, a garment-collar leak and possible foreground/neck leakage. They are retained, not hidden or replaced.</p>'
            '<p>Do not upload or send this draft until the development-round release decision is recorded. The choice is whether to show this frozen prototype with these limitations disclosed or refine the affected supports first. No new model training is required to make that decision.</p></div>'
            '<p>Two pairs per MST category;13previously exposed people. Original Form questions and1–5scale are unchanged. This is formative model feedback, not final independent validation, expert approval or verified segmentation truth. Open each inspection note to see its support board.</p>'
            + ''.join(sections))
    (DELIVERY / 'DRAFT_REVIEW.html').write_text(page, encoding='utf-8')
    hold = ('DRAFT — NOT RELEASED FOR COLLECTION\n\n'
            'All20pair files, publisher labels, model routes and pixel-preservation checks passed. The model is unchanged.\n'
            'Visual inspection found known automatic support issues, particularly facial hair and some neck/collar/foreground boundaries. These are prototype findings, not expert responses or segmentation truth. See DRAFT_REVIEW.html.\n'
            'A user decision is needed before upload/distribution: retain this frozen prototype for development feedback with its issues disclosed, or refine the affected supports first. No Form question change or new fit has been selected.\n')
    (DELIVERY / 'RELEASE_HOLD.txt').write_text(hold, encoding='utf-8')
    archive = DELIVERY / 'expert-images.zip'; renamed = DELIVERY / 'expert-images-DRAFT-NOT-FOR-COLLECTION.zip'
    assert archive.resolve().is_relative_to(DELIVERY.resolve()) and renamed.resolve().is_relative_to(DELIVERY.resolve())
    archive.rename(renamed)
    status = dict(technical_checks_pass=True, publisher_MST_categories=10, pairs=20, subjects=13,
                  reference_attempts=21, reference_technical_failures=1, candidate_reserve_used_for_MST=[4],
                  distribution_ready=False, requires_user_release_decision=True,
                  stage='during_development_feedback_DRAFT', completed_client_date='2026-11-19',
                  known_support_findings_present=True, questions_changed=False, model_changed=False,
                  new_fits=0, expert_responses=0, uploads=0, contacts=0,
                  independent_final_evaluation=False, neutral_ID_draft_used=False,
                  unchanged_model_sha256=proof['model_sha256'])
    write(OUT / 'packet_status.json', status); write(DELIVERY / 'release_status.json', status)
    write(OUT / 'draft_audit.json', dict(passed=True, official_image_subject_MST_Form_joins=20,
          reference_BGR_RGB_joins=20, exact_support_joins=20, protected_outside_checks=20,
          left_reference_right_output_PNG_checks=20, source_hashes_unchanged=30,
          original_preparation_verification_sha256=sha(DELIVERY / 'verification.json'),
          review_page_sha256=sha(DELIVERY / 'DRAFT_REVIEW.html'),
          hold_note_sha256=sha(DELIVERY / 'RELEASE_HOLD.txt'),
          draft_archive_sha256=sha(renamed), distribution_ready=False,
          new_fits=0, new_feature_calls=0, new_correction_renders=0, script_sha256=sha(Path(__file__))))
    print('PASS20independent label/slot/colour/pixel joins; draft release HOLD recorded;0newinference/fits.')


if __name__ == '__main__': main()
