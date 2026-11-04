"""Independent saved-pixel replay, frozen prediction and mask-accounting checks."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.evaluation.correction_prototype import image_errors
from src.model_training.portable_tree import PortableTree
from src.ita_estimation.mst_lookup import MST_FEATURES
from src.ita_estimation.square_measurement import contract


def main():
    out = ROOT / 'outputs/table2_application_mask_comparison_v1'
    target = out / 'verification.json'
    if target.exists():
        raise FileExistsError(target)
    def read(p): return json.loads(p.read_text(encoding='utf-8'))
    def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    def rgb(p): return cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)
    def mask(p): return cv2.imread(str(p), 0) > 0
    summary = read(out / 'summary.json')
    parent = ROOT / 'outputs/table2_reviewed_expansion_evaluation_v1'
    plan = read(parent / 'fit_plan.json')
    rows = {r['pair_id']: r for r in plan['rows']}
    predictions = {r['pair_id']: r for r in read(parent / 'summary.json')['records']}
    assert len(summary['records']) == 24
    assert contract(ROOT)[1] == summary['measurement_contract_sha256']
    for p, h in summary['input_sha256'].items():
        assert digest(ROOT / p) == h, p
    counts = dict(predictions=0, corrected_images=0, masks=0, rejected_mask_only=0)
    for record in summary['records']:
        pair = record['pair_id']; image = rgb(ROOT / record['input_path'])
        reference = rgb(ROOT / record['reference_path']); scoring = mask(ROOT / record['reference_mask_path'])
        current = mask(ROOT / record['input_mask_path'])
        categories = cv2.imread(str(out / 'images' / (pair + '_categories.png')), 0)
        exclusions = mask(out / 'images' / (pair + '_exclusions.png'))
        assert record['candidate_failure'] is None
        masks = {method: mask(out / 'images' / (pair + '_' + method + '_mask.png')) for method in record['masks']}
        np.testing.assert_array_equal(masks['current'], current)
        np.testing.assert_array_equal(masks['legacy_non_skin'], masks['legacy_broad'] & np.isin(categories, [2, 3]))
        assert not (masks['legacy_broad'] & (categories == 1)).any()
        for method, selected in masks.items():
            assert selected.shape == (256, 256) and not (selected & exclusions).any()
            expected = dict(pixels=int(selected.sum()), added=int((selected & ~current).sum()),
                removed=int((current & ~selected).sum()), reference_support_retained=float((selected & scoring).sum()/scoring.sum()),
                outside_reference_support=int((selected & ~scoring).sum()), predicted_hair_selected=int((selected & (categories == 1)).sum()))
            assert expected == record['masks'][method]
            counts['masks'] += 1
        if record['diagnostic_only']:
            assert pair not in rows and 'parameters' not in record and not record['metrics']
            assert not list((out / 'images').glob(pair + '*_corrected.png'))
            counts['rejected_mask_only'] += 1
            continue
        row = rows[pair]; prediction = predictions[pair]
        assert record['parameters'] == prediction['parameters']
        portable = PortableTree(read(parent / f"fold_{prediction['fold_id']}/decision_tree.json"))
        np.testing.assert_allclose(portable.predict_one([row[k] for k in MST_FEATURES]), record['parameters'], atol=1e-12, rtol=0)
        for feature in record['features']:
            assert record['features'][feature] == row[feature]
        counts['predictions'] += 1
        gamma, red, blue = record['parameters']
        # Independent encoded-RGB formula, without calling apply_correction.
        raw = np.power(image.astype(float)/255, 1/gamma) * np.array([red, 1., blue])
        transformed = np.rint(np.clip(raw, 0, 1)*255).astype(np.uint8)
        for method, selected in masks.items():
            expected = image.copy(); expected[selected] = transformed[selected]
            actual = rgb(out / 'images' / (pair + '_' + method + '_corrected.png'))
            np.testing.assert_array_equal(actual, expected)
            np.testing.assert_array_equal(actual[~selected], image[~selected])
            assert image_errors(reference, actual, scoring) == record['metrics'][method]
            if method == 'current':
                assert digest(out / 'images' / (pair + '_current_corrected.png')) == prediction['output_sha256']
            counts['corrected_images'] += 1
        assert image_errors(reference, image, scoring) == record['metrics']['no_correction']
    accepted = [r for r in summary['records'] if not r['diagnostic_only']]
    for group, subset in [('all', accepted), ('identity', [r for r in accepted if r['variant']=='identity']),
                          ('distorted', [r for r in accepted if r['variant']!='identity'])]:
        for method, report in summary['aggregate'][group].items():
            available = [r for r in subset if method in r['metrics']]
            assert report == dict(pairs=len(available), ciede2000=float(np.mean([r['metrics'][method]['ciede2000_source_mask'] for r in available])))
    assert counts == dict(predictions=16, corrected_images=48, masks=72, rejected_mask_only=8)
    assert {r['pair_id'].split('__')[0] for r in summary['records'] if r['diagnostic_only']} == {'51739', '40048', '42532', '63870'}
    artifact_hashes = {str(p.relative_to(out)): digest(p) for p in out.rglob('*') if p.is_file()}
    target.write_text(json.dumps(dict(status='pass', counts=counts, input_hashes_unchanged=True,
        measurement_contract_unchanged=True, portable_predictions_unchanged=True,
        independent_rgb_replay=True, metrics_recomputed=True, rejected_sources_excluded=True,
        summary_sha256=digest(out / 'summary.json'), evidence_sha256=artifact_hashes), indent=2), encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
