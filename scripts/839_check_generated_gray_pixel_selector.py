"""Full fixed GP-inspired descriptor on generated scenes only. No photos/fits."""
from pathlib import Path
import sys
import json
import hashlib
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.gray_pixel_context import gray_pixel_context  # noqa: E402

OUT = ROOT/'outputs/gray_pixel_selector_engineering_v1'


def main():
    dest = OUT/'generated_results_PRIVATE.json'
    if dest.exists():
        raise FileExistsError('Preserve generated results')
    y, x = np.indices((64, 64))
    texture = (24+(7*x+11*y)%48).astype(float)
    neutral = np.repeat(texture[:, :, None]*2, 3, axis=2)
    coloured = texture[:, :, None]*np.array([3., 2., 1.])
    mixed = coloured.copy();mixed[:, 32:] = neutral[:, 32:]
    scenes = [('neutral', neutral, np.ones((64, 64), bool)),
              ('coloured', coloured, np.zeros((64, 64), bool)),
              ('mixed', mixed, x >= 32)]
    records = [];arrays = {};geometry = {}
    for scene, base, material_neutral in scenes:
        for role, gamma, red in [('identity', 1., 1.), ('exposure_under', 1/.7, 1.),
                                  ('exposure_over', .7, 1.), ('colour_cool', 1., 245/255)]:
            continuous = (base/255)**gamma*np.array([red, 1., 1.])
            assert continuous.min() > 0 and continuous.max() < 1
            image = np.rint(255*continuous).astype(np.uint8)
            start = time.perf_counter();result = gray_pixel_context(image);elapsed = time.perf_counter()-start
            selected = result['selected_flat_indices']
            neutral_count = int(material_neutral.ravel()[selected].sum())
            key = scene+'__'+role;arrays[key] = image
            geometry[key] = dict(base_material_neutral_pixels=int(material_neutral.sum()),
                                  selected_generated_neutral_material=neutral_count,
                                  selected_generated_coloured_material=len(selected)-neutral_count)
            records.append(dict(fixture_id=key, generated_fixture=True, scene=scene,
                role=role, forward_gamma=gamma, forward_red=red,
                forward_float_clipped_channels=0,
                quantization_max_code_error=float(np.max(np.abs(image-255*continuous))),
                seconds=elapsed, input_array_sha256=hashlib.sha256(image.tobytes()).hexdigest(),
                **geometry[key], **result))
    # Separate generated storage; no source IDs, scientific row schemas or annotations.
    np.savez_compressed(OUT/'generated_fixtures_ONLY.npz', **arrays)
    pairs = []
    for scene, _, _ in scenes:
        own = [r for r in records if r['scene'] == scene]
        base = next(r for r in own if r['role'] == 'identity')
        for r in own:
            if r['role'] != 'identity':
                pairs.append(dict(scene=scene, role=r['role'],
                    selected_locations_changed=r['selected_flat_indices'] != base['selected_flat_indices'],
                    descriptor_change=[r['features'][k]-base['features'][k] for k in base['features']]))
    report = dict(generated_only=True, generated_conditions=12, scientific_rows=0,
        all_available=all(r['available'] for r in records),
        coloured_material_selected_conditions=sum(r['selected_generated_coloured_material'] > 0 for r in records),
        mixed_coloured_material_selected_conditions=sum(r['scene']=='mixed' and r['selected_generated_coloured_material'] > 0 for r in records),
        selected_locations_changed_pairs=sum(r['selected_locations_changed'] for r in pairs),
        max_seconds=max(r['seconds'] for r in records),
        cached_photo_reads=0, original_photo_reads=0, holdout_reads=0, fits=0,
        new_correction_predictions=0, pairs=pairs, records=records)
    dest.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    bound = [Path(__file__), ROOT/'src/model_training/gray_pixel_context.py',
        ROOT/'tests/test_gray_pixel_context.py', ROOT/'docs/gray-pixel-selector-protocol-2026-11-12.md',
        OUT/'source_paper.pdf', OUT/'generated_fixtures_ONLY.npz']
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in bound},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','pairs']},indent=2))
    for r in records:
        print(r['fixture_id'], r['features'], 'selected',r['selected_flat_indices'], 'neutral_material',r['selected_generated_neutral_material'])


if __name__ == '__main__':
    main()
