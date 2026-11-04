"""Import the user's six new-mask decisions without training or auto-admission."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_preparation.semantic_mask_review import reconcile
from src.ita_estimation.semantic_measurement import contract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('decisions', type=Path)
    args = parser.parse_args()
    manifest = ROOT / 'outputs/semantic_reference_readiness_v1/manifest.json'
    out = ROOT / 'outputs/semantic_reference_mask_import_v1'
    if out.exists():
        raise FileExistsError('Preserve the existing import; revisions need a separate version')
    raw = args.decisions.read_bytes(); data = json.loads(raw)
    rows = reconcile(manifest.read_bytes(), data, ROOT, contract(ROOT)[1])
    out.mkdir()
    (out / 'decisions.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    result = dict(status='complete_exact_mask_decisions_imported_not_training_admission',
        decisions=dict(Counter(r['mask_decision'] for r in rows)),
        original_export_sha256=hashlib.sha256(raw).hexdigest(), manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        source_reviews_repeated=0, automatic_training_admissions=0, model_fits=0,
        measurement_contract_sha256=contract(ROOT)[1])
    (out / 'summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
