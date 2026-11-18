"""One bounded MST-labelled formative-feedback packet; frozen model, no training."""
from pathlib import Path
from collections import Counter
import base64
import csv
import hashlib
import importlib
import json
import sys
import zipfile
import numpy as np
import cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wb314_research_predictor import FrozenWB314, validate_inputs, MODEL_SHA256
from src.skin_masking.correction_preview import render_preview
from src.distortion_generation.camera_inspired_halfstop import generate
from src.evaluation.luminance_chroma_scalar import replay
from wb_feature_direct_verify import route

OUT = ROOT / 'outputs/wb314_mste_development_packet_v1'
DELIVERY = ROOT / 'output/wb314-mst-development-feedback-2026-11-18'
PROTOCOL = ROOT / 'docs/wb314-mste-development-feedback-protocol-2026-11-18.md'
CATALOG = ROOT / 'data/raw/mst-e_data/mst-e_image_details.csv'
MAPPING = ROOT / 'outputs/mst_square256_measurement_v1/summary.json'
MODEL = ROOT / 'outputs/wb314_final_training_v1/model.json'


def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d):
    with Path(p).open('x', encoding='utf-8') as f: json.dump(d, f, indent=2, allow_nan=False)
def recheck(bindings):
    for p, h in bindings.items():
        if sha(p) != h: raise ValueError('Bound input changed: ' + str(p))


def prepare():
    if OUT.exists() or DELIVERY.exists(): raise FileExistsError('Preserve previous attempt')
    helper = importlib.import_module('419_preview_object_protected_face')
    deps, identity = helper.dependencies(); recheck(deps)
    assert (ROOT / 'outputs/faceocc_inference_env_v1/Scripts/python.exe').is_file()
    assert sha(MODEL) == MODEL_SHA256
    assessment = ROOT / 'outputs/wb314_mste_evaluation_metadata_v1'
    assert read(assessment / 'verification.json')['passed'] and read(assessment / 'independent_audit.json')['passed']
    with CATALOG.open(encoding='utf-8-sig', newline='') as f: catalog = list(csv.DictReader(f))
    old = read(MAPPING); exposed = {r['image_id']: r for r in old['records']}
    closed = {r['subject_id'] for r in read(ROOT / 'outputs/additional_mst_eligibility_v1/summary.json')['records']}
    expected = {str(Path(p).resolve()).casefold(): h for p, h in old['input_sha256'].items()}
    pool = {}
    for r in catalog:
        case = 'mst_e__' + r['subject_name'] + '/' + r['image_ID']
        if (case not in exposed or r['subject_name'] in closed or r['lighting'] != 'well_lit'
                or r['mask'] != '0' or r['pose'] not in ['frontal', 'facing_camera']): continue
        prior = exposed[case]
        assert int(r['MST']) == int(prior['source_mst_label']) and r['subject_name'] == prior['subject_id']
        p = Path(prior['source_path']).resolve()
        assert p.parent == (ROOT / 'data/raw/mst-e_data' / r['subject_name']).resolve() and p.name == r['image_ID']
        item = dict(case_id=case, subject_id=r['subject_name'], MST=int(r['MST']),
                    source_path=str(p), source_sha256=expected[str(p).casefold()],
                    lighting=r['lighting'], pose=r['pose'], recorded_mask=r['mask'])
        assert case not in pool
        pool[case] = item
    selection = []
    def rank(r): return hashlib.sha256(('wb314-mste-development-feedback-v1|' + r['case_id']).encode()).hexdigest()
    for label in range(1, 11):
        own = sorted((r for r in pool.values() if r['MST'] == label), key=rank)
        assert len(own) >= 3
        first = own.pop(0)
        second = next((r for r in own if r['subject_id'] != first['subject_id']), own[0]); own.remove(second)
        for number, item in enumerate([first, second, own[0]], 1):
            selection.append(dict(item, candidate_id=f'mst{label:02d}_candidate{number:02d}', priority=number))
    assert len(selection) == len({r['case_id'] for r in selection}) == 30
    paths = [PROTOCOL, CATALOG, MAPPING, MODEL, Path(__file__), ROOT / 'scripts/wb314_research_predictor.py',
             ROOT / 'src/distortion_generation/camera_inspired_halfstop.py',
             ROOT / 'src/model_training/luminance_chroma_operator.py',
             ROOT / 'src/evaluation/luminance_chroma_scalar.py',
             ROOT / 'outputs/wb314_final_changed_ratings_v1/verification.json',
             ROOT / 'outputs/wb314_research_inference_v1/verification.json',
             ROOT / 'outputs/wb314_expert_instrument_respondent_access_v1/instrument_summary.json']
    deps.update({str(p): sha(p) for p in paths}); recheck(deps)
    OUT.mkdir(); (OUT / 'references').mkdir()
    write(OUT / 'bindings.json', deps)
    write(OUT / 'plan.json', dict(authorization='Okay lets do that.', stage='development_expert_feedback',
          selection=selection, candidate_budget=30, final_slots=20, model_sha256=MODEL_SHA256,
          masking_contract_sha256=identity, official_MST_used_as_predictor_input=False,
          glasses_policy='fully_protected_opaque_or_unknown', no_fit=True,
          conditions_per_MST=['combined_under', 'combined_over'], independent_final_evaluation=False,
          source_history='All candidates are among the418previously exposed mapping-development images',
          source_hashes='Old source hashes frozen here; rechecked before any decode',
          no_quality_based_output_replacement=True))
    print('FROZEN30reference candidates/20slots/all10publisher MST labels;0source images decoded.', flush=True)


