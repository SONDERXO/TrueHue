"""One fold-specific316feature comparison; unchanged heads/operator/baselines."""
from pathlib import Path
import sys, copy, math, platform, importlib.metadata
import numpy as np
from sklearn.tree import DecisionTreeRegressor
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from wb_feature_direct_workflow import SETTINGS, read, write, sha, select
from wb_feature_direct_verify import verify_fit, route, close
from joint_cue_tree_workflow import score as score_pixels, ROLES
from src.model_training.luminance_chroma_operator import parameters, render_rgb8
from src.model_training.synthetic_exposure_ranking import score as rank_score
from synthetic_exposure_ranking_checks import scalar_score

QA = ROOT / 'outputs/synthetic_probe_correction_engineering_v3'
DESIGN = ROOT / 'outputs/synthetic_probe_correction_design_v1'
OUT = ROOT / 'outputs/synthetic_probe_correction_prediction_v1'
PROBE = ROOT / 'outputs/synthetic_exposure_probe_v2'
RANK = ROOT / 'outputs/synthetic_exposure_ranking_prediction_v1'
FILES = ['scripts/synthetic_probe_correction_workflow.py', 'scripts/wb_feature_direct_workflow.py',
         'scripts/wb_feature_direct_verify.py', 'scripts/joint_cue_tree_workflow.py',
         'src/model_training/synthetic_exposure_ranking.py',
         'src/model_training/luminance_chroma_operator.py',
         'src/evaluation/luminance_chroma_scalar.py', 'src/evaluation/directional_recoverability.py',
         'src/distortion_generation/camera_inspired_halfstop.py',
         'docs/synthetic-probe-correction-protocol-2026-11-17.md']


def versions():
    return dict(Python=platform.python_version(), **{p: importlib.metadata.version(p)
                for p in ['numpy', 'scipy', 'scikit-learn', 'scikit-image']})


def validate(plan, fold_rows):
    assert len(plan['folds']) == len(fold_rows) == 11 and plan['settings'] == SETTINGS
    prepared = []
    for fold in plan['folds']:
        source = fold['held_source_id']; rows = fold_rows[source]
        if source in plan['head_training_sources'][source]:
            raise ValueError('Outer held source leaked into quality head')
        if len(rows) != 66 or len({r['case_id'] for r in rows}) != 66:
            raise ValueError('Exactly66unique fold rows required')
        for r in rows:
            if r['outer_head_source'] != source:
                raise ValueError('Every row must use THIS outer-fold head')
            x = r['x316']
            if len(x) != 316 or not np.isfinite(x).all() or np.asarray(x, np.float32).astype(float).tolist() != x:
                raise ValueError('Finite float32 width316 required')
            if r['generated_fixture'] is not plan['generated_fixture']:
                raise ValueError('Provenance mismatch')
        held = [{k: r[k] for k in ('case_id', 'source_id', 'role', 'generated_fixture', 'x316')}
                for r in rows if r['source_id'] == source]
        assert [r['case_id'] for r in held] == fold['evaluation_cases'] and len(held) == 6
        prepared.append((fold, select(rows, fold, '316'), held))
    return prepared


