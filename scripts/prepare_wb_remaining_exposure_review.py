"""Finish existing WB314 review coverage without inference or changed corrections."""
from pathlib import Path
import json
import hashlib
import base64
import re
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
PARENT = ROOT / 'outputs/wb_feature_exposure_review_v1'
NINE = ROOT / 'outputs/wb_feature_remaining_under_review_v1'
OUT = ROOT / 'outputs/wb_feature_remaining_exposure_review_v1'
PROTOCOL = ROOT / 'docs/wb-remaining-exposure-review-protocol-2026-11-18.md'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve prior preparation or partial attempt')
    proof = read(WB / 'verification.json')
    assert proof['passed']
    known = {p.replace('\\', '/'): h for p, h in proof['artifacts'].items()}
    assert sha(WB / 'records.json') == known['records.json']
    parent = read(PARENT / 'manifest_PRIVATE.json')
    nine = read(NINE / 'manifest_PRIVATE.json')
    completed = [parent, nine]
    raw_paths = [ROOT / 'outputs/wb_feature_exposure_rereview_ratings_v1/raw_user_review_PRIVATE.json',
                 ROOT / 'outputs/wb_feature_remaining_under_ratings_v1/raw_user_review_PRIVATE.json']
    for manifest, path, directory in zip(completed, raw_paths, [PARENT, NINE]):
        data = read(path)
        assert data['status'] == 'complete_recorded' and data['manifest_sha256'] == sha(directory / 'manifest_PRIVATE.json')
        assert set(data['answers']) == {c['review_id'] for c in manifest['cases']}
    reviewed = {c['case_id'] for m in completed for c in m['cases']}
    assert len(reviewed) == 17
    records = read(WB / 'records.json')
    selected = []
    for role in ['exposure_over', 'combined_under', 'combined_over']:
        own = sorted([r for r in records if r['role'] == role and r['case_id'] not in reviewed], key=lambda r: r['source_id'])
        assert len(own) == 9
        selected.extend(own)
    assert len({r['case_id'] for r in selected}) == 27 and not reviewed & {r['case_id'] for r in selected}
    exposure = {r['case_id'] for r in records if r['role'] in ['exposure_under', 'exposure_over', 'combined_under', 'combined_over']}
    assert reviewed | {r['case_id'] for r in selected} == exposure and len(exposure) == 44
    for row in selected:
        p = WB / 'evaluation' / (row['case_id'] + '.npz')
        assert sha(p) == known['evaluation/' + p.name]
    assert sha(PARENT / 'standalone.html') == read(PARENT / 'preparation_PRIVATE.json')['standalone_sha256']
    OUT.mkdir()
    (OUT / 'images').mkdir()
    write(OUT / 'selection_PRIVATE.json', [{k: r[k] for k in ['case_id', 'source_id', 'role']} for r in selected])
    cases = []
    for i, row in enumerate(selected, 1):
        p = WB / 'evaluation' / (row['case_id'] + '.npz')
        with np.load(p, allow_pickle=False) as pack:
            arrays = {name: pack[key] for name, key in [('input', 'input'), ('candidate', '314'), ('reference', 'reference')]}
        case = {k: row[k] for k in ['case_id', 'source_id', 'role']}
        case.update(review_id=f'wb_remaining_exposure_{i:02d}', cached_pack_sha256=sha(p))
        for name, a in arrays.items():
            assert a.dtype == np.uint8
            dest = OUT / 'images' / f'{i:02d}_{name}.png'
            Image.fromarray(a).save(dest)
            with Image.open(dest) as image:
                assert np.array_equal(np.asarray(image), a)
            case[name] = dest.relative_to(OUT).as_posix()
            case[name + '_sha256'] = sha(dest)
        case['pixel_identical'] = bool(np.array_equal(arrays['input'], arrays['candidate']))
        cases.append(case)
    manifest = {k: v for k, v in parent.items() if k not in ['cases', 'unreviewed_cases', 'selection_sha256', 'protocol_sha256']}
    manifest.update(cases=cases, unreviewed_cases=0, selection_sha256=sha(OUT / 'selection_PRIVATE.json'),
                    protocol_sha256=sha(PROTOCOL), previous_reviews={str(p.relative_to(ROOT)): sha(p) for p in raw_paths},
                    prior_review_cases=17, combined_exposure_cases_if_completed=44)
    write(OUT / 'manifest_PRIVATE.json', manifest)
    config = dict(manifest_sha256=sha(OUT / 'manifest_PRIVATE.json'), qa_fixture=False,
                  cases=[dict(review_id=c['review_id'], **{k: 'data:image/png;base64,' + base64.b64encode((OUT / c[k]).read_bytes()).decode('ascii')
                          for k in ['input', 'candidate', 'reference']}) for c in cases])
    html = (PARENT / 'standalone.html').read_text(encoding='utf-8')
    start = re.search(r'const CONFIG\s*=\s*', html).end()
    _, end = json.JSONDecoder().raw_decode(html[start:])
    html = html[:start] + json.dumps(config) + html[start + end:]
    changes = {
        "const key='truehue_wb_exposure_'+CONFIG.manifest_sha256;": "const key='truehue_wb_remaining_exposure_20261118_'+CONFIG.manifest_sha256;",
        'truehue-wb-feature-exposure-review.json': 'truehue-wb-feature-remaining-exposure-review-2026-11-18.json',
        'All 8 cases recorded.': 'All 27 cases recorded.',
        'This page contains 8 exposure and combined-correction cases.': 'This page contains the 27 previously unreviewed exposure/combined cases. No earlier cases are repeated. Input is the distorted photo; Candidate is the saved correction; Photographic reference is the original target.',
        "review_kind:'exposure_usefulness_and_appearance',manifest_sha256:": "review_kind:'exposure_usefulness_and_appearance',review_round:'remaining_exposure_2026_11_18',manifest_sha256:",
        '<h1>Exposure correction: is the improvement useful?</h1>': '<h1>WB314: remaining exposure and combined cases</h1>',
    }
    for old, new in changes.items():
        assert html.count(old) == 1, old
        html = html.replace(old, new)
    assert len(re.findall(r'data:image/png;base64,[A-Za-z0-9+/=]+', html)) == 81
    for c, embedded in zip(cases, config['cases']):
        for name in ['input', 'candidate', 'reference']:
            raw = base64.b64decode(embedded[name].split(',', 1)[1])
            assert hashlib.sha256(raw).hexdigest() == c[name + '_sha256']
    (OUT / 'standalone.html').write_text(html, encoding='utf-8')
    for row in selected:
        p = WB / 'evaluation' / (row['case_id'] + '.npz')
        assert sha(p) == known['evaluation/' + p.name]
    write(OUT / 'verification.json', dict(passed=True, cases=27, complete_remaining_exposure_roster=True,
          previous_cases_repeated=0, native_PNG_roundtrips=81, embedded_PNGs_exact=81, prior_cases=17,
          manifest_sha256=sha(OUT / 'manifest_PRIVATE.json'), standalone_sha256=sha(OUT / 'standalone.html'),
          source_script_sha256=sha(Path(__file__)), ratings_generated=0, new_fits=0, new_inference=0,
          new_correction_renders=0, controls_unchanged=True, interactive_browser_QA=False))
    print('PASS 27 existing outputs/81 exact PNGs;0 repeated cases/fits/inference/correction changes.', flush=True)


if __name__ == '__main__':
    main()
