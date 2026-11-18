"""Metadata-only comparison specification: no training, prediction or pixels."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/oblique_source_held_comparison_design_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve existing specification')
    prep=ROOT/'outputs/reviewed_ffhq_restoration_preparation_v1'
    folds=read(prep/'folds_PRIVATE.json')
    baseline=ROOT/'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json'
    models=read(baseline)
    assert len(folds)==len(models)==11
    seen=[]
    for fold,model in zip(folds,models):
        assert fold==model['definition']
        fit=fold['fitting_cases'];held=fold['evaluation_cases']
        assert len(fit)==40 and len(held)==4 and not set(fit)&set(held)
        assert all('29863' not in c for c in fit+held)
        seen.extend(held)
    assert len(seen)==len(set(seen))==44
    for fold in folds:assert set(fold['fitting_cases'])==set(seen)-set(fold['evaluation_cases'])
    feasibility=ROOT/'outputs/oblique_training_feasibility_v1'
    verification=read(feasibility/'independent_verification_PRIVATE.json')
    assert verification['passed'] and verification['classification']=='VALID_STRICT_FITTING_IMPROVEMENT'
    execution=read(feasibility/'execution_plan_PRIVATE.json')
    assert folds[0]['fitting_cases']==execution['fitting_cases']
    assert folds[0]['held_publisher_group']==execution['held_group_excluded']
    # Bind saved metadata, never pixels, pixel containers or raw photographs.
    rels=['docs/oblique-tree-source-held-comparison-design-2026-11-12.md',
        'docs/practical-model-completion-contract-2026-11-12.md',
        'docs/practical-model-evaluation-protocol-2026-11-12.md',
        'docs/ffhq-restoration-comparison-protocol-2026-11-11.md',
        'src/model_training/portable_oblique_tree.py','src/model_training/oblique_regression_tao.py',
        'outputs/oblique_training_feasibility_design_v1/plan_PRIVATE.json',
        'outputs/oblique_training_feasibility_v1/candidate_PRIVATE.json',
        'outputs/oblique_training_feasibility_v1/optimization_PRIVATE.json',
        'outputs/oblique_training_feasibility_v1/independent_verification_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/folds_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/rows_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_preparation_v1/review_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_comparison_v1/models_PRIVATE.json',
        'outputs/reviewed_ffhq_restoration_comparison_v1/predictions_PRIVATE.json',
        'scripts/825_verify_bounded_training_comparison.py',
        'scripts/847_specify_oblique_source_held_comparison.py']
    bindings={p:sha(ROOT/p) for p in rels}
    protocol='truehue_oblique_source_held_development_2026_11_12_v1'
    plan=dict(status='SPECIFIED_NOT_EXECUTABLE',stage='EXPOSED_SOURCE_HELD_DEVELOPMENT',
        protocol_id=protocol,folds=folds,planned_new_fits=10,reused_fits=1,planned_predictions=44,
        attempted_roles=48,excluded_source='29863',excluded_roles=4,
        initializations='Exact saved ordinary axis model matched by fold definition; no refit or selection',
        reuse_candidate=dict(path='outputs/oblique_training_feasibility_v1/candidate_PRIVATE.json',
            sha256=sha(feasibility/'candidate_PRIVATE.json'),fold=folds[0]['held_publisher_group']),
        caps_per_new_fit=dict(max_depth=4,max_passes=20,max_proposals=300,max_seconds=60,processes=1,restarts=0),
        order='Finish and independently verify all 11 fitting models before any held prediction/render/score',
        primary_baseline='uncorrected_input',old_comparator='Saved compatible results, descriptive only; no reclassification',
        families=['exposure_under','exposure_over','colour_cool'],identity_cases=11,
        primary_metric='Source-equal within-family mean(input_CIEDE2000-output_CIEDE2000)>0',
        rgb='Required secondary report with all harms and disagreements, not universal gate',
        scoring_support='Existing prepared scoring_mask (alpha>0), same original photographic reference',
        support='Existing reviewed same-geometry masks/alpha; no inference reference-assisted edits',
        renderer='u=input_rgb8/255; round_even(255*(u*(1-alpha)+clip(u**gamma*[red,1,blue],0,1)*alpha)) to uint8',
        metric_replay_tolerance=dict(abs_tol=1e-10,rel_tol=1e-10,source='Existing independent script825 close(); numerical replay only'),
        numerical_equal_policy='abs(input_DE-output_DE)<=1e-10 is numerical equality, not perceptual invisibility; retain raw signed differences',
        output_replay='Exact RGB8 array equality; protected and alpha-zero pixels exactly equal actual input',
        reviewer=dict(identity='User',role='researcher development reviewer',confirmation='Explicit user reply 12 November 2026'),
        display=dict(device='usual computer',browser=None,resolution=None,os_scale=None,colour_settings='unknown until recorded'),
        visual=dict(all_identity=11,all_distorted=33,primary_long_edge_max_css=512,no_upscale=True,
            native_inspection='100 percent of cached 256 working-grid image; not original native detail',
            pair_order='SHA256(UTF8(protocol_id+case_id)) last-byte low bit;0 input=A,1 input=B',
            scores_controls_and_model_labels='Hidden until every initial rating saved',
            ratings='Accepted practical protocol identity/preference/artifact fields; explicit save and durable reload'),
        decision='NOTREADY for failed/unresolved required check; all families need numerical and useful visual benefit; identity no noticeable change; protection exact',
        required_before_execution=['Generated-only runner/render/metric/order/save-reload verification',
            'Hash-bind new runner/verifier/renderer/review files and fixed mapping/measurement provenance from preparation receipt',
            'Bind prepared pixel-container hashes from existing manifest, verify only authorized cached containers during execution',
            'Capture browser/resolution/OS scale/colour-setting record before visual ratings'],
        no_automatic_repair=True,all_data_fit=False,ensemble=False,final_locked_access=False,
        new_fits_executed=0,predictions_executed=0,photo_reads=0,input_sha256=bindings)
    OUT.mkdir()
    def write(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    write('plan_PRIVATE.json',plan)
    write('rating_roster_PRIVATE.json',[dict(case_id=c,pair_order_seed_sha256=hashlib.sha256((protocol+c).encode()).hexdigest(),
        identity_rating=None,preference=None,artifact_panel=None,reason=None,saved=False) for c in seen])
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    write('verification_PRIVATE.json',dict(passed=True,folds=11,distinct_available_cases=44,
        planned_new_fits=10,exact_candidate_reuse=True,all_fit_held_sets_disjoint=True,
        reviewer_confirmed=True,display_details_pending=True,executable=False,new_fits=0,predictions=0,
        pixel_reads=0,held_record_reads=0,input_hashes_unchanged=True,plan_sha256=sha(OUT/'plan_PRIVATE.json')))
    print('PASS: 11 fold definitions / 44 cases / 10 proposed fits + exact reuse; specification only')

if __name__=='__main__':main()
