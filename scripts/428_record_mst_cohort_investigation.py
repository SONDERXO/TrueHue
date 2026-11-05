"""Record primary-source research and an UNSENT inquiry; no network or fitting."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/mst_cohort_source_investigation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
SOURCES=[
 dict(id='stellenbosch_diverse_lighting',priority='first_access_inquiry',
      primary_url='https://www.mdpi.com/2313-433x/10/5/109',
      supporting_url='https://pmc.ncbi.nlm.nih.gov/articles/PMC11122461/',
      code_url='https://github.com/skmbatha/MEng-Skin-tone-estimation-using-VGG-16',
      evidence='paper285participants21375images15lights5poses_manualMST_and_data_on_request',
      limitation='actual_release_subject_label_manifest_recipient_terms_and_category_counts_not_received',
      status='promising_request_only_not_qualified',calibration_permission_verified=False,images_obtained=False),
 dict(id='casual_conversations_v2',priority='evaluation_role_only_pending_permissions',
      primary_url='https://ai.meta.com/datasets/casual-conversations-v2-dataset/',
      supporting_url='https://ai.meta.com/datasets/casual-conversations-v2-downloads/',code_url='',
      evidence='human_apparent_tone_labels_subjectIDs_published_grant_separates_development_and_evaluation_annotations',
      limitation='do_not_assume_supplied_apparent_tone_labels_permitted_for_calibration_fitting',
      status='not_qualified_for_calibration',calibration_permission_verified=False,images_obtained=False),
 dict(id='google_HR_study',priority='request_lead_with_source_specific_requirements',
      primary_url='https://github.com/Google-Health/consumer-health-research/blob/main/rppg/README.md',
      supporting_url='https://github.com/Google-Health/consumer-health-research/blob/main/rppg/term_of_service.md',code_url='',
      evidence='lab_faces_skin_tone_by_request_free_living_forehead_patches_academic_ethics_and_security_conditions',
      limitation='no_recipient_access_actual_label_manifest_or_matching_sample',
      status='request_only_not_qualified',calibration_permission_verified=False,images_obtained=False),
 dict(id='rPPG_demographic_bias',priority='do_not_use_proxy_labels',
      primary_url='https://www.nature.com/articles/s41746-025-01973-9',
      supporting_url='https://github.com/Maksym-Bondarenko/rppg-ethnicity-paper',code_url='',
      evidence='ethnicity_to_tone_heuristics_plus_separate_small_PURE_rater_check',
      limitation='not_a_verified_matching_humanMST_face_cohort_no_proxy_labels_allowed',
      status='unsuitable_as_calibration_label_shortcut',calibration_permission_verified=False,images_obtained=False)]


def main():
    if OUT.exists():raise FileExistsError(OUT)
    prior=ROOT/'outputs/ffhq_source_eligibility_v1'
    hashes=read(prior/'plan.json')['input_sha256']
    hashes.update({str(prior/p):h for p,h in read(prior/'sha256.json').items()})
    files=[Path(__file__),ROOT/'docs/mst-cohort-source-investigation-2026-11-05.md',
           ROOT/'docs/mst-stellenbosch-access-request-draft-2026-11-05.md']
    hashes.update({str(p):sha(p) for p in files})
    assert all(sha(p)==h for p,h in hashes.items())
    assert len(SOURCES)==len({r['id'] for r in SOURCES})==4
    assert all(not r['images_obtained'] and not r['calibration_permission_verified'] for r in SOURCES)
    OUT.mkdir()
    result=dict(review_date='2026-11-05',source_records=SOURCES,
        user_confirmed_STW_no_new_reply_or_files=True,STW_existing_holds_unchanged=True,
        status='new_access_lead_and_unsent_request_ready_no_qualified_cohort_obtained',
        external_verification_scope='web_browsing_of_primary_source_or_publisher_indexed_text_not_local_full_snapshot',
        fetch_limits=['some_MDPI_direct_opens_HTTP429','some_PMC_opens_anti_bot_page_no_bypass',
            'Meta_download_page_dynamic_body_missing_on_direct_open_agreement_text_available_in_index'],
        request_draft_sha256=sha(files[2]),request_recipient='rptheart@sun.ac.za',
        recipient_provenance='paper_corresponding_author_Rensu_P_Theart',message_sent=False,
        accounts_created=0,agreements_accepted=0,payments=0,new_dataset_photos=0,new_models=0,
        new_inference=0,calibration_fits=0,tree_fits=0,calibration_admissions=0,
        old19subject_review_repeated=False,fake_FFHQ_MST_labels=False,
        input_sha256=hashes,source_fact_bytes_archived=False)
    (OUT/'investigation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (OUT/'sources.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(SOURCES[0]));writer.writeheader();writer.writerows(SOURCES)
    with (OUT/'sources.csv').open(newline='',encoding='utf-8') as stream:rows=list(csv.DictReader(stream))
    assert [r['id'] for r in rows]==[r['id'] for r in SOURCES]
    assert all(sha(p)==h for p,h in hashes.items())
    (OUT/'verification.json').write_text(json.dumps(dict(source_rows=4,CSV_JSON_membership_parity=True,
        prior_inputs_and_packages_unchanged=True,request_unsent=True,no_data_or_model_processing=True),indent=2))
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2))
    print(json.dumps({k:result[k] for k in ['status','message_sent','new_dataset_photos','calibration_fits','calibration_admissions']},indent=2))


if __name__=='__main__':main()
