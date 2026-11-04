"""One correction-only repair replay on the 16 saved R1 cases; no fits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.skin_masking.continuous_correction import fill_correction_holes
from src.correction.seamless_blend import apply_blended
from src.ita_estimation.nostril_measurement import contract


def main():
    out = ROOT / 'outputs/continuous_correction_r2'
    if out.exists():
        raise FileExistsError(out)
    manifest = json.loads((ROOT / 'outputs/reference_readiness_r1/manifest.json').read_text())
    identity = contract(ROOT)[1]
    assert identity == manifest['measurement_contract_sha256']
    out.mkdir()
    (out / 'plan.json').write_text(json.dumps(dict(cases=[r['image_id'] for r in manifest['rows']],
        policy='fill_enclosed_correction_only_no_threshold_or_dilation',
        parameters=[.85, 1.05, .95], measurement_contract_sha256=identity,
        source_review='outputs/reference_readiness_r1_import/decisions.json'), indent=2))
    records, cards, boards = [], [], []
    for r in manifest['rows']:
        paths = r['files']
        hashes = {k: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for k, p in paths.items()}
        assert hashes == r['file_sha256']
        image = cv2.imread(str(ROOT / paths['input']))
        old = cv2.imread(str(ROOT / paths['correction_mask']), 0)
        measurement = cv2.imread(str(ROOT / paths['measurement_mask']), 0)
        fixed, report = fill_correction_holes(old)
        replay, _ = fill_correction_holes(fixed)
        assert np.array_equal(fixed, replay) and np.all(fixed[old > 0] == 255)
        _, xx = np.nonzero(measurement)
        width = int(xx.max() - xx.min() + 1)
        before, _, _ = apply_blended(image, old, [.85, 1.05, .95], face_width=width)
        after, alpha, _ = apply_blended(image, fixed, [.85, 1.05, .95], face_width=width)
        clean, _, _ = apply_blended(image, fixed, [1, 1, 1], face_width=width)
        assert np.array_equal(clean, image)
        assert np.array_equal(after[fixed == 0], image[fixed == 0])
        assert (alpha[fixed > 0] > 0).all()
        folder = out / r['key']; folder.mkdir()
        delta = np.zeros_like(image); delta[(fixed > 0) & (old == 0)] = [0, 0, 255]
        board = np.hstack((image, cv2.cvtColor(old, cv2.COLOR_GRAY2BGR),
            cv2.cvtColor(fixed, cv2.COLOR_GRAY2BGR), delta, before, after))
        for name, array in [('board.png', board), ('correction_mask.png', fixed),
                            ('alpha.png', np.rint(alpha * 255).astype(np.uint8)), ('operator_demo.png', after)]:
            assert cv2.imwrite(str(folder / name), array)
        records.append(dict(image_id=r['image_id'], **report, input_sha256=hashes,
            measurement_unchanged=True, previous_correction_approval_transferred=False))
        cards.append('<h2>' + r['key'] + ' — ' + str(report['filled_pixels']) + ' filled pixels</h2><img src="' + r['key'] + '/board.png">')
        boards.append(board)
    for i in range(4):
        cv2.imwrite(str(out / ('contact_' + str(i + 1) + '.png')), np.vstack(boards[i*4:i*4+4]))
    assert contract(ROOT)[1] == identity
    (out / 'records.json').write_text(json.dumps(records, indent=2))
    summary = dict(cases=16, changed_cases=sum(r['filled_pixels'] > 0 for r in records),
        filled_pixels=sum(r['filled_pixels'] for r in records), measurement_contract_sha256=identity,
        all_measurement_bytes_unchanged=True, identity_and_outside_preservation_pass=True,
        no_unprotected_enclosed_holes_after=True, parser_inferences=0, fits=0,
        unresolved='Outer notches, blur/lighting, glasses/beard measurement errors remain; no fitting admission')
    (out / 'verification.json').write_text(json.dumps(summary, indent=2))
    (out / 'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Correction continuity repair</title><style>body{font:18px system-ui;max-width:1600px;margin:auto;padding:20px}img{width:100%}</style><h1>Enclosed correction holes filled</h1><p>Original; old correction mask; repaired correction mask; added pixels in red; old illustrative rendering; repaired illustrative rendering. Fixed settings, not model predictions. Measurement unchanged. Outer notches are not enclosed holes and remain unresolved. Prior masks and user decisions preserved.</p>' + ''.join(cards), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
