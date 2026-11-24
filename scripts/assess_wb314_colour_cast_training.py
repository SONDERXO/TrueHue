"""Compare one cast-augmented WB314 recipe on the exposed development sources."""
import math
from pathlib import Path

import numpy as np

from assess_wb314_background_balance import (
    BASE, ROOT, FrozenWB314, features281, extract, read, sha, weighted_fit, write,
)
from wb_feature_direct_verify import route
from wb_feature_direct_workflow import ROLES
from wb314_research_predictor import MODEL_SHA256, validate_inputs
from src.evaluation.directional_recoverability import metrics
from src.evaluation.luminance_chroma_scalar import replay
from src.model_training.luminance_chroma_operator import decode, encode, render_rgb8


OUT = ROOT / 'outputs/wb314_colour_cast_training_2026-11-24'
PROTOCOL = ROOT / 'docs/wb314-colour-cast-training-protocol-2026-11-24.md'
EXPERT_MODEL = ROOT / 'outputs/wb314_final_training_v1/model.json'
CASTS = {'weaker_cool': (.925, 1.075), 'warm': (1.15, .85),
         'green': (.90, .90), 'magenta': (1.10, 1.10)}
COLOUR_WEIGHT = 1 / (1 + len(CASTS))
METRICS = ('RGB', 'DE')
TOLERANCE = 1e-10


def perturb(reference, red, blue):
    linear = decode(reference / 255.0) * [red, 1.0, blue]
    clipped_channels = int((linear > 1).sum())
    rgb = np.rint(encode(np.minimum(linear, 1.0)) * 255).astype(np.uint8)
    return rgb, [1.0, 1.0, 1 / red, 1 / blue, 1.0], clipped_channels


def prepare():
    plan = read(BASE / 'plan.json')
    original = read(BASE / 'rows.json')
    frozen_bindings = read(EXPERT_MODEL.with_name('bindings.json'))
    assert sha(BASE / 'rows.json') == frozen_bindings[(BASE / 'rows.json').relative_to(ROOT).as_posix()]
    assert len(original) == 66 and len(plan['folds']) == 11
    assert len({row['case_id'] for row in original}) == 66
    sources = {row['source_id'] for row in original}
    assert len(sources) == 11 and sources == {fold['held_source_id'] for fold in plan['folds']}
    assert {(row['source_id'], row['role']) for row in original} == {(s, r) for s in sources for r in ROLES}
    packs = {row['case_id']: row for row in plan['rows']}
    masks = read(ROOT / 'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')
    masks = {row['publisher_group'].removeprefix('ffhq_source_'): row for row in masks if row['role'] == 'identity'}
    rows, images = [], {}
    bindings = {str(path): sha(path) for path in (PROTOCOL, Path(__file__), BASE / 'plan.json', BASE / 'rows.json')}
    predictor = FrozenWB314()
    for row in original:
        case, source, role = (row[k] for k in ('case_id', 'source_id', 'role'))
        spec = packs[case]
        assert [spec[k] for k in ('source_id', 'role', 'y')] == [source, role, row['y']]
        path = ROOT / spec['input_pack']
        assert sha(path) == spec['input_pack_sha256']
        bindings[str(path)] = spec['input_pack_sha256']
        with np.load(path, allow_pickle=False) as pack:
            inputs = tuple(pack[k] for k in ('input', 'reference', 'alpha', 'protected'))
        images[case] = inputs
        rows.append(dict(case_id=case, source_id=source, role=role, x=row['x314'], y=row['y'],
                         weight=COLOUR_WEIGHT if role == 'colour_only' else 1.0))
        if role != 'identity':
            continue
        mask = masks[source]
        mask_path = Path(mask['pixels_file'])
        assert sha(mask_path) == mask['pixels_sha256']
        bindings[str(mask_path)] = mask['pixels_sha256']
        with np.load(mask_path, allow_pickle=False) as pack:
            measurement = pack['measurement_mask']
        image, reference, alpha, protected = inputs
        validate_inputs(reference, measurement, alpha, protected)
        assert np.array_equal(image, reference)
        for condition, (red, blue) in CASTS.items():
            cast, target, clipped = perturb(reference, red, blue)
            assert np.array_equal(cast[..., 1], reference[..., 1]) and not np.array_equal(cast, reference)
            first, _ = features281(cast, measurement, predictor.mapping, predictor.names[:281])
            coefficients, _, _, _ = extract(predictor.wb, predictor.normalize, cast)
            vector = np.asarray(first + coefficients.tolist(), np.float32).astype(float).tolist()
            variant = case + '__' + condition
            images[variant] = cast, reference, alpha, protected
            rows.append(dict(case_id=variant, source_id=source, role=condition, x=vector, y=target,
                             weight=COLOUR_WEIGHT, clipped_input_channels=clipped))
        print(f'Prepared {sum(r["role"] in CASTS for r in rows)}/44 added views', flush=True)
    assert len(rows) == len(images) == 110
    assert all(sha(path) == digest for path, digest in bindings.items())
    for source in sources:
        colour = [r['weight'] for r in rows if r['source_id'] == source and r['role'] in ('colour_only', *CASTS)]
        assert len(colour) == 5 and math.fsum(colour) == 1
    write(OUT / 'bindings_PRIVATE.json', bindings)
    write(OUT / 'training_rows_PRIVATE.json', rows)
    return plan, rows, images


