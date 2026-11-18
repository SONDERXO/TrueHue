"""Bind one fitting-only design. No trainer call, image access or held records."""
from pathlib import Path
import hashlib
import json
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.model_training.portable_oblique_tree import from_axis_tree

OUT = ROOT / 'outputs/oblique_training_feasibility_design_v1'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def main():
    if OUT.exists():
        raise FileExistsError('Preserve existing design; no overwrite')
    old_plan = ROOT / 'outputs/correction_training_contract_v1/plan_PRIVATE.json'
    fitting = read(old_plan)['feasibility']
    model_path = ROOT / 'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json'
    text = model_path.read_text().lstrip()
    assert text.startswith('[')
    first, _ = json.JSONDecoder().raw_decode(text[1:].lstrip())
    assert first['definition']['held_publisher_group'] == fitting['held_group']
    assert first['definition']['fitting_cases'] == fitting['fitting_cases']
    initial = from_axis_tree(first['tree'])  # Schema conversion only; no prediction.
    assert len(initial['feature_names']) == 16
    records = []
    for case in fitting['fitting_cases']:
        path = ROOT / 'outputs/reviewed_ffhq_restoration_preparation_v1' / case / 'record_PRIVATE.json'
        row = read(path)  # Fitting records only; no image/NPZ access.
        assert row['case_id'] == case and row['status'] == 'available'
        assert row['publisher_group'] != fitting['held_group']
        assert len(row['input_vector_float32']) == 16
        assert len(row['nominal_controls']) == 3
        records.append(dict(case_id=case, publisher_group=row['publisher_group'],
                            role=row['experimental_role'], path=path.relative_to(ROOT).as_posix(), sha256=sha(path)))
    assert len(records) == len({r['case_id'] for r in records}) == 40
    roles = dict(Counter(r['role'] for r in records))
    groups = dict(Counter(r['publisher_group'] for r in records))
    assert len(groups) == 10 and set(groups.values()) == {4}
    assert len(roles) == 4 and set(roles.values()) == {10}
    preserved = read(ROOT / 'outputs/oblique_tree_engineering_v1/preserved_inputs_PRIVATE.json')
    assert all(sha(ROOT / p) == h for p, h in preserved.items())
    files = [old_plan, model_path, Path(__file__),
             ROOT/'src/model_training/portable_oblique_tree.py',
             ROOT/'src/model_training/oblique_regression_tao.py',
             ROOT/'tests/test_oblique_regression_engineering.py',
             ROOT/'outputs/oblique_tree_engineering_v1/generated_verification_PRIVATE.json',
             ROOT/'docs/oblique-tree-training-feasibility-design-2026-11-12.md',
             ROOT/'docs/oblique-tree-engineering-protocol-2026-11-12.md']
    bindings = {p.relative_to(ROOT).as_posix(): sha(p) for p in files}
    bindings.update(preserved)
    bindings.update({r['path']: r['sha256'] for r in records})
    plan = dict(status='SPECIFIED_NOT_EXECUTED', executable=False,
        hypothesis='Oblique branch geometry can reduce raw fitting SSE from one saved ordinary axis initialization.',
        held_group_excluded=fitting['held_group'], fitting_rows=records,
        fitting_role_counts=roles, fitting_group_counts=groups,
        initial_tree_source=dict(path=model_path.relative_to(ROOT).as_posix(), entry_index=0,
                                 selection='Existing first fold, not selected by oblique outcomes', refit=False),
        feature_names=initial['feature_names'], target_names=['gamma','red_gain','blue_gain'],
        objective='Raw unweighted sum of squared three-control errors',
        caps=dict(max_depth=4,max_passes=20,max_proposals=300,max_seconds=60,processes=1,restarts=0),
        branch_solver=dict(method='L-BFGS-B',l2_slopes=.01,maxiter=100,maxfun=1000,maxls=20,
                           ftol=1e-10,gtol=1e-8,maxcor=10),
        scaling='Population mean/std from these 40 float32 fitting rows only; zero std becomes 1; fold into export.',
        numerical_improvement='initial_SSE-final_SSE > 1e-12*max(1,initial_SSE)',
        report_requirements=['status and elapsed scope','initial/final/per-control/per-role fitting SSE',
            'monotone history and solver outcomes','accepted branches and coefficient counts',
            'identity control deviations, descriptive only','independent 40-row routes, leaf means and SSE',
            'initial axis-to-oblique prediction parity','all input hashes unchanged'],
        future_run_directory='outputs/oblique_training_feasibility_v1',
        no_automatic_followup=['no budget/penalty/depth/initialization rescue','no held predictions or rendering',
            'no full comparison or final run','no old-candidate rescoring or promotion'],
        real_fits=0, predictions=0, held_records_loaded=0, photo_reads=0, input_sha256=bindings)
    OUT.mkdir()
    def write(name, value):
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    write('plan_PRIVATE.json',plan)
    write('initial_schema_conversion_PRIVATE.json', initial)
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    write('verification_PRIVATE.json',dict(passed=True,fitting_rows=40,source_groups=10,
        role_counts=roles,initial_nodes=len(initial['nodes']),initial_schema_conversion_only=True,
        input_hashes_unchanged=True,plan_sha256=sha(OUT/'plan_PRIVATE.json'),
        converted_initial_sha256=sha(OUT/'initial_schema_conversion_PRIVATE.json'),
        real_fits=0,predictions=0,held_records_loaded=0,photo_reads=0))
    print('PASS: specified 40 fitting rows / 10 groups / one saved initialization; zero fits or predictions')

if __name__ == '__main__':
    main()
