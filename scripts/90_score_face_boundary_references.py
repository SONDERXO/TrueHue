"""Rasterize confirmed development polygons and score existing masks only.

The original draft and later chat completion confirmation remain separate evidence.
No pipeline mask, feature, training table or model is updated by this script.
"""
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.utilities.config import get_config

EXPORT_SHA = '3e4915b76bb1799fc23bbdedf20162f8757760d05520fe916a2bae4d5a8b9553'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def polygon_pixels(points, width, height):
    """Even/odd fill at integer pixel centers; include exact boundary centers.

    Floating vertices are retained, rather than rounded to integer coordinates.
    """
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    inside = np.zeros((height, width), bool)
    boundary = np.zeros_like(inside)
    for a, b in zip(points, points[1:] + points[:1]):
        ax, ay = a
        bx, by = b
        cross = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
        boundary |= ((np.abs(cross) <= 1e-9) & (x >= min(ax, bx)) &
                     (x <= max(ax, bx)) & (y >= min(ay, by)) & (y <= max(ay, by)))
        if by != ay:
            inside ^= ((ay > y) != (by > y)) & (x < ax + (y - ay) * (bx - ax) / (by - ay))
    return inside | boundary


def rasterize(polygons, width, height):
    """0 unlabeled, 1 skin, 2 uncertain, 3 exclude; priority applied last."""
    labels = np.zeros((height, width), np.uint8)
    for value, name in enumerate(('skin', 'uncertain', 'exclude'), 1):
        for polygon in polygons:
            if polygon['label'] == name:
                labels[polygon_pixels(polygon['points'], width, height)] = value
    return labels


