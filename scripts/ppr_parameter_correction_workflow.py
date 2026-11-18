"""One fixed319feature study; frozen portrait parameters are features only."""
from pathlib import Path
import sys, copy, math, hashlib, platform, importlib.metadata
import numpy as np
from sklearn.tree import DecisionTreeRegressor
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from wb_feature_direct_workflow import SETTINGS, read, write, sha, select
from wb_feature_direct_verify import verify_fit, route, close
from joint_cue_tree_workflow import score as score_pixels, ROLES
from src.model_training.luminance_chroma_operator import parameters, render_rgb8

QA = ROOT / 'outputs/ppr_parameter_correction_engineering_v1'
DESIGN = ROOT / 'outputs/ppr_parameter_correction_design_v1'
OUT = ROOT / 'outputs/ppr_parameter_correction_prediction_v1'
FEATURES = ROOT / 'outputs/ppr_parameter_features_v1'
FILES = ['scripts/ppr_parameter_correction_workflow.py', 'scripts/wb_feature_direct_workflow.py',
         'scripts/wb_feature_direct_verify.py', 'scripts/joint_cue_tree_workflow.py',
         'src/model_training/luminance_chroma_operator.py',
         'src/evaluation/luminance_chroma_scalar.py', 'src/evaluation/directional_recoverability.py',
         'src/distortion_generation/camera_inspired_halfstop.py',
         'docs/ppr-parameter-correction-protocol-2026-11-17.md']


def versions():
    return dict(Python=platform.python_version(), **{p: importlib.metadata.version(p)
                for p in ['numpy', 'scipy', 'scikit-learn', 'scikit-image']})


def validate(plan, fold_rows):
    assert len(plan['folds']) == len(fold_rows) == 11 and plan['settings'] == SETTINGS
    prepared = []
    for fold in plan['folds']:
        source = fold['held_source_id']; rows = fold_rows[source]
        if len(rows) != 66 or len({r['case_id'] for r in rows}) != 66:
            raise ValueError('Exactly66unique fold rows required')
        for r in rows:
            x = r['x319']
            if len(x) != 319 or not np.isfinite(x).all() or np.asarray(x, np.float32).astype(float).tolist() != x:
                raise ValueError('Finite float32 width319 required')
            if r['generated_fixture'] is not plan['generated_fixture']:
                raise ValueError('Provenance mismatch')
        held = [{k: r[k] for k in ('case_id', 'source_id', 'role', 'generated_fixture', 'x319')}
                for r in rows if r['source_id'] == source]
        assert [r['case_id'] for r in held] == fold['evaluation_cases'] and len(held) == 6
        prepared.append((fold, select(rows, fold, '319'), held))
    return prepared


