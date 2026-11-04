"""Fixed31 versus39 training pairs, frozen ten features and ten source folds."""
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


def main():
    stage = ROOT/'data/manifests/controlled_expansion39_v1'
    parent = ROOT/'outputs/brightness_features_sourcecv_v1/summary.json'
    output = ROOT/'outputs/development39_sourcecv_v1'
    if output.exists():
        raise FileExistsError(output)
    with (stage/'staged_train.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 39
    by_id = {r['pair_id']: r for r in rows}; old_ids = {r['pair_id'] for r in rows[:31]}
    folds = source_group_folds(rows)
    assert len(folds) == 10 and folds == json.loads((stage/'source_group_folds.json').read_text())['folds']
    prior = json.loads(parent.read_text())
    old_predictions = {(p['pair_id'], p['method']): p for p in prior['predictions']}
    feature_root = stage
    schema = json.loads((feature_root/'feature_schema.json').read_text())
    with (feature_root/'input_features.csv').open(encoding='utf-8', newline='') as stream:
        feature_rows = {r['pair_id']: r for r in csv.DictReader(stream)}
    assert set(feature_rows) == set(by_id) and len(schema['proposed_features']) == 10
    assert schema['baseline_features'] == list(FEATURES)
    for r in rows:
        f = feature_rows[r['pair_id']]
        assert f['available'] == 'True'
        assert all(float(f[k]) == float(r[k]) for k in FEATURES)
    inputs = {}; tracked = [Path(__file__), parent, stage/'staged_train.csv', stage/'source_group_folds.json',
                               ROOT/get_config().CORRECTION_PROTOTYPE_MODEL_PATH, feature_root/'feature_schema.json', feature_root/'input_features.csv', stage/'comparison_plan.json']
    for r in rows:
        assert r['partition'] == r['table_use'] == 'train' and int(r['clipped_pixel_count']) == 0
        paths = [ROOT/r[k] for k in ['input_path', 'reference_path', 'correction_mask_path', 'generation_mask_path']]
        tracked.extend(paths)
        image, reference = [cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB) for p in paths[:2]]
        support, scoring = [cv2.imread(str(p), 0) > 0 for p in paths[2:]]
        inputs[r['pair_id']] = image, reference, support, scoring
    hashes = {str(p): digest(p) for p in tracked}
    output.mkdir(); (output/'fold_models').mkdir(); (output/'review_boards').mkdir()
    policy = dict(methods=['no_correction', 'original31', 'expanded39'], max_depth=3,
        random_state=42, min_samples_leaf=1, target_scaling='none', feature_columns={'original31': schema['proposed_features'], 'expanded39': schema['proposed_features']}, target_columns=list(TARGETS),
        scope='Fixed diagnostic; same39 selected development probes, ten source-group folds, original31 versus expanded39 training; unchanged masks and frozen ten features. No feature/depth search or runtime promotion.',
        training_fit='Parameter MAE on fitting rows; held-source image reconstruction reported separately.')
    (output/'comparison_policy.json').write_text(json.dumps(policy, indent=2), encoding='utf-8')
    predictions, audits, model_hashes = [], [], {}
    for fold in folds:
        all_fitting = [by_id[p] for p in fold['train_pair_ids']]
        evaluation = [by_id[p] for p in fold['inner_validation_pair_ids']]
        for key in ['pair_id', 'source_image_id', 'duplicate_group_id']:
            assert not {r[key] for r in all_fitting} & {r[key] for r in evaluation}
        _, yt = model_arrays(evaluation)
        params = {'no_correction': np.ones((len(evaluation), 3))}
        for method in ['original31', 'expanded39']:
            fitting = [r for r in all_fitting if method == 'expanded39' or r['pair_id'] in old_ids]
            _, y = model_arrays(fitting)
            columns = policy['feature_columns'][method]
            x = np.asarray([[float(feature_rows[r['pair_id']][k]) for k in columns] for r in fitting])
            xt = np.asarray([[float(feature_rows[r['pair_id']][k]) for k in columns] for r in evaluation])
            assert np.isfinite(x).all() and np.isfinite(xt).all()
            model = DecisionTreeRegressor(max_depth=3, random_state=42, min_samples_leaf=1).fit(x, y)
            path = output/'fold_models'/f"fold{fold['fold_id']}_{method}.joblib"
            save_model(model, str(path)); model_hashes[path.name] = digest(path)
            params[method] = model.predict(xt)
            np.testing.assert_array_equal(load_model(str(path)).predict(xt), params[method])
            train_predictions = model.predict(x)
            if method == 'original31':
                for i, r in enumerate(evaluation):
                    if r['pair_id'] not in old_ids: continue
                    np.testing.assert_array_equal(params[method][i], old_predictions[(r['pair_id'], 'brightness10')]['predicted_parameters'])
            audits.append(dict(fold_id=fold['fold_id'], method=method, held_out_group=fold['held_out_duplicate_group'],
                feature_columns=columns, fit_pair_ids=[r['pair_id'] for r in fitting], evaluated_pair_ids=[r['pair_id'] for r in evaluation],
                actual_depth=int(model.get_depth()), leaves=int(model.get_n_leaves()), training_parameter_mae=np.abs(train_predictions-y).mean(axis=0).tolist(),
                training_predicted_parameters=train_predictions.tolist()))
        for i, r in enumerate(evaluation):
            image, reference, support, scoring = inputs[r['pair_id']]; panels = []
            for method, values in params.items():
                corrected = apply_correction(image, support, values[i])
                np.testing.assert_array_equal(corrected[~support], image[~support])
                error = image_errors(reference, corrected, scoring)
                if method == 'original31' and r['pair_id'] in old_ids:
                    assert error == {k: old_predictions[(r['pair_id'], 'brightness10')][k] for k in error}
                predictions.append(dict(pair_id=r['pair_id'], source_image_id=r['source_image_id'], variant=r['variant'],
                    cohort='shared31' if r['pair_id'] in old_ids else 'new8', fold_id=fold['fold_id'], method=method,
                    predicted_parameters=values[i].tolist(), parameter_absolute_error=np.abs(values[i]-yt[i]).tolist(), **error))
                panel = cv2.copyMakeBorder(corrected, 36, 0, 0, 0, cv2.BORDER_CONSTANT)
                for line, label in enumerate([method, r['variant']]):
                    cv2.putText(panel, label, (4, 15+15*line), cv2.FONT_HERSHEY_SIMPLEX, .36, (255,255,255), 1)
                panels.append(panel)
            panel = cv2.copyMakeBorder(reference, 36, 0, 0, 0, cv2.BORDER_CONSTANT)
            cv2.putText(panel, 'Source reference', (4,15), cv2.FONT_HERSHEY_SIMPLEX,.36,(255,255,255),1)
            panels.append(panel)
            assert cv2.imwrite(str(output/'review_boards'/(r['pair_id']+'.png')), cv2.cvtColor(np.hstack(panels), cv2.COLOR_RGB2BGR))
        print('Completed expansion fold', fold['fold_id'], flush=True)
    assert len(predictions) == len({(p['pair_id'],p['method']) for p in predictions}) == 117 and len(audits) == 20

    def aggregate(selected):
        result = {}
        for method in policy['methods']:
            cohort = [p for p in selected if p['method'] == method]
            sources = {p['source_image_id'] for p in cohort}
            result[method] = dict(pairs=len(cohort), sources=len(sources),
                mean_ciede2000=float(np.mean([p['ciede2000_source_mask'] for p in cohort])),
                equal_source_mean_ciede2000=float(np.mean([np.mean([p['ciede2000_source_mask'] for p in cohort if p['source_image_id']==s]) for s in sorted(sources)])),
                parameter_mae=np.mean([p['parameter_absolute_error'] for p in cohort], axis=0).tolist())
        return result

    assert hashes == {p: digest(p) for p in hashes}
    summary = dict(status='complete', policy=policy, aggregates=aggregate(predictions),
        by_cohort={c: aggregate([p for p in predictions if p['cohort']==c]) for c in ['shared31','new8']},
        by_variant={v: aggregate([p for p in predictions if p['variant']==v]) for v in sorted({r['variant'] for r in rows})},
        by_source={s: aggregate([p for p in predictions if p['source_image_id']==s]) for s in sorted({r['source_image_id'] for r in rows})},
        fit_audits=audits, predictions=predictions, input_sha256=hashes, fold_model_sha256=model_hashes,
        verification='All shared31 original31 held-source parameters and image metrics exactly reproduce the prior experiment. Saved models replay; pairs/sources/duplicate groups disjoint; outside-support pixels and original hashes unchanged.',
        limitations='Selected development sources, not final test/independent subjects. No final all-source model or runtime change. Photographic reconstruction, not calibrated skin truth. Neck and operational MST pending.')
    (output/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (output/'review-index.md').write_text('# Fixed31 versus39 training comparison\n\nInput, original31, expanded39, source reference.\n\n'+'\n'.join(f"- [{r['source_image_id']} {r['variant']}](review_boards/{r['pair_id']}.png)" for r in rows),encoding='utf-8')
    print(json.dumps(dict(aggregates=summary['aggregates'], by_variant=summary['by_variant'],
        training_fit=[dict(method=a['method'],fold=a['fold_id'],depth=a['actual_depth'],mae=a['training_parameter_mae']) for a in audits]),indent=2))


if __name__ == '__main__':
    main()
