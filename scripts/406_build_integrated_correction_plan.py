"""Aggregate existing evidence and explicit gates; never import image/ML code."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/integrated_correction_plan_v1'
PARENTS = ['correction_training_readiness_plan_v1', 'synthetic_restoration_target_check_v1',
    'blended_recovery_target_check_v1', 'proposal_distortion_recipe_audit_v1',
    'directional_exposure_recipe_v1', 'synthetic_development_roles_v1', 'core_colour_recipe_v1']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')
    assert json.loads(path.read_text(encoding='utf-8')) == value


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    source_hashes = {}
    manifests = {}
    artifacts_checked = 0
    for name in PARENTS:
        parent = ROOT/'outputs'/name
        manifests[name] = sha(parent/'sha256.json')
        for file, digest in json.loads((parent/'sha256.json').read_text()).items():
            assert sha(parent/file) == digest
            artifacts_checked += 1
        for file in ('protocol.json', 'results.json', 'source_hashes.json'):
            if not (parent/file).exists():
                continue
            data = json.loads((parent/file).read_text(encoding='utf-8'))
            hashes = data if file == 'source_hashes.json' else data.get('source_sha256', {})
            for source, digest in hashes.items():
                assert sha(ROOT/source) == digest
                if source in source_hashes:
                    assert source_hashes[source] == digest
                source_hashes[source] = digest
    frozen = ROOT/'outputs/correction_training_readiness_plan_v1'
    old_parents = json.loads((frozen/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/'outputs'/k/'sha256.json') == v for k, v in old_parents.items())
    for source in ('docs/integrated-correction-development-plan-2026-11-03.md',
                   'scripts/406_build_integrated_correction_plan.py',
                   'src/distortion_generation/development_roles.py',
                   'src/distortion_generation/core_colour_recipe.py',
                   'src/distortion_generation/directional_exposure_recipe.py',
                   'src/model_training/blended_recovery_targets.py'):
        source_hashes[source] = sha(ROOT/source)
    cases = [dict(id='clean', layer='clean', implementation='identity', cast='none', direction='none')]
    for direction in ('under', 'over'):
        cases.append(dict(id='exposure_'+direction, layer='core', implementation='development_roles.core_exposure',
                          cast='none', direction=direction))
    for cast in ('cool', 'warm'):
        cases.append(dict(id='colour_'+cast, layer='core', implementation='core_colour_recipe.render_rgb',
                          cast=cast, direction='none'))
        for direction in ('under', 'over'):
            cases.append(dict(id='combined_'+cast+'_'+direction, layer='core',
                implementation='core_colour_recipe.render_rgb', cast=cast, direction=direction))
    for variant in ('exposure', 'color', 'combined'):
        for direction in (('none',) if variant == 'color' else ('under', 'over')):
            cases.append(dict(id='stress_'+variant+'_'+direction, layer='composite_stress_design',
                implementation='directional_exposure_recipe.render_rgb', variant=variant,
                cast='original_additive', direction=direction))
    assert len(cases) == len({c['id'] for c in cases}) == 14
    assert [sum(c['layer'] == x for c in cases) for x in ('clean','core','composite_stress_design')] == [1,8,5]
    gates = [
        dict(id='recipe_arithmetic', status='generated_only_complete', blocks_training=False,
             evidence='scripts400-405; no real-image/full-pipeline validation'),
        dict(id='source_reference_support', status='unresolved', blocks_training=True,
             evidence='no new photographic/face+neck/scoring admission in this plan'),
        dict(id='person_duplicate_exposure', status='unresolved', blocks_training=True,
             evidence='existing roles preserved; no independent final cohort assigned'),
        dict(id='matching_skin_MST', status='unresolved', blocks_training=True,
             evidence='no reliable adopted matching mapping; 19-subject study not adequate admission'),
        dict(id='feature_and_pair_contract', status='partially_implemented', blocks_training=True,
             evidence='three-output target solver exists; full distorted-input feature/support binding pending'),
        dict(id='cohort_adequacy_allocation_weights_acceptance', status='unresolved', blocks_training=True,
             evidence='predeclare justified criteria before fitting; unset, not passed')]
    contract = dict(version='integrated_three_output_photographic_restoration_plan_v1',
        task='restore synthetic distorted photographs toward original photographic references',
        retained_method='ITA+calibrated_MST+input_facial_statistics -> decision_tree',
        output_schema=['gamma_direct_exponent','red_gain','blue_gain'],
        runtime_adopted=False, four_control_candidate='separate immutable script399 experiment, not this operator',
        proposed_case_matrix=cases, matrix_status='future_diagnostic_proposal_not_training_distribution',
        source_severity='one justified provenance-bound group per admitted source',
        actual_feature_values='distorted_input_only; no reference/official_MST substitution',
        support='admitted actual correction alpha and separate measurement/scoring contracts required',
        grouping='connected person/scene/duplicate groups and descendants in same split',
        reference_use='supervision_and_metrics_only',
        stress_design='retain layer even if actual clipping is zero; observed role separately reported',
        target_solver=dict(start=[1.,1.,1.], bounds=[.25,4.], max_evaluations=500,
            tolerances=1e-10, objective='float_encoded_RGB_squared_error_with_actual_alpha',
            verification='separate_RGB8_residual; local_approximation_not_prediction',
            failed_fit='retained_hold_no_fabricated_labels'),
        evaluation=dict(baseline='uncorrected_input', reference='original_photo',
            metrics=['RGB8_MAE','relative_CIEDE2000','clean_changes','failures','clipping_and_detail_loss'],
            summaries='separate_layers_conditions_supported_labels_and_person_denominators',
            oracle='separate_capacity_diagnostic_never_automatic_prediction',
            expert_review='existing_Google_Form_after_good_initial_model_then_refinement_and_rereview'),
        final_feature_schema=None, final_tree_settings=None, final_allocation=None,
        adequate_cohort_size=None, training_weights=None, final_sampling_distribution=None,
        numeric_acceptance_criteria=None, panel_approved=False)
    contract['canonical_payload_sha256'] = hashlib.sha256(json.dumps(contract,
        sort_keys=True,separators=(',',':')).encode()).hexdigest()
    readiness = dict(training_ready=False, gates=gates, admitted_sources=0,
        photo_batch_activated=False, review_batch_activated=False, photos_processed=0,
        new_target_fits=0, mst_fits=0, tree_fits=0, model_inference=0, runtime_changes=0,
        next_trigger='substantive source/support/person/MST admission evidence; no repeated inventories/formula fits')
    headers = ['attempt_id','source_id','source_sha256','source_terms_evidence','reference_scope',
        'person_component_id','duplicate_component_id','allocation','development_exposure_evidence',
        'source_quality_decision','selected_face_id','severity_group','group_provenance',
        'measurement_contract','actual_skin_evidence','correction_alpha_sha256','scoring_mask_sha256',
        'support_admission_evidence','distorted_input_feature_contract','matching_MST_contract',
        'MST_admission_evidence','pair_contract','status','hold_reasons','decision_evidence']
    OUT.mkdir()
    for name,value in [('recipe_contract.json',contract),('readiness.json',readiness),
                       ('source_hashes.json',source_hashes),('parent_manifest_hashes.json',manifests),
                       ('admission_schema.json',dict(columns=headers,rows=0,purpose='future_evidence_not_queue'))]:
        write_json(OUT/name,value)
    with (OUT/'admission_template.csv').open('w',newline='',encoding='utf-8') as stream:
        csv.writer(stream).writerow(headers)
    with (OUT/'admission_template.csv').open(newline='',encoding='utf-8') as stream:
        assert list(csv.reader(stream)) == [headers]
    reread=json.loads((OUT/'recipe_contract.json').read_text())
    digest=reread.pop('canonical_payload_sha256')
    assert hashlib.sha256(json.dumps(reread,sort_keys=True,separators=(',',':')).encode()).hexdigest()==digest
    assert readiness['training_ready'] is False and any(g['blocks_training'] for g in gates)
    assert all(sha(ROOT/k)==v for k,v in source_hashes.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json')==v for k,v in manifests.items())
    write_json(OUT/'verification.json',dict(parent_packages=len(PARENTS),
        parent_artifact_hashes_checked=artifacts_checked, unique_source_hashes_checked=len(source_hashes),
        frozen_parent_hashes_checked=len(old_parents), proposed_cases=14,
        clean_core_stress_cases=[1,8,5], zero_admitted_rows=True, JSON_roundtrip=True,
        contract_hash_verified=True, processing_and_fits_inactive=True))
    (OUT/'README.txt').write_text('Planning only. Start with docs/integrated-correction-development-plan-2026-11-03.md.\n'
        'No admitted data, photo queue, generated images, new fits, training or panel approval.\n',encoding='utf-8')
    write_json(OUT/'sha256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps(json.loads((OUT/'verification.json').read_text()),indent=2))


if __name__ == '__main__':
    main()
