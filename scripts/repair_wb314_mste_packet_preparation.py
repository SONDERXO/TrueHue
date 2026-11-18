"""One consistent AREA-normalised version of the same20formative-feedback cases."""
from pathlib import Path
import importlib
import json
import hashlib
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import prepare_wb314_mste_development_packet as shared
from wb314_research_predictor import validate_inputs, MODEL_SHA256
from src.skin_masking.correction_preview import render_preview

OLD = ROOT / 'outputs/wb314_mste_development_packet_v1'
OUT = ROOT / 'outputs/wb314_mste_development_packet_v2_area'
DELIVERY = ROOT / 'output/wb314-mst-development-feedback-2026-11-19-v2'
PROTOCOL = ROOT / 'docs/wb314-mste-packet-preparation-repair-2026-11-19.md'
MODEL = ROOT / 'outputs/wb314_final_training_v1/model.json'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(d, f, indent=2, allow_nan=False)
def recheck(d):
    for p, h in d.items():
        if sha(p) != h: raise ValueError('Bound file changed: ' + str(p))


def prepare():
    if OUT.exists() or DELIVERY.exists(): raise FileExistsError('Preserve any earlier repair attempt')
    assert read(OLD / 'draft_audit.json')['passed'] and sha(MODEL) == MODEL_SHA256
    recheck(read(OLD / 'bindings.json'))
    helper = importlib.import_module('419_preview_object_protected_face')
    deps, contract = helper.dependencies(); recheck(deps)
    assert (ROOT / 'outputs/faceocc_inference_env_v1/Scripts/python.exe').is_file()
    old_rows = read(OLD / 'selected_references.json'); assert len(old_rows) == 20
    rows = []
    for r in old_rows:
        source = Path(r['source_path']).resolve()
        assert source.parent == (ROOT / 'data/raw/mst-e_data' / r['subject_id']).resolve()
        assert sha(source) == r['source_sha256']
        row = {k: r[k] for k in ['case_id', 'subject_id', 'MST', 'candidate_id', 'pair_id', 'condition']}
        row.update(original_source_path=str(source), original_source_sha256=r['source_sha256'])
        rows.append(row)
        deps[str(source)] = r['source_sha256']
    for p in [PROTOCOL, Path(__file__), Path(shared.__file__), MODEL,
              OLD / 'selected_references.json', OLD / 'draft_audit.json',
              ROOT / 'scripts/wb314_research_predictor.py',
              ROOT / 'src/distortion_generation/camera_inspired_halfstop.py',
              ROOT / 'src/model_training/luminance_chroma_operator.py',
              ROOT / 'src/evaluation/luminance_chroma_scalar.py']:
        deps[str(p)] = sha(p)
    recheck(deps)
    OUT.mkdir(); (OUT / 'references').mkdir(); (OUT / 'normalised_sources').mkdir()
    write(OUT / 'bindings.json', deps)
    write(OUT / 'plan.json', dict(stage='development_packet_preparation_repair_v2', rows=rows,
          normalisation='whole-frame256INTER_AREA_before_existing_same-size_mask-service_resize',
          cases=20, reference_attempt_budget=20, prediction_budget=20, replacements=0,
          model_sha256=MODEL_SHA256, masking_contract_sha256=contract,
          official_MST_is_predictor_input=False, fits=0,
          authorization_context='Existing packet preparation plus case-specific user appearance feedback; bounded engineering repair, not new training approval'))
    print('FROZEN same20source cases/labels/slots/conditions; AREA repair only;0source decodes.', flush=True)


