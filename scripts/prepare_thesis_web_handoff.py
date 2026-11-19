"""Prepare a text-only thesis handoff from repository files and named aggregate evidence.

Does not traverse data/, models/, outputs/ or locked allocations. Only the exact
aggregate files below are read from outputs; all archive members come from Git's
tracked/unignored source paths. Personal appeal material stays local.
"""
from pathlib import Path
import argparse
from datetime import date
import ast
import hashlib
import json
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'output/thesis-web-handoff-2026-11-18'
DOCS = ROOT / 'docs/thesis'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def text(path):
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16'), 'utf-16'
    try:
        return raw.decode('utf-8-sig'), 'utf-8'
    except UnicodeDecodeError:
        return raw.decode('cp1252'), 'cp1252'


def repository_paths():
    data = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT)
    return sorted(set(p.decode('utf-8') for p in data.split(b'\0') if p))


def eligible(path):
    parts = Path(path).parts
    return (parts[0] not in {'data', 'models', 'outputs', 'output', 'tmp', '.git'}
            and 'appeal' not in path.lower() and '.kotlin' not in parts
            and Path(path).suffix.lower() in {'.md', '.py', '.json', '.txt', '.js', '.cjs', '.html', '.cmd',
                '.kt', '.kts', '.xml', '.yml', '.yaml', '.csv', '.tsv', '.ps1', '.toml', '.properties',
                '.gradle', '.bat', '.gitignore', '.code-workspace'}
            or path in {'.gitignore', 'LICENSE', 'gradlew', 'android-app/gradlew'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination-name', default=None,
                        help='New folder name under output/; prior handoffs are preserved.')
    parser.add_argument('--checkpoint-date', default='2026-11-18',
                        help='Client-local evidence date in YYYY-MM-DD format.')
    args = parser.parse_args()
    checkpoint = date.fromisoformat(args.checkpoint_date).isoformat()
    args.destination_name = args.destination_name or 'thesis-web-handoff-' + checkpoint
    if not args.destination_name or Path(args.destination_name).name != args.destination_name or args.destination_name in {'.', '..'}:
        raise ValueError('A single new output folder name is required')
    destination = ROOT / 'output' / args.destination_name
    if destination.exists():
        raise FileExistsError('Preserve this dated handoff; use a new destination for another update')
    DOCS.mkdir(exist_ok=True)
    previous = json.loads((DOCS / 'evidence-snapshot.json').read_text(encoding='utf-8')) if (DOCS / 'evidence-snapshot.json').exists() else {}
    snapshot = dict(checkpoint=checkpoint, kind='Selected aggregate evidence, not raw data or final qualification',
                    model_ready=False, studies={})
    # Preserve explicit stage/requirement notes and curated historical evidence.
    # Named source extracts below refresh the studies they own.
    snapshot.update({k: v for k, v in previous.items() if k not in {'checkpoint', 'kind', 'model_ready', 'studies'}})
    snapshot['studies'].update(previous.get('studies', {}))
    specs = {
        'wb314': ('outputs/wb_feature_direct_prediction_v1/summary.json', ['by_role', 'role_gates', 'added_colour_benefit', 'candidate_numeric_eligible', 'baseline_numeric_eligible']),
        'exposure_eight_rereview': ('outputs/wb_feature_exposure_rereview_ratings_v1/assessment_PRIVATE.json', ['status', 'complete_cases', 'total', 'preference_counts', 'appearance_counts', 'raw_sha256']),
        'remaining_nine_under_review': ('outputs/wb_feature_remaining_under_ratings_v1/assessment_PRIVATE.json', ['status', 'complete_cases', 'total', 'preference_counts', 'appearance_counts', 'raw_sha256']),
        'whole_pure_under_review': ('outputs/wb_feature_remaining_under_ratings_v1/combined_pure_under_assessment.json', ['cases', 'expected_role_cases', 'complete', 'preference_counts', 'appearance_counts']),
        'actual_piq_head': ('outputs/piq23_actual_head_v1/summary.json', ['Train', 'Test', 'narrow_quality_screen_pass']),
        'actual_piq_correction': ('outputs/piq23_probe_correction_prediction_v1/summary.json', ['by_role', 'role_gates', 'under_improvement', 'colour_nonworse', 'numerical_eligible', 'identity_changed']),
        'actual_piq_cue_audit': ('outputs/piq23_probe_correction_prediction_v1/independent_audit.json', ['passed', 'cue_splits', 'models_using_cues', 'numerical_eligible']),
        'complete_ppr': ('outputs/ppr_full_pipeline_prediction_v1/summary.json', ['by_role', 'role_gates', 'under_improvement', 'colour_nonworse', 'numerical_eligible', 'identity_changed', 'decision']),
        'complete_source_held_exposure_review': ('outputs/wb_feature_remaining_exposure_ratings_v1/combined_exposure_assessment.json', ['complete', 'expected', 'cases', 'preference_counts', 'appearance_counts', 'by_role']),
        'frozen_predictor_changed_review': ('outputs/wb314_final_changed_ratings_v1/assessment_PRIVATE.json', ['status', 'complete_cases', 'total', 'preference_counts', 'appearance_counts', 'by_role', 'raw_sha256', 'model_sha256', 'event_replay_matches', 'event_count', 'independent_evaluation', 'expert_MOS', 'qualification_complete']),
        'single_wb314_predictor': ('outputs/wb314_final_candidate_freeze_v1/model_card.json', ['version', 'status', 'model_sha256', 'sources', 'training_cases', 'features', 'real_all_development_fits', 'user_review_new_changed_cases', 'user_review_new_candidate_preferred', 'user_review_new_acceptable', 'exact_pixel_join_nonidentity_cases', 'joined_preference_counts', 'joined_appearance_acceptable', 'identity_outputs_exact_input', 'reviewers', 'expert_MOS', 'independent_final_evaluation', 'qualification_complete', 'raw_photo_to_mask_path_integrated', 'current_app_defaults_changed', 'normalized_input_to_output_checks', 'exact_feature_values_replayed', 'notes']),
        'normalized_input_inference_parity': ('outputs/wb314_research_inference_v1/verification.json', ['passed', 'cases', 'exact_feature_values', 'exact_controls', 'exact_RGB8_outputs', 'input_and_WB_state_immutable', 'generated_invalid_input_guards', 'invalid_feature_guards', 'binary64_threshold_boundary_guards', 'real_fits', 'elapsed_seconds', 'qualification_complete', 'masking_inferred', 'defaults_changed', 'versions']),
        'existing_expert_instrument': ('outputs/wb314_expert_instrument_respondent_access_v1/instrument_summary.json', ['title', 'item_count', 'item_type_counts', 'rating_items', 'comment_items', 'all_rating_options', 'rating_endpoint_labels', 'section_scale_labels', 'image_item_definitions', 'submission_made', 'questions_changed', 'source_html_sha256']),
        'expert_feedback_preparation_draft': ('output/wb314-expert-feedback-draft-2026-11-18/verification.json', ['passed', 'pair_count', 'source_count', 'per_condition', 'native_pixel_PNG_roundtrips', 'resampling', 'new_fits', 'feature_calls', 'predictions', 'correction_renders', 'submitted_responses', 'online_form_edits', 'images_uploaded', 'protocol_sha256']),
        'separate_MSTE_evaluation_eligibility': ('outputs/wb314_mste_evaluation_metadata_v1/summary.json', ['decision', 'official_label_coverage', 'catalog_rows', 'unique_subject_image_keys', 'publisher_subjects', 'prior_mapping_development_subjects', 'closed_screen_subjects', 'closed_subject_catalog_keys', 'catalog_keys_outside_closed_subjects', 'other_catalog_keys_for_same_exposed_subjects', 'previously_unused_subjects', 'outside_closed_category_subject_counts', 'positive_new_unreserved_evaluation_admissions', 'interpretation', 'fits', 'source_image_decodes', 'locked_content_or_manifest_reads', 'Form_edits', 'expert_responses']),
        'MSTE_development_packet_status': ('outputs/wb314_mste_development_packet_v1/packet_status.json', ['technical_checks_pass', 'publisher_MST_categories', 'pairs', 'subjects', 'reference_attempts', 'reference_technical_failures', 'candidate_reserve_used_for_MST', 'distribution_ready', 'requires_user_release_decision', 'stage', 'completed_client_date', 'known_support_findings_present', 'questions_changed', 'model_changed', 'new_fits', 'expert_responses', 'uploads', 'contacts', 'independent_final_evaluation', 'unchanged_model_sha256']),
        'MSTE_development_packet_pixel_checks': ('outputs/wb314_mste_development_packet_v1/verification.json', ['passed', 'model_sha256', 'pairs', 'publisher_MST_categories', 'slots_per_category', 'subjects', 'subject_counts_by_MST', 'condition_counts', 'portable_route_checks', 'exact_scalar_RGB8_checks', 'exact_PNG_roundtrips', 'actual_model_fits', 'questions_changed', 'Form_edits', 'uploads', 'expert_responses', 'independent_final_evaluation', 'dataset_training', 'reference_attempts']),
        'MSTE_packet_appearance_trace': ('outputs/wb314_mste_packet_appearance_feedback_v1/trace.json', ['passed', 'user_feedback_kind', 'release_approval_received', 'expert_ratings_created', 'no_new_human_per_case_labels', 'source_resize_exact_cases', 'synthetic_input_exact_cases', 'outside_preservation_exact_cases', 'supported_mechanism', 'sharpening_trace', 'new_model_calls', 'new_fits', 'new_correction_renders', 'source_images_redecoded_for_trace', 'source_or_output_pixels_modified', 'model_sha256']),
        'MSTE_packet_v2_preparation_and_presentation': ('outputs/wb314_mste_development_packet_v2_area/packet_status.json', ['passed', 'pairs', 'subjects', 'publisher_MST_categories', 'condition_counts', 'official_label_Form_slot_source_joins', 'independently_replayed_routes', 'independently_replayed_RGB8', 'protected_outside_checks', 'full_frame_PNG_checks', 'exact_native_face_crop_checks', 'original_source_hash_checks', 'changed_controls_from_v1', 'new_fits', 'model_sha256', 'normalization', 'presentation', 'distribution_ready', 'appearance_concern_resolved', 'questions_changed', 'Form_edits', 'uploads', 'expert_responses', 'new_user_ratings', 'independent_final_evaluation', 'known_support_limitations_retained', 'reference_attempts', 'reference_failures', 'replacements', 'reference_process_exit_code', 'prediction_process_exit_code']),
        'MSTE_V2_development_round1_release': ('outputs/wb314_mste_development_round1_release_v1/summary.json', ['round_id', 'model_sha256', 'local_materials_released', 'user_authorized_initial_development_round', 'pairs', 'subjects', 'publisher_MST_categories', 'byte_identical_V2_PNG_copies', 'exact_Form_slot_joins', 'questions_changed', 'live_Form_updated', 'Form_images_inserted', 'connected_document_sessions', 'browser_control_available', 'live_Form_step_pending', 'expert_responses', 'invitations_sent', 'new_fits', 'new_predictions', 'resampling', 'independent_final_appraisal', 'final_model_adoption', 'known_support_limitations_disclosed', 'old_drafts_and_feedback_preserved']),
        'MSTE_V2_large_presentation': ('outputs/wb314_development_feedback_large_v1/summary.json', ['round_id', 'presentation_version', 'parent_model_sha256', 'pairs', 'subjects', 'MST_categories', 'scale', 'native_face_width_range', 'large_face_width_range', 'exact_pixel_repeat_checks', 'native_PNG_byte_copies', 'all16_offsets_checked_per_pair', 'invented_high_resolution_detail', 'sharpening', 'new_model_calls', 'new_fits', 'source_portrait_decodes', 'masks_changed', 'questions_changed', 'model_changed', 'live_Form_updated', 'expert_responses_created', 'prior_packages_preserved', 'presentation_user_requested']),
        'MSTE_V2_before_after_pairing': ('outputs/wb314_before_after_feedback_v1/summary.json', ['round_id', 'presentation', 'model_sha256', 'pairs', 'subjects', 'publisher_MST_categories', 'unchanged_Form_slot_joins', 'exact_input_left_checks', 'exact_saved_candidate_right_checks', 'exact_4x_repeat_checks', 'left_is_clean_reference', 'clean_reference_kept_for_quantitative_restoration', 'questions_changed', 'scale_changed', 'intro_clarification_prepared', 'live_Form_updated', 'new_fits', 'new_model_calls', 'new_source_portrait_decodes', 'new_human_ratings', 'model_changed', 'masks_changed', 'previous_outputs_and_packages_preserved', 'rating_transfer', 'independent_final_evaluation']),
        'MSTE_normal_photo_preview': ('outputs/wb314_normal_photo_preview_v1/summary.json', ['passed', 'model_sha256', 'cases', 'subjects', 'MST_categories', 'input_role', 'exact_unchanged_outputs', 'changed_outputs', 'logical_model_calls', 'portable_route_checks', 'exact_scalar_RGB8_checks', 'input_immutability_checks', 'protected_outside_checks', 'PNG_roundtrips', 'new_fits', 'new_source_portrait_decodes', 'synthetic_distortion_calls', 'mask_inference', 'model_changed', 'high_resolution_output', 'expert_responses', 'new_human_ratings', 'improvement_on_naturally_faulty_photos_established', 'independent_final_validation', 'automatic_new_photo_masking_qualified', 'Form_edits', 'automatic_expert_packet_replacement']),
        'MSTE_normal_photo_interpretation': ('outputs/wb314_normal_photo_preview_v1/independent_audit_and_interpretation.json', ['passed', 'cases', 'exact_input_outputs', 'changed_outputs', 'normal_inputs_selecting_brightening_gain', 'brightening_gain_values', 'all20_normal_inputs_join_cached_undistorted_references', 'independent_protected_outside_checks', 'exact_embedded_PNG_bytes', 'contact_sheets_viewed', 'assistant_visual_concern', 'general_improvement_on_normal_photos_established', 'no_failure_gate_retrofitted', 'model_changed', 'expert_packet_automatically_replaced', 'new_audit_model_calls', 'new_fits', 'interactive_browser_tested']),
        'WB314_headroom_cap_assessment': ('outputs/wb314_exposure_headroom_assessment_v1/summary.json', ['passed', 'gates', 'cases', 'changed_outputs_by_group', 'capped_controls_by_group', 'new_model_calls', 'new_fits', 'scalar_changed_control_checks', 'protected_outside_checks', 'raw_and_guarded_normal_target_overflow', 'auto_wrapper_integration_permitted', 'original_tree_unchanged', 'all_normal_correction_necessity_solved', 'new_human_ratings', 'scientific_or_final_adoption']),
        'WB314_headroom_independent_audit': ('outputs/wb314_exposure_headroom_assessment_v1/independent_audit.json', ['passed', 'guard_assessment_screen_pass', 'all106_protection_and_old_output_checks', 'original66_input_artifact_hash_joins', 'independent_scalar_headroom_bounds', 'focused_triple_PNG_checks', 'focused_embedded_PNG_checks', 'active_wrapper_changed', 'model_changed', 'new_fits', 'new_model_calls']),
        'WB314_headroom_confirmed_feedback': ('outputs/wb314_exposure_headroom_user_feedback_v1/publication_aggregate_summary.json', ['passed', 'clarification_complete', 'user_feedback_mixed', 'cap_adopted', 'active_model_changed', 'old_screen_still_failed', 'model_necessity_detection_proven', 'new_model_calls', 'new_fits', 'new_guard_variants', 'guard_pixel_scope_diagnosis_complete', 'existing11_FFHQ_masks_available_hash_verified', 'followon_scope_proposal_executed']),
        'WB314_facial_headroom_scope': ('outputs/wb314_facial_headroom_assessment_v1/summary.json', ['passed', 'gates', 'cases', 'model_sha256', 'policy', 'guard_module_sha256', 'prior_outputs_exact', 'prior_outputs', 'expected_normal_outputs_exact', 'normal_outputs', 'changed_controls', 'changed_control_scalar_checks', 'protected_outside_checks', 'input_immutability_checks', 'new_model_inference', 'new_fits', 'source_JPEG_decodes', 'mask_inference', 'automatic_integration_permitted', 'general_correction_necessity_proven', 'final_qualification_complete', 'expert_Form_changed', 'new_human_ratings']),
        'WB314_non_replacing_headroom_advisory': ('outputs/wb314_headroom_advisory_integration_v1/final_summary.json', ['passed', 'finalized', 'cached_cases', 'primary_RGB8_exact_previous', 'primary_controls_features_exact', 'candidate_exact_existing_scoped_outputs', 'separate_candidate_differences', 'input_immutability_checks', 'primary_and_candidate_arrays_independent', 'native_constructor_without_inference', 'cached_base_replay_calls', 'new_trained_model_or_encoder_inference', 'new_fits', 'new_guard_variant', 'headroom_applied_to_primary', 'automatic_highlight_repair', 'original_scoped_screen_pass', 'primary_policy', 'advisory_policy', 'model_sha256', 'primary_pipeline_qualification_complete', 'Android_defaults_changed', 'expert_Form_changed', 'new_human_ratings', 'generated_wrapper_tests', 'generated_fixture_and_sequence_issue_recorded', 'production_wrapper_unchanged_after_cached_replay', 'primary_preview_PNG_byte_joins', 'candidate_preview_PNG_checks', 'embedded_PNG_byte_and_dimension_checks', 'research_advisory_integrated', 'scoped_cap_automatically_adopted']),
    }
    specs['WB314_normal_photo_Form_release'] = (
        'outputs/wb314_normal_photo_expert_form_release_v1/summary.json',
        ['passed', 'round_id', 'model_sha256', 'pairs', 'subjects', 'publisher_MST_categories',
         'exact_primary_PNG_copies', 'exact_official_label_Form_slot_joins', 'embedded_PNG_byte_checks',
         'normal_inputs_without_added_synthetic_distortion', 'protected_alternatives_included',
         'questions_changed', 'existing_instrument_definitions_verified', 'intro_clarification_prepared',
         'live_Form_updated', 'Form_images_inserted_by_agent', 'connected_document_sessions',
         'live_Form_step_pending', 'expert_responses_accessed', 'invitations_sent', 'responses_submitted',
         'new_fits', 'new_predictions', 'new_correction_renders', 'source_JPEG_reads',
         'new_human_ratings', 'independent_final_validation', 'correction_model_finished'])
    for name, (source, keys) in specs.items():
        p = ROOT / source
        data = json.loads(p.read_text(encoding='utf-8'))
        selected = {k: data[k] for k in keys}
        if name == 'actual_piq_head':
            for split in ['Train', 'Test']:
                selected[split] = {k: v for k, v in selected[split].items() if k != 'per_scene'}
        snapshot['studies'][name] = dict(local_source=source, source_sha256=sha(p), values=selected)
    write_json(DOCS / 'evidence-snapshot.json', snapshot)

    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    documents = [p for p in paths if p.startswith('docs/') and p.endswith('.md') and p != 'docs/thesis/document-index.md']
    lines = ['# Complete research document index', '',
             'Generated from the current source checkout. Read [THESIS_START_HERE.md](../../THESIS_START_HERE.md) first.',
             'Titles identify records; they do not certify completion or supersede later results. Local artifact paths inside records are not published evidence files.', '',
             'Personal appeal-letter material is excluded. Original file encodings are preserved in Git; the upload text uses decoded UTF-8 copies.', '']
    for p in documents:
        value, _ = text(ROOT / p)
        title = next((s.lstrip('# ').strip() for s in value.splitlines() if s.startswith('# ')), Path(p).stem)
        title = title.replace('[', '(').replace(']', ')').replace('\n', ' ')
        relative = Path(p).relative_to('docs').as_posix()
        lines.append(f'- [{title}](../{relative}) — `{p}`')
    (DOCS / 'document-index.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    syntax_errors = []
    encodings = []
    secret_findings = []
    checks = {
        'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,})',
        'openai_key': r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
        'aws_key': r'\bAKIA[0-9A-Z]{16}\b',
    }
    for p in paths:
        content, encoding = text(ROOT / p)
        if encoding != 'utf-8':
            encodings.append(dict(path=p, encoding=encoding))
        for kind, pattern in checks.items():
            if re.search(pattern, content):
                secret_findings.append(dict(path=p, kind=kind))
        if p.endswith('.py'):
            try:
                ast.parse(content, filename=p)
            except SyntaxError as error:
                syntax_errors.append(dict(path=p, line=error.lineno, error=error.msg))
    if secret_findings:
        raise RuntimeError('Publication scan needs review: ' + json.dumps(secret_findings))
    if syntax_errors:
        raise RuntimeError('Python syntax errors: ' + json.dumps(syntax_errors))

    report = dict(checkpoint=checkpoint, publication_scope='Research documentation/source on development branch; not a validated release',
                  indexed_documents=len(documents), source_python_files=sum(p.endswith('.py') for p in paths),
                  syntax_errors=syntax_errors, high_confidence_secret_findings=secret_findings,
                  historical_non_UTF8_files_preserved=encodings,
                  focused_checks=dict(tests=['tests/test_correction_preview.py', 'tests/test_manual_refinement.py', 'tests/test_demo_current_masking.py'],
                                      result='Prior checkpoint: 28 passed in 5.11s', note='Historical generated-fixture checks, not rerun for this documentation/research-adapter publication. Current adapter parity is separately reported in evidence-snapshot.json; neither is scientific qualification.'),
                  source_data_and_models_included=False, locked_allocations_accessed=False,
                  original_proposal_and_current_editable_manuscript_included=False,
                  personal_appeal_material_included=False)
    write_json(DOCS / 'publication-check.json', report)
    paths = [p for p in repository_paths() if eligible(p) and (ROOT / p).is_file()]
    paths = [p for p in paths if p != 'docs/thesis/file-manifest.json']
    entries = [dict(path=p, bytes=(ROOT / p).stat().st_size, sha256=sha(ROOT / p)) for p in paths]
    write_json(DOCS / 'file-manifest.json', dict(files=entries, note='Manifest excludes itself; checks raw local bytes before Git line-ending conversion.'))
    paths.append('docs/thesis/file-manifest.json')

    destination.mkdir(parents=True)
    context_paths = ['THESIS_START_HERE.md', 'docs/thesis/chatgpt-writing-prompt.md', 'docs/thesis/research-map.md',
                     'docs/thesis/evidence-snapshot.json', 'docs/thesis/publication-check.json', 'AGENTS.md']
    context_paths += [p for p in paths if p.startswith('docs/') and p.endswith('.md') and p not in context_paths]
    # Keep each text part well below the official 2M-token ceiling even under the
    # conservative one-token-per-UTF8-byte bound. This is not a tokenizer estimate.
    pieces = []
    current = f'TRUEHUE THESIS HANDOFF — {checkpoint}\nRead THESIS_START_HERE.md first. Historical records can be superseded.\n'
    for p in context_paths:
        content, encoding = text(ROOT / p)
        section = f'\n\n===== FILE: {p} | original_encoding={encoding} | sha256={sha(ROOT / p)} =====\n{content}\n===== END FILE =====\n'
        if len((current + section).encode('utf-8')) > 1_400_000 and current:
            pieces.append(current)
            current = 'TRUEHUE THESIS HANDOFF CONTINUATION — read part01 and THESIS_START_HERE.md first.\n'
        current += section
    if current:
        pieces.append(current)
    for i, content in enumerate(pieces, 1):
        (destination / f'TrueHue-thesis-context-part{i:02d}.txt').write_text(content, encoding='utf-8')
    archive_name = f'TrueHue-research-source-{checkpoint}.zip'
    with zipfile.ZipFile(destination / archive_name, 'x', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(set(paths)):
            archive.write(ROOT / p, p)
    write_json(destination / 'verification.json', dict(passed=True, checkpoint=checkpoint, source_files=len(set(paths)), documents=len(documents),
               text_parts=len(pieces), parts={p.name: sha(p) for p in destination.glob('*.txt')},
               source_zip_sha256=sha(destination / archive_name),
               raw_datasets_photos_weights_private_outputs_included=False))
    print(json.dumps(dict(passed=True, documents=len(documents), source_files=len(set(paths)),
                         python_syntax_files=report['source_python_files'], text_parts=len(pieces),
                         historical_encodings_preserved=len(encodings), delivery=str(destination)), indent=2))


if __name__ == '__main__':
    main()
