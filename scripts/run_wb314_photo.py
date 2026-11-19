"""Run the frozen research correction with the existing single-photo mask service.

Explicit local input/output paths only. No fitting, downloads, dataset selection,
app-default changes or expert-packet edits. Analysis uses 256 pixels; primary
outputs render on original pixels at original size. The separate headroom
candidate never replaces the primary image.
"""
import argparse
import hashlib
from importlib import import_module
import json
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
from src.demo.service import read_photo
from src.correction.original_resolution import lift_analysis_support, render_original_rgb8
from src.skin_masking.correction_preview import GLASSES_MODES, render_preview
from wb314_headroom_advisory import WB314WithHeadroomAdvisory
from wb314_research_predictor import MODEL_SHA256, validate_inputs


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def save_png(path, image):
    # imencode supports local paths with non-ASCII characters on Windows.
    ok, encoded = cv2.imencode('.png', image)
    if not ok:
        raise OSError('Could not encode output PNG')
    Path(path).write_bytes(encoded.tobytes())


def prepare_masks(image, folder, glasses):
    """Use the same area-normalized input/mask construction as the V2 research path."""
    helper = import_module('scripts.419_preview_object_protected_face')
    hashes, identity = helper.dependencies()
    normalized_path = folder / 'normalized_input.png'
    hashes[str(normalized_path)] = sha(normalized_path)
    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError('Mask-service dependency changed before preparation')
    current, facial, categories, points, visible, metadata = helper.prepare_photo(normalized_path, folder, hashes)
    if not np.array_equal(current, image):
        raise ValueError('Mask service changed normalized input pixels')
    measurement_report = helper.read(folder / 'measurement_report.json')
    if measurement_report.get('status') != 'success':
        raise ValueError(measurement_report.get('reason', 'Facial measurement unavailable'))
    measurement = cv2.imdecode(np.frombuffer((folder / 'candidate_measurement_mask.png').read_bytes(), np.uint8), cv2.IMREAD_GRAYSCALE)
    preview = render_preview(current, facial, categories, points, visible,
                             glasses=glasses, parameters=(1., 1., 1.))
    if preview.report.get('requires_glasses_choice'):
        raise ValueError('Detected glasses remain uncertain; explicitly choose clear or opaque before correction')
    for path, digest in hashes.items():
        if sha(path) != digest:
            raise ValueError('Mask-service dependency changed during preparation')
    return measurement, preview.alpha, preview.protected, dict(
        measurement=measurement_report, masking=preview.report,
        mask_contract_sha256=identity, mask_source=metadata,
        geometry_origin='computed_on_this_normalized_input',
        automatic_mask_quality_validated=False)


def check_output(output, rgb, alpha, protected):
    if not isinstance(output, np.ndarray) or output.dtype != np.uint8 or output.shape != rgb.shape:
        raise ValueError('Correction must return matching RGB8 output')
    if not np.array_equal(output[protected], rgb[protected]):
        raise ValueError('Correction changed protected pixels')
    if not np.array_equal(output[alpha == 0], rgb[alpha == 0]):
        raise ValueError('Correction changed pixels outside application support')


