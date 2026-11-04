"""Bounded generated-ramp diagnostic for the authorised formula revision."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.correction.seamless_blend import inward_alpha
from src.distortion_generation.directional_exposure_recipe import render_rgb
from src.model_training.blended_recovery_targets import fit_target, render_rgb8

OUT = ROOT / 'outputs/directional_exposure_recipe_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    reference = np.tile(np.arange(256, dtype=np.uint8)[None, :, None], (16, 1, 3))
    mask = np.full((16, 256), 255, np.uint8)
    mask[:, :4] = 0; mask[:, -4:] = 0
    alpha, _ = inward_alpha(mask, face_width=80)
    score = alpha > 0
    saved = reference.copy()
    arrays = dict(reference=reference, alpha=alpha)
    rows = []
    scenarios = [('clean', 'none'), ('color', 'none'), ('exposure', 'under'),
                 ('exposure', 'over'), ('combined', 'under'), ('combined', 'over')]
    for group in ('light', 'medium', 'dark'):
        for variant, direction in scenarios:
            image, report = render_rgb(reference, alpha, group, variant, direction)
            fit = fit_target(image, reference, alpha, score)
            assert fit['parameters'] is not None
            restored = render_rgb8(image, alpha, fit['parameters'])
            assert np.array_equal(image[~score], reference[~score])
            assert np.array_equal(restored[~score], reference[~score])
            if variant == 'clean':
                assert np.array_equal(restored, reference)
            key = f'{group}_{variant}_{direction}'
            arrays[key] = image; arrays[key+'_restored'] = restored
            rows.append(dict(id=key, recipe=report, target_fit=fit))
    direction_checks = []
    for direction in ('under', 'over'):
        values = [arrays[f'{g}_exposure_{direction}'].astype(int)
                  for g in ('light', 'medium', 'dark')]
        sign = 1 if direction == 'under' else -1
        assert np.all(sign*(values[0]-reference.astype(int)) <= 0)
        assert np.all(sign*(values[1]-values[0]) <= 0)
        assert np.all(sign*(values[2]-values[1]) <= 0)
        direction_checks.append(dict(direction=direction, ordered_on_generated_pixels=True))
    assert np.array_equal(reference, saved)
    frozen = ROOT/'outputs/correction_training_readiness_plan_v1'
    old_sources = json.loads((frozen/'source_hashes.json').read_text())
    old_parents = json.loads((frozen/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/k) == v for k, v in old_sources.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json') == v for k, v in old_parents.items())
    sources = ['src/distortion_generation/directional_exposure_recipe.py',
               'src/distortion_generation/table2_composite.py',
               'src/model_training/blended_recovery_targets.py',
               'scripts/403_check_directional_exposure_recipe.py',
               'Thesis Proposal Document.pdf']
    result = dict(status='experimental_development_formula_not_training_or_panel_adoption',
        source_sha256={p: sha(ROOT/p) for p in sources},
        source='generated neutral RGB8 ramp, not actual skin or labelled subjects',
        scenarios=scenarios, scoring='all positive-alpha pixels including fractional edges',
        local_target_fits=15, clean_shortcuts=3, photos=0, tree_fits=0, mst_fits=0,
        admissions=0, runtime_changes=0, frozen_sources_verified=len(old_sources),
        frozen_parent_manifest_hashes_verified=len(old_parents),
        direction_checks=direction_checks, results=rows)
    OUT.mkdir()
    np.savez_compressed(OUT/'generated_arrays.npz', **arrays)
    (OUT/'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    # Persisted-array roundtrip, not statistical validation.
    with np.load(OUT/'generated_arrays.npz') as archive:
        assert set(archive.files) == set(arrays)
        for key, value in arrays.items():
            np.testing.assert_array_equal(archive[key], value)
    (OUT/'sha256.json').write_text(json.dumps({p.name: sha(p) for p in OUT.iterdir()
        if p.is_file()}, indent=2), encoding='utf-8')
    print(json.dumps([dict(id=r['id'], error=r['target_fit']['rgb8_mae_codes'],
        clipped=r['recipe']['clipped_channel_samples']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
