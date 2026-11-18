"""Exact cached-pixel draft for the existing20-slot form; no collection or cloud edits."""
from pathlib import Path
import base64
from collections import Counter
import hashlib
import html
import json
import zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
FINAL = ROOT / 'outputs/wb314_final_training_v1'
OUT = ROOT / 'output/wb314-expert-feedback-draft-2026-11-18'
PROTOCOL = ROOT / 'docs/wb314-expert-feedback-preparation-2026-11-18.md'
ROLES = ['colour_only', 'exposure_under', 'exposure_over', 'combined_under', 'combined_over']


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, d):
    with p.open('x', encoding='utf-8') as f: json.dump(d, f, indent=2, allow_nan=False)


def main():
    if OUT.exists(): raise FileExistsError('Preserve any earlier draft')
    proof = read(FINAL / 'verification.json'); assert proof['passed'] and proof['real_fits'] == 1
    for p, digest in proof['artifacts'].items(): assert sha(FINAL / p) == digest
    audit = read(FINAL / 'independent_audit.json'); assert audit['passed']
    review = read(ROOT / 'outputs/wb314_final_changed_ratings_v1/assessment_PRIVATE.json')
    assert review['complete_cases'] == 22 and review['appearance_counts']['acceptable'] == 22
    instrument = read(ROOT / 'outputs/wb314_expert_instrument_respondent_access_v1/instrument_summary.json')
    assert instrument['rating_items'] == instrument['comment_items'] == 20
    known = {p.replace('\\', '/'): h for p, h in read(WB / 'verification.json')['artifacts'].items()}
    pool = [r for r in read(FINAL / 'render_comparison.json')['records'] if r['role'] in ROLES]
    used = set(); counts = Counter(); selected = []
    def rank(row):
        return hashlib.sha256(('wb314-expert-development-2026-11-18-v1|' + row['case_id']).encode()).hexdigest()
    for repeat in range(4):
        for role in ROLES:
            row = min((r for r in pool if r['role'] == role and r['case_id'] not in used),
                      key=lambda r: (counts[r['source_id']], rank(r)))
            selected.append(row); used.add(row['case_id']); counts[row['source_id']] += 1
    assert len(used) == 20 and len(counts) == 11
    assert Counter(r['role'] for r in selected) == Counter({r: 4 for r in ROLES})
    for row in selected:
        name = row['case_id'] + '.npz'
        assert sha(WB / 'evaluation' / name) == known['evaluation/' + name]
        assert sha(FINAL / 'evaluation' / name) == row['saved_sha256']
    OUT.mkdir(); (OUT / 'pairs').mkdir()
    write(OUT / 'selection_PRIVATE.json', dict(status='DRAFT_PENDING_NEUTRAL_ID_ADAPTATION',
          protocol_sha256=sha(PROTOCOL), model_sha256=review['model_sha256'],
          algorithm='Four cycles of five roles; lowest source use, then fixed SHA256; no quality/tone inputs',
          records=[{k: r[k] for k in ['case_id', 'source_id', 'role']} for r in selected],
          source_counts=dict(counts), role_counts=dict(Counter(r['role'] for r in selected)),
          independent_evaluation=False, all_MST_labels_unqualified=True))
    intro = '''Draft replacement introduction for the initial development-feedback round

You are invited to provide expert feedback on a research prototype for facial exposure and colour correction. Each pair shows the original photographic reference on the left and this frozen model's correction of a synthetically distorted photograph on the right.

Focus on the facial skin region. Give one overall score using the existing scale, considering exposure, colour accuracy and texture together. Judge naturalness and agreement with the photographic reference rather than general photographic style. Optional comments can identify problems and guide model refinement.

Scale: 1 Bad; 2 Poor; 3 Fair; 4 Good; 5 Excellent.

These are development examples from a single frozen predictor. Pair numbers identify images; they are not Monk Skin Tone labels. This round does not establish per-tone performance, independent final validation or on-device Android performance. The planned supported tone-group and final appraisals remain separate requirements.

Keep the existing consent, evaluator-information, overall-score and optional-comment questions. Replace each MST-labelled section heading with its matching Image Pair number only. Do not add expert responses or change rating anchors.

Do not distribute this draft using the current MST-labelled form. The neutral-ID adaptation needs the researcher's decision and matching form edits first.
'''
    (OUT / 'form-revision-draft.txt').write_text(intro, encoding='utf-8')
    cases = []; sections = []
    for number, row in enumerate(selected, 1):
        name = row['case_id'] + '.npz'
        with np.load(WB / 'evaluation' / name, allow_pickle=False) as z: reference = z['reference']
        with np.load(FINAL / 'evaluation' / name, allow_pickle=False) as z: candidate = z['candidate']
        assert reference.dtype == candidate.dtype == np.uint8 and reference.shape == candidate.shape == (256, 256, 3)
        pair = np.concatenate([reference, candidate], axis=1)
        dest = OUT / 'pairs' / f'pair_{number:02d}.png'
        Image.fromarray(pair).save(dest)
        with Image.open(dest) as im: decoded = np.asarray(im)
        assert np.array_equal(decoded[:, :256], reference) and np.array_equal(decoded[:, 256:], candidate)
        case = dict(pair_id=f'pair_{number:02d}', section_title=f'Image Pair {number:02d}',
                    **{k: row[k] for k in ['case_id', 'source_id', 'role']},
                    png=dest.relative_to(OUT).as_posix(), png_sha256=sha(dest),
                    parent_pack_sha256=sha(WB / 'evaluation' / name), final_pack_sha256=sha(FINAL / 'evaluation' / name))
        cases.append(case)
        embedded = base64.b64encode(dest.read_bytes()).decode('ascii')
        sections.append(f'<section><h2>{case["section_title"]}</h2><p>Photographic reference (left) | Frozen research correction (right)</p><img width="512" height="256" alt="Reference and corrected image" src="data:image/png;base64,{embedded}"></section>')
    write(OUT / 'manifest_PRIVATE.json', dict(model_sha256=review['model_sha256'],
          selection_sha256=sha(OUT / 'selection_PRIVATE.json'), cases=cases,
          status='DRAFT_PENDING_NEUTRAL_ID_ADAPTATION', expert_responses=0, qualified_MST_labels=0))
    page = '<!doctype html><meta charset="utf-8"><title>WB314 expert-feedback draft</title><style>body{font:17px system-ui;max-width:900px;margin:24px auto;padding:0 20px}section{margin:30px 0;border-top:1px solid #aaa}img{max-width:100%;height:auto}.draft{padding:16px;background:#fff3d4}</style><h1>WB314 initial expert-feedback draft</h1><p class="draft">Not released for collection. These pair IDs have no verified MST categories. Align the form introduction and headings before use. No expert responses have been collected.</p><p>One frozen research predictor;20development pairs from11sources. Reference left, correction right. This is not final independent validation.</p>' + ''.join(sections)
    (OUT / 'gallery.html').write_text(page, encoding='utf-8')
    write(OUT / 'verification.json', dict(passed=True, pair_count=20, source_count=11,
          per_condition=4, native_pixel_PNG_roundtrips=20, resampling=False,
          new_fits=0, feature_calls=0, predictions=0, correction_renders=0,
          submitted_responses=0, online_form_edits=0, images_uploaded=0,
          protocol_sha256=sha(PROTOCOL), script_sha256=sha(Path(__file__)),
          artifacts={p.relative_to(OUT).as_posix(): sha(p) for p in OUT.rglob('*') if p.is_file()}))
    with zipfile.ZipFile(OUT / 'wb314-expert-feedback-draft.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for p in OUT.rglob('*'):
            if p.is_file() and p.suffix != '.zip': z.write(p, p.relative_to(OUT).as_posix())
    print('PASS20exact cached pairs/11sources/4per condition;0fits or online changes. Draft awaits neutral-ID decision.')


if __name__ == '__main__': main()
