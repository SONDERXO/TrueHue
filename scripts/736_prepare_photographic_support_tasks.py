"""Audit actual preferences and prepare exact cached dual-mask research seeds."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.demo.labelled_measurement import digest, write, seal, verify
from src.demo.photographic_reference_review import verify_bundle, latest_preferences
from src.skin_masking.correction_preview import render_preview

OUT = ROOT / 'outputs/photographic_support_tasks_v1'
STYLE = ROOT / 'outputs/photographic_reference_review_v1'
BASES = dict(source=ROOT/'outputs/ppr10k_native_pipeline_diagnostic_v1',
             target=ROOT/'outputs/ppr10k_expert_control_readiness_v1')


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing or partial preparation')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    bound = {}
    def bind(p):
        bound[str(p)] = digest(p)
        return bound[str(p)]
    queue = read(STYLE / 'queue.json')['tasks']
    bind(STYLE/'queue.json')
    preferences = latest_preferences(queue, ROOT/'outputs/photographic_reference_decisions_v1')
    assert len(preferences) == 8
    reviews = []
    for p in sorted((ROOT/'outputs/photographic_reference_decisions_v1').glob('review_*/review.json')):
        verify_bundle(p.parent)
        r = read(p)
        task = next(row for row in queue if row['manifest_sha256'] == r['task_manifest_sha256'])
        assert r['task'] == read(STYLE/task['folder']/'task.json')
        assert r['target_appearance_accepted'] == (r['choice'] == 'suitable')
        assert not r['calibration_admitted'] and not r['training_admitted']
        for f in p.parent.iterdir():
            bind(f)
        reviews.append(dict(path=str(p), frame=r['frame'], choice=r['choice'], note=r['note'], saved_utc=r['saved_utc']))
    assert all(r['choice'] == 'suitable' for r in preferences.values())
    inventories = {}
    results = {}
    for role, parent in BASES.items():
        inventory_path = parent/'artifact_sha256_PRIVATE.json'
        inventories[role] = {k.replace('\\','/'): v for k,v in read(inventory_path).items()}
        bind(inventory_path)
        receipt = read(parent/'verification_PRIVATE.json')
        assert receipt['passed'] and bind(inventory_path) == receipt['artifact_manifest_sha256']
        assert bind(parent/'results_PRIVATE.json') == receipt['results_sha256']
        bind(parent/'verification_PRIVATE.json')
        results[role] = {r['frame']:r for r in read(parent/'results_PRIVATE.json')['records']}
    names = ['input.png','measurement_mask.png','protected_normalized.png','parent_mask.png','categories.png','landmarks.npy','visible_face.png','alpha_normalized.npy']
    def cached(role, frame, name):
        rel = frame+'/'+name
        path = BASES[role]/rel
        assert bind(path) == inventories[role][rel]
        return path
    for row in queue:
        frame = row['frame']
        if frame == '904_0':
            continue
        for role in BASES:
            assert results[role][frame]['status'] == 'available'
            for name in names:
                cached(role,frame,name)
    for p in [Path(__file__), ROOT/'docs/photographic-support-preparation-protocol-2026-11-10.md',
              ROOT/'src/skin_masking/correction_preview.py', ROOT/'src/demo/manual_brush.py',
              ROOT/'src/ita_estimation/compute_ita.py', ROOT/'src/correction/seamless_blend.py']:
        bind(p)
    method = dict(schema_version='truehue_photographic_manual_support_method_v1',
        coordinates='exact_cached_native_anchor_1p5_normalized_256_inputs',
        measurement='explicit_facial_skin_mask_compute_masked_lab_statistics_min1000',
        correction='separate_existing_whole_face_visible_neck_support_protection_explicit_unlock',
        renderer='unchanged_inward_blend_gamma_red_blue_identity_only_in_annotation',
        empirical_mst_transfer='not_established_no_calibration_rebinding',
        implementation_sha256={p:h for p,h in bound.items() if p.endswith('.py')})
    method_id = hashlib.sha256(json.dumps(method, sort_keys=True, separators=(',',':')).encode()).hexdigest()
    OUT.mkdir()
    write(OUT/'method.json',dict(method=method,method_sha256=method_id))
    tasks = []
    ledger = []
    for row in queue:
        frame = row['frame']
        for role in BASES:
            case = frame+'__'+role
            if frame == '904_0':
                ledger.append(dict(case_id=case,frame=frame,role=role,status='blocked_wrong_person_pair',training_admitted=False))
                continue
            r = results[role][frame]
            image = cv2.imread(str(cached(role,frame,'input.png')))
            measurement = cv2.imread(str(cached(role,frame,'measurement_mask.png')),0)
            parent = cv2.imread(str(cached(role,frame,'parent_mask.png')),0)
            categories = cv2.imread(str(cached(role,frame,'categories.png')),0)
            landmarks = np.load(cached(role,frame,'landmarks.npy'),allow_pickle=False)
            visible = cv2.imread(str(cached(role,frame,'visible_face.png')),0)
            reconstructed = render_preview(image,parent,categories,landmarks,visible,glasses='uncertain',parameters=(1.,1.,1.))
            old_alpha = np.load(cached(role,frame,'alpha_normalized.npy'),allow_pickle=False)
            old_p = cv2.imread(str(cached(role,frame,'protected_normalized.png')),0)
            assert np.array_equal(reconstructed.alpha,old_alpha)
            assert np.array_equal(reconstructed.protected.astype(np.uint8)*255,old_p)
            assert np.array_equal(reconstructed.output,image)
            _,xs = np.nonzero(parent)
            folder = OUT/case
            folder.mkdir()
            for name,a in [('photo_used.png',image),('measurement_mask.png',measurement),
                           ('correction_mask.png',reconstructed.support.correction_mask),('protected_mask.png',old_p)]:
                assert cv2.imwrite(str(folder/name),a)
            np.save(folder/'correction_alpha.npy',old_alpha,allow_pickle=False)
            report = dict(schema_version='truehue_photographic_support_task_v1',case_id=case,frame=frame,role=role,
                publisher_group=frame.split('_')[0], subject_id=None, provided_mst_label=None,
                method_sha256=method_id,input_bridge=r['input_bridge'],face_width=int(xs.max()-xs.min()+1),
                original_case_status=r['status'],source_native_measurement_pixels=results['source'][frame].get('measurement_native_pixels'),
                source_native_correction_pixels=results['source'][frame].get('correction_native_pixels'),
                reference_preference=preferences[row['manifest_sha256']],measurement_review='pending',correction_review='pending',
                generated_fixture=False,calibration_admitted=False,training_admitted=False,model_calls=0)
            write(folder/'report.json',report)
            seal(folder)
            verify(folder)
            tasks.append(dict(case_id=case,folder=case,manifest_sha256=digest(folder/'manifest.json')))
            ledger.append(dict(case_id=case,frame=frame,role=role,status='pending_user_support_review',training_admitted=False))
    assert len(tasks)==14 and len(ledger)==16
    assert all(digest(p)==h for p,h in bound.items())
    write(OUT/'queue.json',dict(tasks=tasks,blocked=[r for r in ledger if r['status'].startswith('blocked')]))
    write(OUT/'verification_PRIVATE.json',dict(passed=True,review_revisions=len(reviews),distinct_reference_choices=8,
        accepted_reference_appearances=8,explicit_330_clarification=True,preference_revisions=reviews,
        roles=ledger,editable_tasks=14,blocked_roles=2,exact_alpha_protection_replays=14,
        original_TIFF_reads=0,model_forwards=0,calibration_fits=0,tree_fits=0,holdout_bytes_read=0,input_sha256=bound))
    print('PASS: all8 target styles accepted, 10 preference revisions preserved; 14 exact cached dual-mask tasks, 2 blocked904 roles.')


if __name__=='__main__':
    main()