def references():
    if (OUT / 'reference_started.json').exists(): raise FileExistsError('No reference-run restart')
    recheck(read(OUT / 'bindings.json')); plan = read(OUT / 'plan.json')
    helper = importlib.import_module('419_preview_object_protected_face')
    valid = {}; source_checks = []
    for r in plan['selection']:
        p = Path(r['source_path'])
        try: actual = sha(p)
        except OSError as e: actual = None
        okay = actual == r['source_sha256']
        valid[r['candidate_id']] = okay
        source_checks.append(dict(candidate_id=r['candidate_id'], matches=okay, actual_sha256=actual))
    write(OUT / 'source_hash_checks.json', source_checks)
    write(OUT / 'reference_started.json', dict(plan_sha256=sha(OUT / 'plan.json'), fits=0))
    records = []; selected = []
    try:
        for label in range(1, 11):
            accepted = 0
            for r in [r for r in plan['selection'] if r['MST'] == label]:
                if accepted == 2: break
                folder = OUT / 'references' / r['candidate_id']; folder.mkdir()
                record = dict(r, status='failed', scientific_admission=False)
                try:
                    if not valid[r['candidate_id']]: raise ValueError('Source missing or differs from frozen original hash')
                    hashes = dict(read(OUT / 'bindings.json')); hashes[r['source_path']] = r['source_sha256']
                    image, facial, categories, points, visible, metadata = helper.prepare_photo(Path(r['source_path']), folder, hashes)
                    report = read(folder / 'measurement_report.json')
                    if report['status'] != 'success': raise ValueError(report.get('reason', 'Measurement unavailable'))
                    measurement = cv2.imread(str(folder / 'candidate_measurement_mask.png'), cv2.IMREAD_GRAYSCALE)
                    preview = render_preview(image, facial, categories, points, visible, glasses='opaque', parameters=(1., 1., 1.))
                    rgb = image[:, :, ::-1].copy()
                    validate_inputs(rgb, measurement, preview.alpha, preview.protected)
                    pack = folder / 'reference_support.npz'
                    np.savez(pack, reference=rgb, measurement=measurement, alpha=preview.alpha, protected=preview.protected)
                    m = rgb.copy(); chosen = measurement > 0
                    m[chosen] = np.rint(.55 * m[chosen] + .45 * np.array([0, 220, 0])).astype(np.uint8)
                    a = rgb.copy(); chosen = preview.alpha > 0
                    a[chosen] = np.rint(.55 * a[chosen] + .45 * np.array([0, 220, 220])).astype(np.uint8)
                    p = rgb.copy(); chosen = preview.protected
                    p[chosen] = np.rint(.55 * p[chosen] + .45 * np.array([220, 0, 0])).astype(np.uint8)
                    row = Image.new('RGB', (1024, 280), 'white'); row.paste(Image.fromarray(np.concatenate([rgb, m, a, p], axis=1)), (0, 24))
                    ImageDraw.Draw(row).text((4, 5), f'{r["candidate_id"]} | MST {label} | reference / measurement / application / protection', fill='black')
                    row.save(folder / 'qa.png')
                    record.update(status='technical_support_available', pack_sha256=sha(pack),
                                  measurement_pixels=int(np.count_nonzero(measurement)),
                                  application_pixels=int(np.count_nonzero(preview.alpha)),
                                  visual_reference_and_support_check='pending',
                                  geometry_origin='reference_fixed_across_synthetic_pair_not_new_photo_validation')
                    accepted += 1
                    selected.append(dict(record, pair_id=f'image_pair_{2*(label-1)+accepted:02d}',
                                         condition='combined_under' if accepted == 1 else 'combined_over'))
                except ValueError as e:
                    record.update(reason=str(e))
                records.append(record)
                write(folder / 'packet_reference_status.json', record)
                print(f'Reference {r["candidate_id"]}: {record["status"]}; category slots {accepted}/2', flush=True)
        write(OUT / 'reference_records.json', records)
        write(OUT / 'selected_references.json', selected)
        for start in range(0, len(selected), 4):
            rows = []
            for r in selected[start:start+4]:
                with Image.open(OUT / 'references' / r['candidate_id'] / 'qa.png') as im: rows.append(im.copy())
            sheet = Image.new('RGB', (1024, 280 * len(rows)), 'white')
            for i, im in enumerate(rows): sheet.paste(im, (0, i * 280))
            sheet.save(OUT / f'reference_contact_{start//4+1:02d}.png')
        recheck(read(OUT / 'bindings.json'))
        write(OUT / 'reference_verification.json', dict(passed=len(selected) == 20, attempted=len(records),
              prepared=len(selected), technical_failures=sum(r['status'] == 'failed' for r in records),
              max_attempts=30, visual_review_pending=True, fits=0, correction_predictions=0))
        print(f'REFERENCE STAGE complete: {len(selected)}/20slots;{len(records)}attempts. Visual check pending.', flush=True)
    except Exception as e:
        write(OUT / 'reference_failure.json', dict(error=repr(e), completed=len(records), retry_allowed=False)); raise


