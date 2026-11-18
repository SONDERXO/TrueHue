"""Independent saved-result/hashes/margin/summary audit; no fitting or images."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/synthetic_exposure_ranking_prediction_v1'
ADMISSION = ROOT / 'outputs/synthetic_exposure_ranking_admission_v1'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b):
    assert math.isclose(a, b, abs_tol=1e-10, rel_tol=1e-10), (a, b)


def stats(rows):
    n = len(rows)
    return dict(comparisons=n, wins=sum(r['margin'] > 0 for r in rows),
                ties=sum(r['margin'] == 0 for r in rows),
                losses=sum(r['margin'] < 0 for r in rows),
                strict_accuracy=sum(r['margin'] > 0 for r in rows) / n,
                half_credit_accuracy=sum((r['margin'] > 0) + .5 * (r['margin'] == 0) for r in rows) / n,
                logistic_loss=math.fsum(max(0., -r['margin']) + math.log1p(math.exp(-abs(r['margin']))) for r in rows) / n,
                mean_margin=math.fsum(r['margin'] for r in rows) / n,
                min_margin=min(r['margin'] for r in rows), max_margin=max(r['margin'] for r in rows))


def main():
    dest = OUT / 'independent_assessment_verification.json'
    if dest.exists():
        raise FileExistsError(dest)
    verification = read(OUT / 'verification.json')
    assert verification['passed'] and verification['real_head_fits'] == 11
    count = 0
    for relative, expected in verification['artifact_sha256'].items():
        p = (OUT / relative).resolve(); p.relative_to(OUT)
        assert sha(p) == expected, relative
        count += 1
    for relative, expected in read(OUT / 'bindings.json').items():
        p = (ROOT / relative).resolve(); p.relative_to(ROOT)
        assert sha(p) == expected, relative
    rows = read(ADMISSION / 'roster.json')
    source_by_case = {r['case_id']: r['source_id'] for r in rows}
    sources = sorted(set(source_by_case.values()))
    assert len(sources) == 11 and len(rows) == 66
    assert all(source_by_case[r['case_id']] != r['held_source']
               for r in read(OUT / 'fitting_access.json'))
    maximum_state_error = maximum_loss_error = 0.
    for source in sources:
        head = read(OUT / source / 'head.json')
        proof = read(OUT / source / 'fitting_verification.json')
        expected = sorted(k for k, s in source_by_case.items() if s != source)
        assert head['training_ids'] == expected and len(expected) == 60
        assert source not in head['training_sources']
        assert proof['passed'] and proof['independently_replayed_updates'] == 50
        assert len(head['explicit_pair_ids']) == 40 and head['generated_fixture'] is False
        assert proof['head_sha256'] == sha(OUT / source / 'head.json')
        maximum_state_error = max(maximum_state_error, proof['scalar_state_max_error'])
        maximum_loss_error = max(maximum_loss_error, proof['scalar_loss_max_error'])
    scores = read(OUT / 'held_scores_sealed.json')
    margins = read(OUT / 'held_margins_sealed.json')
    assert len(scores) == 66 and len(margins) == 44
    by_role = {(r['source_id'], r['role']): r for r in scores}
    assert len(by_role) == 66
    for r in scores:
        close(r['score'], r['scalar_score'])
    for r in margins:
        a = by_role[r['source_id'], r['preferred_role']]
        b = by_role[r['source_id'], r['other_role']]
        assert a['source_id'] == b['source_id']
        close(r['margin'], a['score'] - b['score'])
        scalar_margin = a['scalar_score'] - b['scalar_score']
        close(r['margin'], scalar_margin)
        assert (r['margin'] > 0) == (scalar_margin > 0)
        assert r['strict_win'] == (r['margin'] > 0)
        assert r['tie'] == (r['margin'] == 0)
        close(r['logistic_loss'], max(0., -r['margin']) + math.log1p(math.exp(-abs(r['margin']))))
    result = read(OUT / 'assessment.json')
    other_roles = ('exposure_under', 'exposure_over', 'combined_under', 'combined_over')
    comparisons = 0
    for name, selected in [('overall', margins)] + [(r, [a for a in margins if a['other_role'] == r]) for r in other_roles] + [(s, [a for a in margins if a['source_id'] == s]) for s in sources]:
        expected = stats(selected)
        actual = result['overall'] if name == 'overall' else result['families'][name] if name in other_roles else result['per_source'][name]
        for key, value in expected.items():
            close(actual[key], value); comparisons += 1
    positive = all(stats([a for a in margins if a['other_role'] == r])['strict_accuracy'] > .5 for r in other_roles)
    assert result['positive_hypothesis'] == verification['positive_hypothesis'] == positive
    assert not result['model_ready'] and not result['next_correction_experiment_selected']
    report = dict(passed=True, artifact_hashes=count, real_head_fits=11,
                  independently_replayed_Adam_updates=550, independent_summary_values=comparisons,
                  scalar_state_max_error=maximum_state_error, scalar_loss_max_error=maximum_loss_error,
                  source_exclusion=True, held_preferences=44, independent_margin_signs=True,
                  positive_hypothesis=positive, additional_fits=0, image_reads=0)
    with dest.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