def run_photo(source, destination, *, glasses):
    """Process one explicit photo; failed stages never fall back to old controls."""
    if glasses not in GLASSES_MODES:
        raise ValueError('Explicit clear, opaque or uncertain glasses choice required')
    source = Path(source).resolve()
    folder = Path(destination).resolve()
    folder.mkdir(parents=True, exist_ok=False)
    report = dict(status='failed', failed_stage='input', research_only=True,
        model_sha256=MODEL_SHA256, source_path=str(source), glasses=glasses,
        normalization='whole_frame_256_INTER_AREA_BGR_then_explicit_RGB',
        new_fits=0, correction_calls_attempted=0, correction_calls_completed=0,
        qualification_complete=False, automatic_mask_quality_validated=False,
        mst_mapping_validated=False, original_resolution_output=True,
        original_pixels_resized_for_output=False, original_aspect_ratio_preserved=True,
        native_resolution_mask_accuracy_validated=False,
        headroom_applied_to_primary=False, app_defaults_changed=False,
        expert_packet_changed=False, fallback_to_legacy=False)
    try:
        image, source_hash = read_photo(source)
        report.update(source_sha256=source_hash, original_shape=list(image.shape))
        normalized = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)
        save_png(folder / 'normalized_input.png', normalized)
        report['failed_stage'] = 'masking'
        measurement, alpha, protected, masks = prepare_masks(normalized, folder, glasses)
        rgb = normalized[:, :, ::-1].copy()
        validate_inputs(rgb, measurement, alpha, protected)
        report.update(masks)
        # Do not construct or call a trained predictor before mask validation.
        report['failed_stage'] = 'correction'
        predictor = WB314WithHeadroomAdvisory()
        before = [array.tobytes() for array in (rgb, measurement, alpha, protected)]
        report['correction_calls_attempted'] = 1
        result = predictor.correct(rgb, measurement, alpha, protected)
        report['correction_calls_completed'] = 1
        if before != [array.tobytes() for array in (rgb, measurement, alpha, protected)]:
            raise ValueError('Predictor mutated input or masks')
        if result.get('model_sha256') != MODEL_SHA256 or result.get('headroom_applied_to_primary') is not False:
            raise ValueError('Unchanged frozen primary policy required')
        check_output(result['output'], rgb, alpha, protected)
        alternative = result['headroom_candidate']
        if alternative is not None:
            check_output(alternative, rgb, alpha, protected)
        report['failed_stage'] = 'original_resolution_render'
        original_rgb = image[:, :, ::-1].copy()
        original_alpha, original_protected = lift_analysis_support(alpha, protected, original_rgb.shape)
        primary_original = render_original_rgb8(original_rgb, original_alpha, original_protected, result['controls'])
        check_output(primary_original, original_rgb, original_alpha, original_protected)
        candidate_original = None
        if alternative is not None:
            candidate_original = render_original_rgb8(original_rgb, original_alpha, original_protected,
                                                     result['headroom_candidate_controls'])
            check_output(candidate_original, original_rgb, original_alpha, original_protected)
        if sha(source) != source_hash:
            raise ValueError('Source photo changed during processing')
        report['failed_stage'] = 'export'
        save_png(folder / 'primary_correction.png', primary_original[:, :, ::-1])
        save_png(folder / 'analysis_correction_256.png', result['output'][:, :, ::-1])
        if candidate_original is not None:
            save_png(folder / 'separate_headroom_candidate.png', candidate_original[:, :, ::-1])
            save_png(folder / 'analysis_headroom_candidate_256.png', alternative[:, :, ::-1])
        save_png(folder / 'measurement_mask.png', measurement)
        save_png(folder / 'protected_mask.png', protected.astype(np.uint8) * 255)
        np.save(folder / 'application_alpha.npy', alpha, allow_pickle=False)
        save_png(folder / 'original_protected_mask.png', original_protected.astype(np.uint8) * 255)
        np.save(folder / 'original_application_alpha.npy', original_alpha, allow_pickle=False)
        report.update(status='research_output_ready', failed_stage=None,
            controls=result['controls'], features=result['features'], leaf=result['leaf'],
            feature_details=result.get('feature_details'),
            headroom_advisory=result['headroom_advisory'],
            separate_candidate_controls=result['headroom_candidate_controls'],
            primary_output='primary_correction.png',
            output_shape=list(primary_original.shape), analysis_output='analysis_correction_256.png',
            output_encoding='lossless_RGB8_PNG',
            original_support_mapping='linear_alpha_with_nearest_membership_and_protection_v1',
            headroom_advisory_scope='computed_on_256_analysis_not_original_resolution_highlight_guarantee',
            separate_candidate_output='separate_headroom_candidate.png' if alternative is not None else None,
            protected_and_outside_pixels_preserved=True, input_arrays_immutable=True)
        write_json(folder / 'report.json', report)
        artifacts = {path.name: sha(path) for path in folder.iterdir() if path.is_file()}
        write_json(folder / 'manifest.json', dict(status=report['status'], artifacts=artifacts,
            source_sha256=source_hash, runner_sha256=sha(Path(__file__)), model_sha256=MODEL_SHA256))
        return report
    except Exception as error:
        report.update(status='failed', reason=str(error))
        write_json(folder / 'report.json', report)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='One explicitly selected local photo')
    parser.add_argument('--output', type=Path, required=True, help='New folder; existing results are never overwritten')
    parser.add_argument('--glasses', choices=GLASSES_MODES, required=True)
    args = parser.parse_args()
    report = run_photo(args.source, args.output, glasses=args.glasses)
    print(json.dumps(dict(status=report['status'], output=str(args.output.resolve()),
                          qualification_complete=False)))


if __name__ == '__main__':
    main()
