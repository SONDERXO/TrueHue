"""Freeze exact source-held prediction design from saved metadata, without image/model imports."""
from pathlib import Path
import ast
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/five_control_source_held_prediction_design_v1'
IDS=sorted(['54632','39568','29617','16061','52445','32685','53146','48879','49131','59807','46795'])
ROLES=['identity','colour_only','exposure_under','exposure_over','combined_under','combined_over']


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial design')
    bindings={}
    def read(relative):
        path=ROOT/relative;bindings[relative]=sha(path)
        return json.loads(path.read_text(encoding='utf-8'))
    baseline='outputs/ffhq_directional_recoverability_v1'
    candidate='outputs/affine_capacity_comparison_v1'
    bv=read(baseline+'/verification_PRIVATE.json');cv=read(candidate+'/verification_PRIVATE.json')
    ca=read(candidate+'/assessment_PRIVATE.json')
    assert bv['passed'] and cv['passed'] and ca['status']=='NUMERIC_CAPACITY_ELIGIBLE_ONLY_NOT_PREDICTOR_QUALIFICATION'
    assert ca['verification_sha256']==sha(ROOT/candidate/'verification_PRIVATE.json')
    oldplan=read('outputs/blue_axis_source_held_design_v1/plan_PRIVATE.json')
    oldrows=read('outputs/blue_axis_preparation_v1/rows_PRIVATE.json')
    mapping=read('outputs/shared_core_mst_features_v1/mapping_PRIVATE.json')
    assert mapping['status']=='development_unvalidated_transfer' and not mapping['runtime_adopted']
    assert all(s.startswith('stellenbosch_') for s in mapping['fitting_subjects'])
    names=oldplan['feature_names'];assert len(names)==len(set(names))==281
    supports={s['source_id']:s for s in oldplan['support_sources']};assert set(supports)==set(IDS)
    identities={r['source'].removeprefix('ffhq_source_'):r for r in oldrows if r['role']=='identity'}
    assert set(identities)==set(IDS)
    rows=[];values=[];bound_cases=[]
    for source_id in IDS:
        for role in ROLES:
            rel=f'{candidate}/candidate/{source_id}/{role}.json'
            expected=cv['artifact_sha256'][f'candidate\\{source_id}\\{role}.json']
            assert sha(ROOT/rel)==expected
            r=read(rel);target=r['target']
            assert r['source_id']==source_id and r['role']==role and r['generated_fixture'] is False
            assert target['status'] in ['available_approximate_target','exact_neutral_target']
            y=target['parameters'];assert len(y)==5 and all(math.isfinite(v) for v in y)
            assert all(lo<=v<=hi for lo,v,hi in zip([.25,.25,.25,.5,-.3],y,[4,4,4,2,.3]))
            if role=='identity':assert y==[1.,1.,1.,1.,0.]
            assert not target['training_admitted'] and not target['runtime_adopted']
            case_id=f'five_prediction_ffhq_{source_id}__{role}'
            if any(target.get('active_bounds',[])):bound_cases.append(case_id)
            inp=f'cases\\{source_id}\\{role}.npz';support=f'cases\\{source_id}\\support.npz'
            rows.append(dict(case_id=case_id,source_id=source_id,role=role,generated_fixture=False,
                stage='planned_exposed_development_only_not_final_admission',
                input_pack=f'{baseline}/cases/{source_id}/{role}.npz',input_pack_sha256=bv['artifact_sha256'][inp],
                allowed_input_key='input',cached_support_pack=f'{baseline}/cases/{source_id}/support.npz',
                cached_support_sha256=bv['artifact_sha256'][support],
                allowed_support_keys=['reference','alpha','protected'],
                reference_use='identity_parity_or_scoring_only_not_inference_features',
                target_record=rel,target_record_sha256=expected,y=y,
                condition_number=target.get('jacobian_condition_number'),active_bounds=target.get('active_bounds'),
                parent_training_admitted=target['training_admitted'],
                official_tone_label=None))
            values.append(y)
    folds=[]
    for source_id in IDS:
        fitting=[r['case_id'] for r in rows if r['source_id']!=source_id]
        held=[r['case_id'] for r in rows if r['source_id']==source_id]
        assert len(fitting)==60 and len(held)==6 and not set(fitting)&set(held)
        folds.append(dict(held_source_id=source_id,fitting_cases=fitting,evaluation_cases=held,
                          fitting_source_ids=[s for s in IDS if s!=source_id],fitting_rows=60,held_rows=6))
    feature_sources=[]
    for source_id in IDS:
        selected=supports[source_id]['selected'];old=identities[source_id]
        feature_sources.append(dict(source_id=source_id,measurement_path=str(Path(selected['directory'])/'measurement_mask.png'),
            measurement_sha256=selected['files']['measurement_mask.png'],
            selected_receipt=str(Path(selected['directory'])/selected['receipt']),selected_receipt_sha256=selected['receipt_sha256'],
            identity_saved_feature_case=old['case_id'],identity_saved_feature_vector=old['x'],
            identity_feature_parity_required='all281float32exact_before_nonidentity_features_or_fits'))
    settings_source=ROOT/'src/model_training/gap_training_feasibility.py'
    tree=ast.parse(settings_source.read_text(encoding='utf-8'))
    expr=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SETTINGS' for t in n.targets))
    assert isinstance(expr,ast.Call) and isinstance(expr.func,ast.Name) and expr.func.id=='dict'
    settings={k.arg:ast.literal_eval(k.value) for k in expr.keywords}
    assert settings['max_depth']==4 and settings['random_state']==42
    means=[math.fsum(y[j] for y in values)/66 for j in range(5)]
    sse=[math.fsum((y[j]-means[j])**2 for y in values) for j in range(5)]
    for rel in ['docs/five-control-source-held-prediction-protocol-2026-11-14.md',
        'scripts/specify_five_control_prediction_test.py','scripts/verify_five_control_prediction_design.py',
        'src/model_training/blue_axis_preparation.py','src/model_training/gap_training_feasibility.py',
        'src/ita_estimation/compute_ita.py','src/ita_estimation/shared_core_mst.py',
        'src/model_training/whole_scene_features.py','src/model_training/green_distribution_features.py',
        'src/model_training/histogram_gap_features.py','src/model_training/joint_log_colour.py',
        'src/model_training/portable_tree.py','src/model_training/affine_prepower_targets.py']:
        bindings[rel]=sha(ROOT/rel)
    assert len(rows)==66 and len(bound_cases)==6
    plan=dict(status='SPECIFIED_NONEXECUTABLE_PENDING_GENERATED_ADAPTER_QA_AND_REAL_FEATURE_PARITY',
        feature_names=names,target_names=['gamma','red_gain','blue_gain','input_scale','input_offset'],
        rows=rows,folds=folds,feature_sources=feature_sources,settings=settings,
        mapper_path='outputs/shared_core_mst_features_v1/mapping_PRIVATE.json',
        mapper_sha256=bindings['outputs/shared_core_mst_features_v1/mapping_PRIVATE.json'],
        mapper_scope='unchanged_unvalidated_development_map_not_official_tone_labels',
        planned_tree_fits=11,planned_fitting_route_replays=660,planned_held_tree_predictions=66,
        planned_fitting_constant_means=11,planned_constant_held_renders=66,
        target_refits=0,baseline_tree_refits=0,planned_identity_feature_replays=11,
        planned_new_nonidentity_feature_vectors=55,bound_hit_cases_retained=bound_cases,
        saved_target_root_SSE=sse,saved_target_root_SSE_fractions=[v/sum(sse) for v in sse],
        numerical_screen='66available; each5nonidentity-role mean primary RGB and DE strictly better than input AND fitting-onlyconstant; protectionexact; numeric_identity_changes_reported_not_human_unwanted_judgments',
        no_automatic_review=True,model_ready=False,real_arrays_read=0,new_features_computed=0,
        fits_executed=0,predictions_executed=0,input_sha256=bindings)
    OUT.mkdir()
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==h for n,h in bindings.items())
    print('Specified66rows/11source-held60-6folds/11max trees; no arrays, features, fits or predictions.')


if __name__=='__main__':main()
