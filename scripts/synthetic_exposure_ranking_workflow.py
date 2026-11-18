"""Bounded approved ranking study: generated QA, metadata binding, eleven fits."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
from pathlib import Path
import sys
import argparse
import copy
import hashlib
import json
import math
import platform
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training import synthetic_exposure_ranking as model
from src.model_training.exposure_quality_training import batch_objective
from synthetic_exposure_ranking_checks import verify_model, scalar_score, close

SOURCES = ('16061', '29617', '32685', '39568', '46795', '48879',
           '49131', '52445', '53146', '54632', '59807')
BASE = ROOT / 'outputs/synthetic_exposure_ranking_design_v1'
QA = ROOT / 'outputs/synthetic_exposure_ranking_engineering_v2'
DESIGN = ROOT / 'outputs/synthetic_exposure_ranking_admission_v1'
REAL = ROOT / 'outputs/synthetic_exposure_ranking_prediction_v1'
FILES = ['src/model_training/synthetic_exposure_ranking.py',
         'src/model_training/exposure_quality_training.py',
         'src/model_training/portrait_exposure_quality.py',
         'scripts/synthetic_exposure_ranking_checks.py',
         'scripts/synthetic_exposure_ranking_workflow.py',
         'docs/synthetic-exposure-ranking-proposal-2026-11-17.md',
         'docs/synthetic-exposure-ranking-execution-protocol-2026-11-17.md']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def versions():
    return dict(Python=platform.python_version(), NumPy=np.__version__, blas_threads=2)


def code_bindings():
    return {p: sha(ROOT / p) for p in FILES}


def check_bindings(bindings):
    for relative, digest in bindings.items():
        path = (ROOT / relative).resolve()
        path.relative_to(ROOT)
        if sha(path) != digest:
            raise ValueError('Binding changed: ' + relative)


def fitting(out, rows, provider, generated):
    out.mkdir(exist_ok=False)
    heads = {}; proofs = {}; access = []
    started = completed = updates = 0
    try:
        for held in SOURCES:
            records = model.fitting_records(rows, held, generated)
            allowed = {r['case_id'] for r in records}
            assert len(records) == 60 and held not in {r['source_id'] for r in records}
            def fitting_provider(key):
                if key not in allowed:
                    raise ValueError('Fitting provider cannot read held source')
                access.append(dict(held_source=held, case_id=key, stage='fit_or_independent_fit_replay'))
                return provider(key)
            folder = out / held
            folder.mkdir()
            # Complete validation before counting a model construction.
            model.prepare(records, fitting_provider, held, generated)
            started += 1
            head, trace, states = model.fit(records, fitting_provider, held, generated)
            updates += len(trace)
            completed += 1
            write(folder / 'head.json', head)
            write(folder / 'trace.json', trace)
            np.savez_compressed(folder / 'optimizer_states.npz', **states)
            # Independent verification reads the saved head and saved states.
            with np.load(folder / 'optimizer_states.npz', allow_pickle=False) as pack:
                proof = verify_model(read(folder / 'head.json'), read(folder / 'trace.json'),
                                     {k: pack[k] for k in pack.files}, records,
                                     fitting_provider, held)
            proof['head_sha256'] = sha(folder / 'head.json')
            proof['states_sha256'] = sha(folder / 'optimizer_states.npz')
            write(folder / 'fitting_verification.json', proof)
            heads[held] = head; proofs[held] = proof
            print('Verified fitting head ' + held + ': 50 independent scalar Adam updates.', flush=True)
        assert started == completed == 11 and updates == 550
        write(out / 'all_models_verified.json', dict(passed=True, models=11, updates=550,
              head_sha256={s: proofs[s]['head_sha256'] for s in SOURCES},
              held_scoring_started=False, generated_fixture=generated))
        write(out / 'fitting_access.json', access)
        return heads, proofs
    except Exception as exc:
        write(out / 'execution_failure.json', dict(error=repr(exc), models_started=started,
              models_completed=completed, optimizer_updates_completed=updates,
              held_scoring_started=False, generated_fixture=generated))
        raise


def seal(out, rows, provider, heads, proofs):
    if set(heads) != set(SOURCES) or set(proofs) != set(SOURCES):
        raise ValueError('All eleven fitting proofs required BEFORE held scoring')
    certificate = read(out / 'all_models_verified.json')
    if not certificate['passed'] or certificate['models'] != 11:
        raise ValueError('Missing all-model certificate')
    for source in SOURCES:
        assert proofs[source]['passed']
        assert sha(out / source / 'head.json') == certificate['head_sha256'][source]
    scores = []; margins = []; max_score_error = 0.
    for source in SOURCES:
        head = heads[source]
        assert source not in head['training_sources']
        held = sorted((r for r in rows if r['source_id'] == source), key=lambda r: r['case_id'])
        assert len(held) == 6
        by_role = {}
        for row in held:
            vector = provider(row['case_id'])
            q = model.score(head, vector); independent = scalar_score(head, vector)
            close(q, independent)
            max_score_error = max(max_score_error, abs(q - independent))
            scores.append(dict(case_id=row['case_id'], source_id=source, role=row['role'],
                               score=q, scalar_score=independent))
            by_role[row['role']] = q
        for preferred, other in model.PREFERENCES:
            margin = by_role[preferred] - by_role[other]
            margins.append(dict(source_id=source, preferred_role=preferred, other_role=other,
                                margin=margin, strict_win=margin > 0, tie=margin == 0,
                                logistic_loss=max(0., -margin) + math.log1p(math.exp(-abs(margin)))))
    assert len(scores) == 66 and len(margins) == 44
    write(out / 'held_scores_sealed.json', scores)
    write(out / 'held_margins_sealed.json', margins)
    write(out / 'held_seal_verification.json', dict(passed=True, all_models_verified_first=True,
          scores=66, preferences=44, scalar_score_max_error=max_score_error,
          scores_sha256=sha(out / 'held_scores_sealed.json'),
          margins_sha256=sha(out / 'held_margins_sealed.json')))
    return margins


def summary(items):
    return dict(comparisons=len(items), wins=sum(r['strict_win'] for r in items),
                ties=sum(r['tie'] for r in items),
                losses=sum(not r['strict_win'] and not r['tie'] for r in items),
                strict_accuracy=sum(r['strict_win'] for r in items) / len(items),
                half_credit_accuracy=sum(r['strict_win'] + .5 * r['tie'] for r in items) / len(items),
                logistic_loss=math.fsum(r['logistic_loss'] for r in items) / len(items),
                mean_margin=math.fsum(r['margin'] for r in items) / len(items),
                min_margin=min(r['margin'] for r in items), max_margin=max(r['margin'] for r in items))


def assess(out, margins, heads, provider, rows):
    # Called only after all held quantities have been frozen.
    frozen = read(out / 'held_margins_sealed.json')
    assert frozen == margins
    families = {other: summary([r for r in frozen if r['other_role'] == other])
                for _, other in model.PREFERENCES}
    per_source = {s: summary([r for r in frozen if r['source_id'] == s]) for s in SOURCES}
    fitting_summaries = {}
    for held, head in heads.items():
        vals = []
        for preferred, other in head['explicit_pair_ids']:
            margin = model.score(head, provider(preferred)) - model.score(head, provider(other))
            vals.append(dict(margin=margin, strict_win=margin > 0, tie=margin == 0,
                             logistic_loss=max(0., -margin) + math.log1p(math.exp(-abs(margin)))))
        fitting_summaries[held] = summary(vals)
    report = dict(families=families, per_source=per_source, overall=summary(frozen),
                  fitting_per_fold=fitting_summaries, zero_score_logistic_loss=math.log(2),
                  positive_hypothesis=all(v['strict_accuracy'] > .5 for v in families.values()),
                  correction_usefulness_established=False, model_ready=False,
                  independent_tone_qualification=False, expert_MOS=False,
                  next_correction_experiment_selected=False)
    write(out / 'assessment.json', report)
    return report


def generated():
    if QA.exists():
        raise FileExistsError(QA)
    QA.mkdir()
    rows = []; features = {}
    for i, source in enumerate(SOURCES):
        for role in model.ROLES:
            key = 'GENERATED_' + source + '__' + role
            t = -.5 if role.endswith('under') else .5 if role.endswith('over') else 0.
            cast = .3 if role.startswith('combined') or role == 'colour_only' else 0.
            x = np.zeros(4096, dtype=np.float32)
            x[:6] = [i / 10, t, -t * t, cast, t * cast, i / 10 * t]
            rows.append(dict(case_id=key, source_id=source, role=role, generated_fixture=True))
            features[key] = x
    originals = {k: v.copy() for k, v in features.items()}
    out = QA / 'MOCK_NOT_INFERENCE'
    heads, proofs = fitting(out, rows, features.__getitem__, True)
    margins = seal(out, rows, features.__getitem__, heads, proofs)
    result = assess(out, margins, heads, features.__getitem__, rows)
    records = model.fitting_records(rows, SOURCES[0], True)
    repeated, retrace, restates = model.fit(records, features.__getitem__, SOURCES[0], True)
    assert repeated == heads[SOURCES[0]]
    assert retrace == read(out / SOURCES[0] / 'trace.json')
    with np.load(out / SOURCES[0] / 'optimizer_states.npz', allow_pickle=False) as pack:
        assert all(np.array_equal(restates[k], pack[k]) for k in pack.files)
    access = []
    permitted = {r['case_id'] for r in records}
    def poison_provider(key):
        assert key in permitted, 'Held payload accessed'
        access.append(key)
        return features[key]
    model.prepare(records, poison_provider, SOURCES[0], True)
    assert set(access) == permitted
    invalid = []
    def rejected(name, fn):
        try:
            fn()
        except (ValueError, FileExistsError):
            invalid.append(name)
        else:
            raise AssertionError('Invalid accepted: ' + name)
    held_in = records + [r | {'partition': 'Train'} for r in rows if r['source_id'] == SOURCES[0]]
    rejected('held_before_feature_access', lambda: model.prepare(held_in, lambda _: (_ for _ in ()).throw(AssertionError()), SOURCES[0], True))
    for kind in ('test', 'provenance', 'duplicate', 'missing_role', 'width', 'dtype', 'nonfinite'):
        rr = copy.deepcopy(records)
        bad_features = {k: v.copy() for k, v in features.items()}
        if kind == 'test': rr[0]['partition'] = 'Test'
        elif kind == 'provenance': rr[0]['generated_fixture'] = False
        elif kind == 'duplicate': rr[-1]['case_id'] = rr[0]['case_id']
        elif kind == 'missing_role': rr = rr[:-1]
        elif kind == 'width': bad_features[rr[0]['case_id']] = np.zeros(4095, np.float32)
        elif kind == 'dtype': bad_features[rr[0]['case_id']] = bad_features[rr[0]['case_id']].astype(np.float64)
        elif kind == 'nonfinite': bad_features[rr[0]['case_id']][0] = np.nan
        rejected(kind, lambda: model.prepare(rr, bad_features.__getitem__, SOURCES[0], True))
    pairs = model.pair_ids(records)
    rejected('reversed_pair', lambda: model.prepare(records, poison_provider, SOURCES[0], True, [pairs[0][::-1]] + pairs[1:]))
    rejected('duplicate_pair', lambda: model.prepare(records, poison_provider, SOURCES[0], True, [pairs[1]] + pairs[1:]))
    rejected('cross_source_pair', lambda: model.prepare(records, poison_provider, SOURCES[0], True, [(pairs[0][0], pairs[-1][1])] + pairs[1:]))
    rejected('overwrite', lambda: write(out / 'all_models_verified.json', {}))
    rejected('missing_fit_barrier', lambda: seal(out, rows, lambda _: (_ for _ in ()).throw(AssertionError()),
                                               dict(list(heads.items())[:-1]), proofs))
    def intentional_failure(step, *_):
        raise RuntimeError('intentional generated failure after update ' + str(step))
    try:
        model.fit(records, poison_provider, SOURCES[0], True, observer=intentional_failure)
    except RuntimeError as exc:
        write(QA / 'intentional_failure_preserved.json', dict(error=str(exc), generated_fixture=True))
    else:
        raise AssertionError('Failure swallowed')
    class PoisonRecord(dict):
        def __getitem__(self, key):
            if key in ('y', 'reference', 'input_pack'):
                raise AssertionError('Forbidden metadata payload accessed')
            return super().__getitem__(key)
    assert model.fitting_records([PoisonRecord(r) for r in rows], SOURCES[0], True) == records
    # Dense independent objective/gradient and finite differences.
    rng = np.random.default_rng(17)
    z = rng.normal(0, .1, (4, 4096)); w = rng.normal(0, .01, 4096)
    p = np.array([[1, 0], [2, 0], [3, 1]]); weights = np.array([.2, .3, .5])
    loss, grad = batch_objective(w, z, p, weights, np.arange(3))
    differences = [[float(a) - float(b) for a, b in zip(z[i], z[j])] for i, j in p]
    sm = [math.fsum(float(a) * b for a, b in zip(w, d)) for d in differences]
    sl = math.fsum(float(a) * (max(0., -v) + math.log1p(math.exp(-abs(v))))
                   for a, v in zip(weights, sm)) + .0005 * math.fsum(float(a) ** 2 for a in w)
    close(loss, sl)
    sg = [-math.fsum(float(a) * d[j] / (1 + math.exp(v)) for a, d, v in zip(weights, differences, sm))
          + .001 * float(w[j]) for j in range(4096)]
    dense_error = float(np.max(np.abs(grad - sg)))
    assert dense_error < 1e-10
    fd_error = 0.
    for j in (0, 1, 17, 281, 1024, 2048, 4095):
        delta = np.zeros(4096); delta[j] = 1e-6
        fd = (batch_objective(w + delta, z, p, weights, np.arange(3))[0]
              - batch_objective(w - delta, z, p, weights, np.arange(3))[0]) / 2e-6
        fd_error = max(fd_error, abs(fd - grad[j]))
    assert fd_error < 1e-8
    assert all(np.array_equal(features[k], v) for k, v in originals.items())
    report = dict(passed=True, generated_full_fold_fits=11, generated_repeat_fits=1,
                  intentional_generated_partial_failure=1, real_head_fits=0,
                  scalar_optimizer_updates=550, dense_gradient_error=dense_error,
                  gradient_finite_difference_error=fd_error, rejected=invalid,
                  repeat='EXACT', immutable_inputs=True, held_payload_poison=True,
                  forbidden_target_reference_payload_poison=True,
                  actual_encoder_calls=0, actual_pixel_reads=0,
                  generated_quality_not_real_quality=True,
                  algebra_counterexamples=read(BASE / 'generated_verification.json'),
                  versions=versions(), code_sha256=code_bindings())
    write(QA / 'verification.json', report)
    print(json.dumps(report, indent=2), flush=True)


def prepare_real():
    if DESIGN.exists():
        raise FileExistsError(DESIGN)
    auth = read(BASE / 'user_authorization.json')
    assert auth['approved']
    qa = read(QA / 'verification.json')
    assert qa['passed'] and qa['versions'] == versions()
    check_bindings(qa['code_sha256'])
    data = ROOT / 'outputs/camera_halfstop_data_v1'
    neural = ROOT / 'outputs/camera_halfstop_neural_v1'
    nc = read(neural / 'completion_PRIVATE.json'); dc = read(data / 'completion_PRIVATE.json')
    proof_path = ROOT / 'outputs/camera_halfstop_prediction_v1/verification_PRIVATE.json'
    proof = read(proof_path)
    assert nc['passed'] and nc['encoder_unchanged'] and nc['vectors'] == 66
    assert dc['passed'] and dc['cases'] == 66 and proof['passed']
    assert proof['identity4096_exact'] == 11
    assert sha(neural / 'features.npz') == nc['feature_sha256']
    assert sha(data / 'plan_PRIVATE.json') == nc['data_plan_sha256'] == dc['plan_sha256']
    assert sha(data / 'rows281_PRIVATE.json') == dc['rows281_sha256']
    plan = read(data / 'plan_PRIVATE.json')
    original = read(data / 'rows281_PRIVATE.json')
    metadata_by_id = {r['case_id']: {k: r[k] for k in ('case_id', 'source_id', 'role',
                      'generated_fixture', 'parent_training_admitted', 'experimental_role')}
                      for r in original}
    roster = []
    for row in plan['rows']:
        r = metadata_by_id[row['case_id']]
        assert all(row[k] == r[k] for k in ('source_id', 'role', 'generated_fixture'))
        assert r['generated_fixture'] is False and r['parent_training_admitted'] is False
        roster.append(r)
    model.metadata(roster, False)
    assert len(roster) == 66 and {r['source_id'] for r in roster} == set(SOURCES)
    # Only declared numerical feature keys, never any input/reference/support pack.
    with np.load(neural / 'features.npz', allow_pickle=False) as pack:
        assert set(pack.files) == set(metadata_by_id)
        for r in roster:
            v = pack[r['case_id']]
            assert v.shape == (4096,) and v.dtype == np.float32 and np.isfinite(v).all()
    bindings = dict(qa['code_sha256'])
    for path in [BASE / 'user_authorization.json', QA / 'verification.json',
                 neural / 'features.npz', neural / 'completion_PRIVATE.json',
                 data / 'plan_PRIVATE.json', data / 'rows281_PRIVATE.json',
                 data / 'completion_PRIVATE.json', proof_path]:
        bindings[path.relative_to(ROOT).as_posix()] = sha(path)
    DESIGN.mkdir()
    write(DESIGN / 'roster.json', sorted(roster, key=lambda r: r['case_id']))
    write(DESIGN / 'bindings.json', bindings)
    write(DESIGN / 'verification.json', dict(passed=True, feature_vectors=66,
          scalar_feature_values=270336, cached_only=True, real_head_fits=0,
          image_reads=0, encoder_calls=0, parent_admission_false_retained=True,
          known_person_crossing_not_established=True, person_separation='UNKNOWN',
          official_MST_labels='UNKNOWN', pretraining_overlap='UNKNOWN',
          feature_file_sha256=nc['feature_sha256'], roster_sha256=sha(DESIGN / 'roster.json'),
          versions=versions()))
    print('PASS actual cached feature/metadata bindings, 66x4096; zero fits/pixels/encoder calls.', flush=True)


def run_real():
    if REAL.exists():
        raise FileExistsError('Real attempt already exists; no automatic refit')
    bindings = read(DESIGN / 'bindings.json')
    check_bindings(bindings)
    admission = read(DESIGN / 'verification.json')
    assert admission['passed'] and admission['versions'] == versions()
    assert sha(DESIGN / 'roster.json') == admission['roster_sha256']
    rows = read(DESIGN / 'roster.json')
    path = ROOT / 'outputs/camera_halfstop_neural_v1/features.npz'
    try:
        with np.load(path, allow_pickle=False) as pack:
            def provider(key):
                return pack[key]
            heads, proofs = fitting(REAL, rows, provider, False)
            write(REAL / 'bindings.json', bindings)
            margins = seal(REAL, rows, provider, heads, proofs)
            result = assess(REAL, margins, heads, provider, rows)
        check_bindings(bindings)
        artifacts = {p.relative_to(REAL).as_posix(): sha(p)
                     for p in sorted(REAL.rglob('*')) if p.is_file()}
        write(REAL / 'verification.json', dict(passed=True, real_head_fits=11,
              real_optimizer_updates=550, independent_optimizer_replays=550,
              all_fitting_proofs_before_held_scores=True, held_scores=66, held_preferences=44,
              correction_fits=0, encoder_calls=0, pixel_reads=0, ratings=0,
              positive_hypothesis=result['positive_hypothesis'], model_ready=False,
              versions=versions(), artifact_sha256=artifacts))
        print(json.dumps(result, indent=2), flush=True)
    except Exception as exc:
        if REAL.exists() and not (REAL / 'execution_failure.json').exists():
            write(REAL / 'execution_failure.json', dict(error=repr(exc),
                  no_automatic_refit=True, stage='post_fit_or_scoring'))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['generated', 'prepare', 'run'])
    stage = parser.parse_args().stage
    {'generated': generated, 'prepare': prepare_real, 'run': run_real}[stage]()
