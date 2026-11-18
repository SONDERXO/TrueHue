"""Assess the eight fixed PPR pairs from saved metadata; no image/model reads."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'outputs/ppr10k_new_group_comparison_v1'
OUT = ROOT / 'outputs/ppr10k_saved_readiness_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing or partial assessment')
    inputs = {}
    expected = json.loads((PARENT / 'sha256.json').read_text())
    manifest_path = PARENT / 'sha256.json'
    inputs[str(manifest_path.relative_to(ROOT))] = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    def read(name):
        p = PARENT / name
        raw = p.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == expected[name], (name, 'historical manifest mismatch')
        inputs[str(p.relative_to(ROOT))] = digest
        return json.loads(raw)

    sample = read('frozen_sample.json')
    audit = read('image_audit.json')
    results = read('results.json')
    regions = read('source_regions.json')
    verification = read('verification.json')
    protocol = read('fit_protocol.json')
    assert protocol['plan_sha256'] == inputs[str((PARENT/'frozen_sample.json').relative_to(ROOT))]
    assert protocol['regions_sha256'] == inputs[str((PARENT/'source_regions.json').relative_to(ROOT))]
    frames = sample['frames']
    assert len(frames) == len(set(frames)) == 8
    assert all(int(g) < 1356 for g in sample['groups'])
    assert set(regions) == set(frames)
    by_frame = {r['frame']: r for r in results['results']}
    assert set(by_frame) == set(frames)
    av = {(r['frame'], r['role']): r for r in audit}
    assert len(av) == 16
    checks = {r['frame']: r for r in verification['checks']}
    assert set(checks) == set(frames)
    assert verification['original_tiff_hashes_and_profiles'] == 16
    rows = []
    for frame in frames:
        source, target = (av[(frame, role)] for role in ['source', 'target_a'])
        assert source['shape'] == target['shape']
        assert source['dtype'] == 'uint16' and target['dtype'] == 'uint8'
        assert source['icc_sha256'] == target['icc_sha256']
        paths = []
        for a in [source, target]:
            assert a['sha256'] == expected[a['file']]
            p = PARENT / a['file']
            assert p.is_file() and p.stat().st_size > 0
            paths.append(dict(path=str(p.relative_to(ROOT)), bytes=p.stat().st_size,
                historical_sha256=a['sha256'], current_image_bytes_checked=False))
        assert all(checks[frame][n] for n in ['two_independent_exact_formula_replays',
                     'metrics_and_clipping_match', 'masks_match'])
        r = by_frame[frame]
        assert r['status'] == 'completed'
        assert r['fit_pixels'] + r['check_pixels'] == r['pixels']
        assert all(r['clipping'][k]['total'] == 3*r['pixels'] for k in ['three', 'four'])
        assert all(r['solvers'][k]['success'] for k in ['three', 'four'])
        for k in ['three', 'four']:
            assert math.isfinite(r['metrics'][k]['check']['de00_mean'])
        rows.append(dict(frame=frame, publisher_group=frame.split('_')[0],
            source_observation=r['source_observation'], original_files=paths,
            shape=source['shape'], source_dtype=source['dtype'], target_dtype=target['dtype'],
            embedded_profile='matching saved ICC hashes; historical sRGB verification reused',
            dimensions='pass_saved_metadata', registration='unverified',
            automatic_selected_face='not_established_by_saved_diagnostic',
            automatic_skin_measurement='not_established',
            automatic_face_neck_support='not_established',
            calibrated_mst_compatibility='not_established; no supplied MST labels',
            person_independence='unknown; publisher group is not identity',
            photographic_reference='editor_a; aesthetic target, not intrinsic colour',
            historical_polygon_pixels=r['pixels'],
            three_control_check_de00=r['metrics']['three']['check']['de00_mean'],
            four_control_check_de00=r['metrics']['four']['check']['de00_mean'],
            three_control_clipped_samples=r['clipping']['three']['samples'],
            four_control_clipped_samples=r['clipping']['four']['samples'],
            polygon_channel_samples=3*r['pixels'],
            unchanged_check_de00='not_present_in_saved_eight_pair_results',
            target_representability='approximation_only; no predeclared acceptability threshold',
            training_ready=False, final_evaluation_eligible=False))
    means = {k:sum(r[f'{k}_control_check_de00'] for r in rows)/8 for k in ['three','four']}
    assert all(abs(means[k]-results['summary']['mean_check_de00'][k]) < 1e-12 for k in means)
    assert sum(r['four_control_clipped_samples'] > r['three_control_clipped_samples'] for r in rows) == results['summary']['increased_clipping']
    # Independently join audit rows and scalar aggregate, retaining original order.
    assert [r['frame'] for r in rows] == frames
    for r in rows:
        raw = next(x for x in results['results'] if x['frame'] == r['frame'])
        assert r['three_control_check_de00'] == raw['metrics']['three']['check']['de00_mean']
        assert len([a for a in audit if a['frame'] == r['frame']]) == 2
    script = Path(__file__).resolve()
    inputs[str(script.relative_to(ROOT))] = hashlib.sha256(script.read_bytes()).hexdigest()
    for rel, h in inputs.items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == h
    summary = dict(attempted_pairs=8, retained_pairs=8, saved_dimension_matches=8,
        historical_profile_checks=16, newly_image_verified=0, historical_metadata_hashes_verified=6,
        training_ready=0, readiness_unresolved=8, rejected_as_photographs=0,
        mean_check_de00=means, increased_clipping_with_four_controls=6,
        independent_metadata_replay=True, image_byte_reads=0, new_forwards=0,
        new_fits=0, holdout_reads=0, criterion_changes=0,
        disposition='No training admission; prepare fixed automatic-support/correspondence feasibility protocol, not model training.')
    OUT.mkdir()
    (OUT/'readiness_PRIVATE.json').write_text(json.dumps(dict(summary=summary, rows=rows,
        input_sha256=inputs, original_manifest_sha256=inputs[str(manifest_path.relative_to(ROOT))]),
        indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
