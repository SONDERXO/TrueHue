"""Acquire only the four pinned base-model arrays; verify Git blob and safe load."""
import hashlib
import argparse
import io
import json
from pathlib import Path
import urllib.request
import numpy as np

ASSETS = {
    'encoderBias.npy': (43328, 'a5d0f4573af2b491f02b5b24b89ec9ddbd8e6bfc'),
    'encoderWeights.npy': (2376128, '261e2f244601e2c349bf740c3e4f0168a30fd7c3'),
    'features.npy': (13757828, '7ccc531df057af205d8283da1d7a91a80f12623a'),
    'mappingFuncs.npy': (8254748, 'cb23db295c0e78cdafcbe4a7af6b44c44a04c1f5'),
}
REV = '98340313cc7d1728e286ad9ba03e8f9a0e8b82c5'


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', type=int, default=1, choices=(1, 2))
    args = parser.parse_args()
    dest = root / f'outputs/wb_cue_base_assets_v{args.attempt}'
    if dest.exists():
        raise RuntimeError('Refuse overwrite; inspect preserved partial acquisition')
    dest.mkdir()
    records = []
    try:
        for name, (size, blob) in ASSETS.items():
            url = f'https://raw.githubusercontent.com/mahmoudnafifi/WB_sRGB/{REV}/WB_sRGB_Python/models/{name}'
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read(size + 1)
            assert len(data) == size, (name, len(data), size)
            assert hashlib.sha1(f'blob {size}\0'.encode() + data).hexdigest() == blob, name
            arr = np.load(io.BytesIO(data), allow_pickle=False)
            assert arr.dtype.kind in 'fi' and np.isfinite(arr).all(), name
            (dest / name).write_bytes(data)
            records.append({'name': name, 'bytes': size, 'git_blob': blob,
                            'sha256': hashlib.sha256(data).hexdigest(),
                            'shape': list(arr.shape), 'dtype': str(arr.dtype)})
        shape = {r['name']: r['shape'] for r in records}
        assert shape['encoderWeights.npy'][0] == 10800
        width = shape['encoderWeights.npy'][1]
        assert shape['features.npy'][1] == width
        assert shape['mappingFuncs.npy'] == [shape['features.npy'][0], 33]
        assert shape['encoderBias.npy'] in ([10800, 1], [10800], [1, 10800])
        status = 'PINNED_SAFE_ARRAY_LOAD_PASS'
    except Exception as exc:
        (dest / 'failure.json').write_text(json.dumps({'error': str(exc), 'completed': records}, indent=2), encoding='utf-8')
        raise
    receipt = {'status': status, 'revision': REV, 'assets': records,
               'total_bytes': sum(r['bytes'] for r in records), 'allow_pickle': False,
               'portrait_reads': 0, 'fits': 0, 'inference_calls': 0}
    (dest / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
