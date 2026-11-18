"""Desktop-only integration of existing masks with separately measured legacy controls."""
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
import time
import uuid

import cv2
import numpy as np

from src.distortion_generation.paper_gamma import legacy_to_paper_parameters
from src.skin_masking.correction_preview import GLASSES_MODES, render_preview

ROOT = Path(__file__).resolve().parents[2]


def compose_result(legacy, image, facial, categories, points, visible, metadata, *, glasses):
    """Keep historical feature/MST provenance; never map the new mask with its lookup."""
    if legacy.image is None or not np.array_equal(legacy.image, image):
        raise ValueError('Current and legacy square images must match exactly')
    report = dict(legacy.report)
    if legacy.corrected is None or report.get('status') != 'development_experimental_mst':
        raise ValueError('Legacy controls unavailable; no substitute correction is applied')
    converted = legacy_to_paper_parameters(*report['parameters'])
    parameters = tuple(converted[k] for k in ('gamma', 'red_gain', 'blue_gain'))
    preview = render_preview(image, facial, categories, points, visible,
                             glasses=glasses, parameters=parameters)
    preview.report.update(parameters_are_illustrative=False, correction_model_used=True,
                          correction_model='historical_baseline5_fold1_separate_original_measurement',
                          combined_pipeline_validated=False)
    measurement = dict(metadata.get('measurement_report') or {})
    measurement.setdefault('face_count',1)
    measurement_mask = metadata.get('measurement_mask')
    if measurement.get('status') != 'success' or measurement_mask is None:
        raise ValueError('Current facial measurement unavailable; no mask fallback')
    report.update(historical_measurement=report['measurement'], measurement=measurement,
        historical_measurement_contract_sha256=report.get('measurement_contract_sha256'),
        historical_features=report.get('features'), display_features=measurement.get('features'),
        masking_mode='current', masking=preview.report,
        mst_measurement_source='historical_mask_only_not_current_mask',
        controls_measurement_source='unchanged_historical_features',
        renderer_parameters_direct_gamma=list(parameters),
        application_pixels=int(np.count_nonzero(preview.alpha)),
        combined_pipeline_validated=False, quality_gate_passed=False)
    report['limitations'] = list(report.get('limitations', []))+[
        'New masks with older controls are an unvalidated desktop demonstration',
        'MST and model controls use separate historical measurements, not the displayed current mask',
        'Clear-lens rims are approximate; uncertain glasses remain protected']
    if report.get('mst'):
        report['mst'] = dict(report['mst'], measurement_source='historical_mask')
    if not np.array_equal(preview.output[preview.protected], image[preview.protected]):
        raise RuntimeError('Protected pixels changed')
    if not np.array_equal(preview.output[preview.alpha == 0], image[preview.alpha == 0]):
        raise RuntimeError('Outside correction alpha changed')
    return SimpleNamespace(report=report, image=image, mask=preview.support.correction_mask,
        corrected=preview.output, measurement_mask=measurement_mask,
        protected_mask=preview.protected.astype(np.uint8)*255, alpha=preview.alpha)


class CurrentMaskDemoPipeline:
    def __init__(self, legacy, glasses='uncertain'):
        if glasses not in GLASSES_MODES:
            raise ValueError('Explicit known glasses mode required')
        self.legacy = legacy
        self.glasses = glasses

    def run(self, image):
        started=time.perf_counter()
        folder = ROOT/'outputs'/('desktop_current_masks_'+uuid.uuid4().hex)
        folder.mkdir(parents=True, exist_ok=False)
        square = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)
        report = dict(status='failed', failed_stage='current_masking', measurement=dict(status='failed'),
            masking_mode='current', mst=None, features=None, parameters=None,
            experimental=True, scientifically_validated=False, quality_gate_passed=False,
            masking_artifacts=str(folder))
        try:
            helper = import_module('scripts.419_preview_object_protected_face')
            hashes, identity = helper.dependencies()
            source = folder/'decoded_source.png'
            ok, encoded = cv2.imencode('.png', image)
            if not ok:
                raise ValueError('Cannot encode local masking input')
            source.write_bytes(encoded.tobytes())
            hashes[str(source)] = helper.sha(source)
            data = helper.prepare_photo(source, folder, hashes)
            current_image, facial, categories, points, visible, metadata = data
            measurement = helper.read(folder/'measurement_report.json')
            if measurement.get('status') != 'success':
                raise ValueError(measurement.get('reason', 'Current skin measurement failed'))
            legacy = self.legacy.run(image)
            helper.write(folder/'legacy_report.json',legacy.report)
            if legacy.mask is not None:helper.save(folder/'legacy_measurement_mask.png',legacy.mask)
            metadata.update(measurement_report=measurement,
                measurement_mask=cv2.imread(str(folder/'candidate_measurement_mask.png'), 0))
            result = compose_result(legacy, current_image, facial, categories, points, visible,
                                    metadata, glasses=self.glasses)
            if not all(helper.sha(p) == h for p, h in hashes.items()):
                raise ValueError('Masking inputs changed during processing')
            result.report.update(masking_artifacts=str(folder), current_measurement_contract_sha256=identity,
                                 measurement_contract_sha256=identity)
            result.report['historical_elapsed_ms']=result.report.get('elapsed_ms')
            result.report['elapsed_ms']=(time.perf_counter()-started)*1000
            result.report['timing_note']='Desktop total includes current masks, isolated CPU FaceOcc, separate legacy prediction and blending; not Android timing.'
            return result
        except Exception as error:
            # A failed mask must never fall through to the old correction output.
            report.update(reason=str(error), measurement=dict(status='failed', reason=str(error)))
            parent=folder/'parent_report.json'
            if parent.exists():
                import json
                parent_report=json.loads(parent.read_text(encoding='utf-8'))
                if parent_report.get('stage')=='face_detection':
                    report.update(failed_stage='face_detection',measurement=parent_report)
            legacy_path=folder/'legacy_report.json'
            if legacy_path.exists():
                import json
                legacy_report=json.loads(legacy_path.read_text(encoding='utf-8'))
                if legacy_report.get('status')!='development_experimental_mst':
                    report.update(failed_stage='legacy_correction',reason=legacy_report.get('reason',str(error)),
                                  historical_measurement=legacy_report.get('measurement'),
                                  current_masking_succeeded=True)
            (folder/'desktop_failure.txt').write_text(str(error), encoding='utf-8')
            return SimpleNamespace(report=report, image=square, mask=None, corrected=None)