def fit_all(plan, fold_rows, out, factory=DecisionTreeRegressor):
    if out.exists(): raise FileExistsError(out)
    prepared = validate(plan, fold_rows)
    out.mkdir(); (out / 'models').mkdir()
    write(out / 'plan.json', plan); write(out / 'fold_rows.json', fold_rows)
    entries = []; models = {}; constants = {}; natives = {}; started = 0
    try:
        for fold, fitting, held in prepared:
            source = fold['held_source_id']; started += 1
            assert started <= 11
            write(out / 'fit_accounting.json', dict(started=started, maximum=11))
            x = np.asarray([r['x'] for r in fitting], np.float32)
            y = np.asarray([r['y'] for r in fitting], np.float64)
            native = factory(**SETTINGS); native.fit(x, y); tree = native.tree_
            nodes = []
            for i in range(tree.node_count):
                if tree.children_left[i] == -1:
                    nodes.append(dict(kind='leaf', values=tree.value[i, :, 0].tolist()))
                else:
                    nodes.append(dict(kind='split', feature=int(tree.feature[i]), threshold=float(tree.threshold[i]),
                                      left=int(tree.children_left[i]), right=int(tree.children_right[i])))
            exported = dict(schema='truehue_camera_control_cart_research_v1', dimensions=319,
                            target_names=['gamma', 'exposure_gain', 'red_balance', 'blue_balance', 'chroma_scale'],
                            settings=native.get_params(deep=False), comparison='<=', nodes=nodes)
            assert exported['settings'] == SETTINGS
            checked = [route(exported, r['x']) for r in fitting]
            assert [p for _, p in checked] == native.predict(x).tolist()
            assert [leaf for leaf, _ in checked] == native.apply(x).tolist()
            constants[source] = verify_fit(exported, fitting, fold, SETTINGS)
            path = 'models/' + source + '.json'; write(out / path, exported)
            entries.append(dict(source=source, path=path, sha256=sha(out / path)))
            models[source] = exported; natives[source] = native
            print('PPR319 tree verified ' + str(started) + '/11', flush=True)
        write(out / 'all_fits_verified.json', dict(verified_fits=11, fitting_routes=660, models=entries))
        for e in entries: assert sha(out / e['path']) == e['sha256']
        sealed = []
        for fold, fitting, held in prepared:
            source = fold['held_source_id']
            native_values = natives[source].predict(np.asarray([r['x319'] for r in held], np.float32)).tolist()
            native_leaves = natives[source].apply(np.asarray([r['x319'] for r in held], np.float32)).tolist()
            for r, expected, expected_leaf in zip(held, native_values, native_leaves):
                leaf, controls = route(models[source], r['x319']); parameters(controls)
                assert controls == expected and leaf == expected_leaf
                sealed.append({k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture']} |
                              dict(controls=controls, leaf=leaf, constant=constants[source]))
        assert len(sealed) == 66
        write(out / 'held_controls_sealed.json', sealed)
        write(out / 'prediction_seal.json', dict(predictions=66, sha256=sha(out / 'held_controls_sealed.json')))
    except Exception as exc:
        write(out / 'failure.json', dict(error=repr(exc), started_fits=started)); raise


def matrices(plan, rows):
    # Omit held targets entirely from each fold's stored inference payload.
    return {f['held_source_id']: [{k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture', 'x319']}
              | (dict(y=r['y']) if r['source_id'] != f['held_source_id'] else {}) for r in rows]
            for f in plan['folds']}


def generated():
    if QA.exists(): raise FileExistsError(QA)
    from src.distortion_generation.camera_inspired_halfstop import generate, inverse
    rng = np.random.default_rng(42); rows = []; arrays = {}
    for s in range(11):
        reference = rng.integers(20, 210, (12, 13, 3), dtype=np.uint8)
        alpha = np.ones((12, 13)); alpha[0] = 0; alpha[-1] = .5
        protected = np.zeros(alpha.shape, bool); protected[0] = True
        for j, role in enumerate(ROLES):
            image, _ = generate(reference, role); case = str(s) + '_' + role
            x = rng.normal(0, .001, 319).astype(np.float32); x[314] = j
            rows.append(dict(case_id=case, source_id=str(s), role=role, generated_fixture=True,
                             y=list(inverse(role)), x319=x.astype(float).tolist()))
            arrays[case] = dict(input=image, reference=reference, alpha=alpha, protected=protected, saved314=image.copy())
    folds = [dict(held_source_id=str(s), fitting_cases=[r['case_id'] for r in rows if r['source_id'] != str(s)],
                  evaluation_cases=[r['case_id'] for r in rows if r['source_id'] == str(s)]) for s in range(11)]
    plan = dict(folds=folds, settings=SETTINGS, generated_fixture=True)
    fold_rows = matrices(plan, rows)
    class Poison(dict):
        def __getitem__(self, key):
            if key in ('x319', 'y'): raise AssertionError('Held fitting payload read')
            return super().__getitem__(key)
    assert len(select([Poison(r) if r['source_id'] == '0' else r for r in fold_rows['0']], folds[0], '319')) == 60
    class TargetPoison(dict):
        def __getitem__(self, key):
            if key == 'y': raise AssertionError('Held target read')
            return super().__getitem__(key)
    poisoned = {s: [TargetPoison(r) if r['source_id'] == s else r for r in rr] for s, rr in fold_rows.items()}
    assert len(validate(plan, poisoned)) == 11
    QA.mkdir(); calls = []
    def forbidden(**_): calls.append(True); raise AssertionError('Unexpected model construction')
    invalid = []
    for kind in ('width', 'finite', 'provenance'):
        bad = copy.deepcopy(fold_rows)
        if kind == 'width': bad['0'][0]['x319'].pop()
        elif kind == 'finite': bad['0'][0]['x319'][0] = float('nan')
        else: bad['0'][0]['generated_fixture'] = False
        try: fit_all(plan, bad, QA / ('invalid_' + kind), forbidden)
        except ValueError: invalid.append(kind)
        else: raise AssertionError('Invalid accepted: ' + kind)
    assert not calls
    def failed(**_): raise RuntimeError('intentional generated construction failure')
    try: fit_all(plan, fold_rows, QA / 'preserved_failure', failed)
    except RuntimeError: pass
    else: raise AssertionError('Failure swallowed')
    assert (QA / 'preserved_failure/failure.json').exists()
    run = QA / 'run'; before = copy.deepcopy(fold_rows); fit_all(plan, fold_rows, run)
    assert fold_rows == before
    def loader(row, p):
        assert (run / 'all_fits_verified.json').exists() and (run / 'prediction_seal.json').exists()
        a = dict(arrays[row['case_id']]); a['constant'] = render_rgb8(a['input'], a['alpha'], a['protected'], p['constant'])
        return a
    result = score_pixels(rows, run, loader)
    try: fit_all(plan, fold_rows, run, forbidden)
    except FileExistsError: pass
    else: raise AssertionError('Overwrite accepted')
    assert not calls
    empty = QA / 'missing_seal'; empty.mkdir(); write(empty / 'prediction_seal.json', dict(predictions=0))
    try: score_pixels(rows, empty, lambda *_: (_ for _ in ()).throw(AssertionError('Early pixels')))
    except AssertionError: pass
    else: raise AssertionError('Missing seal accepted')
    write(QA / 'verification.json', dict(passed=True, generated_fits=11, real_fits=0,
          fitting_routes=660, held_controls=66, scalar_render_checks=66, invalid=invalid,
          fit_payload_poison=True, held_target_absent=True, all_fits_before_held=True, missing_seal_guard=True,
          no_overwrite=True, failure_preserved=True, inputs_immutable=True,
          generated_numeric_eligible=result['numerical_eligible'], versions=versions(),
          code_sha256={p: sha(ROOT / p) for p in FILES}))
    print('PASS generated319/11trees/66scalarpixels; zero real correction fits.', flush=True)


def prepare():
    if DESIGN.exists(): raise FileExistsError(DESIGN)
    qa = read(QA / 'verification.json'); assert qa['passed'] and qa['versions'] == versions()
    for p, h in qa['code_sha256'].items(): assert sha(ROOT / p) == h
    fv = read(FEATURES / 'verification.json'); assert fv['passed'] and fv['cases'] == 66 and fv['coefficients'] == 330
    assert sha(FEATURES / 'records.json') == fv['records_sha256']
    bound = dict(qa['code_sha256']) | read(FEATURES / 'bindings.json')
    wb = ROOT / 'outputs/wb_feature_direct_prediction_v1'
    receipt = read(wb / 'verification.json'); assert receipt['passed']
    known = {p.replace('\\', '/'): h for p, h in receipt['artifacts'].items()}
    for name in ['rows.json', 'plan.json', 'records.json', 'summary.json', 'held_controls_sealed.json']:
        assert sha(wb / name) == known[name]; bound[(wb / name).relative_to(ROOT).as_posix()] = known[name]
    original = read(wb / 'rows.json'); original_plan = read(wb / 'plan.json')
    assert original_plan['settings'] == SETTINGS
    cues = read(FEATURES / 'records.json'); by_id = {r['case_id']: r for r in cues}
    assert len(cues) == len(by_id) == 66 and set(by_id) == {r['case_id'] for r in original}
    rows = []
    for r in original:
        q = by_id[r['case_id']]
        assert all(r[k] == q[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture'])
        assert r['generated_fixture'] is False
        c = q['coefficients']; assert len(c) == 5 and np.isfinite(c).all() and np.asarray(c, np.float32).astype(float).tolist() == c
        assert len(r['x314']) == 314
        rows.append({k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture', 'y']} |
                    dict(x319=r['x314'] + c, input_rgb_sha256=q['input_rgb_sha256']))
        path = wb / 'evaluation' / (r['case_id'] + '.npz')
        assert sha(path) == known['evaluation/' + r['case_id'] + '.npz']
        bound[path.relative_to(ROOT).as_posix()] = known['evaluation/' + r['case_id'] + '.npz']
    plan = dict(folds=original_plan['folds'], settings=SETTINGS, generated_fixture=False, model_ready=False)
    fold_rows = matrices(plan, rows); validate(plan, fold_rows)
    for p in [QA / 'verification.json', FEATURES / 'verification.json', FEATURES / 'records.json', FEATURES / 'bindings.json']:
        bound[p.relative_to(ROOT).as_posix()] = sha(p)
    for p, h in bound.items(): assert sha(ROOT / p) == h
    DESIGN.mkdir(); write(DESIGN / 'plan.json', plan); write(DESIGN / 'fold_rows.json', fold_rows)
    write(DESIGN / 'rows.json', rows); write(DESIGN / 'bindings.json', bound)
    write(DESIGN / 'verification.json', dict(passed=True, folds=11, rows_per_fold=66, dimensions=319,
          raw_coefficient_values=330, prefix_values_verified=66 * 314, real_fits=0,
          held_targets_absent=True, parameter_model_refits=0, pixel_decodes=0, versions=versions(),
          output_sha256={name: sha(DESIGN / name) for name in ['plan.json', 'fold_rows.json', 'rows.json']}))
    print('PASS bound319features/330rawcoefficients/unchanged314prefix/heldtargetsabsent; zero fits/pixels.', flush=True)


def run():
    if OUT.exists(): raise FileExistsError('Real correction attempt already exists')
    qa = read(DESIGN / 'verification.json'); assert qa['passed'] and qa['versions'] == versions()
    bound = read(DESIGN / 'bindings.json')
    for p, h in bound.items(): assert sha(ROOT / p) == h
    for p, h in qa['output_sha256'].items(): assert sha(DESIGN / p) == h
    plan = read(DESIGN / 'plan.json'); fold_rows = read(DESIGN / 'fold_rows.json'); rows = read(DESIGN / 'rows.json')
    fit_all(plan, fold_rows, OUT); write(OUT / 'bindings.json', bound)
    wb = ROOT / 'outputs/wb_feature_direct_prediction_v1'
    previous = {r['case_id']: r for r in read(wb / 'records.json')}
    old_controls = {r['case_id']: r for r in read(wb / 'held_controls_sealed.json')}
    access = []
    try:
        def loader(row, p):
            assert (OUT / 'prediction_seal.json').exists()
            for a, b in zip(p['constant'], old_controls[row['case_id']]['constant']): close(a, b, 1e-12)
            with np.load(wb / 'evaluation' / (row['case_id'] + '.npz'), allow_pickle=False) as pack:
                arrays = {k: pack[k].copy() for k in ['input', 'reference', 'alpha', 'protected', '314', 'constant']}
            assert hashlib.sha256(arrays['input'].tobytes()).hexdigest() == row['input_rgb_sha256']
            access.append(dict(case_id=row['case_id'], keys=list(arrays), stage='after11fitproofs_and66sealed_controls'))
            arrays['saved314'] = arrays.pop('314'); arrays['parent_scores'] = previous[row['case_id']]['regions']
            return arrays
        result = score_pixels(rows, OUT, loader)
        for p, h in bound.items(): assert sha(ROOT / p) == h
        write(OUT / 'scoring_access.json', access)
        records = read(OUT / 'records.json'); count = 0
        for role in ROLES:
            for label in ['input', 'constant', 'saved314', 'joint']:
                for metric in ['RGB', 'DE']:
                    mean = math.fsum(r['regions']['primary'][label][metric] for r in records if r['role'] == role) / 11
                    close(result['by_role'][role][label][metric], mean); count += 1
        gate = all(result['by_role'][r]['joint'][m] < result['by_role'][r][b][m] - 1e-10
                   for r in ROLES[1:] for m in ['RGB', 'DE'] for b in ['input', 'constant'])
        under = all(result['by_role']['exposure_under']['joint'][m] < result['by_role']['exposure_under']['saved314'][m] - 1e-10 for m in ['RGB', 'DE'])
        colour = all(result['by_role']['colour_only']['joint'][m] <= result['by_role']['colour_only']['saved314'][m] + 1e-10 for m in ['RGB', 'DE'])
        assert result['numerical_eligible'] == (gate and under and colour)
        write(OUT / 'verification.json', dict(passed=True, real_control_fits=11, parameter_model_refits=0,
              fitting_routes=660, held_controls=66, scalar_render_metric_checks=66,
              independent_summary_values=count, held_targets_absent=True, all_fits_before_held=True,
              controls_sealed_before_reference_pixels=True, numerical_eligible=result['numerical_eligible'],
              model_ready=False, versions=versions(), candidate_alias_in_reused_scorer='joint_means_PPR319_here',
              artifact_sha256={p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
        print('PPR319 numerical_eligible=' + str(result['numerical_eligible']) + '; identity_changed=' + str(result['identity_changed']), flush=True)
    except Exception as exc:
        write(OUT / 'scoring_failure.json', dict(error=repr(exc), completed_case_access=len(access))); raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=['generated', 'prepare', 'run'])
    {'generated': generated, 'prepare': prepare, 'run': run}[parser.parse_args().stage]()
