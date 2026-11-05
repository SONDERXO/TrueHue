"""One fixed FFHQ support diagnostic; no training or calibration admission."""
import argparse
import hashlib
import html
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
import cv2
import numpy as np
from scipy.io import loadmat
from src.utilities.config import get_config
from src.ita_estimation.nostril_measurement import measure
from src.ita_estimation.faceocc_development import contract, evaluate_parent
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.face_parsing_experiment import DenseFaceParser
from src.skin_masking.full_face_support import build_full_face_support
from src.skin_masking.continuous_correction import continuous_support
from src.correction.seamless_blend import apply_blended

OUT = ROOT/'outputs/ffhq_mask_support_v1'
IDS = '54632 39568 29617 29863 16061 52445 32685 53146 48879 49131 59807 46795'.split()
read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def save(path, array):
    if not cv2.imwrite(str(path), array):
        raise IOError(str(path))


def overlay(image, mask, color):
    result = image.copy(); selected = mask > 0
    result[selected] = np.rint(.6*image[selected]+.4*np.array(color)).astype(np.uint8)
    return result


def historical_hashes():
    folder = ROOT/'outputs/integrated_correction_plan_v1'
    sources = read(folder/'source_hashes.json')
    hashes = {str(ROOT/k): v for k, v in sources.items()}
    for name, digest in read(folder/'parent_manifest_hashes.json').items():
        hashes[str(ROOT/'outputs'/name/'sha256.json')] = digest
    for name, digest in read(ROOT/'outputs/correction_training_readiness_plan_v1/parent_manifest_hashes.json').items():
        hashes[str(ROOT/'outputs'/name/'sha256.json')] = digest
    assert all(sha(p) == h for p, h in hashes.items())
    return hashes


