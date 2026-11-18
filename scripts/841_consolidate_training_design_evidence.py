"""Metadata-only consolidation. Never reads images or imports training code."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/consolidated_training_design_decision_v1'

DOCS = [
    'correction-model-and-paper-realignment-2026-11-11.md',
    'table2-target-fit-results.md', 'table2-counterfactual-coverage-results.md',
    'reviewed-primary-training-results.md',
    'expanded-correction-training-protocol-2026-11-08.md',
    'expanded-correction-training-results-2026-11-08.md',
    'reserved-clean-veto-protocol-2026-11-08.md',
    'training-exposure-colour-audit-2026-11-09.md',
    'green-feature-correction-results-2026-11-09.md',
    'reviewed-correction-comparison-results-2026-11-11.md',
    'source-matched-restoration-comparison-results-2026-11-11.md',
    'relative-correction-loss-results-2026-11-11.md',
    'nominal-control-regression-results-2026-11-11.md',
    'correction-training-target-audit-results-2026-11-11.md',
    'bounded-training-comparison-results-2026-11-11.md',
    'primary-training-evidence-feasibility-2026-11-11.md',
    'spatial-input-correction-results-2026-11-11.md',
    'gray-pixel-selector-results-2026-11-12.md',
    'traditional-feature-scope-decision-2026-11-11.md',
    'existing-dataset-correction-evidence-readiness-2026-11-11.md',
]


def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing consolidation')
    bindings = {}
    def read(relative):
        p = ROOT/relative
        assert p.suffix == '.json'  # no pixel archives, model binaries or images
        b = p.read_bytes();bindings[relative] = hashlib.sha256(b).hexdigest()
        return json.loads(b)
    for name in DOCS:
        p = ROOT/'docs'/name
        bindings['docs/'+name] = hashlib.sha256(p.read_bytes()).hexdigest()
    paper = read('outputs/proposal_scope_validation_20261103_v1/pages.json')
    pages = [r for r in paper if r['pdf_page'] in [12, 13, 14, 60, 62, 63, 65, 66, 67]]
    assert len(pages) == 9
    expanded = read('outputs/expanded_correction_models_v1/models_PRIVATE.json')
    later = read('outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    broad_audit = read('outputs/training_exposure_colour_audit_v1/audit_PRIVATE.json')
    older = expanded['full']['training_cases'];remaining = later['full']['training_cases']
    assert len(set(older)) == len(older) == 1117
    assert len(set(remaining)) == len(remaining) == 890
    assert set(remaining) < set(older)
    original_sources = {c.split('__', 1)[0] for c in older}
    remaining_sources = {c.split('__', 1)[0] for c in remaining}
    removed = set(older)-set(remaining)
    assert len(original_sources) == 102 and len(remaining_sources) == 82
    assert len(removed) == 227 and len(original_sources-remaining_sources) == 20
    assert len(later['full']['reserved_clean_vectors']) == 20
    families = Counter()
    for case in remaining:
        recipe = case.split('__', 1)[1]
        family = ('clean' if recipe == 'clean' else 'colour_only' if recipe.startswith('colour_')
                  or recipe == 'stress_color_none' else 'exposure_only' if recipe in
                  ['exposure_under', 'exposure_over', 'stress_exposure_under', 'stress_exposure_over'] else 'combined')
        families[family] += 1
    assert dict(families) == broad_audit['summary']['families']
    ffhq = read('outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json')
    assert len(ffhq) == 44 and all(not r['generated_fixture'] for r in ffhq)
    assert len({r['publisher_group'] for r in ffhq}) == 11
    assert Counter(r['experimental_role'] for r in ffhq) == dict(
        identity=11, exposure_under=11, exposure_over=11, colour_cool=11)
    assert len({r['features']['input_mst_score'] for r in ffhq if r['experimental_role']=='identity'}) == 1
    assert not any(r['provided_mst_label'] is not None for r in ffhq)
    baseline = read('outputs/reviewed_ffhq_restoration_comparison_v1/summary_PRIVATE.json')
    search = read('outputs/bounded_training_comparison_v1/summary_PRIVATE.json')
    spatial = read('outputs/spatial_input_correction_comparison_v1/summary_PRIVATE.json')
    nominal = read('outputs/nominal_control_regression_comparison_v1/summary_PRIVATE.json')
    assert all(not x['development_checks_passed'] for x in [baseline, search, spatial, nominal])
    for relative in ['outputs/reviewed_ffhq_restoration_comparison_v1/verification_PRIVATE.json',
        'outputs/bounded_training_comparison_v1/verification_PRIVATE.json',
        'outputs/spatial_input_correction_comparison_v1/verification_PRIVATE.json']:
        assert read(relative)['passed']
    summary = dict(expanded_full_fit_rows=1117, expanded_originals=102,
        later_full_fit_rows=890, later_originals=82,
        reserved_rows_removed_from_fitting=227, reserved_usable_clean_originals=20,
        later_family_counts=dict(families), ffhq_rows=44, ffhq_sources=11,
        ffhq_roles=dict(Counter(r['experimental_role'] for r in ffhq)),
        ffhq_original_MST_distinct_values=1, ffhq_provided_MST_labels=0,
        saved_failed_comparisons_checked=4,
        no_new_supported_training_data_design_identified=True,
        new_fits=0, new_predictions=0, photo_bytes_read=0, holdout_bytes_read=0,
        limits='Different contracts/cohorts/targets are not pooled or causally ranked; metadata replay is not a new model evaluation.')
    OUT.mkdir()
    (OUT/'summary_PRIVATE.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (OUT/'paper_pages_PRIVATE.json').write_text(json.dumps(pages,indent=2)+'\n',encoding='utf-8')
    bindings['scripts/841_consolidate_training_design_evidence.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bindings,indent=2)+'\n',encoding='utf-8')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h for p,h in bindings.items())
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
