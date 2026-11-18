"""Replay saved generated-vector accounting without importing torch or model code."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/reiqa_frozen_generated_v1'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def main():
    target = OUT/'independent_verification_PRIVATE.json'
    if target.exists():
        raise FileExistsError(target)
    report = json.loads((OUT/'verification_PRIVATE.json').read_text())
    assert report['status'] == 'GENERATED_MECHANICS_PASS_ONLY'
    assert report['dataset_reads'] == report['correction_tree_fits'] == 0
    for name,expected in report['source_bindings'].items():
        assert digest(ROOT/name) == expected, name
    checkpoint = ROOT/'outputs/reiqa_checkpoint_pilot_v1/quality_aware_r50.pth'
    assert digest(checkpoint) == report['checkpoint_sha256']
    assert digest(OUT/'generated_features.npz') == report['generated_features_sha256']
    expected = ['identity','gamma_under','gamma_over','red','blue','combined']
    measurements = []
    with np.load(OUT/'generated_features.npz',allow_pickle=False) as saved:
        assert saved.files == expected
        reference = saved['identity'].reshape(-1).tolist()
        for row in report['records']:
            values = saved[row['case']]
            assert values.shape == (1,4096) and str(values.dtype) == 'float32'
            vector = values.reshape(-1).tolist()
            assert all(math.isfinite(v) for v in vector)
            differences = [v-r for v,r in zip(vector,reference)]
            norm = math.sqrt(math.fsum(v*v for v in differences))
            maximum = max(abs(v) for v in differences)
            # Float32 torch reduction vs independent double scalar reduction only.
            assert math.isclose(norm,row['feature_l2_change'],rel_tol=1e-6,abs_tol=1e-6)
            assert math.isclose(maximum,row['max_abs_change'],rel_tol=1e-6,abs_tol=1e-6)
            measurements.append({'case':row['case'],'scalar_l2':norm,'scalar_max_abs':maximum})
    assert report['repeat_identity_exact'] and report['weights_and_buffers_unchanged']
    assert report['independent_topology_max_abs_diff'] == 0
    result = {'status':'SAVED_VECTOR_ACCOUNTING_PASS', 'vectors':6,'finite_values':24576,
              'scope':'not independent neural execution or correction quality',
              'measurements':measurements,'verifier_sha256':digest(Path(__file__))}
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
