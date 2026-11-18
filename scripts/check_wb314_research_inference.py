"""One implementation parity run on existing development inputs; zero fits or selection."""
from pathlib import Path
import importlib.metadata
import json
import time
import cv2
import numpy as np
from wb314_research_predictor import ROOT, FrozenWB314, validate_inputs, read, sha

OUT = ROOT / 'outputs/wb314_research_inference_v1'
FINAL = ROOT / 'outputs/wb314_final_training_v1'
WB = ROOT / 'outputs/wb_feature_direct_prediction_v1'


def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def generated_checks():
    tree = FrozenWB314.__new__(FrozenWB314)
    tree.model = {'nodes': [dict(kind='split', feature=0, threshold=1 - 2**-26, left=1, right=2),
                           dict(kind='leaf', values=[1., 1., 1., 1., 1.]),
                           dict(kind='leaf', values=[1., 2., 1., 1., 1.])]}
    assert tree.predict_features(np.ones(314, np.float32))[1] == 2
    below = np.ones(314, np.float32); below[0] = np.nextafter(np.float32(1), np.float32(0))
    assert tree.predict_features(below)[1] == 1
    rgb = np.full((256, 256, 3), 128, np.uint8)
    mask = np.full((256, 256), 255, np.uint8)
    alpha = np.ones((256, 256), float)
    protected = np.zeros((256, 256), bool)
    validate_inputs(rgb, mask, alpha, protected)
    count = 0
    for kind in ['rgb_shape', 'rgb_dtype', 'measurement_values', 'measurement_empty',
                 'alpha_nan', 'alpha_range', 'alpha_empty', 'protected_dtype', 'protected_overlap']:
        args = [a.copy() for a in [rgb, mask, alpha, protected]]
        if kind == 'rgb_shape': args[0] = args[0][:128]
        elif kind == 'rgb_dtype': args[0] = args[0].astype(float)
        elif kind == 'measurement_values': args[1][0, 0] = 1
        elif kind == 'measurement_empty': args[1][:] = 0
        elif kind == 'alpha_nan': args[2][0, 0] = np.nan
        elif kind == 'alpha_range': args[2][0, 0] = 1.1
        elif kind == 'alpha_empty': args[2][:] = 0
        elif kind == 'protected_dtype': args[3] = args[3].astype(np.uint8)
        else: args[3][0, 0] = True
        try: validate_inputs(*args)
        except ValueError: count += 1
        else: raise AssertionError('Invalid inference input accepted: ' + kind)
    return count


