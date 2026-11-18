"""Audit newly completed reviews in a fresh directory, preserving the first audit."""
from pathlib import Path
import importlib.util
import json
ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'scripts/728_audit_labelled_annotations.py'
    spec = importlib.util.spec_from_file_location('annotation_audit_implementation', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = ROOT / 'outputs/labelled_annotation_audit_v2'
    original_write = module.write

    def write_review(path, payload):
        if Path(path).name == 'audit_PRIVATE.json':
            summary = payload['summary']
            if not summary['missing_cases']:
                summary['reason'] = 'saved_coverage_complete_support_and_grouped_calibration_design_pending'
            payload['input_sha256'][str(Path(__file__).resolve())] = module.digest(Path(__file__))
        original_write(path, payload)

    module.write = write_review
    module.main()


if __name__ == '__main__':
    main()
