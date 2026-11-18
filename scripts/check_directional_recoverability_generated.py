"""Generated-only 11-source/66-role engineering rehearsal. No real plan loader call."""
from pathlib import Path
import sys
import json
import hashlib
import math
import platform
import importlib.metadata
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.evaluation import directional_recoverability as flow
from src.evaluation import directional_recoverability_scalar as scalar
from src.evaluation.directional_recoverability_loading import load_sources
from src.model_training import blended_recovery_targets as targets


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if sys.argv[1:] != ['--generated-only']:
        raise SystemExit('Explicit --generated-only required')
    out = ROOT / 'outputs/directional_recoverability_engineering_v1'
    if out.exists():
        raise FileExistsError('Preserve completed or partial engineering run')
    dependencies = ['src/evaluation/directional_recoverability.py',
        'src/evaluation/directional_recoverability_scalar.py',
        'src/evaluation/directional_recoverability_loading.py',
        'src/distortion_generation/directional_exposure_recipe.py',
        'src/distortion_generation/table2_composite.py',
        'src/distortion_generation/paper_gamma.py',
        'src/model_training/blended_recovery_targets.py',
        'scripts/check_directional_recoverability_generated.py',
        'tests/test_directional_recoverability.py',
        'docs/ffhq-directional-recoverability-protocol-2026-11-14.md',
        'outputs/ffhq_directional_recoverability_design_v1/plan_PRIVATE.json']
    bindings = {p: sha(ROOT / p) for p in dependencies}
    design = json.loads((ROOT / dependencies[-1]).read_text(encoding='utf-8'))
    assert design['conditions'] == 66 and design['maximum_local_target_optimizations'] == 55
    for p, digest in design['input_sha256'].items():
        assert sha(ROOT / p) == digest
    out.mkdir()
    versions = {'Python': platform.python_version(), **{p: importlib.metadata.version(p)
                for p in ['numpy', 'scipy', 'scikit-image', 'opencv-python']}}
    flow.write(out/'execution_plan_PRIVATE.json', {'scope': 'generated_only',
               'code_design_sha256': bindings, 'versions': versions})
    refs, supports = [], []
    for index in range(11):
        folder = out / 'inputs' / f'generated_{index:02}'
        folder.mkdir(parents=True)
        image = np.random.default_rng(704 + index).integers(0, 256, (12, 12, 3), dtype=np.uint8)
        image[3, 3] = 0
        image[4, 4] = 255
        alpha = np.ones((12, 12), float)
        alpha[[0, -1], :] = 0
        alpha[:, [0, -1]] = 0
        alpha[1, 1:-1] = .25
        alpha[-2, 1:-1] = .75
        protected = np.zeros((12, 12), np.uint8)
        protected[5, 5] = 255
        alpha[protected > 0] = 0
        # Poison member cannot be decoded with allow_pickle=False; only input_rgb8 is allowed.
        np.savez(folder/'identity.npz', input_rgb8=image, forbidden=np.array([object()], dtype=object))
        np.save(folder/'alpha.npy', alpha)
        assert cv2.imwrite(str(folder/'protected_mask.png'), protected)
        flow.write(folder/'receipt.json', {'generated_fixture': True, 'source_id': folder.name})
        refs.append(dict(source_id=folder.name, identity_container=str(folder/'identity.npz'),
                         identity_sha256=sha(folder/'identity.npz'), allowed_key='input_rgb8', official_tone_label=None))
        supports.append(dict(source_id=folder.name, selected=dict(directory=str(folder),
            receipt='receipt.json', receipt_sha256=sha(folder/'receipt.json'), alpha_filename='alpha.npy',
            files={n:sha(folder/n) for n in ['alpha.npy','protected_mask.png']})))
    plan = dict(source_references=refs, support_sources=supports)
    flow.write(out/'generated_source_plan_PRIVATE.json', plan)
    sources = load_sources(ROOT, plan, generated_fixture=True)
    calls = []
    original_solver = targets.least_squares
    def counted(fun, start, **kwargs):
        np.testing.assert_array_equal(start, [1, 1, 1])
        np.testing.assert_array_equal(kwargs['bounds'], [[.25]*3, [4.]*3])
        assert kwargs['max_nfev'] == 500 and kwargs['method'] == 'trf' and kwargs['loss'] == 'linear'
        assert kwargs['ftol'] == kwargs['xtol'] == kwargs['gtol'] == 1e-10
        calls.append(True)
        return original_solver(fun, start, **kwargs)
    targets.least_squares = counted
    try:
        records = flow.execute_sources(sources, out/'generated_run')
    finally:
        targets.least_squares = original_solver
    assert len(records) == 66 and len(calls) == 55
    counts = {}
    for source in sources:
        folder = out/'generated_run'/source['source_id']
        for role in flow.ROLES:
            record = json.loads((folder/(role+'.json')).read_text(encoding='utf-8'))
            with np.load(folder/(role+'.npz'), allow_pickle=False) as pack:
                image = pack['input']
                output = pack['output'] if 'output' in pack.files else None
            assert scalar.verify(source, record, image, output)
            counts[role] = counts.get(role, 0) + 1
    assert set(counts.values()) == {11}
    summary = json.loads((out/'generated_run/summary.json').read_text(encoding='utf-8'))
    for role in flow.ROLES:
        own = [r for r in records if r['role'] == role]
        paired = [r for r in own if r['regions']['primary']['output'] is not None]
        assert summary[role]['attempted'] == 11 and summary[role]['available'] == len(paired)
        for prefix in ('input','output','benefit'):
            for metric in ('RGB','DE'):
                expected = math.fsum(r['regions']['primary'][prefix][metric] for r in paired) / len(paired)
                assert math.isclose(expected, summary[role]['primary'][prefix][metric], abs_tol=1e-10)
    assert all(sha(ROOT/p) == digest for p,digest in bindings.items())
    artifact_hashes = {str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
    flow.write(out/'verification_PRIVATE.json', dict(passed=True, scope='generated_engineering_only',
        source_count=11, records=66, actual_generated_local_solver_calls=55,
        independent_formula_render_objective_metric_checks=66,
        role_counts=counts, poison_other_npz_members_not_decoded=True,
        independent_source_equal_summaries=True, versions=versions, input_sha256=bindings,
        artifact_sha256=artifact_hashes, real_dataset_arrays=0, real_target_fits=0,
        correction_tree_fits=0, real_model_quality_established=False,
        real_execution_output_created=False, locked_content_or_manifest_access=False))
    print('PASS: generated11sources/66cases/55solver calls; scalar replay, metrics and summaries verified.')


if __name__ == '__main__':
    main()
