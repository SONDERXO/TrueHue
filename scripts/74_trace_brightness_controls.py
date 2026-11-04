"""Trace four/ten-feature control errors and input-mask coverage; no fitting."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.model_training.train_model import load_model


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parent = ROOT/'outputs/brightness_features_sourcecv_v1'
    destination = ROOT/'outputs/brightness_control_diagnosis_v1'
    if destination.exists():
        raise FileExistsError(destination)
    summary_path = parent/'summary.json'
    summary = json.loads(summary_path.read_text())
    table = ROOT/'data/manifests/controlled_expansion31_v1/staged_train.csv'
    with table.open(encoding='utf-8', newline='') as stream:
        rows = {r['pair_id']: r for r in csv.DictReader(stream)}
    original_ids = set(list(rows)[:22])
    feature_path = ROOT/'outputs/brightness_feature_audit_v1/input_features.csv'
    with feature_path.open(encoding='utf-8', newline='') as stream:
        feature_rows = {r['pair_id']:r for r in csv.DictReader(stream)}
    mask_audit_path = ROOT/'outputs/brightness_feature_audit_v1/summary.json'
    mask_records = {r['pair_id']:r for r in json.loads(mask_audit_path.read_text())['records']}
    coverage = {}
    mask_hashes = {}
    for pair,row in rows.items():
        if row['variant'] not in ['identity_control','mild_bright_exposure']: continue
        path = ROOT/mask_records[pair]['estimation_mask_path']
        mask_hashes[str(path)] = digest(path)
        mask = cv2.imread(str(path),0)>0
        yy,xx = np.nonzero(mask)
        x0,y0,x1,y1 = xx.min(),yy.min(),xx.max()+1,yy.max()+1
        xm,ym = (x0+x1-1)/2,(y0+y1-1)/2
        counts = [int(((xx<=xm)&(yy<=ym)).sum()),int(((xx>xm)&(yy<=ym)).sum()),int(((xx<=xm)&(yy>ym)).sum()),int(((xx>xm)&(yy>ym)).sum())]
        coverage[pair] = dict(mask_pixels=int(mask.sum()),image_fraction=float(mask.mean()),bbox_occupancy=float(mask.sum()/((x1-x0)*(y1-y0))),quadrant_pixels=counts,minimum_quadrant_fraction=min(counts)/int(mask.sum()),erosion_sensitivity=mask_records[pair]['fixed_bounds_absolute_change'],note='Input-mask geometry only; occupied bounding box is not anatomical face or ground-truth skin.')
    predictions = {(p['pair_id'], p['method']): p for p in summary['predictions']}
    traces, hashes = [], {str(summary_path): digest(summary_path), str(table): digest(table), str(feature_path): digest(feature_path), str(mask_audit_path): digest(mask_audit_path), **mask_hashes}
    for audit in summary['fit_audits']:
        method = audit['method']
        path = parent/'fold_models'/f"fold{audit['fold_id']}_{method}.joblib"
        hashes[str(path)] = digest(path)
        assert digest(path) == summary['fold_model_sha256'][path.name]
        model = load_model(str(path))
        fitting = [rows[p] for p in audit['fit_pair_ids']]
        evaluation = [rows[p] for p in audit['evaluated_pair_ids']]
        for key in ['pair_id', 'source_image_id', 'duplicate_group_id']:
            assert not {r[key] for r in fitting} & {r[key] for r in evaluation}
        columns = audit['feature_columns']
        train_x = np.asarray([[float(feature_rows[r['pair_id']][k]) for k in columns] for r in fitting])
        train_y = np.asarray([[float(r[k]) for k in TARGETS] for r in fitting])
        # Training-fold scale only. Diagnostic distances have no acceptance cutoff
        # and do not alter predictions. ITA overlaps information with L/b.
        scale = train_x.std(axis=0)
        scale[scale == 0] = 1
        leaves = model.apply(train_x)
        for row in evaluation:
            if row['variant'] not in ['identity_control', 'mild_bright_exposure']:
                continue
            p = predictions[(row['pair_id'], method)]
            x = np.asarray([float(feature_rows[row['pair_id']][k]) for k in columns])
            target = np.asarray([float(row[k]) for k in TARGETS])
            predicted = model.predict(x[None, :])[0]
            np.testing.assert_array_equal(predicted, p['predicted_parameters'])
            leaf = int(model.apply(x[None, :])[0])
            member_indices = np.flatnonzero(leaves == leaf)
            np.testing.assert_allclose(train_y[member_indices].mean(axis=0), predicted, atol=1e-12, rtol=0)
            distances = np.linalg.norm((train_x-x)/scale, axis=1)
            nearest = np.argsort(distances, kind='stable')[:3]

            def describe(i):
                r = fitting[int(i)]
                return dict(pair_id=r['pair_id'], source_image_id=r['source_image_id'], variant=r['variant'],
                    added_pair=r['pair_id'] not in original_ids,
                    features=train_x[i].tolist(), target_parameters=train_y[i].tolist(),
                    absolute_target_difference=np.abs(train_y[i]-target).tolist(),
                    fold_standardized_distance=float(distances[i]))

            path_nodes = model.decision_path(x[None, :]).indices
            branches = []
            for node in path_nodes:
                feature = int(model.tree_.feature[node])
                if feature >= 0:
                    branches.append(dict(feature=columns[feature], threshold=float(model.tree_.threshold[node]),
                        observed=float(x[feature]), direction='left' if x[feature] <= model.tree_.threshold[node] else 'right'))
            baseline = predictions[(row['pair_id'], 'no_correction')]['ciede2000_source_mask']
            traces.append(dict(pair_id=row['pair_id'], source_image_id=row['source_image_id'], variant=row['variant'],
                method=method, fold_id=audit['fold_id'], features=x.tolist(), target_parameters=target.tolist(),
                predicted_parameters=predicted.tolist(), leaf_id=leaf, branches=branches, feature_columns=columns, mask_coverage=coverage[row['pair_id']],
                leaf_members=[describe(i) for i in member_indices], nearest_training_examples=[describe(i) for i in nearest],
                features_within_individual_train_ranges=bool(((x >= train_x.min(axis=0)) & (x <= train_x.max(axis=0))).all()),
                leaf_target_range=np.ptp(train_y[member_indices], axis=0).tolist(),
                error=p['ciede2000_source_mask'], no_correction_error=baseline,
                excess_error=float(p['ciede2000_source_mask']-baseline)))
    assert len(traces) == 32
    paired = []
    for pair in sorted({t['pair_id'] for t in traces}):
        old = next(t for t in traces if t['pair_id'] == pair and t['method'] == 'baseline4')
        new = next(t for t in traces if t['pair_id'] == pair and t['method'] == 'brightness10')
        paired.append(dict(pair_id=pair, source_image_id=new['source_image_id'], variant=new['variant'],
            old_error=old['error'], expanded_error=new['error'], error_change=new['error']-old['error'],
            old_prediction=old['predicted_parameters'], expanded_prediction=new['predicted_parameters'],
            expanded_leaf_added_members=sum(m['added_pair'] for m in new['leaf_members']),
            expanded_leaf_variants=dict(Counter(m['variant'] for m in new['leaf_members'])),
            old_leaf_variants=dict(Counter(m['variant'] for m in old['leaf_members'])),
            harmed_before=old['excess_error']>1e-12, harmed_after=new['excess_error']>1e-12,
            coverage=coverage[pair]))
    aggregates = {}
    for method in summary['policy']['methods'][1:]:
        selected = [t for t in traces if t['method'] == method]
        aggregates[method] = dict(controls=16, worsened_identity=sum(t['variant']=='identity_control' and t['excess_error']>1e-12 for t in selected),
            worsened_mild=sum(t['variant']=='mild_bright_exposure' and t['excess_error']>1e-12 for t in selected),
            within_individual_feature_ranges=sum(t['features_within_individual_train_ranges'] for t in selected),
            leaves_with_multiple_variant_targets=sum(len({tuple(m['target_parameters']) for m in t['leaf_members']})>1 for t in selected))
    assert hashes == {p: digest(Path(p)) for p in hashes}
    destination.mkdir()
    board_paths=[]
    for pair,info in coverage.items():
        image=cv2.imread(str(ROOT/rows[pair]['input_path']));mask=cv2.imread(mask_records[pair]['estimation_mask_path'],0)>0
        overlay=image.copy();overlay[mask]=(overlay[mask]*.55+np.asarray([0,180,0])*.45).astype(np.uint8)
        panel=np.hstack([image,overlay]);panel=cv2.copyMakeBorder(panel,34,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(panel,Path(rows[pair]['source_image_id']).stem+' '+rows[pair]['variant']+' input / selected mask',(4,20),cv2.FONT_HERSHEY_SIMPLEX,.42,(255,255,255),1)
        board_paths.append(panel)
        cv2.imwrite(str(destination/(pair+'_mask.png')),panel)
    for n in range(2):cv2.imwrite(str(destination/f'masks_contact{n+1}.png'),np.vstack(board_paths[n*8:(n+1)*8]))
    report = dict(status='complete', no_fitting=True, aggregates=aggregates,
        controls_worse_than_original=sum(p['error_change']>1e-12 for p in paired),
        paired_controls=sorted(paired, key=lambda p: -p['error_change']), traces=traces, input_sha256=hashes,
        limitations='Nearest distances use training-fold standard deviations, not validated similarity thresholds. L/b and ITA are correlated. A shared leaf or nearby measurement is not proof of physical ambiguity, bad source data, or impossibility for other models/features. No target/reference information enters predictions.')
    (destination/'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['aggregates', 'controls_worse_than_original', 'paired_controls']}, indent=2))


if __name__ == '__main__':
    main()