def render():
    if (OUT / 'render_started.json').exists() or DELIVERY.exists(): raise FileExistsError('Preserve existing render/delivery')
    assert read(OUT / 'reference_verification.json')['passed']
    visual = read(OUT / 'reference_visual_check.json')
    assert visual['ready_for_formative_packet'] and visual['independent_segmentation_truth'] is False
    recheck(read(OUT / 'bindings.json')); rows = read(OUT / 'selected_references.json')
    assert len(rows) == 20 and len({r['pair_id'] for r in rows}) == 20
    for r in rows:
        assert sha(OUT / 'references' / r['candidate_id'] / 'reference_support.npz') == r['pack_sha256']
    predictor = FrozenWB314()
    write(OUT / 'render_started.json', dict(model_sha256=sha(MODEL), actual_model_fits=0, slots=20))
    (OUT / 'evaluation').mkdir(); records = []
    try:
        for r in rows:
            with np.load(OUT / 'references' / r['candidate_id'] / 'reference_support.npz', allow_pickle=False) as z:
                reference, measurement, alpha, protected = [z[k].copy() for k in ['reference', 'measurement', 'alpha', 'protected']]
            image, operation = generate(reference, r['condition'])
            before = [a.tobytes() for a in [reference, image, measurement, alpha, protected]]
            result = predictor.correct(image, measurement, alpha, protected)
            leaf, controls = route(predictor.model, result['features'])
            assert controls == result['controls'] and leaf == result['leaf']
            scalar, _ = replay(image, image, alpha, protected, controls)
            assert np.array_equal(scalar, result['output'])
            assert before == [a.tobytes() for a in [reference, image, measurement, alpha, protected]]
            path = OUT / 'evaluation' / (r['pair_id'] + '.npz')
            np.savez(path, reference=reference, input=image, candidate=result['output'], measurement=measurement, alpha=alpha, protected=protected)
            records.append(dict(r, controls=controls, leaf=leaf, features=result['features'], operation=operation,
                                evaluation_sha256=sha(path), scalar_RGB8_exact=True, arrays_immutable=True))
            print('Frozen model/scalar verification ' + str(len(records)) + '/20', flush=True)
        recheck(read(OUT / 'bindings.json')); assert sha(MODEL) == MODEL_SHA256
        write(OUT / 'predictions_sealed.json', dict(model_sha256=MODEL_SHA256, records=records,
              sealed_before_quality_scoring=True, reference_error_analysis_performed=False, fits=0))
        DELIVERY.mkdir(); (DELIVERY / 'pairs').mkdir(); sections = []; manifest = []
        for r in records:
            with np.load(OUT / 'evaluation' / (r['pair_id'] + '.npz'), allow_pickle=False) as z:
                reference, candidate = z['reference'], z['candidate']
            pair = np.concatenate([reference, candidate], axis=1)
            path = DELIVERY / 'pairs' / (r['pair_id'] + f'_mst{r["MST"]:02d}.png')
            Image.fromarray(pair).save(path)
            with Image.open(path) as im: assert np.array_equal(np.asarray(im), pair)
            number = int(r['pair_id'].split('_')[-1])
            title = f'Image Pair {number:02d} - MST Category: {r["MST"]:02d}'
            manifest.append(dict(pair_id=r['pair_id'], Form_section=title, MST=r['MST'],
                                 subject_id=r['subject_id'], case_id=r['case_id'], condition=r['condition'],
                                 png=path.relative_to(DELIVERY).as_posix(), png_sha256=sha(path),
                                 evaluation_sha256=r['evaluation_sha256']))
            sections.append(f'<section><h2>{title}</h2><p>Photographic reference (left) | WB314 correction (right)</p><img width="512" height="256" alt="Reference left and correction right" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"></section>')
        write(DELIVERY / 'manifest_PRIVATE.json', dict(stage='during_development_feedback', model_sha256=MODEL_SHA256,
              cases=manifest, source_subjects=len({r['subject_id'] for r in records}),
              official_MST_provenance='Publisher subject labels, not model predictions',
              known_source_exposure=True, independent_final_evaluation=False, expert_responses=0))
        page = '<!doctype html><meta charset="utf-8"><title>MST-labelled WB314 development feedback</title><style>body{font:17px system-ui;max-width:900px;margin:24px auto;padding:0 20px}section{border-top:1px solid #aaa;margin:25px 0}img{max-width:100%;height:auto}</style><h1>WB314: development-stage expert feedback</h1><p>20pairs, two per publisher MST category. Reference left, frozen research correction right. These are previously exposed development subjects, not an independent final test. Use your existing Form questions, rating scale and comments unchanged.</p>' + ''.join(sections)
        (DELIVERY / 'gallery.html').write_text(page, encoding='utf-8')
        guide = ('MST-labelled WB314 initial expert-feedback images\n\n'
                 'Use all20pairs in the numbered existing Form sections. Match the MST category in each filename and heading. Each PNG has the source photographic reference on the left and frozen WB314 correction on the right.\n\n'
                 'Keep consent, evaluator information, overall1-5rating and comments unchanged. The existing score combines exposure, colour and texture into overall quality; it does not produce four separate numerical MOS columns. No Form content has been edited or uploaded by this preparation.\n\n'
                 'This is during-development feedback to guide refinement. Publisher MST labels are used for grouping. Photos repeat known development subjects;20pairs do not mean20independent people. These are256px processed-image comparisons with reference-derived fixed support, assumed sRGB and two fixed joint exposure/colour perturbations. They do not establish calibrated intrinsic colour, automatic-new-photo validity, validated MST estimation, final fairness or Android performance.\n\n'
                 'No ratings, expert participation or invitation sending is assumed. Preserve this model version and image membership when collecting genuine feedback. Keep later refinement rounds and final appraisal separate.\n')
        (DELIVERY / 'upload-instructions.txt').write_text(guide, encoding='utf-8')
        proof = dict(passed=True, model_sha256=MODEL_SHA256, pairs=20, publisher_MST_categories=10,
                     slots_per_category=2, subjects=len({r['subject_id'] for r in records}),
                     subject_counts_by_MST={str(k): len({r['subject_id'] for r in records if r['MST'] == k}) for k in range(1, 11)},
                     condition_counts=dict(Counter(r['condition'] for r in records)),
                     portable_route_checks=20, exact_scalar_RGB8_checks=20, exact_PNG_roundtrips=20,
                     actual_model_fits=0, questions_changed=False, Form_edits=0, uploads=0, expert_responses=0,
                     independent_final_evaluation=False, dataset_training=False,
                     reference_attempts=read(OUT / 'reference_verification.json')['attempted'],
                     artifacts={p.relative_to(DELIVERY).as_posix(): sha(p) for p in DELIVERY.rglob('*') if p.is_file()})
        write(DELIVERY / 'verification.json', proof); write(OUT / 'verification.json', proof)
        with zipfile.ZipFile(DELIVERY / 'expert-images.zip', 'x', zipfile.ZIP_DEFLATED) as z:
            for p in sorted((DELIVERY / 'pairs').glob('*.png')): z.write(p, p.relative_to(DELIVERY).as_posix())
            z.write(DELIVERY / 'upload-instructions.txt', 'upload-instructions.txt')
        print('PACKET VERIFIED20MST-labelled pairs;0fits/questions changed/expert responses.', flush=True)
    except Exception as e:
        write(OUT / 'render_failure.json', dict(error=repr(e), completed=len(records), retry_allowed=False)); raise


if __name__ == '__main__': {'prepare': prepare, 'references': references, 'render': render}[sys.argv[1]]()
