"""Independent ledger/history/count checks; no original-source or model access."""
from pathlib import Path
import hashlib
import json
import sys
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/refined_measurement_preparation_v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    target = OUT / 'independent_verification_PRIVATE.json'
    queue_path = OUT / 'labelled_queue_with_history_PRIVATE.json'
    if target.exists() or queue_path.exists():
        raise FileExistsError('Preserve previous verification')
    first = read(OUT / 'verification_PRIVATE.json')
    assert first['passed']
    for p, h in first['input_sha256'].items():
        assert sha(p) == h
    method = read(OUT / 'method.json')
    assert hashlib.sha256(json.dumps(method['method'], sort_keys=True, separators=(',', ':')).encode()).hexdigest() == method['method_sha256']
    counts = []
    rows = read(OUT / 'records_PRIVATE.json')
    for row in rows:
        assert not row['training_admitted'] and not row['calibration_admitted']
        if row['generated_fixture']:
            continue
        folder = Path(row['export'])
        report = read(folder / 'report.json')
        manual = report['manual_refinement']
        base = next(Path(p).parent for p, h in first['input_sha256'].items()
                    if Path(p).name == 'manifest.json' and h == manual['base_manifest_sha256'])
        load = lambda parent, name: cv2.imread(str(parent / name), 0) > 0
        calculated = {}
        for kind in ['correction', 'measurement']:
            before, after = load(base, kind + '_mask.png'), load(folder, kind + '_mask.png')
            calculated['added_' + kind + '_pixels'] = int((after & ~before).sum())
            calculated['removed_' + kind + '_pixels'] = int((before & ~after).sum())
        calculated['explicitly_unprotected_pixels'] = int((load(base, 'protected_mask.png') & ~load(folder, 'protected_mask.png')).sum())
        assert calculated == row['change_counts']
        assert all(manual[k] == v for k, v in calculated.items())
        original = cv2.imread(str(folder / 'photo_used.png'))
        output = cv2.imread(str(folder / 'experimental_correction.png'))
        alpha = np.load(folder / 'correction_alpha.npy', allow_pickle=False)
        assert np.array_equal(output[alpha == 0], original[alpha == 0])
        assert np.array_equal(output[load(folder, 'protected_mask.png')], original[load(folder, 'protected_mask.png')])
        assert not manual['model_reinferred'] and not manual['mst_recomputed']
        counts.append(dict(run_id=row['run_id'], counts=calculated, unchanged_outside_alpha=True, protected_unchanged=True))
    assert len([r for r in rows if not r['generated_fixture'] and r['latest_available_revision']]) == 1
    history_path = ROOT / 'outputs/native_mst_measurement_readiness_v1/results_PRIVATE.json'
    history = {r['source_case']: r for r in read(history_path)['records']}
    queue = read(OUT / 'labelled_queue_PRIVATE.json')
    for row in queue:
        source = row['source_metadata']
        old = history[source['source_case']]
        assert all(old[k] == v for k, v in source.items())
        row['historical_native_outcome'] = {k: old.get(k) for k in ['status', 'stage', 'reason', 'measurement_contract_sha256']}
    assert len(queue) == 30 and len({r['source_metadata']['subject_id'] for r in queue}) == 10
    assert sum(r['historical_native_outcome']['status'] == 'available' for r in queue) == 21
    queue_path.write_text(json.dumps(queue, indent=2), encoding='utf-8')
    inputs = {str(p): sha(p) for p in OUT.glob('*.json')}
    for p in [Path(__file__), ROOT / 'scripts/721_prepare_refined_measurements.py', history_path]:
        inputs[str(p)] = sha(p)
    target.write_text(json.dumps(dict(passed=True, checked=counts, queue_cases=30,
        historical_available=21, historical_unavailable_retained=9,
        model_calls=0, fits=0, original_source_reads=0, holdout_bytes_read=0,
        input_sha256=inputs), indent=2), encoding='utf-8')
    print('PASS: 2 real revisions, counts/output invariants, 30 queued cases including 9 unavailable')


if __name__ == '__main__':
    main()
