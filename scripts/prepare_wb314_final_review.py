"""Audit the one frozen predictor and display only changed, nonidentity outputs."""
from pathlib import Path
import base64
import collections
import hashlib
import json
import math
import re
import struct
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / 'outputs/wb314_final_training_v1'
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'
OUT = ROOT / 'outputs/wb314_final_changed_review_v1'
TEMPLATE = ROOT / 'outputs/wb_feature_exposure_review_v1/standalone.html'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    if OUT.exists():
        raise FileExistsError('Preserve any previous preparation attempt')
    proof = read(FINAL / 'verification.json')
    assert proof['passed'] and proof['real_fits'] == 1 and proof['scalar_render_checks'] == 66
    for p, digest in proof['artifacts'].items():
        assert sha(FINAL / p) == digest, p
    for p, digest in read(FINAL / 'bindings.json').items():
        assert sha(ROOT / p) == digest, p
    model = read(FINAL / 'model.json')
    assert sha(FINAL / 'model.json') == read(FINAL / 'model_seal.json')['model_sha256']
    assert model['dimensions'] == 314 and model['generated_fixture'] is False
    assert model['settings'] == read(WB / 'plan.json')['settings']
    rows = read(WB / 'rows.json')
    predictions = {r['case_id']: r for r in read(FINAL / 'training_predictions.json')}
    records = read(FINAL / 'render_comparison.json')['records']
    assert len(rows) == len(predictions) == len(records) == 66
    assert {r['case_id'] for r in records} == set(predictions)
    members = collections.defaultdict(list)
    # Separate scalar traversal: binary32 inputs, binary64 thresholds, <= branch.
    for row in rows:
        index, depth = 0, 0
        while model['nodes'][index]['kind'] != 'leaf':
            n = model['nodes'][index]
            x = struct.unpack('f', struct.pack('f', row['x314'][n['feature']]))[0]
            index = n['left'] if x <= n['threshold'] else n['right']
            depth += 1
            assert depth <= 4
        pred = predictions[row['case_id']]
        assert pred['source_id'] == row['source_id'] and pred['role'] == row['role']
        assert pred['leaf'] == index and pred['controls'] == model['nodes'][index]['values']
        members[index].append(row)
    assert set(members) == {i for i, n in enumerate(model['nodes']) if n['kind'] == 'leaf'}
    for index, own in members.items():
        for j in range(5):
            assert abs(math.fsum(r['y'][j] for r in own) / len(own)
                       - model['nodes'][index]['values'][j]) < 1e-12
    known = {p.replace('\\', '/'): h for p, h in read(WB / 'verification.json')['artifacts'].items()}
    changed, untouched_originals = [], []
    for record in records:
        name = record['case_id'] + '.npz'
        source, dest = WB / 'evaluation' / name, FINAL / 'evaluation' / name
        assert sha(source) == known['evaluation/' + name]
        assert sha(dest) == record['saved_sha256']
        with np.load(source, allow_pickle=False) as z, np.load(dest, allow_pickle=False) as new:
            a, old, image = new['candidate'], z['314'], z['input']
            equal = bool(np.array_equal(a, old))
            assert record['pixel_equal_old'] == equal
            assert record['pixels_changed_vs_old'] == int(np.any(a != old, axis=2).sum())
            assert record['pixel_equal_input'] == bool(np.array_equal(a, image))
            assert np.array_equal(a[z['protected']], image[z['protected']])
            assert np.array_equal(a[z['alpha'] == 0], image[z['alpha'] == 0])
            if record['role'] == 'identity':
                assert np.array_equal(a, image)  # All11 originals remain untouched.
                if not equal:
                    untouched_originals.append(record['case_id'])
            elif not equal:
                changed.append(record)
    assert len(changed) == 22 and len(untouched_originals) == 2
    audit = dict(passed=True, real_fits_performed_by_audit=0, portable_routes=66,
                 leaf_mean_checks=len(members) * 5, artifact_hashes=len(proof['artifacts']),
                 pixel_comparisons=66, protected_and_outside_checks=66,
                 unchanged_outputs=42, changed_nonidentity_outputs=22,
                 all11_identity_outputs_exact_input=True,
                 changed_identity_outputs_restored_exact_input=untouched_originals,
                 model_sha256=sha(FINAL / 'model.json'), qualification_complete=False)
    write(FINAL / 'independent_audit.json', audit)
    OUT.mkdir()
    (OUT / 'images').mkdir()
    cases = []
    order = ['colour_only', 'exposure_under', 'combined_under']
    changed.sort(key=lambda r: (order.index(r['role']), r['source_id']))
    for i, record in enumerate(changed, 1):
        source = WB / 'evaluation' / (record['case_id'] + '.npz')
        dest = FINAL / 'evaluation' / source.name
        with np.load(source, allow_pickle=False) as z, np.load(dest, allow_pickle=False) as new:
            arrays = dict(input=z['input'], candidate=new['candidate'], reference=z['reference'])
        case = {k: record[k] for k in ['case_id', 'source_id', 'role', 'controls', 'pixels_changed_vs_old']}
        case.update(review_id=f'wb314_final_changed_{i:02d}', parent_pack_sha256=sha(source),
                    final_pack_sha256=sha(dest))
        for name, array in arrays.items():
            path = OUT / 'images' / f'{i:02d}_{name}.png'
            Image.fromarray(array).save(path)
            with Image.open(path) as image:
                assert np.array_equal(np.asarray(image), array)
            case[name] = path.relative_to(OUT).as_posix()
            case[name + '_sha256'] = sha(path)
        cases.append(case)
    manifest = dict(schema='truehue_wb314_final_changed_review_manifest_v1', cases=cases,
                    review_round='wb314_final_changed_2026_11_18', generated_fixture=False,
                    model_sha256=sha(FINAL / 'model.json'),
                    final_verification_sha256=sha(FINAL / 'verification.json'),
                    independent_audit_sha256=sha(FINAL / 'independent_audit.json'),
                    unchanged_outputs_excluded=42,
                    restored_originals_excluded=untouched_originals,
                    previous_judgments_not_assigned_to_new_outputs=True,
                    scope='Development resubstitution outputs; not independent evaluation or expert MOS')
    write(OUT / 'manifest_PRIVATE.json', manifest)
    config = dict(manifest_sha256=sha(OUT / 'manifest_PRIVATE.json'), qa_fixture=False,
                  cases=[dict(review_id=c['review_id'], **{
                      k: 'data:image/png;base64,' + base64.b64encode((OUT / c[k]).read_bytes()).decode('ascii')
                      for k in ['input', 'candidate', 'reference']}) for c in cases])
    assert sha(TEMPLATE) == read(TEMPLATE.parent / 'preparation_PRIVATE.json')['standalone_sha256']
    html = TEMPLATE.read_text(encoding='utf-8')
    start = re.search(r'const CONFIG\s*=\s*', html).end()
    _, end = json.JSONDecoder().raw_decode(html[start:])
    html = html[:start] + json.dumps(config) + html[start + end:]
    changes = {
        '<title>Exposure correction usefulness</title>': '<title>Frozen WB314 predictor: changed outputs</title>',
        '<h1>Exposure correction: is the improvement useful?</h1>': '<h1>Frozen WB314 predictor: 22 changed corrections</h1>',
        "const key='truehue_wb_exposure_'+CONFIG.manifest_sha256;": "const key='truehue_wb314_final_changed_20261118_'+CONFIG.manifest_sha256;",
        'truehue-wb-feature-exposure-review.json': 'truehue-wb314-final-changed-review-2026-11-18.json',
        'All 8 cases recorded.': 'All 22 cases recorded.',
        'This page contains 8 exposure and combined-correction cases.': 'These 22 corrections changed when the fixed recipe was fitted once on all development rows. The 42 identical outputs and two originals restored exactly to input are excluded. Input is the distorted photo; Candidate is the single frozen predictor; Photographic reference is the original target. Judge the current candidate, including how the face fits the background. Previous answers are not filled in.',
        "review_kind:'exposure_usefulness_and_appearance',manifest_sha256:": "review_kind:'exposure_usefulness_and_appearance',review_round:'wb314_final_changed_2026_11_18',manifest_sha256:",
    }
    for old, new in changes.items():
        assert html.count(old) == 1, old
        html = html.replace(old, new)
    assert len(re.findall(r'data:image/png;base64,[A-Za-z0-9+/=]+', html)) == 66
    for c, embedded in zip(cases, config['cases']):
        for name in ['input', 'candidate', 'reference']:
            assert hashlib.sha256(base64.b64decode(embedded[name].split(',', 1)[1])).hexdigest() == c[name + '_sha256']
    (OUT / 'standalone.html').write_text(html, encoding='utf-8')
    write(OUT / 'verification.json', dict(passed=True, cases=22, native_PNG_roundtrips=66,
          embedded_PNGs_exact=66, manifest_sha256=sha(OUT / 'manifest_PRIVATE.json'),
          standalone_sha256=sha(OUT / 'standalone.html'), source_script_sha256=sha(Path(__file__)),
          ratings_generated=0, new_fits=0, new_correction_renders=0, interactive_browser_QA=False,
          role_counts=dict(collections.Counter(c['role'] for c in cases))))
    print('PASS independent66route/pixel/hash audit;22changed corrections/66exact PNGs;0new fits or ratings.')


if __name__ == '__main__':
    main()
