"""Independent saved316fold/model/margin/gate binding audit; zero fits/pixels."""
from pathlib import Path
import sys, json, math, hashlib
import numpy as np
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from wb_feature_direct_verify import verify_fit, route
from wb_feature_direct_workflow import SETTINGS
from synthetic_exposure_ranking_checks import scalar_score
OUT = ROOT / 'outputs/synthetic_probe_correction_prediction_v1'
DESIGN = ROOT / 'outputs/synthetic_probe_correction_design_v1'
RANK = ROOT / 'outputs/synthetic_exposure_ranking_prediction_v1'
PROBE = ROOT / 'outputs/synthetic_exposure_probe_v2'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def close(a, b): assert math.isclose(a, b, abs_tol=1e-10, rel_tol=1e-10), (a, b)


def main():
    dest = OUT / 'independent_verification.json'
    if dest.exists(): raise FileExistsError(dest)
    verification = read(OUT / 'verification.json'); assert verification['passed']
    hashes = 0
    for p, h in verification['artifact_sha256'].items():
        target = (OUT / p).resolve(); target.relative_to(OUT)
        assert sha(target) == h; hashes += 1
    for p, h in read(OUT / 'bindings.json').items(): assert sha(ROOT / p) == h
    for p, h in read(PROBE / 'execution_bindings.json')['sha256'].items(): assert sha(ROOT / p) == h
    plan = read(OUT / 'plan.json'); fold_rows = read(OUT / 'fold_rows.json')
    old = {r['case_id']: r for r in read(ROOT / 'outputs/wb_feature_direct_prediction_v1/rows.json')}
    controls = {r['case_id']: r for r in read(OUT / 'held_controls_sealed.json')}
    assert len(controls) == 66
    fit_routes = held_routes = prefix_checks = cue_checks = cue_splits = 0
    models_with_cue = []
    with np.load(ROOT / 'outputs/camera_halfstop_neural_v1/features.npz', allow_pickle=False) as base, np.load(PROBE / 'features.npz', allow_pickle=False) as probes:
        for fold in plan['folds']:
            source = fold['held_source_id']; model = read(OUT / 'models' / (source + '.json'))
            head = read(RANK / source / 'head.json')
            assert sorted(head['training_ids']) == sorted(fold['fitting_cases'])
            assert source not in head['training_sources']
            rows = fold_rows[source]; fitting = []
            for row in rows:
                case = row['case_id']; assert row['outer_head_source'] == source
                assert row['x316'][:314] == old[case]['x314']; prefix_checks += 314
                values = [scalar_score(head, base[case]), scalar_score(head, probes[case + '__minus']), scalar_score(head, probes[case + '__plus'])]
                expected_cues = np.asarray([values[1] - values[0], values[2] - values[0]], np.float32).astype(float).tolist()
                # One cast to float32; scalar-reduction differences checked at1e-10.
                for actual, expected in zip(row['x316'][314:], expected_cues): close(actual, expected); cue_checks += 1
                if case in fold['fitting_cases']:
                    fitting.append({k: row[k] for k in ('case_id', 'source_id', 'role', 'generated_fixture', 'y')} | dict(x=row['x316']))
                else:
                    assert 'y' not in row
                    assert row['source_id'] == source
                    leaf, p = route(model, row['x316'])
                    assert leaf == controls[case]['leaf'] and p == controls[case]['controls']; held_routes += 1
            ordered = {r['case_id']: r for r in fitting}
            fitting = [ordered[k] for k in fold['fitting_cases']]
            verify_fit(model, fitting, fold, SETTINGS); fit_routes += 60
            used = sum(node['kind'] == 'split' and node['feature'] >= 314 for node in model['nodes'])
            cue_splits += used
            if used: models_with_cue.append(source)
    result = read(OUT / 'summary.json'); records = read(OUT / 'records.json')
    means = {}; count = 0
    for role in ['identity', 'colour_only', 'exposure_under', 'exposure_over', 'combined_under', 'combined_over']:
        means[role] = {}
        for label in ['input', 'constant', 'saved314', 'joint']:
            means[role][label] = {}
            for metric in ['RGB', 'DE']:
                value = math.fsum(r['regions']['primary'][label][metric] for r in records if r['role'] == role) / 11
                means[role][label][metric] = value
                close(value, result['by_role'][role][label][metric]); count += 1
    gates = {r: all(means[r]['joint'][m] < means[r][b][m] - 1e-10 for m in ['RGB', 'DE'] for b in ['input', 'constant']) for r in means if r != 'identity'}
    under = all(means['exposure_under']['joint'][m] < means['exposure_under']['saved314'][m] - 1e-10 for m in ['RGB', 'DE'])
    colour = all(means['colour_only']['joint'][m] <= means['colour_only']['saved314'][m] + 1e-10 for m in ['RGB', 'DE'])
    assert result['role_gates'] == gates and result['under_improvement'] == under and result['colour_nonworse'] == colour
    assert result['numerical_eligible'] == verification['numerical_eligible'] == (all(gates.values()) and under and colour)
    assert fit_routes == 660 and held_routes == 66 and cue_checks == 1452
    report = dict(passed=True, artifacts_hashed=hashes, additional_fits=0, image_reads=0,
                  independent_fit_routes=fit_routes, independent_held_routes=held_routes,
                  scalar_prefix_values=prefix_checks, scalar_cue_values=cue_checks,
                  independent_means=count, cue_splits=cue_splits, models_using_cues=models_with_cue,
                  outer_head_source_exclusion=True, held_targets_absent=True,
                  numerical_eligible=result['numerical_eligible'], model_ready=False)
    with dest.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