def main():
    if OUT.exists(): raise FileExistsError('Preserve original integration attempt')
    guards = generated_checks()
    ratings = ROOT / 'outputs/wb314_final_changed_ratings_v1'
    v = read(ratings / 'verification.json'); assert v['passed']
    for p, h in v['artifacts'].items(): assert sha(ratings / p) == h
    assessment = read(ratings / 'assessment_PRIVATE.json')
    assert assessment['status'] == 'complete_recorded' and assessment['appearance_counts']['acceptable'] == 22
    final = read(FINAL / 'verification.json'); assert final['passed']
    for p, h in final['artifacts'].items(): assert sha(FINAL / p) == h
    bindings = {p.replace('\\', '/'): h for p, h in
                read(ROOT / 'outputs/camera_halfstop_data_v1/bindings_PRIVATE.json')['input_sha256'].items()}
    source_plan = 'outputs/five_control_source_held_prediction_design_v1/plan_PRIVATE.json'
    assert sha(ROOT / source_plan) == bindings[source_plan]
    sources = {r['source_id']: r for r in read(ROOT / source_plan)['feature_sources']}
    rows = read(WB / 'rows.json')
    predictions = {r['case_id']: r for r in read(FINAL / 'training_predictions.json')}
    known = {p.replace('\\', '/'): h for p, h in read(WB / 'verification.json')['artifacts'].items()}
    declared = {p: h for p, h in read(FINAL / 'bindings.json').items()}
    for r in rows:
        s = sources[r['source_id']]
        declared[s['measurement_path']] = s['measurement_sha256']
        p = 'outputs/wb_feature_direct_prediction_v1/evaluation/' + r['case_id'] + '.npz'
        declared[p] = known['evaluation/' + r['case_id'] + '.npz']
    for p, h in declared.items(): assert sha(ROOT / p) == h, p
    model = FrozenWB314()  # All generated input guards precede any portrait-array decode.
    for bad in [np.zeros(313), np.full(314, np.nan), np.full(314, np.inf), np.ones(314, complex)]:
        try: model.predict_features(bad)
        except ValueError: pass
        else: raise AssertionError('Invalid feature vector accepted')
    OUT.mkdir()
    write(OUT / 'bindings.json', declared)
    write(OUT / 'plan.json', dict(kind='Input-to-output implementation parity, not new scientific evaluation',
          cases=66, feature_extractions=66, real_fits=0, parameter_searches=0,
          source_inputs='Existing cached development inputs and approved cached measurement masks',
          defaults_changed=False, model_sha256=assessment['model_sha256']))
    records = []; started = time.perf_counter()
    immutable = [model.wb.features, model.wb.mappingFuncs, model.wb.encoderWeights, model.wb.encoderBias]
    state = [a.tobytes() for a in immutable]
    masks = {}
    try:
        for row in rows:
            case = row['case_id']
            with np.load(WB / 'evaluation' / (case + '.npz'), allow_pickle=False) as z:
                rgb, alpha, protected = [z[k].copy() for k in ['input', 'alpha', 'protected']]
            source = sources[row['source_id']]
            if row['source_id'] not in masks:
                masks[row['source_id']] = cv2.imread(str(ROOT / source['measurement_path']), cv2.IMREAD_GRAYSCALE)
            measurement = masks[row['source_id']]
            before = [a.tobytes() for a in [rgb, measurement, alpha, protected]]
            result = model.correct(rgb, measurement, alpha, protected)
            assert result['features'] == row['x314'], 'Feature contract mismatch: ' + case
            expected = predictions[case]
            assert result['controls'] == expected['controls'] and result['leaf'] == expected['leaf']
            with np.load(FINAL / 'evaluation' / (case + '.npz'), allow_pickle=False) as z:
                assert np.array_equal(result['output'], z['candidate']), 'RGB8 mismatch: ' + case
            assert before == [a.tobytes() for a in [rgb, measurement, alpha, protected]]
            records.append(dict(case_id=case, features_exact=True, controls_exact=True,
                                output_exact=True, caller_arrays_immutable=True))
            if len(records) % 11 == 0: print(f'Frozen input-to-output parity {len(records)}/66', flush=True)
        assert state == [a.tobytes() for a in immutable]
        for p, h in declared.items(): assert sha(ROOT / p) == h
        write(OUT / 'records.json', records)
        paths = [Path(__file__), ROOT / 'scripts/wb314_research_predictor.py',
                 ROOT / 'scripts/wb_cue_adapter.py', ROOT / 'scripts/wb_cue_equivalent_ties.py',
                 ROOT / 'src/model_training/blue_axis_preparation.py',
                 ROOT / 'src/model_training/luminance_chroma_operator.py']
        write(OUT / 'verification.json', dict(passed=True, cases=66, exact_feature_values=66 * 314,
              exact_controls=66, exact_RGB8_outputs=66, input_and_WB_state_immutable=True,
              generated_invalid_input_guards=guards, invalid_feature_guards=4,
              binary64_threshold_boundary_guards=2,
              real_fits=0, elapsed_seconds=time.perf_counter() - started,
              qualification_complete=False, masking_inferred=False, defaults_changed=False,
              versions={k: importlib.metadata.version(k) for k in ['numpy', 'opencv-python', 'scipy']},
              source_bindings={p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
              artifacts={p.name: sha(p) for p in OUT.iterdir() if p.is_file()}))
        print('PASS66 normalized input/mask-to-output paths;0fits/default changes.', flush=True)
    except Exception as exc:
        write(OUT / 'failure.json', dict(error=repr(exc), completed=len(records), retry_allowed=False))
        raise


if __name__ == '__main__': main()
