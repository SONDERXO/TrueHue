"""Execute the predeclared eight-source expansion comparison, never promote a model."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.data_preparation.source_group_folds import source_group_folds
from src.evaluation.correction_prototype import model_arrays, apply_correction, image_errors
from src.model_training.train_model import save_model, load_model
from src.utilities.config import get_config


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    stage = ROOT/'data/manifests/controlled_expansion31_v1'
    output = ROOT/'outputs/development_expansion_sourcecv_v1'
    if output.exists():
        raise FileExistsError(output)
    rows = read(stage/'staged_train.csv')
    original = read(ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv')
    assert rows[:22] == original and len(rows) == 31
    old_ids = {r['pair_id'] for r in original}
    by_id = {r['pair_id']: r for r in rows}
    folds = source_group_folds(rows)
    assert folds == json.loads((stage/'source_group_folds.json').read_text())['folds']
    plan = json.loads((stage/'comparison_plan.json').read_text())
    assert plan['settings'] == dict(max_depth=3, random_state=42, min_samples_leaf=1, target_scaling='none')
    assert len(folds) == 8
    assert all(r['partition'] == r['table_use'] == 'train' and int(r['clipped_pixel_count']) == 0 for r in rows)
    tracked = [Path(__file__), *stage.glob('*.json'), stage/'staged_train.csv',
               ROOT/'data/manifests/correction_controls_sourcecv_v1/development_train.csv',
               ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH]
    inputs = {}
    for r in rows:
        paths = [ROOT/r[k] for k in ['input_path', 'reference_path', 'correction_mask_path', 'generation_mask_path']]
        tracked.extend(paths)
        image, reference = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in paths[:2]]
        support, scoring = [cv2.imread(str(p), 0) > 0 for p in paths[2:]]
        assert image.shape == reference.shape == (256, 256, 3) and scoring.any()
        inputs[r['pair_id']] = image, reference, support, scoring
    hashes = {str(p): digest(p) for p in tracked}
    output.mkdir(); (output/'fold_models').mkdir(); (output/'review_boards').mkdir()
    (output/'comparison_policy.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
    predictions, audits, model_hashes = [], [], {}
    for fold in folds:
        evaluation = [by_id[p] for p in fold['inner_validation_pair_ids']]
        x_test, _ = model_arrays(evaluation)
        parameter_sets = {'no_correction': np.ones((len(evaluation), 3))}
        for method in plan['methods'][1:]:
            fitting = [by_id[p] for p in fold['train_pair_ids'] if method == 'expanded31_controls_tree' or p in old_ids]
            for key in ['pair_id', 'source_image_id', 'duplicate_group_id']:
                assert not {r[key] for r in fitting} & {r[key] for r in evaluation}
            x, y = model_arrays(fitting)
            learner = DecisionTreeRegressor(max_depth=3, random_state=42, min_samples_leaf=1).fit(x, y)
            path = output/'fold_models'/f"fold{fold['fold_id']}_{method}.joblib"
            save_model(learner, str(path)); model_hashes[path.name] = digest(path)
            parameter_sets[method] = learner.predict(x_test)
            np.testing.assert_array_equal(load_model(str(path)).predict(x_test), parameter_sets[method])
            audits.append(dict(fold_id=fold['fold_id'], method=method, held_out_group=fold['held_out_duplicate_group'],
                               fit_pair_ids=[r['pair_id'] for r in fitting], evaluated_pair_ids=[r['pair_id'] for r in evaluation]))
        for i, r in enumerate(evaluation):
            image, reference, support, scoring = inputs[r['pair_id']]
            panels = []
            for method, values in parameter_sets.items():
                params = values[i]
                corrected = apply_correction(image, support, params)
                np.testing.assert_array_equal(corrected[~support], image[~support])
                predictions.append(dict(pair_id=r['pair_id'], source_image_id=r['source_image_id'], variant=r['variant'],
                    cohort='shared22' if r['pair_id'] in old_ids else 'new9', method=method, fold_id=fold['fold_id'],
                    predicted_parameters=params.tolist(), features=[float(r[k]) for k in FEATURES],
                    parameter_absolute_error=np.abs(params-np.asarray([float(r[k]) for k in TARGETS])).tolist(),
                    **image_errors(reference, corrected, scoring)))
                cv2.imwrite(str(output/(r['pair_id']+'__'+method+'.png')), cv2.cvtColor(corrected, cv2.COLOR_RGB2BGR))
                panel = cv2.copyMakeBorder(corrected, 36, 0, 0, 0, cv2.BORDER_CONSTANT)
                cv2.putText(panel, method.replace('_controls_tree', ''), (4, 15), cv2.FONT_HERSHEY_SIMPLEX, .40, (255, 255, 255), 1)
                cv2.putText(panel, r['variant'], (4, 30), cv2.FONT_HERSHEY_SIMPLEX, .35, (255, 255, 255), 1)
                panels.append(panel)
            panels.append(cv2.copyMakeBorder(reference, 36, 0, 0, 0, cv2.BORDER_CONSTANT))
            cv2.imwrite(str(output/'review_boards'/(r['pair_id']+'.png')), cv2.cvtColor(np.hstack(panels), cv2.COLOR_RGB2BGR))
        print('Completed fold', fold['fold_id'], flush=True)
    assert len(predictions) == 93 and len(audits) == 16
    assert len({(r['pair_id'], r['method']) for r in predictions}) == 93
    assert hashes == {p: digest(p) for p in hashes}

    def aggregate(selected):
        report = {}
        for method in plan['methods']:
            cohort = [p for p in selected if p['method'] == method]
            sources = sorted({p['source_image_id'] for p in cohort})
            report[method] = dict(pairs=len(cohort), sources=len(sources),
                mean_ciede2000=float(np.mean([p['ciede2000_source_mask'] for p in cohort])),
                equal_source_mean_ciede2000=float(np.mean([np.mean([p['ciede2000_source_mask'] for p in cohort if p['source_image_id'] == s]) for s in sources])),
                parameter_mae=np.mean([p['parameter_absolute_error'] for p in cohort], axis=0).tolist())
        return report

    summary = dict(status='complete', plan=plan, aggregates=aggregate(predictions),
        by_cohort={c: aggregate([p for p in predictions if p['cohort'] == c]) for c in ['shared22', 'new9']},
        by_variant={v: aggregate([p for p in predictions if p['variant'] == v]) for v in sorted({r['variant'] for r in rows})},
        by_source={s: aggregate([p for p in predictions if p['source_image_id'] == s]) for s in sorted({r['source_image_id'] for r in rows})},
        predictions=predictions, fit_audits=audits, input_sha256=hashes, fold_model_sha256=model_hashes,
        verification=dict(source_and_duplicate_disjoint=True, saved_model_prediction_replay=True, unchanged_outside_support=True, original_artifacts_unchanged=True),
        limitation='Selected development sources, not independent subjects/final test; reconstruction relative to photographs, not calibrated skin truth. No neck implementation or runtime promotion.')
    (output/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (output/'review-index.md').write_text('# Source-held-out comparison\n\nPanels: input, original22, expanded31, source reference.\n\n'+ '\n'.join(f"- [{r['source_image_id']} {r['variant']}](review_boards/{r['pair_id']}.png)" for r in rows), encoding='utf-8')
    print(json.dumps({k: summary[k] for k in ['aggregates', 'by_cohort', 'by_variant']}, indent=2))


if __name__ == '__main__':
    main()
