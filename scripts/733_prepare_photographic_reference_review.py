"""New reference-style readiness package from exact cached eight-pair previews."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.labelled_measurement import digest, write, seal, verify

OUT = ROOT / 'outputs/photographic_reference_review_v1'
SOURCE = ROOT / 'outputs/ppr10k_native_pipeline_diagnostic_v1'
TARGET = ROOT / 'outputs/ppr10k_expert_control_readiness_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing or partial review package')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    bound = {}
    def metadata(p):
        bound[str(p)] = digest(p)
        return read(p)
    source = metadata(SOURCE / 'results_PRIVATE.json')
    target = metadata(TARGET / 'results_PRIVATE.json')
    sv = metadata(SOURCE / 'verification_PRIVATE.json')
    tv = metadata(TARGET / 'verification_PRIVATE.json')
    assert sv['passed'] and tv['passed']
    assert sv['results_sha256'] == digest(SOURCE / 'results_PRIVATE.json')
    assert tv['results_sha256'] == digest(TARGET / 'results_PRIVATE.json')
    inventories = {}
    for parent, receipt in [(SOURCE, sv), (TARGET, tv)]:
        p = parent / 'artifact_sha256_PRIVATE.json'
        assert digest(p) == receipt['artifact_manifest_sha256']
        inventories[parent] = {k.replace('\\', '/'): v for k, v in metadata(p).items()}
    contract = metadata(ROOT / 'outputs/photographic_tree_contract_audit_v1/audit_PRIVATE.json')
    refined = metadata(ROOT / 'outputs/refined_mst_assessment_v1/results_PRIVATE.json')
    refined_verify = metadata(ROOT / 'outputs/refined_mst_assessment_v1/verification_PRIVATE.json')
    assert refined_verify['passed'] and not refined['calibration_admitted']
    lookup = {r['frame']: r for r in target['records']}
    assert len(source['records']) == len(lookup) == 8
    # Verify only explicitly named cached previews, never metadata source paths.
    cached = {}
    for s in source['records']:
        frame = s['frame']
        for role, parent, name in [('source', SOURCE, 'source_rgb8.png'), ('target', TARGET, 'target_rgb8.png')]:
            rel = frame + '/' + name
            p = parent / rel
            assert digest(p) == inventories[parent][rel]
            bound[str(p)] = digest(p)
            cached[(frame, role)] = p
    for p in [Path(__file__), ROOT / 'docs/photographic-reference-continuation-protocol-2026-11-10.md']:
        bound[str(p)] = digest(p)
    OUT.mkdir()
    tasks = []
    ledger = []
    for s in source['records']:
        frame = s['frame']
        t = lookup[frame]
        correct = s['historical_face_match'] and t['status'] == 'available'
        folder = OUT / frame
        folder.mkdir()
        a, b = [cv2.imread(str(cached[(frame, role)])) for role in ['source', 'target']]
        assert a.shape == b.shape
        scale = min(360/a.shape[1], 440/a.shape[0])
        size = (round(a.shape[1]*scale), round(a.shape[0]*scale))
        display = []
        for role, image in [('source', a), ('target', b)]:
            panel = np.full((440, 360, 3), 45, np.uint8)
            thumb = cv2.resize(image, size, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
            x, y = (360-size[0])//2, (440-size[1])//2
            panel[y:y+size[1], x:x+size[0]] = thumb
            assert cv2.imwrite(str(folder / (role + '.png')), panel)
            display.append(panel)
        issue = 'wrong-person source / unavailable intended target' if not correct else (
            'fragmented profile source: 44 native correction pixels' if frame == '1188_0' else 'support and reference review pending')
        task = dict(frame=frame, publisher_group=frame.split('_')[0],
            source_preview_sha256=digest(cached[(frame, 'source')]),
            target_preview_sha256=digest(cached[(frame, 'target')]),
            source_shape=list(a.shape), display_shape=[440, 360], common_display_scale=scale,
            correct_person_pair=bool(correct), historical_issue=issue,
            source_native_measurement_pixels=s.get('measurement_native_pixels'),
            source_native_correction_pixels=s.get('correction_native_pixels'),
            target_appearance_review='pending', measurement_support_review='pending',
            correction_support_review='pending', registration_verified=False,
            calibration_admitted=False, training_admitted=False)
        write(folder / 'task.json', task)
        seal(folder)
        verify(folder)
        tasks.append(dict(frame=frame, folder=frame, manifest_sha256=digest(folder / 'manifest.json'), issue=issue))
        for role, record in [('photographic_source', s), ('expert_identity_candidate', t)]:
            ledger.append(dict(frame=frame, publisher_group=task['publisher_group'], role=role,
                technical_measurement_available=record['status'] == 'available',
                correct_person_pair=bool(correct), human_measurement_review=False,
                human_correction_support_review=False, target_appearance_accepted=False,
                compatible_mst_artifact=None, native_manual_calibration_transfer='not_established',
                complete_qualified_16features=False, registration_verified=False,
                current_operator_targets_available=False, identity_role_proposed=role == 'expert_identity_candidate',
                training_admitted=False, failure_reason=issue))
        header = np.full((35, 720, 3), 255, np.uint8)
        cv2.putText(header, frame + ' | original source / editor-A reference', (8, 23), cv2.FONT_HERSHEY_SIMPLEX, .55, (0, 0, 0), 1)
        assert cv2.imwrite(str(OUT / (frame + '_pair.png')), np.vstack([header, np.hstack(display)]))
    assert all(digest(p) == h for p, h in bound.items())
    write(OUT / 'queue.json', dict(schema_version='truehue_photographic_reference_review_v1', tasks=tasks))
    write(OUT / 'readiness_PRIVATE.json', dict(roles=ledger, total_pairs=8, total_roles=16,
        qualified_vectors=0, technical_raw_four=sum(r['technical_measurement_available'] for r in ledger),
        correct_person_pairs=sum(t['correct_person_pair'] for t in [read(OUT/r['folder']/'task.json') for r in tasks]),
        refinement_change='30 labelled manual calibration cases reviewed; no PPR supports reviewed',
        previous_feature_names=contract['feature_names'], selected_intervention='photographic_supervision_only_if_qualified',
        disposition='no_new_fit_reference_style_and_support_contract_needed', calibration_fits=0, correction_tree_fits=0,
        original_source_image_reads=0, cached_preview_reads=16, model_calls=0, holdout_bytes_read=0,
        input_sha256=bound))
    print('Prepared eight source/editor-A pairs; 16 roles retained, 7 correct-person pairs, 0 training admissions.')


if __name__ == '__main__':
    main()
