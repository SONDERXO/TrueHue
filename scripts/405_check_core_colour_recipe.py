"""One fixed colour/combined development check on a generated chromatic ramp."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from src.distortion_generation.core_colour_recipe import render_rgb, VERSION
from src.distortion_generation.development_roles import assign_role
from src.model_training.blended_recovery_targets import fit_target, render_rgb8

OUT = ROOT/'outputs/core_colour_recipe_v1'
PARENT = ROOT/'outputs/synthetic_development_roles_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    parent_hashes = json.loads((PARENT/'sha256.json').read_text())
    assert all(sha(PARENT/k) == v for k, v in parent_hashes.items())
    parent_protocol = json.loads((PARENT/'protocol.json').read_text())
    assert all(sha(ROOT/k) == v for k, v in parent_protocol['source_sha256'].items())
    sources = ['src/distortion_generation/core_colour_recipe.py',
        'src/distortion_generation/development_roles.py',
        'src/distortion_generation/table2_composite.py',
        'src/model_training/blended_recovery_targets.py',
        'scripts/405_check_core_colour_recipe.py', 'Thesis Proposal Document.pdf']
    protocol = dict(recipe_version=VERSION, source_sha256={k: sha(ROOT/k) for k in sources},
        parent_manifest_sha256=sha(PARENT/'sha256.json'),
        source='fixed generated chromatic RGB8 ramp: R=x,G=255-x,B=(37*x)%256;16 rows',
        application='reuse parent alpha; float transform then blend then one RGB8 round',
        casts=['cool', 'warm'], directions=['none', 'under', 'over'],
        groups=['light', 'medium', 'dark'], expected_probes=18, clean_controls=1,
        strength='k=1-abs(corresponding Table2 colour slider)/255; no sweep',
        colour='cool:red*=k; warm:blue*=k; green unchanged before exposure',
        combined='power-only exposure first, then single-channel attenuation',
        clipping_role='use forward out-of-range count, never target error to select cases',
        targets='one local three-control blended fit per nonclean case; no threshold admission',
        limitations=['attenuation also darkens','not additive Table2 equivalence',
                     'not physical/calibrated white balance','quantisation and boundary residuals retained'],
        training_admitted=False, final_distribution=None)
    OUT.mkdir()
    (OUT/'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    x = np.arange(256, dtype=np.uint8)
    reference = np.tile(np.stack([x, x[::-1], ((x.astype(int)*37)%256).astype(np.uint8)], -1)[None], (16, 1, 1))
    with np.load(PARENT/'new_generated_arrays.npz') as archive:
        alpha = archive['alpha'].copy()
    saved = reference.copy()
    arrays = dict(reference=reference, alpha=alpha)
    rows = []
    for group in protocol['groups']:
        for cast in protocol['casts']:
            for direction in protocol['directions']:
                image, recipe = render_rgb(reference, alpha, group, cast, direction)
                float_rgb = reference.astype(float)/255
                raw = np.power(float_rgb, recipe['effective_direct_exponent'])*recipe['gains']
                replay = np.rint(255*(float_rgb*(1-alpha[..., None])+raw*alpha[..., None])).astype(np.uint8)
                np.testing.assert_array_equal(image, replay)
                role = assign_role(reference, image, alpha, scenario=recipe['scenario'],
                    clipped_channel_samples=recipe['clipped_channel_samples'])
                fit = fit_target(image, reference, alpha, alpha > 0)
                key = f'{group}_{cast}_{direction}'
                arrays[key] = image
                if fit['parameters'] is not None:
                    output = render_rgb8(image, alpha, fit['parameters'])
                    assert np.array_equal(output[alpha == 0], reference[alpha == 0])
                    arrays[key+'_restored'] = output
                rows.append(dict(id=key, recipe=recipe, role=role, target_fit=fit))
    clean = fit_target(reference, reference, alpha, alpha > 0)
    clean_output = render_rgb8(reference, alpha, clean['parameters'])
    np.testing.assert_array_equal(clean_output, reference)
    arrays['clean'] = reference.copy(); arrays['clean_restored'] = clean_output
    rows.append(dict(id='clean', recipe=None, role=assign_role(reference, reference, alpha,
        scenario='clean', clipped_channel_samples=0), target_fit=clean))
    np.testing.assert_array_equal(reference, saved)
    frozen = ROOT/'outputs/correction_training_readiness_plan_v1'
    for name, prefix in [('source_hashes.json', ROOT), ('parent_manifest_hashes.json', ROOT/'outputs')]:
        for key, digest in json.loads((frozen/name).read_text()).items():
            path = prefix/key if name == 'source_hashes.json' else prefix/key/'sha256.json'
            assert sha(path) == digest
    result = dict(protocol_sha256=sha(OUT/'protocol.json'), results=rows,
        role_counts={role: sum(r['role']['role'] == role for r in rows)
            for role in sorted({r['role']['role'] for r in rows})},
        new_local_target_fits=18, clean_shortcuts=1, arithmetic_replays=18,
        parent_cases_preserved=24, parent_cases_refitted=0,
        raw_photos=0, model_inference=0, mst_fits=0, tree_fits=0, admissions=0,
        runtime_changes=0, frozen_source_hashes_verified=7, frozen_parent_hashes_verified=7,
        status='generated_candidate_diagnostic_not_prediction_or_final_training_recipe')
    (OUT/'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    with (OUT/'cases.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['id','role','target_status','input_mae_codes','restored_mae_codes'])
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(id=r['id'],role=r['role']['role'],target_status=r['target_fit']['status'],
                input_mae_codes=r['target_fit'].get('input_rgb8_mae_codes'),
                restored_mae_codes=r['target_fit'].get('rgb8_mae_codes')))
    np.savez_compressed(OUT/'generated_arrays.npz', **arrays)
    with np.load(OUT/'generated_arrays.npz') as archive:
        assert set(archive.files) == set(arrays)
        for key, value in arrays.items():
            np.testing.assert_array_equal(archive[key], value)
    assert all(sha(PARENT/k) == v for k, v in parent_hashes.items())
    assert all(sha(ROOT/k) == v for k, v in protocol['source_sha256'].items())
    (OUT/'sha256.json').write_text(json.dumps({p.name: sha(p) for p in OUT.iterdir()
        if p.is_file()}, indent=2), encoding='utf-8')
    print(json.dumps([dict(id=r['id'],error=r['target_fit'].get('rgb8_mae_codes'),
        status=r['target_fit']['status']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