def score(mask, labels, interior=False):
    positive, negative = labels == 1, labels == 3
    if interior:
        kernel = np.ones((3, 3), np.uint8)
        positive = cv2.erode(positive.astype(np.uint8), kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
        negative = cv2.erode(negative.astype(np.uint8), kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
    skin = int(positive.sum())
    exclude = int(negative.sum())
    selected_skin = int((mask & positive).sum())
    selected_exclude = int((mask & negative).sum())
    return dict(labeled_skin_pixels=skin, selected_skin_pixels=selected_skin,
                missed_skin_pixels=skin-selected_skin,
                skin_coverage=selected_skin/skin if skin else None,
                labeled_exclusion_pixels=exclude, selected_exclusion_pixels=selected_exclude,
                exclusion_selection_rate=selected_exclude/exclude if exclude else None,
                selected_uncertain_pixels=int((mask & (labels == 2)).sum()),
                selected_unlabeled_pixels=int((mask & (labels == 0)).sum()))


def main():
    output = ROOT/'outputs/face_boundary_reference_v1'
    tables = ROOT/'data/manifests/face_boundary_reference_v1'
    if tables.exists():
        raise FileExistsError('Reference import already exists; preserve it and version subsequent runs')
    archive = ROOT/'outputs/face_boundary_review_v1/export_validation'/EXPORT_SHA
    export = archive/'truehue_face_boundary_review.json'
    validation = archive/'validation.json'
    manifest = ROOT/'data/manifests/face_boundary_review_v1/review_manifest.json'
    data = json.loads(export.read_text())
    prior = json.loads(validation.read_text())
    spec = json.loads(manifest.read_text())
    assert digest(export) == EXPORT_SHA == prior['export_sha256']
    assert prior['structural_validation'] == 'pass' and not prior['errors']
    assert digest(manifest) == data['manifest_sha256'] == prior['manifest_sha256']
    assert data['draft'] is True
    expected = {r['image_id']: r for r in spec['images']}
    assert len(data['images']) == len(expected) == 3
    assert {r['image_id'] for r in data['images']} == set(expected)
    assert [r['image_id'] for r in data['images'] if not r['complete']] == ['fairface__train/40048.jpg']
    confirmation = dict(date='2026-10-26',source='User message in project conversation',
        exact_statement="I mustve forgot to mark it complete. It's complete so you continue",
        completed_image_id='fairface__train/40048.jpg',applies_to_export_sha256=EXPORT_SHA,
        effect='All three frames reviewer-complete; original draft bytes/flags and all polygon coordinates/notes preserved')
    config = get_config()
    tracked = [Path(__file__), export, validation, manifest,
        ROOT/'data/manifests/material_review_v1/material_review_labels.json',
        ROOT/'data/manifests/source60_user_review_v1/reconciled_pairs.json',
        ROOT/'data/manifests/development_exposure_additions.jsonl',
        ROOT/config.CORRECTION_PROTOTYPE_MODEL_PATH]
    comparisons = []
    for ident, folder in [('40048', 'non_skin_regenerated_remaining28_v1'), ('60162', 'non_skin_regenerated_two_v1')]:
        parent = ROOT/'outputs'/folder/'images'
        comparisons.append((ident, 'generation', parent/(ident+'_generation.png')))
        for path in sorted(parent.glob(ident+'_*_support.png')):
            pair = path.name.removesuffix('_support.png')
            for stage, suffix in [('measurement', '_baseline_estimate.png'), ('correction', '_support.png')]:
                comparisons.append((ident, pair+'_'+stage, parent/(pair+suffix)))
            candidate = ROOT/'outputs/padded_correction_crop_v1/masks'/(pair+'_candidate.png')
            if candidate.exists():
                comparisons.append((ident, pair+'_padded_candidate', candidate))
    # Native 224 paint baseline is an older policy, explicitly not the newer veto.
    for variant in ('clean', 'global_color_shift'):
        stem = 'fairface__train_16798.jpg_'+variant
        comparisons.append(('16798', variant+'_older_pre_semantic_veto_correction',
                            ROOT/'outputs/additions_only_boundary_v1'/(stem+'_support.png')))
    tracked += [path for _, _, path in comparisons]
    for ref in spec['images']:
        for path_key, sha_key in [('image_path', 'image_sha256'), ('source_path', 'source_sha256')]:
            path = ROOT/ref[path_key]
            assert digest(path) == ref[sha_key]
            tracked.append(path)
    hashes = {str(path.relative_to(ROOT)): digest(path) for path in tracked}
    tables.mkdir(parents=True)
    output.mkdir(exist_ok=True)
    (output/'labels').mkdir()
    (output/'boards').mkdir()
    (tables/'completion_confirmation.json').write_text(json.dumps(confirmation, indent=2), encoding='utf-8')
    (tables/'original_export.json').write_bytes(export.read_bytes())
    references, counts, records = {}, [], []
    for annotation in data['images']:
        ref = expected[annotation['image_id']]
        image = cv2.imread(str(ROOT/ref['image_path']))
        assert image.shape[:2] == (ref['height'], ref['width'])
        ident = Path(ref['image_id']).stem
        labels = rasterize(annotation['polygons'], ref['width'], ref['height'])
        references[ident] = (labels, image)
        assert cv2.imwrite(str(output/'labels'/(ident+'_labels.png')), labels)
        counts.append(dict(image_id=ref['image_id'], reviewed_complete=True,
            completion_basis='chat_confirmation' if not annotation['complete'] else 'export_checkbox',
            notes=annotation['notes'], pixel_counts={name: int((labels == value).sum())
                for value, name in enumerate(('unlabeled', 'skin', 'uncertain', 'exclude'))}))
    for ident, name, path in comparisons:
        labels, image = references[ident]
        raw = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        assert raw is not None and raw.shape == labels.shape
        assert set(np.unique(raw)).issubset({0, 255})
        mask = raw > 0
        records.append(dict(image_id=ident, comparison=name, mask_path=path.relative_to(ROOT).as_posix(),
            full=score(mask, labels), one_pixel_interior=score(mask, labels, interior=True)))
        shown = image.copy()
        shown[(labels == 1) & ~mask] = [255, 100, 0]  # blue: missed labeled skin
        shown[(labels == 3) & mask] = [0, 0, 255]  # red: selected labeled exclusion
        shown[(labels == 1) & mask] = np.rint(.5*shown[(labels == 1) & mask]+[0, 100, 0]).astype(np.uint8)
        board = cv2.copyMakeBorder(np.hstack([image, shown]), 30, 0, 0, 0, cv2.BORDER_CONSTANT)
        cv2.putText(board, name, (3, 20), cv2.FONT_HERSHEY_SIMPLEX, .35, (255, 255, 255), 1)
        assert cv2.imwrite(str(output/'boards'/(ident+'_'+name+'.png')), board)
    # Independent OpenCV point-in-polygon replay at every exact pixel center.
    for annotation in data['images']:
        ref = expected[annotation['image_id']]
        replay = np.zeros((ref['height'], ref['width']), np.uint8)
        for value, label in enumerate(('skin', 'uncertain', 'exclude'), 1):
            for polygon in annotation['polygons']:
                if polygon['label'] != label:
                    continue
                contour = np.asarray(polygon['points'], np.float32)
                for y in range(ref['height']):
                    for x in range(ref['width']):
                        if cv2.pointPolygonTest(contour, (float(x), float(y)), False) >= 0:
                            replay[y, x] = value
        assert np.array_equal(replay, references[Path(ref['image_id']).stem][0])
    assert hashes == {path: digest(ROOT/path) for path in hashes}
    summary = dict(status='confirmed_development_references_scored_no_policy_adoption',
        export_sha256=EXPORT_SHA, confirmation=confirmation, references=counts, comparisons=records,
        raster_convention='Integer pixel centers, float vertices, boundary included; 0 unlabeled/1 skin/2 uncertain/3 exclude; exclude overrides uncertain overrides skin',
        sensitivity='One-pixel 3x3 erosion of each scored class separately; diagnostic only, not added human uncertainty',
        limitations='Three exposed development sources, coarse manual boundaries, not calibrated truth or final evaluation. Outside polygons unscored. 16798 older pre-veto policy, not evidence for current semantic-veto safety. Existing input geometry unchanged; no mask resizing. Measurement coverage is descriptive, not full-coverage acceptance.',
        verification='All saved reference pixels independently replayed with OpenCV pointPolygonTest; all tracked bytes unchanged',
        input_sha256=hashes, models_fitted=0)
    (output/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(dict(references=counts, comparisons=len(records), verification=summary['verification']), indent=2))


if __name__ == '__main__':
    main()