def prepare():
    if OUT.exists():
        raise FileExistsError(OUT)
    cfg = get_config(); spec, identity = contract(ROOT)
    parent = ROOT/'outputs/ffhq_source_preparation_v1'
    sources = read(parent/'attempts.json')
    assert [r['id'] for r in sources] == IDS
    assert [r['id'] for r in read(parent/'selected_before_pixels.json')['sources']] == IDS
    hashes = historical_hashes()
    for k, v in read(parent/'sha256.json').items():
        assert sha(parent/k) == v
        hashes[str(parent/k)] = v
    def bind_contract(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == 'dependency_sha256':
                    hashes.update({str(ROOT/p): h for p, h in v.items()})
                else:
                    bind_contract(v)
    bind_contract(spec)
    for path in [Path(__file__), ROOT/'scripts/415_run_ffhq_support_logits.py',
                 ROOT/'scripts/369_run_faceocc_logits.py',
                 ROOT/'docs/ffhq-mask-support-protocol-2026-11-05.md',
                 ROOT/'src/skin_masking/face_neck_support.py',
                 ROOT/'src/skin_masking/continuous_correction.py',
                 ROOT/'src/correction/seamless_blend.py', ROOT/'src/distortion_generation/paper_gamma.py']:
        hashes[str(path)] = sha(path)
    for r in sources:
        assert r['access']['success'] and sha(ROOT/r['path']) == r['access']['sha256']
        hashes[str(ROOT/r['path'])] = r['access']['sha256']
    assert all(sha(p) == h for p, h in hashes.items())
    OUT.mkdir(); (OUT/'logits').mkdir()
    write(OUT/'plan.json', dict(status='frozen_before_inference', sources=sources,
          contract=spec, contract_sha256=identity, input_sha256=hashes,
          MST=None, training_admitted=False, calibration_admitted=False))
    helper = importlib.import_module('11_prepare_training_manifests')
    detector = lambda im: helper._detect_face_boxes(im, ROOT/cfg.FACE_MODEL_PATH, .85)
    net = DenseFaceParser(ROOT/cfg.MODELS_ROOT/'face_parser_experimental_v1/resnet18.onnx')
    template = loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records = []; attempts = []
    for i, row in enumerate(sources, 1):
        folder = OUT/row['id']; folder.mkdir(); cached = {}
        rec = dict(id=row['id'], case_index=i, source_path=row['path'],
                   correction_status='unavailable', measurement_status='unavailable',
                   MST=None, training_admitted=False, calibration_admitted=False)
        def landmarks(im, box):
            points, margin, status = helper.detect_landmarks_with_margin(im, box, ROOT/cfg.FACE_LANDMARKER_MODEL_PATH)
            cached['landmark_detail'] = dict(margin=margin, status=status)
            cached['points'] = None if points is None else points+np.array(box[:2])
            return cached['points']
        class Parser:
            def categories_bgr(self, im):
                cached['categories'] = net.categories_bgr(im)
                return cached['categories']
        try:
            image = cv2.imread(str(ROOT/row['path']))
            result = measure(image, detector, landmarks, Parser())
            rec['parent_report'] = result.report
            rec['landmark_detail'] = cached.get('landmark_detail')
            if result.image is not None:
                save(folder/'input.png', result.image)
            if cached.get('points') is not None:
                np.save(folder/'landmarks.npy', cached['points'])
            if 'categories' in cached:
                save(folder/'categories.png', cached['categories'])
            if result.mask is not None:
                save(folder/'baseline_mask.png', result.mask)
            if result.report['status'] == 'success':
                # These stages are independent: a support failure must not prevent FaceOcc.
                try:
                    support = continuous_support(build_full_face_support(result.image, result.mask,
                        cached['categories'], cached['points'], face_count=1))
                    _, x = np.nonzero(result.mask); width = int(x.max()-x.min()+1)
                    demo, alpha, blend = apply_blended(result.image, support.correction_mask,
                        [.85, 1.05, .95], face_width=width)
                    neutral, _, _ = apply_blended(result.image, support.correction_mask,
                        [1., 1., 1.], face_width=width)
                    assert np.array_equal(neutral, result.image)
                    outside = support.correction_mask == 0
                    assert not alpha[outside].any() and np.array_equal(demo[outside], result.image[outside])
                    for name, array in [('correction_mask', support.correction_mask),
                         ('neck_mask', support.neck_mask), ('support_measurement_mask', support.measurement_mask),
                         ('operator_demo', demo), ('correction_alpha', np.rint(alpha*255).astype(np.uint8))]:
                        save(folder/(name+'.png'), array)
                    np.save(folder/'alpha.npy', alpha)
                    shown = overlay(result.image, support.correction_mask, [0,255,0])
                    shown = overlay(shown, support.neck_mask, [255,255,0])
                    save(folder/'correction_overlay.png', shown)
                    rec.update(correction_status='technical_success', support_report=support.report,
                        blend_report=blend, correction_pixels=int((support.correction_mask>0).sum()),
                        neck_pixels=int((support.neck_mask>0).sum()),
                        correction_touches_border=bool(np.any(np.concatenate((support.correction_mask[0],support.correction_mask[-1],support.correction_mask[:,0],support.correction_mask[:,-1])))),
                        neutral_identity_verified=True, outside_unchanged_verified=True)
                except (ValueError, RuntimeError, cv2.error) as error:
                    rec['correction_failure'] = str(error)
                try:
                    aligned, matrix, bridge = align_input(result.image, cached['points'], template)
                    save(folder/'aligned.png', aligned)
                    rec.update(measurement_status='inference_ready', matrix=matrix.tolist(), bridge=bridge)
                    attempts.append(dict(image_id=row['id'], case_index=i, aligned_path=str(folder/'aligned.png')))
                except ValueError as error:
                    rec['measurement_failure'] = str(error)
            else:
                rec['measurement_failure'] = result.report.get('reason')
        except (ValueError, RuntimeError, cv2.error) as error:
            rec['processing_failure'] = str(error)
        records.append(rec)
        write(folder/'preparation.json', rec)
        print(row['id']+' '+rec['correction_status']+' '+rec['measurement_status'], flush=True)
    write(OUT/'baseline.json', records)
    assert all(sha(p) == h for p, h in hashes.items())
    for p in OUT.rglob('*'):
        if p.is_file():
            hashes[str(p)] = sha(p)
    write(OUT/'inference_plan.json', dict(attempts=attempts, input_sha256=hashes))


def finalize():
    if (OUT/'results.json').exists():
        raise FileExistsError('Already finalized')
    plan = read(OUT/'inference_plan.json'); run = read(OUT/'inference.json')
    assert run['plan_sha256'] == sha(OUT/'inference_plan.json')
    assert all(sha(p) == h for p, h in plan['input_sha256'].items())
    predictions = {r['image_id']: r for r in run['records']}
    assert set(predictions) == {r['image_id'] for r in plan['attempts']}
    template = loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records = read(OUT/'baseline.json'); cards = []; sheets = []; replays = 0
    for rec in records:
        folder = OUT/rec['id']; image = cv2.imread(str(folder/'input.png'))
        if rec['measurement_status'] == 'inference_ready':
            pred = predictions[rec['id']]
            if pred['status'] == 'success':
                path = OUT/pred['logits_path']; assert sha(path) == pred['logits_sha256']
                parent = SimpleNamespace(report=rec['parent_report'], image=image,
                    mask=cv2.imread(str(folder/'baseline_mask.png'), 0))
                points = np.load(folder/'landmarks.npy', allow_pickle=False)
                logits = np.load(path, allow_pickle=False)
                result = evaluate_parent(parent, points, template, lambda _: logits)
                replay = evaluate_parent(parent, points, template, lambda _: logits)
                assert result.report == replay.report
                if result.mask is not None:
                    assert np.array_equal(result.mask, replay.mask)
                    assert not result.mask[parent.mask == 0].any()
                    save(folder/'candidate_mask.png', result.mask)
                    save(folder/'measurement_overlay.png', overlay(image, result.mask, [0,255,0]))
                    selected = image.copy(); selected[result.mask == 0] = 35
                    save(folder/'selected.png', selected)
                assert np.array_equal(result.aligned, cv2.imread(str(folder/'aligned.png')))
                assert result.report['mst'] is None and not result.report['training_admitted']
                rec.update(measurement_status=result.report['status'], candidate_report=result.report)
                replays += 1
            else:
                rec.update(measurement_status='inference_failed', measurement_failure=pred['reason'])
        if image is not None:
            panels = [image]
            for name in ['correction_overlay.png','measurement_overlay.png','selected.png','operator_demo.png']:
                panel = cv2.imread(str(folder/name)) if (folder/name).exists() else np.full_like(image, 50)
                panels.append(panel)
            board = np.hstack(panels); save(folder/'board.png', board)
            label = np.full((26, board.shape[1], 3), 255, np.uint8)
            cv2.putText(label, rec['id']+' correction='+rec['correction_status']+' measurement='+rec['measurement_status'],
                        (5,18), cv2.FONT_HERSHEY_SIMPLEX, .45, (0,0,0), 1)
            sheets.append(np.vstack([label,board]))
        rec['file_sha256'] = {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        cards.append('<section><h2>'+rec['id']+'</h2><p>'+html.escape(rec['correction_status']+'; measurement '+rec['measurement_status'])+
                     '</p><img src="'+rec['id']+'/board.png"><p><a href="'+rec['id']+'/input.png">Working input</a> · '+
                     '<a href="../../'+rec['source_path']+'">Original 1024px photo</a></p></section>')
    for i in range(0,len(sheets),3):
        save(OUT/f'contact_{i//3+1}.png', np.vstack(sheets[i:i+3]))
    assert [r['id'] for r in records] == IDS
    assert all(sha(p) == h for p, h in plan['input_sha256'].items())
    historical_hashes()
    result = dict(records=records, total=12, forwards=run['forwards'], saved_service_replays=replays,
        correction_successes=sum(r['correction_status']=='technical_success' for r in records),
        measurement_successes=sum(r['measurement_status']=='success' for r in records),
        training_admissions=0, MST_fits=0, tree_fits=0, target_fits=0, new_variants=0,
        pinned_history_unchanged=True, source_hashes_unchanged=True,
        actual_skin_validity='unverified', scientific_admission=False, human_review_requested=False,
        contract_sha256=read(OUT/'plan.json')['contract_sha256'])
    write(OUT/'results.json', result)
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>FFHQ support feasibility</title>'+
        '<style>body{font:18px system-ui;max-width:1450px;margin:auto;padding:20px}img{width:100%}section{border-top:1px solid #aaa}</style>'+
        '<h1>Same twelve FFHQ sources: support feasibility</h1><p>Original working input; correction (green face/cyan neck); '+
        'FaceOcc measurement (green); measurement pixels only; illustrative fixed-setting operator. '+
        'Whole-frame 256px analysis, not full-resolution validation. Occluders inside the face belong to correction by design. '+
        'Technical success is not admission. MST deferred; no training or annotation task.</p>'+
        '<p><a href="../ffhq_source_visual_assessment_v1/review.html">Attribution and source limitations</a></p>'+''.join(cards), encoding='utf-8')
    write(OUT/'sha256.json', {p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--finalize', action='store_true')
    finalize() if parser.parse_args().finalize else prepare()
