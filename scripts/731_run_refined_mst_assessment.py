"""Run exactly the authorized ten-fold isotonic assessment; no image reads."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sklearn
from src.demo.labelled_measurement import digest, write
from src.ita_estimation.refined_mst_assessment import assess

OUT = ROOT / 'outputs/refined_mst_assessment_v1'
DESIGN = ROOT / 'outputs/refined_mst_grouped_design_v1'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve all completed or partial assessment outputs')
    read = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))
    receipt = read(DESIGN / 'review_and_fold_verification_PRIVATE.json')
    assert receipt['passed']
    # Metadata/protocol/code only. Existing image hashes remain inherited rather
    # than reopening photographs or masks merely to verify this metadata stage.
    bound = dict(receipt['input_sha256'])
    for p in list(bound):
        if p.endswith('.png'):
            del bound[p]
    for p, h in bound.items():
        assert digest(p) == h
    for p in [Path(__file__), ROOT / 'src/ita_estimation/refined_mst_assessment.py',
              ROOT / 'docs/refined-mst-grouped-design-2026-11-10.md',
              DESIGN / 'review_and_fold_verification_PRIVATE.json']:
        bound[str(p)] = digest(p)
    rows = read(DESIGN / 'rows_PRIVATE.json')
    folds = read(DESIGN / 'folds_PRIVATE.json')
    assert len(rows) == 30 and len(folds) == 10
    OUT.mkdir()
    write(OUT / 'execution_plan_PRIVATE.json', dict(input_sha256=bound,
        sklearn_version=sklearn.__version__, authorized_calibration_fits=10,
        method_sha256=rows[0]['measurement_method_sha256'], correction_tree_fits=0))
    result = assess(rows, folds)
    assert result['calibration_fits'] == 10 and len(result['predictions']) == 30
    assert all(digest(p) == h for p, h in bound.items())
    write(OUT / 'results_PRIVATE.json', result)
    print(json.dumps(dict(metrics=result['metrics'], by_condition=result['by_condition']), indent=2))


if __name__ == '__main__':
    main()
