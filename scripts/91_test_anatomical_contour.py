"""Execute the fixed two-arm mask ablation on saved development inputs only."""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.skin_masking.anatomical_contour_experiment import anatomy, removal, extend
from src.skin_masking.selfie_material_segmenter import SelfieMaterialSegmenter
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.evaluation.mask_support_quality import support_retention
from src.distortion_generation.generate_distortions import transform_rgb


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    config = get_config()
    prepare = importlib.import_module('11_prepare_training_manifests')
    ycb = importlib.import_module('56_compare_ycrcb_estimation')
    scoring = importlib.import_module('90_score_face_boundary_references')
    brightness = importlib.import_module('72_audit_brightness_features')
    output = ROOT/'outputs/anatomical_contour_v1'
    if output.exists():
        raise FileExistsError(output)
    approved_path = ROOT/'data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json'
    approved = set(json.loads(approved_path.read_text())['approved_pairs'])
    chosen, sources, tracked = [], {}, [Path(__file__), approved_path,
        ROOT/'docs/anatomical-contour-protocol.md', ROOT/'src/skin_masking/anatomical_contour_experiment.py',
        ROOT/'src/skin_masking/landmark_exclusion.py', ROOT/'src/skin_masking/mouth_exclusion.py',
        ROOT/'src/skin_masking/face_outline_experiment.py', ROOT/'scripts/11_prepare_training_manifests.py',
        ROOT/'scripts/56_compare_ycrcb_estimation.py', ROOT/'scripts/90_score_face_boundary_references.py',
        ROOT/'scripts/72_audit_brightness_features.py', ROOT/'outputs/brightness_feature_audit_v1/feature_schema.json',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',
        ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/'data/manifests/face_boundary_reference_v1/completion_confirmation.json',
        ROOT/'data/manifests/face_boundary_reference_v1/original_export.json',
        ROOT/config.FACE_MODEL_PATH, ROOT/config.FACE_LANDMARKER_MODEL_PATH,
        ROOT/config.SELFIE_SEGMENTER_MODEL_PATH, ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    for folder in ('non_skin_regenerated_remaining28_v1', 'non_skin_regenerated_two_v1'):
        parent = ROOT/'outputs'/folder
        summary_path = parent/'summary.json'
        tracked.append(summary_path)
        for row in json.loads(summary_path.read_text())['attempts']:
            ident = Path(row['image_id']).stem
            pair = ident+'_'+row['variant']
            if folder == 'non_skin_regenerated_two_v1' and pair not in approved:
                continue
            chosen.append((parent/'images', row, pair))
            sources[ident] = parent/'images'
            tracked += [parent/'images'/(pair+suffix) for suffix in ('_input.png', '_baseline_estimate.png', '_support.png')]
    assert len(chosen) == 32 and len(sources) == 9
    for ident, parent in sources.items():
        tracked += [parent/(ident+suffix) for suffix in ('_reference.png', '_generation.png')]
    point_manifest = ROOT/'data/manifests/material_review_v1/review_manifest.json'
    point_labels = point_manifest.with_name('material_review_labels.json')
    points = json.loads(point_manifest.read_text())['points']
    labels = json.loads(point_labels.read_text())
    assert not labels['draft'] and labels['manifest_sha256'] == digest(point_manifest)
    label_map = {p['point_id']: p['label'] for p in labels['labels']}
    tracked += [point_manifest, point_labels]
    raw_paths = {ident: ROOT/config.DATA_RAW/'FairFace'/ident.split('__', 1)[1] for ident in {p['image_id'] for p in points}}
    for ident, path in raw_paths.items():
        tracked.append(path)
        for variant in ('clean', 'global_color_shift'):
            stem = ident.replace('/', '_')+'_'+variant
            tracked += [ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png'),
                        ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')]
    ref_manifest = ROOT/'data/manifests/face_boundary_review_v1/review_manifest.json'
    tracked.append(ref_manifest)
    reference_records = json.loads(ref_manifest.read_text())['images']
    refs = {}
    for ref in reference_records:
        ident = Path(ref['image_id']).stem
        label_path = ROOT/'outputs/face_boundary_reference_v1/labels'/(ident+'_labels.png')
        refs[ident] = cv2.imread(str(label_path), 0)
        tracked += [label_path, ROOT/ref['image_path']]
        assert refs[ident].shape == (ref['height'], ref['width'])
    sentinel = ROOT/config.DATA_RAW/'FairFace/train/83184.jpg'
    tracked.append(sentinel)
    hashes = {str(path.relative_to(ROOT)): digest(path) for path in tracked}
    output.mkdir()
    for name in ('masks', 'boards', 'geometry'):
        (output/name).mkdir()
    (output/'protocol.md').write_bytes((ROOT/'docs/anatomical-contour-protocol.md').read_bytes())
    (output/'run_status.json').write_text('{"status":"running"}')
    segmenter = SelfieMaterialSegmenter(ROOT/config.SELFIE_SEGMENTER_MODEL_PATH)
    records, observations, geometry_records, panels = [], [], [], {}

    def read_mask(path):
        mask = cv2.imread(str(path), 0)
        if mask is None or not set(np.unique(mask)).issubset({0, 255}):
            raise ValueError('Missing/nonbinary mask: '+str(path))
        return mask > 0

    def geometry(image, key, categories):
        boxes = prepare._detect_face_boxes(image, ROOT/config.FACE_MODEL_PATH, .85)
        if len(boxes) != 1:
            raise ValueError('Expected single face')
        box = list(map(int, boxes[0]))
        x, y, w, h = box
        landmarks, margin, status = prepare.detect_landmarks_with_margin(image, box, ROOT/config.FACE_LANDMARKER_MODEL_PATH)
        if landmarks is None:
            raise ValueError('Unavailable landmarks')
        full = landmarks + [x, y]
        original, expanded, oval, details = anatomy(image, full)
        pad = max(2, int(np.ceil(.10*max(w,h))))
        x0, y0, x1, y1 = max(0,x-pad), max(0,y-pad), min(image.shape[1],x+w+pad), min(image.shape[0],y+h+pad)
        # Same raw proposal/oval retention criterion as script88, before new E margin.
        raw = ycb.ycrcb_mask(image[y0:y1,x0:x1], original[y0:y1,x0:x1])
        proposal = raw & np.isin(categories[y0:y1,x0:x1], [2,3])
        ratio = float((proposal & oval[y0:y1,x0:x1]).sum()/proposal.sum()) if proposal.any() else 0.
        info = dict(key=key, face_box=box, margin=margin, status=status,
                    oval_retention=ratio, extension_geometry_allowed=ratio >= .75, **details)
        geometry_records.append(info)
        np.save(output/'geometry'/(key+'_landmarks.npy'), full)
        for name, mask in [('original_excluded',original),('expanded_excluded',expanded),('oval',oval)]:
            assert cv2.imwrite(str(output/'geometry'/(key+'_'+name+'.png')), mask.astype(np.uint8)*255)
        return original, expanded, oval, box, info

    def process(image, key, ident, masks, measurement, extra=None):
        cats = segmenter.categories_bgr(image)
        try:
            original, excluded, oval, box, geo = geometry(image, key, cats)
        except ValueError as error:
            record = dict(key=key, image_id=ident, status='geometry_unavailable', reason=str(error), stages={}, **(extra or {}))
            records.append(record)
            return record, None
        result, result_masks = {}, {}
        for stage, old in masks.items():
            assert old.shape == image.shape[:2]
            reduced = removal(old, excluded)
            arms = {'E': reduced}
            ec_info = dict(status='available_measurement_unchanged_from_E')
            if stage == 'measurement':
                arms['EC'] = reduced.copy()
            else:
                try:
                    arms['EC'], details = extend(image, old, excluded, oval, cats, measurement, box, geo['extension_geometry_allowed'])
                    ec_info = dict(status='available', **details)
                except ValueError as error:
                    ec_info = dict(status='unavailable', reason=str(error))
            stage_result = dict(original_pixels=int(old.sum()), selected_inside_original_exclusions=int((old & original).sum()),
                                EC_availability=ec_info, arms={})
            for arm, mask in arms.items():
                assert not (mask & excluded).any()
                assert not ((old & ~mask) & ~excluded).any()
                if arm == 'E':
                    assert not (mask & ~old).any()
                path = output/'masks'/(key+'_'+stage+'_'+arm+'.png')
                assert cv2.imwrite(str(path), mask.astype(np.uint8)*255)
                item = dict(pixels=int(mask.sum()), removed_pixels=int((old & ~mask).sum()), added_pixels=int((mask & ~old).sum()))
                if ident in refs:
                    item.update(reference=scoring.score(mask, refs[ident]), interior_reference=scoring.score(mask, refs[ident], True),
                        added_labeled_exclusions=int((mask & ~old & (refs[ident] == 3)).sum()),
                        added_unlabeled=int((mask & ~old & (refs[ident] == 0)).sum()))
                    stage_result['original_reference'] = scoring.score(old, refs[ident])
                stage_result['arms'][arm] = item
            result[stage] = stage_result
            result_masks[stage] = arms
            shown = []
            for title, mask in [('Original', old), ('E', arms['E']), ('EC', arms.get('EC'))]:
                display = image.copy()
                if mask is not None:
                    display[mask] = np.rint(.55*display[mask]+[0,99,0]).astype(np.uint8)
                display = cv2.copyMakeBorder(display, 28, 0, 0, 0, cv2.BORDER_CONSTANT)
                cv2.putText(display, key+' '+stage, (3,11), cv2.FONT_HERSHEY_SIMPLEX,.27,(255,255,255),1)
                cv2.putText(display, title if mask is not None else 'EC UNAVAILABLE', (3,23), cv2.FONT_HERSHEY_SIMPLEX,.3,(255,255,255),1)
                shown.append(display)
            panels.setdefault(ident, []).append(np.hstack(shown))
        record = dict(key=key, image_id=ident, status='geometry_available', geometry=geo, stages=result, **(extra or {}))
        if 'measurement' in masks:
            record['measurement_statistics'] = {}
            for arm in ('E','EC'):
                mask = result_masks['measurement'][arm]
                stats = compute_masked_lab_statistics(image, mask.astype(np.uint8)*255, 1000)
                record['measurement_statistics'][arm] = dict(statistics=stats, brightness=brightness.brightness_features(image,mask))
        records.append(record)
        return record, result_masks

    try:
        for ident, parent in sorted(sources.items()):
            image = cv2.imread(str(parent/(ident+'_reference.png')))
            old = read_mask(parent/(ident+'_generation.png'))
            record, masks = process(image, ident+'_source', ident, {'generation':old}, old)
        for parent, row, pair in chosen:
            ident = Path(row['image_id']).stem
            image = cv2.imread(str(parent/(pair+'_input.png')))
            measurement = read_mask(parent/(pair+'_baseline_estimate.png'))
            correction = read_mask(parent/(pair+'_support.png'))
            record, masks = process(image, pair, ident, {'measurement':measurement,'correction':correction}, measurement,
                dict(original_human_decision=row.get('original_human_decision','accept'), training_eligible=False))
            if masks is not None:
                generation = read_mask(parent/(ident+'_generation.png'))
                record['retention_old_generation_denominator'] = {arm:support_retention(generation,masks['measurement'][arm],masks['correction'][arm])
                    for arm in ('E','EC') if arm in masks['correction']}
        for image_id, path in sorted(raw_paths.items()):
            ident = Path(image_id).stem
            clean = cv2.imread(str(path))
            cats = segmenter.categories_bgr(clean)
            clean_stem = image_id.replace('/','_')+'_clean'
            generation = read_mask(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(clean_stem+'_baseline_estimate.png')) & np.isin(cats,[2,3])
            for variant in ('clean','global_color_shift'):
                image = clean if variant == 'clean' else cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
                cats = segmenter.categories_bgr(image)
                stem = image_id.replace('/','_')+'_'+variant
                measurement = read_mask(ROOT/'outputs/ycrcb_estimation_ablation_v1'/(stem+'_baseline_estimate.png')) & np.isin(cats,[2,3])
                correction = read_mask(ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')) & np.isin(cats,[2,3])
                stages = {'measurement':measurement,'correction':correction}
                # Generation always evaluated on clean source pixels, never shifted input.
                if variant == 'clean':
                    stages['generation'] = generation
                record, masks = process(image, ident+'_regression_'+variant, ident, stages, measurement,
                    dict(regression=True,variant=variant))
                for point in (p for p in points if p['image_id'] == image_id):
                    x,y = point['x'],point['y']
                    assert image.shape[:2] == (point['height'],point['width'])
                    observations.append(dict(point_id=point['point_id'],image_id=ident,variant=variant,label=label_map[point['point_id']],
                        stages={stage:dict(before=bool(mask[y,x]),arms={arm:bool(a[y,x]) for arm,a in masks[stage].items()} if masks is not None else {}) for stage,mask in stages.items()}))
        for variant in ('clean','global_color_shift'):
            image = cv2.imread(str(sentinel))
            if variant != 'clean':
                image = cv2.cvtColor(np.rint(transform_rgb(cv2.cvtColor(image,cv2.COLOR_BGR2RGB).astype(float)/255,gamma=1.,red_gain=.85,blue_gain=1.15)*255).astype(np.uint8),cv2.COLOR_RGB2BGR)
            cats = segmenter.categories_bgr(image)
            try:
                geometry(image,'83184_sentinel_'+variant,cats)
            except ValueError as error:
                geometry_records.append(dict(key='83184_sentinel_'+variant,status='unavailable',reason=str(error)))
        for ident, strips in panels.items():
            # Four rows/page, all stages visible without shrinking native pixels.
            for page, offset in enumerate(range(0,len(strips),4),1):
                assert cv2.imwrite(str(output/'boards'/f'{ident}_page{page}.png'),np.vstack(strips[offset:offset+4]))
        assert len(observations) == 48
        assert hashes == {name:digest(ROOT/name) for name in hashes}
        summary = dict(status='complete_no_adoption_no_regeneration_no_fitting',records=records,
            point_observations=observations,geometry=geometry_records,input_sha256=hashes,
            input_count=32,source_count=9,models_fitted=0,
            limitations='Saved inputs use old generation masks. New masks not a regenerated dataset. E may be assessable where EC is unavailable; unavailable EC is not a fallback pass. Native regressions apply old masks plus semantic veto before candidate arms.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        (output/'run_status.json').write_text('{"status":"complete"}')
        print(json.dumps(dict(records=len(records),geometry_statuses=dict(Counter(r['status'] for r in records)),observations=len(observations),boards=len(list((output/'boards').glob('*.png'))))))
    finally:
        segmenter.close()


if __name__ == '__main__':
    main()