def references():
    if (OUT / 'reference_started.json').exists(): raise FileExistsError('No repair reference-run restart')
    deps = read(OUT / 'bindings.json'); recheck(deps)
    rows = read(OUT / 'plan.json')['rows']
    helper = importlib.import_module('419_preview_object_protected_face')
    write(OUT / 'reference_started.json', dict(cases=20, replacements=0, fits=0))
    records = []; selected = []
    try:
        for r in rows:
            folder = OUT / 'references' / r['candidate_id']; folder.mkdir()
            record = dict(r, status='failed', scientific_admission=False)
            try:
                raw = cv2.imread(r['original_source_path'], cv2.IMREAD_COLOR)
                if raw is None: raise ValueError('Pinned JPEG did not decode')
                normalised_bgr = cv2.resize(raw, (256, 256), interpolation=cv2.INTER_AREA)
                norm = OUT / 'normalised_sources' / (r['candidate_id'] + '.png')
                if not cv2.imwrite(str(norm), normalised_bgr): raise OSError('Could not save normalised input')
                hashes = dict(deps); hashes[str(norm)] = sha(norm)
                image, facial, categories, points, visible, metadata = helper.prepare_photo(norm, folder, hashes)
                assert np.array_equal(image, normalised_bgr), 'Unexpected additional mask-service pixel transform'
                report = read(folder / 'measurement_report.json')
                if report['status'] != 'success': raise ValueError(report.get('reason', 'Measurement unavailable'))
                measurement = cv2.imread(str(folder / 'candidate_measurement_mask.png'), cv2.IMREAD_GRAYSCALE)
                preview = render_preview(image, facial, categories, points, visible, glasses='opaque', parameters=(1., 1., 1.))
                rgb = image[:, :, ::-1].copy(); validate_inputs(rgb, measurement, preview.alpha, preview.protected)
                pack = folder / 'reference_support.npz'
                np.savez(pack, reference=rgb, measurement=measurement, alpha=preview.alpha, protected=preview.protected)
                overlays = [rgb]
                for chosen, colour in [(measurement > 0, [0, 220, 0]), (preview.alpha > 0, [0, 220, 220]), (preview.protected, [220, 0, 0])]:
                    a = rgb.copy(); a[chosen] = np.rint(.55*a[chosen]+.45*np.array(colour)).astype(np.uint8); overlays.append(a)
                qa = Image.new('RGB', (1024, 280), 'white')
                qa.paste(Image.fromarray(np.concatenate(overlays, axis=1)), (0, 24))
                ImageDraw.Draw(qa).text((4, 5), f'{r["pair_id"]} MST{r["MST"]} AREA v2 | reference / measurement / application / protection', fill='black')
                qa.save(folder / 'qa.png')
                record.update(status='technical_support_available', source_path=str(norm), source_sha256=sha(norm),
                              pack_sha256=sha(pack), measurement_pixels=int(np.count_nonzero(measurement)),
                              source_dimensions=list(raw.shape), extra_same_size_resize_exact=True,
                              visual_reference_and_support_check='pending',
                              geometry_origin='reference_fixed_across_synthetic_pair_not_new_photo_validation')
                selected.append(record)
            except ValueError as e: record['reason'] = str(e)
            records.append(record); write(folder / 'packet_reference_status.json', record)
            print(f'AREA reference {r["pair_id"]}: {record["status"]} ({len(records)}/20)', flush=True)
        write(OUT / 'reference_records.json', records); write(OUT / 'selected_references.json', selected)
        for start in range(0, len(selected), 4):
            images = []
            for r in selected[start:start+4]:
                with Image.open(OUT / 'references' / r['candidate_id'] / 'qa.png') as im: images.append(im.copy())
            sheet = Image.new('RGB', (1024, 280*len(images)), 'white')
            for i, im in enumerate(images): sheet.paste(im, (0, 280*i))
            sheet.save(OUT / f'reference_contact_{start//4+1:02d}.png')
        recheck(deps)
        write(OUT / 'reference_verification.json', dict(passed=len(selected)==20, attempted=20, prepared=len(selected),
              technical_failures=20-len(selected), visual_review_pending=True, fits=0, correction_predictions=0))
        print(f'AREA reference stage complete: {len(selected)}/20;no replacements.', flush=True)
    except Exception as e:
        write(OUT / 'reference_failure.json', dict(error=repr(e), completed=len(records), retry_allowed=False)); raise


def render():
    # Reuse the unchanged verified predictor/render/export path with explicit
    # version2artifact roots. No legacy source or result file is overwritten.
    shared.OUT = OUT; shared.DELIVERY = DELIVERY; shared.PROTOCOL = PROTOCOL
    shared.render()


if __name__ == '__main__': {'prepare':prepare, 'references':references, 'render':render}[sys.argv[1]]()
