"""Allowlisted cached input-only feature preparation. No model fit/prediction."""
from pathlib import Path
import sys
import json
import hashlib
import time
import math

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.spatial_nss_features import (  # noqa: E402
    SPATIAL_NSS_FEATURES, spatial_nss_features, normalized_coefficients,
)

BASE = ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
OUT = ROOT/'outputs/spatial_input_preparation_v1'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError('Preserve prior preparation')
    rows = read(BASE/'rows_PRIVATE.json')
    names = read(ROOT/'outputs/reviewed_ffhq_restoration_design_v1/plan_PRIVATE.json')['feature_names']
    assert len(rows) == 44 and len(names) == 16
    bindings = {str(p):sha(p) for p in [BASE/'rows_PRIVATE.json', BASE/'folds_PRIVATE.json',
        ROOT/'src/model_training/spatial_nss_features.py', Path(__file__),
        ROOT/'docs/spatial-input-representation-preparation-2026-11-11.md']}
    # Preflight every allowlisted location before opening any pixel archive.
    paths = []
    for r in rows:
        assert not r['generated_fixture'] and r['status'] == 'available'
        p = Path(r['pixels_file']).resolve()
        assert p == (BASE/r['case_id']/'paired_pixels.npz').resolve()
        paths.append(p)
    records = []
    kernel = np.exp(-np.arange(-3, 4, dtype=float)**2/(2*(7/6)**2))
    kernel /= kernel.sum()
    weights = kernel[:, None]*kernel[None, :]
    independent_error = 0.
    OUT.mkdir()
    for r, p in zip(rows, paths):
        assert sha(p) == r['pixels_sha256']
        with np.load(p, allow_pickle=False) as z:
            image = z['input_rgb8']
        assert image.shape == (256, 256, 3) and image.dtype == np.uint8
        start = time.perf_counter()
        features, statuses = spatial_nss_features(image)
        seconds = time.perf_counter()-start
        # Independent scalar Gaussian-window replay at boundary and interior.
        y = image.astype(float) @ np.array([.299, .587, .114])
        padded = np.pad(y, 3, mode='reflect')
        coeff = normalized_coefficients(y)
        for i, j in [(0, 0), (128, 128), (255, 255)]:
            window = padded[i:i+7, j:j+7]
            mean = float(np.sum(weights*window))
            variance = float(np.sum(weights*(window-mean)**2))
            expected = (y[i, j]-mean)/(math.sqrt(variance)+1)
            independent_error = max(independent_error, abs(expected-coeff[i, j]))
        values = np.array(list(features.values()), dtype=np.float32).tolist()
        records.append(dict(case_id=r['case_id'], publisher_group=r['publisher_group'],
            experimental_role=r['experimental_role'], generated_fixture=False,
            old_input_vector_float32=r['input_vector_float32'],
            spatial_features=features, input_vector_float32=r['input_vector_float32']+values,
            nominal_controls=r['nominal_controls'], distribution_status=statuses,
            source_archive=str(p), source_archive_sha256=r['pixels_sha256'],
            input_array_sha256=hashlib.sha256(image.tobytes()).hexdigest(), seconds=seconds,
            training_admitted=False))
    assert independent_error < 1e-9
    assert all(v['input_vector_float32'][:16] == r['input_vector_float32'] and
               v['nominal_controls'] == r['nominal_controls'] and
               np.isfinite(v['input_vector_float32']).all() for v, r in zip(records, rows))
    responses = []
    for g in sorted({r['publisher_group'] for r in records}):
        own = [r for r in records if r['publisher_group'] == g]
        normal = next(r for r in own if r['experimental_role'] == 'identity')
        for r in own:
            if r['experimental_role'] != 'identity':
                responses.append(dict(group=g, role=r['experimental_role'],
                    changed_float32_coordinates=sum(a != b for a, b in zip(
                        r['input_vector_float32'][16:], normal['input_vector_float32'][16:]))))
    summary = dict(available=44, attempted_available=44, source_groups=11,
        old_feature_count=16, added_feature_count=36, total_feature_count=52,
        generated_fixtures=0, unchanged_prefixes=44, unchanged_targets=44,
        cached_input_arrays_read=44, original_photo_reads=0, reference_arrays_loaded=0,
        holdout_reads=0, fits=0, new_correction_predictions=0,
        max_seconds=max(r['seconds'] for r in records),
        max_independent_coefficient_error=independent_error,
        non_two_sided_product_distributions=sum(s['status'] != 'two_sided' for r in records for s in r['distribution_status']),
        saturated_shape_coordinates=sum(v in [.2, 10.] for r in records for k, v in r['spatial_features'].items() if k.endswith('shape')),
        minimum_changed_derivative_coordinates=min(r['changed_float32_coordinates'] for r in responses),
        source_folds_unchanged=True, improvement_claim=False)
    for name, data in [('rows', records), ('summary', summary), ('responses', responses),
        ('feature_names', names+list(SPATIAL_NSS_FEATURES)), ('input_sha256', bindings)]:
        (OUT/(name+'_PRIVATE.json')).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n',encoding='utf-8')
    assert all(sha(Path(p)) == h for p, h in bindings.items())
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