def fit_all(plan, fold_rows, out, factory=DecisionTreeRegressor):
    if out.exists(): raise FileExistsError(out)
    prepared = validate(plan, fold_rows)  # All folds BEFORE any model construction.
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
            exported = dict(schema='truehue_camera_control_cart_research_v1', dimensions=316,
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
            print('Synthetic316 tree verified ' + str(started) + '/11', flush=True)
        write(out / 'all_fits_verified.json', dict(verified_fits=11, fitting_routes=660, models=entries))
        for e in entries: assert sha(out / e['path']) == e['sha256']
        sealed = []
        for fold, fitting, held in prepared:
            source = fold['held_source_id']
            native_values = natives[source].predict(np.asarray([r['x316'] for r in held], np.float32)).tolist()
            for r, expected in zip(held, native_values):
                leaf, controls = route(models[source], r['x316']); parameters(controls)
                assert controls == expected
                sealed.append({k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture']} |
                              dict(controls=controls, leaf=leaf, constant=constants[source]))
        assert len(sealed) == 66
        write(out / 'held_controls_sealed.json', sealed)
        write(out / 'prediction_seal.json', dict(predictions=66, sha256=sha(out / 'held_controls_sealed.json')))
    except Exception as exc:
        write(out / 'failure.json', dict(error=repr(exc), started_fits=started)); raise


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
            x = rng.normal(0, .001, 314).astype(np.float32); x[0] = j
            rows.append(dict(case_id=case, source_id=str(s), role=role, generated_fixture=True,
                             y=list(inverse(role)), x314=x.astype(float).tolist()))
            arrays[case] = dict(input=image, reference=reference, alpha=alpha, protected=protected, saved314=image.copy())
    folds = [dict(held_source_id=str(s), fitting_cases=[r['case_id'] for r in rows if r['source_id'] != str(s)],
                  evaluation_cases=[r['case_id'] for r in rows if r['source_id'] == str(s)]) for s in range(11)]
    plan = dict(folds=folds, settings=SETTINGS, generated_fixture=True,
                head_training_sources={str(s): [str(t) for t in range(11) if t != s] for s in range(11)})
    fold_rows = {str(s): [{k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture', 'y']} |
                           dict(outer_head_source=str(s), x316=r['x314'] + [float(s), float(i)])
                           for i, r in enumerate(rows)] for s in range(11)}
    class Poison(dict):
        def __getitem__(self, key):
            if key in ('x316', 'y'): raise AssertionError('Held fitting payload read')
            return super().__getitem__(key)
    assert len(select([Poison(r) if r['source_id'] == '0' else r for r in fold_rows['0']], folds[0], '316')) == 60
    # Global validation may check all input vectors, but never held targets.
    class TargetPoison(dict):
        def __getitem__(self, key):
            if key == 'y': raise AssertionError('Held target accessed during validation')
            return super().__getitem__(key)
    poisoned = {s: [TargetPoison(r) if r['source_id'] == s else r for r in rr]
                for s, rr in fold_rows.items()}
    assert len(validate(plan, poisoned)) == 11
    QA.mkdir(); calls = []
    def forbidden(**_): calls.append(True); raise AssertionError('Unexpected model construction')
    invalid = []
    for kind in ('width', 'finite', 'wrong_head', 'head_training_leak'):
        bad = copy.deepcopy(fold_rows); bad_plan = copy.deepcopy(plan)
        if kind == 'width': bad['0'][0]['x316'].pop()
        elif kind == 'finite': bad['0'][0]['x316'][0] = float('nan')
        elif kind == 'wrong_head': bad['0'][0]['outer_head_source'] = '1'
        else: bad_plan['head_training_sources']['0'].append('0')
        try: fit_all(bad_plan, bad, QA / ('invalid_' + kind), forbidden)
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
          fit_payload_poison=True, all_fits_before_held=True, missing_seal_guard=True,
          no_overwrite=True, failure_preserved=True, inputs_immutable=True,
          generated_numeric_eligible=result['numerical_eligible'], versions=versions(),
          code_sha256={p: sha(ROOT / p) for p in FILES}))
    print('PASS full316/fold-head exclusion/generated11trees/66scalarpixels; zero real correction fits.', flush=True)


def prepare():
    if DESIGN.exists(): raise FileExistsError(DESIGN)
    qa = read(QA / 'verification.json'); assert qa['passed'] and qa['versions'] == versions()
    for p, h in qa['code_sha256'].items(): assert sha(ROOT / p) == h
    pv = read(PROBE / 'verification.json'); assert pv['passed'] and pv['new_probe_vectors'] == 132
    assert sha(PROBE / 'features.npz') == pv['features_sha256']
    wb = ROOT / 'outputs/wb_feature_direct_prediction_v1'
    receipt = read(wb / 'verification.json'); assert receipt['passed']
    known = {p.replace('\\', '/'): h for p, h in receipt['artifacts'].items()}
    bound = dict(qa['code_sha256'])
    for name in ['rows.json', 'plan.json', 'records.json', 'summary.json', 'held_controls_sealed.json']:
        assert sha(wb / name) == known[name]; bound[(wb / name).relative_to(ROOT).as_posix()] = known[name]
    rows = read(wb / 'rows.json'); original_plan = read(wb / 'plan.json')
    plan = dict(folds=original_plan['folds'], settings=SETTINGS, generated_fixture=False,
                head_training_sources={}, model_ready=False)
    fold_rows = {}; checks = 0
    with np.load(ROOT / 'outputs/camera_halfstop_neural_v1/features.npz', allow_pickle=False) as base, np.load(PROBE / 'features.npz', allow_pickle=False) as probes:
        assert set(base.files) == {r['case_id'] for r in rows}
        for fold in plan['folds']:
            source = fold['held_source_id']; head_path = RANK / source / 'head.json'; head = read(head_path)
            assert head['generated_fixture'] is False and source not in head['training_sources']
            assert sorted(head['training_ids']) == sorted(fold['fitting_cases'])
            plan['head_training_sources'][source] = head['training_sources']
            bound[head_path.relative_to(ROOT).as_posix()] = sha(head_path)
            fold_rows[source] = []
            for r in rows:
                case = r['case_id']; vectors = [base[case], probes[case + '__minus'], probes[case + '__plus']]
                native = [rank_score(head, v) for v in vectors]; independent = [scalar_score(head, v) for v in vectors]
                for a, b in zip(native, independent): close(a, b, 1e-10); checks += 1
                cue = np.asarray([native[1] - native[0], native[2] - native[0]], np.float32).astype(float).tolist()
                x = r['x314'] + cue
                assert x[:314] == r['x314'] and len(x) == 316
                projected = {k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture']}
                if r['source_id'] != source:
                    projected['y'] = r['y']
                fold_rows[source].append(projected | dict(outer_head_source=source, x316=x))
    validate(plan, fold_rows)
    for r in rows:
        path = wb / 'evaluation' / (r['case_id'] + '.npz')
        assert sha(path) == known['evaluation/' + r['case_id'] + '.npz']
        bound[path.relative_to(ROOT).as_posix()] = sha(path)
    for p in [QA / 'verification.json', PROBE / 'verification.json', PROBE / 'features.npz',
              PROBE / 'execution_bindings.json', RANK / 'verification.json',
              ROOT / 'outputs/camera_halfstop_neural_v1/features.npz']:
        bound[p.relative_to(ROOT).as_posix()] = sha(p)
    for p, h in bound.items(): assert sha(ROOT / p) == h
    DESIGN.mkdir(); write(DESIGN / 'plan.json', plan); write(DESIGN / 'fold_rows.json', fold_rows)
    write(DESIGN / 'rows.json', [{k: r[k] for k in ['case_id', 'source_id', 'role', 'generated_fixture', 'y']} for r in rows])
    write(DESIGN / 'bindings.json', bound)
    write(DESIGN / 'verification.json', dict(passed=True, folds=11, rows_per_fold=66, dimensions=316,
          independent_scores=checks, prefix_values_verified=11 * 66 * 314, real_fits=0,
          outer_head_excludes_outer_held=True, training_rows_use_outer_head=True,
          head_refits=0, pixel_decodes=0, versions=versions(),
          output_sha256={name: sha(DESIGN / name) for name in ['plan.json', 'fold_rows.json', 'rows.json']}))
    print('PASS all11fold-specific316 matrices and outer-head exclusions; 2178scalar scores; zero fits/pixels.', flush=True)


def run():
    if OUT.exists(): raise FileExistsError('Real correction attempt already exists')
    qa = read(DESIGN / 'verification.json'); assert qa['passed'] and qa['versions'] == versions()
    for p, h in read(DESIGN / 'bindings.json').items(): assert sha(ROOT / p) == h
    for p, h in qa['output_sha256'].items(): assert sha(DESIGN / p) == h
    plan = read(DESIGN / 'plan.json'); fold_rows = read(DESIGN / 'fold_rows.json'); rows = read(DESIGN / 'rows.json')
    fit_all(plan, fold_rows, OUT)
    bound = read(DESIGN / 'bindings.json'); write(OUT / 'bindings.json', bound)
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
            access.append(dict(case_id=row['case_id'], keys=list(arrays), stage='after11fitproofs_and66sealed_controls'))
            arrays['saved314'] = arrays.pop('314'); arrays['parent_scores'] = previous[row['case_id']]['regions']
            return arrays
        result = score_pixels(rows, OUT, loader)
        for p, h in bound.items(): assert sha(ROOT / p) == h
        write(OUT / 'scoring_access.json', access)
        # Separate scalar summary/gate recount from saved case records.
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
        write(OUT / 'verification.json', dict(passed=True, real_control_fits=11, head_refits=0,
              fitting_routes=660, held_controls=66, scalar_render_metric_checks=66,
              independent_summary_values=count, outer_head_exclusion=True, all_fits_before_held=True,
              controls_sealed_before_reference_pixels=True, numerical_eligible=result['numerical_eligible'],
              model_ready=False, versions=versions(), candidate_alias_in_reused_scorer='joint_means_synthetic316_here',
              artifact_sha256={p.relative_to(OUT).as_posix(): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}))
        print(result, flush=True)
    except Exception as exc:
        write(OUT / 'scoring_failure.json', dict(error=repr(exc), completed_case_access=len(access))); raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('stage', choices=['generated', 'prepare', 'run'])
    {'generated': generated, 'prepare': prepare, 'run': run}[parser.parse_args().stage]()
