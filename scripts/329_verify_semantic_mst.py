"""Replay saved measurements/calibration; prepare a bounded diagnostic gallery."""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from sklearn.isotonic import IsotonicRegression
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.ita_estimation.semantic_measurement import contract
from src.ita_estimation.square_measurement import contract as legacy_contract
from src.model_training.facial_endpoint_features import facial_endpoint_features


def main():
    source = ROOT / 'outputs/semantic_mst_measurement_v1'
    out = ROOT / 'outputs/semantic_mst_verification_v1'
    if out.exists():
        raise FileExistsError(out)
    measured = json.loads((source / 'summary.json').read_text())
    plan = json.loads((source / 'plan.json').read_text())
    report = json.loads((ROOT / 'outputs/semantic_mst_calibration_v1/summary.json').read_text())
    rows = measured['records']; byid = {r['image_id']: r for r in rows}
    assert contract(ROOT)[1] == report['measurement_contract_sha256'] == plan['measurement_contract_sha256']
    assert legacy_contract(ROOT)[1] == plan['legacy_measurement_contract_sha256']
    assert len(rows) == len(byid) == 418
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert all(digest(Path(p)) == value for p, value in measured['input_sha256'].items())
    # Selection ignores outcomes: exactly one hash-selected attempt per subject.
    selected = {min((r['image_id'] for r in rows if r['subject_id'] == subject),
                    key=lambda name: hashlib.sha256(('semantic-qa-v1/'+name).encode()).hexdigest())
                for subject in {r['subject_id'] for r in rows}}
    out.mkdir(); (out / 'boards').mkdir()
    (out / 'diagnostic_selection.json').write_text(json.dumps(dict(
        rule='One deterministic hash-selected attempt per subject, no success/label/lighting filter',
        image_ids=sorted(selected), not_a_quality_approval=True), indent=2))
    replays = 0; cards = []
    for row in rows:
        if row.get('mask_path'):
            path = source / row['mask_path']
            assert digest(path) == row['mask_sha256']
            mask = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            assert mask.shape == (256, 256) and set(np.unique(mask)) <= {0, 255}
            image = cv2.resize(cv2.imread(row['source_path']), (256, 256), interpolation=cv2.INTER_LINEAR)
            stats = compute_masked_lab_statistics(image, mask, 1000)
            assert stats == row['statistics']
            if row['status'] == 'success':
                values = {f'input_{k}': stats[k] for k in ('mean_l_star', 'mean_a_star', 'mean_b_star', 'ita_degrees')}
                values.update(facial_endpoint_features(image, mask > 0)['features'])
                assert values == row['features']; replays += 1
            if row['image_id'] in selected:
                alpha = .45 * (mask > 0)[:, :, None]
                overlay = np.rint(image * (1-alpha) + np.array([0, 255, 0]) * alpha).astype(np.uint8)
                board = out / 'boards' / (row['image_id'].replace('/', '_') + '.png')
                assert cv2.imwrite(str(board), np.hstack((image, overlay, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))))
                cards.append(f'<section><h2>{html.escape(row["subject_id"])}</h2><p>{html.escape(row["image_id"])}</p><img src="boards/{html.escape(board.name)}"><p>Unreviewed candidate. Inspect hair, glasses, mouth, background and missing skin.</p></section>')
        elif row['image_id'] in selected:
            cards.append(f'<section><h2>{html.escape(row["subject_id"])}</h2><p>{html.escape(row["image_id"])} — processing failed: {html.escape(row.get("reason", "unavailable"))}</p></section>')
    refits = 0
    for saved in report['fold_models']:
        training = [byid[i] for i in saved['fit_image_ids']]
        counts = Counter(r['subject_id'] for r in training)
        assert saved['held_subject'] not in counts
        expected = {r['image_id'] for r in rows if r['status'] == 'success' and r['subject_id'] != saved['held_subject']}
        assert set(saved['fit_image_ids']) == expected
        weights = [1/counts[r['subject_id']] for r in training]
        assert weights == saved['fit_image_weights']
        model = IsotonicRegression(increasing=False, out_of_bounds='clip', y_min=1, y_max=10)
        model.fit([r['features']['input_ita_degrees'] for r in training],
                  [r['source_mst_label'] for r in training], sample_weight=weights)
        assert model.X_thresholds_.tolist() == saved['x_knots'] and model.y_thresholds_.tolist() == saved['y_knots']
        refits += 1
    assert replays == measured['successes'] == len(report['predictions'])
    page = '<!doctype html><meta charset="utf-8"><title>Fuller-face MST measurement diagnostics</title><style>body{font:18px system-ui;max-width:1000px;margin:30px auto;padding:20px}img{max-width:100%}section{border-top:1px solid #aaa;margin-top:30px}</style><h1>Fuller-face measurement diagnostics</h1><p>One fixed attempt per previously exposed development subject. Left: input; middle: selected skin; right: binary mask. These are not ground truth or approved masks. No new review is requested by this page.</p>' + ''.join(cards)
    (out / 'diagnostics.html').write_text(page, encoding='utf-8')
    result = dict(status='passed', measured_feature_replays=replays, candidate_refit_replays=refits,
                  source_separation=True, legacy_contract_unchanged=True,
                  diagnostic_attempts=len(selected), new_mask_approvals=0,
                  reserved_correction_pixel_access=0, new_scientific_candidates=0,
                  measurement_contract_sha256=report['measurement_contract_sha256'])
    (out / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