def predict(plan, rows):
    old_models = read(BASE / 'all_fits_verified.json')['models']
    controls = {}
    for index, fold in enumerate(plan['folds'], 1):
        source = fold['held_source_id']
        baseline_entry = next(model for model in old_models if model['arm'] == '314' and model['source_id'] == source)
        baseline_path = BASE / baseline_entry['path']
        assert sha(baseline_path) == baseline_entry['sha256']
        baseline = read(baseline_path)
        candidate = weighted_fit(rows, source)
        candidate['model_role'] = 'cast_diversity_assessment_only'
        write(OUT / f'held_{index:02d}_PRIVATE.json', candidate)
        for row in rows:
            if row['source_id'] == source:
                assert row['case_id'] not in controls
                controls[row['case_id']] = {name: route(model, row['x'])[1]
                                            for name, model in (('baseline', baseline), ('candidate', candidate))}
        print(f'Verified {index}/11 source-held fits', flush=True)
    assert len(controls) == 110
    write(OUT / 'held_controls_PRIVATE.json', controls)
    return controls


def score(rows, images, controls):
    scores = []
    for index, row in enumerate(rows, 1):
        case = row['case_id']
        image, reference, alpha, protected = images[case]
        support = alpha > 0
        record = {k: row[k] for k in ('case_id', 'role')}
        record['input'] = metrics(image, reference, support)
        for name, parameters in controls[case].items():
            output = render_rgb8(image, alpha, protected, parameters)
            scalar, _ = replay(image, reference, alpha, protected, parameters)
            assert np.array_equal(output, scalar), (case, name)
            assert np.array_equal(output[protected | ~support], image[protected | ~support]), (case, name)
            record[name] = metrics(output, reference, support)
            record[name + '_changed'] = not np.array_equal(output, image)
        scores.append(record)
        if index % 11 == 0:
            print(f'Scored {index}/110 held inputs', flush=True)
    write(OUT / 'scores_PRIVATE.json', scores)
    return scores


def assess(scores):
    summary, gates = {}, {}
    for role in (*ROLES, *CASTS):
        cases = [entry for entry in scores if entry['role'] == role]
        assert len(cases) == 11
        means = {kind: {m: math.fsum(row[kind][m] for row in cases) / len(cases) for m in METRICS}
                 for kind in ('input', 'baseline', 'candidate')}
        harms = {kind: {m: sum(row[kind][m] > row['input'][m] + TOLERANCE for row in cases) for m in METRICS}
                 for kind in ('baseline', 'candidate')}
        results = {'means': means, 'worse_than_input': harms}
        summary[role] = results
        if role in CASTS:
            improved = sum(all(row['candidate'][m] < row['input'][m] - TOLERANCE for m in METRICS) for row in cases)
            results['improved_on_both_metrics'] = improved
            gates[role + '_means_improve'] = all(means['candidate'][m] < means[kind][m] - TOLERANCE
                                                   for m in METRICS for kind in ('baseline', 'input'))
            gates[role + '_majority_improves'] = improved >= 6
        else:
            gates[role + '_means_preserved'] = all(means['candidate'][m] <= means['baseline'][m] + TOLERANCE for m in METRICS)
            gates[role + '_no_extra_harm'] = all(harms['candidate'][m] <= harms['baseline'][m] for m in METRICS)
    identity = [entry for entry in scores if entry['role'] == 'identity']
    changed = {kind: sum(row[kind + '_changed'] for row in identity) for kind in ('baseline', 'candidate')}
    gates['identity_edit_count_preserved'] = changed['candidate'] <= changed['baseline']
    return {'by_condition': summary, 'identity_edits': changed, 'gates': gates, 'passed': all(gates.values())}


def main():
    assert sha(EXPERT_MODEL) == MODEL_SHA256
    OUT.mkdir()
    plan, rows, images = prepare()
    controls = predict(plan, rows)
    scores = score(rows, images, controls)
    assert sha(EXPERT_MODEL) == MODEL_SHA256
    results = dict(assess(scores), source_held_fits=11, added_views=44, source_portraits=11,
                   scalar_and_protection_checks=220, final_fits=0, expert_model_sha256=MODEL_SHA256,
                   clipped_input_channels={role: sum(row['clipped_input_channels'] for row in rows
                                                      if row['role'] == role) for role in CASTS})
    write(OUT / 'summary.json', results)
    print(f'Passed {sum(results["gates"].values())}/{len(results["gates"])} candidate gates', flush=True)


if __name__ == '__main__':
    main()
