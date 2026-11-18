"""Bind a fitting-only design without extracting pixels, fitting or predicting."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/histogram_gap_training_feasibility_design_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    if OUT.exists():raise FileExistsError('Preserve design')
    oldplan=ROOT/'outputs/correction_training_contract_v1/plan_PRIVATE.json'
    roster=read(oldplan)['feasibility']
    modelpath=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json'
    text=modelpath.read_text(encoding='utf-8').lstrip();assert text.startswith('[')
    first,_=json.JSONDecoder().raw_decode(text[1:].lstrip())
    assert first['definition']['fitting_cases']==roster['fitting_cases']
    assert first['definition']['held_publisher_group']==roster['held_group']=='ffhq_source_16061'
    audit=ROOT/'outputs/histogram_gap_exposed_input_audit_v1'
    receipt=read(audit/'verification_PRIVATE.json');assert receipt['passed']
    assert sha(audit/'features_PRIVATE.json')==receipt['feature_records_sha256']
    names=first['tree']['feature_names']+[f'scene_{c}_{b}_internal_gap_fraction' for c in ['red','green','blue'] for b in ['low','high']]
    assert len(names)==len(set(names))==22
    records=[];bindings={}
    for case in roster['fitting_cases']:
        path=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'/case/'record_PRIVATE.json';r=read(path)
        assert r['case_id']==case and r['publisher_group']!=roster['held_group']
        assert r['status']=='available' and not r['generated_fixture'] and '29863' not in case
        assert len(r['input_vector_float32'])==16 and len(r['nominal_controls'])==3
        records.append(dict(case_id=case,source=r['publisher_group'],role=r['experimental_role'],record=path.relative_to(ROOT).as_posix()))
        bindings[path.relative_to(ROOT).as_posix()]=sha(path)
    assert len(records)==40 and len({r['source'] for r in records})==10
    assert all(sum(r['role']==role for r in records)==10 for role in ['identity','exposure_under','exposure_over','colour_cool'])
    files=['scripts/861_specify_histogram_gap_training_feasibility.py','docs/histogram-gap-training-feasibility-protocol-2026-11-12.md',
        'src/model_training/histogram_gap_features.py','src/model_training/portable_tree.py',
        'outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',
        'outputs/histogram_gap_exposed_input_audit_v1/verification_PRIVATE.json',
        'outputs/histogram_gap_generated_robustness_v1/verification_PRIVATE.json',
        'scripts/810_run_reviewed_ffhq_comparison.py']
    for p in [oldplan,modelpath]+[ROOT/f for f in files]:bindings[p.relative_to(ROOT).as_posix()]=sha(p)
    settings=dict(criterion='squared_error',splitter='best',max_depth=4,random_state=42,min_samples_leaf=1,
        min_samples_split=2,min_weight_fraction_leaf=0.,max_features=None,max_leaf_nodes=None,
        min_impurity_decrease=0.,ccp_alpha=0.,monotonic_cst=None)
    plan=dict(status='SPECIFIED_NOT_EXECUTABLE',hypothesis='Frozen six descriptors complement old16inputs for gamma-direction selection',
        fitting_records=records,excluded_group=roster['held_group'],feature_names=names,
        new_feature_names=names[16:],target_names=['gamma','red_gain','blue_gain'],
        audited_features_path='outputs/histogram_gap_exposed_input_audit_v1/features_PRIVATE.json',
        baseline=dict(path=modelpath.relative_to(ROOT).as_posix(),entry_index=0,refit=False),
        algorithm='one_multioutput_axis_DecisionTreeRegressor',settings=settings,
        fit_calls=1,restarts=0,scaling=False,sample_weights=None,source_or_role_features=False,
        inference_reference_subtraction=False,comparison_objective='raw unweighted three-control SSE',
        numerical_strict_gain='before-after > 1e-12*max(1,before)',
        output_directory='outputs/histogram_gap_training_feasibility_v1',
        generated_runner_verification_required=True,held_predictions_allowed=False,pixel_reads_allowed=False,
        no_automatic_followup=True,old_failures_reclassified=False,
        input_sha256=bindings,real_fits_executed=0,predictions=0)
    OUT.mkdir()
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,fitting_rows=40,groups=10,
        input_features=22,old_features=16,new_features=6,held_group_excluded=True,
        source_hashes_unchanged=True,fit_calls_executed=0,predictions=0,pixel_reads=0,
        plan_sha256=sha(OUT/'plan_PRIVATE.json')),indent=2)+'\n',encoding='utf-8')
    print('PASS: fixed40 fitting rows / 22 inputs / one ordinary tree specified; no fit/prediction/photo read')

if __name__=='__main__':main()
