"""Import genuine frozen-predictor feedback without changing model or old reviews."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'outputs/wb314_final_changed_review_v1'
FINAL = ROOT / 'outputs/wb314_final_training_v1'
OUT = ROOT / 'outputs/wb314_final_changed_ratings_v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, type=Path)
    args = parser.parse_args()
    if OUT.exists():
        raise FileExistsError('Preserve previous import')
    raw = args.file.read_bytes()
    data = json.loads(raw.decode('utf-8-sig'))
    manifest = read(REVIEW / 'manifest_PRIVATE.json')
    prep = read(REVIEW / 'verification.json')
    assert prep['passed'] and prep['cases'] == 22
    assert sha(REVIEW / 'manifest_PRIVATE.json') == prep['manifest_sha256']
    assert sha(REVIEW / 'standalone.html') == prep['standalone_sha256']
    assert data['schema'] == 'truehue_exposure_usefulness_review_v1'
    assert data['review_kind'] == 'exposure_usefulness_and_appearance'
    assert data['review_round'] == manifest['review_round'] == 'wb314_final_changed_2026_11_18'
    assert data['manifest_sha256'] == sha(REVIEW / 'manifest_PRIVATE.json') and data['qa_fixture'] is False
    for name, field in [('model.json', 'model_sha256'), ('verification.json', 'final_verification_sha256'),
                        ('independent_audit.json', 'independent_audit_sha256')]:
        assert sha(FINAL / name) == manifest[field]
    final = read(FINAL / 'verification.json')
    assert final['passed'] and final['real_fits'] == 1
    for p, digest in final['artifacts'].items():
        assert sha(FINAL / p) == digest
    for p, digest in read(FINAL / 'bindings.json').items():
        assert sha(ROOT / p) == digest
    cases = manifest['cases']
    ids = [c['review_id'] for c in cases]
    changes = read(FINAL / 'render_comparison.json')['records']
    expected = {r['case_id'] for r in changes if not r['pixel_equal_old'] and r['role'] != 'identity'}
    assert len(ids) == len(set(ids)) == len(expected) == 22
    assert {c['case_id'] for c in cases} == expected
    for c in cases:
        assert sha(FINAL / 'evaluation' / (c['case_id'] + '.npz')) == c['final_pack_sha256']
        for name in ['input', 'candidate', 'reference']:
            assert sha(REVIEW / c[name]) == c[name + '_sha256']
    prefs = ['candidate', 'input', 'no_useful_difference', 'uncertain']
    looks = ['acceptable', 'unwanted', 'uncertain']
    answers = data['answers']
    assert isinstance(answers, dict) and set(answers) <= set(ids)
    for a in answers.values():
        assert a['preference'] in [None, *prefs] and a['appearance'] in [None, *looks]
        assert isinstance(a['note'], str)
    replay = {}
    assert isinstance(data['events'], list)
    for e in data['events']:
        assert e['review_id'] in ids
        if e['field'] == 'all':
            assert e['value'] == 'cleared'
            replay.pop(e['review_id'], None)
        else:
            assert e['field'] in ['preference', 'appearance']
            assert e['value'] in (prefs if e['field'] == 'preference' else looks)
            replay.setdefault(e['review_id'], {})[e['field']] = e['value']
    assert set(replay) == set(answers)
    assert all(replay[k].get(f) == a[f] for k, a in answers.items() for f in ['preference', 'appearance'])
    completed = [i for i in ids if i in answers and answers[i]['preference'] in prefs and answers[i]['appearance'] in looks]
    stopped = [i for i in ids if i in answers and answers[i]['appearance'] in ['unwanted', 'uncertain']]
    status = ('stopped_' + answers[stopped[0]]['appearance'] if stopped else
              'complete_recorded' if len(completed) == len(ids) else 'partial')
    assert data['status'] == status
    if stopped:
        assert not any(i in answers for i in ids[ids.index(stopped[0]) + 1:])
    records = [{k: c[k] for k in ['review_id', 'case_id', 'source_id', 'role']} |
               dict(answer=answers[c['review_id']]) for c in cases if c['review_id'] in answers]
    result = dict(status=status, complete_cases=len(completed), total=22,
                  preference_counts={v: sum(a['preference'] == v for a in answers.values()) for v in prefs},
                  appearance_counts={v: sum(a['appearance'] == v for a in answers.values()) for v in looks},
                  by_role={role: dict(preference_counts=dict(Counter(r['answer']['preference'] for r in records if r['role'] == role)),
                                     appearance_counts=dict(Counter(r['answer']['appearance'] for r in records if r['role'] == role)))
                           for role in sorted({c['role'] for c in cases})},
                  records=records, raw_sha256=hashlib.sha256(raw).hexdigest(),
                  model_sha256=manifest['model_sha256'], manifest_sha256=data['manifest_sha256'],
                  event_replay_matches=True, event_count=len(data['events']),
                  new_fits=0, new_renders=0, generated_ratings=0,
                  independent_evaluation=False, expert_MOS=False, qualification_complete=False,
                  historical_background_note_retracted=False)
    paths = [REVIEW / 'manifest_PRIVATE.json', REVIEW / 'verification.json', FINAL / 'model.json',
             FINAL / 'verification.json', FINAL / 'independent_audit.json', FINAL / 'render_comparison.json',
             ROOT / 'outputs/wb_feature_remaining_exposure_ratings_v1/combined_exposure_assessment.json',
             ROOT / 'outputs/wb_feature_colour_user_correction_v1/assessment_PRIVATE.json', Path(__file__)]
    bindings = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    OUT.mkdir()
    (OUT / 'raw_user_review_PRIVATE.json').write_bytes(raw)
    assert sha(OUT / 'raw_user_review_PRIVATE.json') == result['raw_sha256']
    write(OUT / 'assessment_PRIVATE.json', result)
    write(OUT / 'bindings.json', bindings)
    for p, digest in bindings.items():
        assert sha(ROOT / p) == digest
    write(OUT / 'verification.json', dict(passed=True, raw_bytes_preserved=True,
          event_replay_matches=True, exact_changed_roster=True, model_binding_valid=True,
          artifacts={p.name: sha(p) for p in OUT.iterdir() if p.is_file()},
          new_fits=0, new_renders=0, generated_ratings=0))
    print(json.dumps({k: result[k] for k in ['status', 'complete_cases', 'preference_counts',
          'appearance_counts', 'by_role', 'raw_sha256', 'event_count']}, indent=2))


if __name__ == '__main__':
    main()
