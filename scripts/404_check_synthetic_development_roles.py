"""Freeze and check core/stress/clean separation; generated arrays only."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.distortion_generation.development_roles import core_exposure, assign_role, VERSION
from src.model_training.blended_recovery_targets import fit_target, render_rgb8

OUT = ROOT/'outputs/synthetic_development_roles_v1'
PARENT = ROOT/'outputs/directional_exposure_recipe_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    parent_hashes = json.loads((PARENT/'sha256.json').read_text())
    assert all(sha(PARENT/k) == v for k, v in parent_hashes.items())
    parent = json.loads((PARENT/'results.json').read_text())
    assert all(sha(ROOT/k) == v for k, v in parent['source_sha256'].items())
    sources = ['src/distortion_generation/development_roles.py',
               'src/model_training/blended_recovery_targets.py',
               'src/distortion_generation/table2_composite.py',
               'scripts/404_check_synthetic_development_roles.py']
    protocol = dict(version=VERSION, source_sha256={k: sha(ROOT/k) for k in sources},
        parent_manifest_sha256=sha(PARENT/'sha256.json'),
        fixed_parent_cases=18, fixed_new_cases=6,
        core='power-only exposure, direct exponents 1/g under and g over; no offset/contrast/colour',
        groups=['light', 'medium', 'dark'], directions=['under', 'over'],
        source='reuse saved generated neutral ramp and alpha, not skin/tone-labelled photos',
        role_rules=['outside change => invalid_support',
                    'clean requires bit-identical image and zero forward clipping',
                    'positive forward clipping => clipping_stress, retained',
                    'nonclean unchanged => unchanged_distortion',
                    'otherwise => core_candidate, not proof of recoverability'],
        clipping='operator-reported preblend out-of-range count; RGB8 endpoints alone are not clipping evidence',
        selection='no role uses target-fit residual; no automatic training admission or exclusion/refit',
        evaluation='report every case; clean changes, core residuals and stress failures separately',
        training_distribution=None, quality_threshold=None,
        remaining='normal colour/combined policy, real data/support/identity/MST/evaluation admission unresolved')
    OUT.mkdir()
    (OUT/'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    rows = []
    arrays = {}
    with np.load(PARENT/'generated_arrays.npz') as archive:
        reference = archive['reference'].copy(); alpha = archive['alpha'].copy()
        arrays.update(reference=reference, alpha=alpha)
        for item in parent['results']:
            recipe = item['recipe']; image = archive[item['id']]
            role = assign_role(reference, image, alpha, scenario=recipe['variant'],
                               clipped_channel_samples=recipe['clipped_channel_samples'])
            rows.append(dict(id=item['id'], origin='saved_parent_not_refitted', role=role,
                target_fit=item['target_fit'], recipe=recipe))
    for group in protocol['groups']:
        for direction in protocol['directions']:
            image, recipe = core_exposure(reference, alpha, group, direction)
            # Independent arithmetic replay, including final RGB8 quantisation.
            x = reference.astype(float)/255
            raw = np.power(x, recipe['effective_direct_exponent'])
            replay = np.rint(255*(x*(1-alpha[..., None])+raw*alpha[..., None])).astype(np.uint8)
            np.testing.assert_array_equal(image, replay)
            role = assign_role(reference, image, alpha, scenario='exposure',
                               clipped_channel_samples=recipe['clipped_channel_samples'])
            target = fit_target(image, reference, alpha, alpha > 0)
            key = f'core_{group}_{direction}'
            arrays[key] = image
            if target['parameters'] is not None:
                restored = render_rgb8(image, alpha, target['parameters'])
                assert np.array_equal(restored[alpha == 0], reference[alpha == 0])
                arrays[key+'_restored'] = restored
            rows.append(dict(id=key, origin='new_fixed_generated_probe', role=role,
                             recipe=recipe, target_fit=target))
    counts = {role: sum(row['role']['role'] == role for row in rows)
              for role in sorted({row['role']['role'] for row in rows})}
    frozen = ROOT/'outputs/correction_training_readiness_plan_v1'
    frozen_sources = json.loads((frozen/'source_hashes.json').read_text())
    frozen_parents = json.loads((frozen/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/k) == v for k, v in frozen_sources.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json') == v for k, v in frozen_parents.items())
    assert all(sha(PARENT/k) == v for k, v in parent_hashes.items())
    result = dict(protocol_sha256=sha(OUT/'protocol.json'), roles=counts, results=rows,
        new_target_fits=6, saved_parent_cases_reused=18, core_arithmetic_replays=6,
        raw_photos=0, model_inference=0, mst_fits=0, tree_fits=0, admissions=0,
        runtime_changes=0, frozen_sources_verified=7, frozen_parent_hashes_verified=7,
        status='development_separation_only_not_final_training_distribution')
    (OUT/'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    with (OUT/'cases.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['id', 'origin', 'role', 'clipped_channels',
            'target_status', 'input_mae_codes', 'restored_mae_codes'])
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(id=row['id'], origin=row['origin'], role=row['role']['role'],
                clipped_channels=row['role']['clipped_channel_samples'],
                target_status=row['target_fit']['status'],
                input_mae_codes=row['target_fit'].get('input_rgb8_mae_codes'),
                restored_mae_codes=row['target_fit'].get('rgb8_mae_codes')))
    np.savez_compressed(OUT/'new_generated_arrays.npz', **arrays)
    with np.load(OUT/'new_generated_arrays.npz') as archive:
        assert set(archive.files) == set(arrays)
        for key, value in arrays.items():
            np.testing.assert_array_equal(archive[key], value)
    with (OUT/'cases.csv').open(newline='', encoding='utf-8') as stream:
        assert [r['id'] for r in csv.DictReader(stream)] == [r['id'] for r in rows]
    assert all(sha(ROOT/k) == v for k, v in protocol['source_sha256'].items())
    (OUT/'sha256.json').write_text(json.dumps({p.name: sha(p) for p in OUT.iterdir()
        if p.is_file()}, indent=2), encoding='utf-8')
    print(json.dumps(dict(roles=counts, new_core=[dict(id=r['id'],
        error=r['target_fit'].get('rgb8_mae_codes'),
        quantised_new_endpoints=r['recipe']['new_endpoint_channel_samples'])
        for r in rows if r['origin'] == 'new_fixed_generated_probe']), indent=2))


if __name__ == '__main__':
    main()
