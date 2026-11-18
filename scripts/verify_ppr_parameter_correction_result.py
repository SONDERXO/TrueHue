"""Read-only independent319 artifact/feature/route/summary audit; no fits/pixels."""
from pathlib import Path
import sys, math, struct
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from wb_feature_direct_workflow import read, write, sha, SETTINGS, select
from wb_feature_direct_verify import route, verify_fit, close
from joint_cue_tree_workflow import ROLES


def main():
    out = ROOT / 'outputs/ppr_parameter_correction_prediction_v1'
    design = ROOT / 'outputs/ppr_parameter_correction_design_v1'
    destination = out / 'independent_audit.json'
    if destination.exists(): raise FileExistsError(destination)
    v = read(out / 'verification.json'); assert v['passed'] and v['real_control_fits'] == 11
    for name, expected in v['artifact_sha256'].items(): assert sha(out / name) == expected
    for name, expected in read(out / 'bindings.json').items(): assert sha(ROOT / name) == expected
    for name, expected in read(design / 'verification.json')['output_sha256'].items():
        assert sha(design / name) == expected
    wb = ROOT / 'outputs/wb_feature_direct_prediction_v1'
    parent = {r['case_id']: r for r in read(wb / 'rows.json')}
    cues = {r['case_id']: r for r in read(ROOT / 'outputs/ppr_parameter_features_v1/records.json')}
    rows = read(design / 'rows.json'); by_id = {r['case_id']: r for r in rows}
    assert len(rows) == len(by_id) == 66 and set(by_id) == set(parent) == set(cues)
    for r in rows:
        old = parent[r['case_id']]; cue = cues[r['case_id']]
        assert r['x319'][:314] == old['x314'] and r['x319'][314:] == cue['coefficients']
        assert all(struct.unpack('!f', struct.pack('!f', x))[0] == x for x in r['x319'])
        assert r['y'] == old['y'] and r['input_rgb_sha256'] == cue['input_rgb_sha256']
        assert all(r[k] == old[k] == cue[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture'])
    plan = read(out / 'plan.json'); folds = read(out / 'fold_rows.json')
    assert plan['folds'] == read(wb / 'plan.json')['folds'] and plan['settings'] == SETTINGS
    cert = read(out / 'all_fits_verified.json'); assert cert['verified_fits'] == len(cert['models']) == 11
    seal = read(out / 'prediction_seal.json'); assert seal['predictions'] == 66 and sha(out / 'held_controls_sealed.json') == seal['sha256']
    held = read(out / 'held_controls_sealed.json'); held_by = {r['case_id']: r for r in held}
    assert len(held) == len(held_by) == 66 and set(held_by) == set(by_id)
    constants = {}; models = {}; fitting_count = held_count = split_count = 0; cue_models = []
    for entry in cert['models']:
        source = entry['source']; assert sha(out / entry['path']) == entry['sha256']
        model = read(out / entry['path']); assert model['dimensions'] == 319
        fold = next(f for f in plan['folds'] if f['held_source_id'] == source)
        rr = folds[source]; assert len(rr) == 66
        for r in rr:
            assert r['x319'] == by_id[r['case_id']]['x319']
            if r['source_id'] == source: assert 'y' not in r
            else: assert r['y'] == by_id[r['case_id']]['y']
        fitting = select(rr, fold, '319'); constants[source] = verify_fit(model, fitting, fold, SETTINGS)
        fitting_count += len(fitting); models[source] = model
        cue_splits = [n for n in model['nodes'] if n['kind'] == 'split' and n['feature'] >= 314]
        split_count += len(cue_splits)
        if cue_splits: cue_models.append(source)
        assert all(0 <= n['feature'] < 319 and math.isfinite(n['threshold']) for n in model['nodes'] if n['kind'] == 'split')
        for case in fold['evaluation_cases']:
            leaf, controls = route(model, by_id[case]['x319']); p = held_by[case]
            assert leaf == p['leaf'] and controls == p['controls']
            for a, b in zip(p['constant'], constants[source]): close(a, b, 1e-12)
            held_count += 1
    assert fitting_count == 660 and held_count == 66
    records = read(out / 'records.json'); summary = read(out / 'summary.json')
    assert len(records) == 66 and {r['case_id'] for r in records} == set(by_id)
    for r in records:
        assert r['controls'] == held_by[r['case_id']]['controls'] and r['leaf'] == held_by[r['case_id']]['leaf']
        assert r['parameter_MAE'] == [abs(a-b) for a,b in zip(r['controls'], by_id[r['case_id']]['y'])]
    means = {role: {label: {metric: math.fsum(r['regions']['primary'][label][metric] for r in records if r['role'] == role)/11
              for metric in ['RGB', 'DE']} for label in ['input', 'constant', 'saved314', 'joint']} for role in ROLES}
    assert means == summary['by_role']
    gates = {role: all(means[role]['joint'][m] < means[role][base][m]-1e-10
             for m in ['RGB','DE'] for base in ['input','constant']) for role in ROLES[1:]}
    under = all(means['exposure_under']['joint'][m] < means['exposure_under']['saved314'][m]-1e-10 for m in ['RGB','DE'])
    colour = all(means['colour_only']['joint'][m] <= means['colour_only']['saved314'][m]+1e-10 for m in ['RGB','DE'])
    assert gates == summary['role_gates'] and under == summary['under_improvement'] and colour == summary['colour_nonworse']
    assert summary['numerical_eligible'] == (all(gates.values()) and under and colour)
    changed = [r['case_id'] for r in records if r['role'] == 'identity' and r['changed_pixels'] > 0]
    assert len(changed) == summary['identity_changed']
    feature_access = read(ROOT / 'outputs/ppr_parameter_features_v1/access.json')
    assert len(feature_access) == 66 and all(r['keys'] == ['input'] for r in feature_access)
    scoring_access = read(out / 'scoring_access.json')
    assert len(scoring_access) == 66 and all(r['stage'] == 'after11fitproofs_and66sealed_controls' for r in scoring_access)
    result = dict(passed=True, artifact_hashes=len(v['artifact_sha256']), source_bindings=len(read(out / 'bindings.json')),
                  prefix_values=66*314, raw_coefficients=330, fitting_routes=fitting_count, held_routes=held_count,
                  independent_mean_values=48, feature_splits=split_count, feature_using_models=cue_models,
                  identity_changed=changed, role_gates=gates, numerical_eligible=summary['numerical_eligible'],
                  new_fits=0, pixel_decodes=0, model_ready=False)
    write(destination, result); print(result)


if __name__ == '__main__': main()
