"""Record full-resolution source screen and safe lineage holds; no ML or fits."""
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/ffhq_source_eligibility_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
BLOCK='ffhq_fixed12_development_person_relationships_unresolved'
NOTES={
 '54632': ('Visible forehead/cheeks/nose and fine skin/beard detail are judgeable; softer eye detail, bright cap, beard and head covering remain.',
           'Neck obscured by beard, side covering and crop; do not infer complete neck.', 'hold_observed_beard_pixels'),
 '39568': ('Visible facial detail and hair boundary are judgeable; directional shadows, forehead highlights and a strand across face remain.',
           'Some visible neck under chin, lower part cropped; neck support still needs eligibility.', 'unverified_skin_not_admitted'),
 '29617': ('Visible nose/cheek/mouth/chin detail is judgeable; sunglasses and hand conceal other regions and remain part of the reference.',
           'Hand, clothing and lower crop restrict neck; occluded anatomy is unavailable.', 'unverified_occlusion_stubble_boundaries'),
 '29863': ('Visible facial texture is judgeable despite dim/uneven appearance; prominent beard and white head covering retained as limitations.',
           'Partial neck visible below beard toward collar; support may include covering under severe distortion.', 'hold_observed_beard_pixels'),
 '16061': ('Visible facial/stubble detail is judgeable; clear lenses contain strong reflections over the eyes, not a clear-eye truth reference.',
           'Partial neck visible near shirt collar; clothing boundary and crop remain.', 'unverified_glasses_fringe_stubble_boundaries'),
 '52445': ('Visible face is judgeable with fine surface detail and some soft areas; clothing/foreground sits immediately below chin.',
           'No clearly exposed neck in original; do not require invented neck or equate zero neck mask with facial-reference failure.', 'unverified_skin_not_admitted'),
 '32685': ('Visible cheeks/nose/mouth are judgeable despite downward pose and softer bright appearance; fringe covers upper forehead.',
           'Neck mostly hidden by pose and collar; saved collar inclusion is a support concern, not demonstrated neck skin.', 'unverified_fringe_and_chin_boundaries'),
 '53146': ('Visible facial texture is judgeable; strong sunlight/shadows, squint and cap remain; no claim of recoverable clipped detail.',
           'Only limited lower/side neck near crop/collar; no complete neck claim.', 'unverified_cap_shadow_stubble_boundaries'),
 '48879': ('Visible face is judgeable at oblique pose with soft fine detail; blond hair crosses temple/outer cheek and remains in original.',
           'Partial neck visible beside scarf and hair; pose/hair association uncertain.', 'hold_observed_possible_hair_pixels'),
 '49131': ('Broad facial detail is judgeable; some softness and stubble remain, with visible tonal variation rather than calibrated colour.',
           'Broad visible neck above collar; actual-input jaw/neck transition is a separate support issue.', 'unverified_stubble_and_fine_boundaries'),
 '59807': ('Visible facial texture is judgeable; thin clear-glasses rims, reflections, fringe, microphone and hand remain observable limits.',
           'Visible neck is partly hidden by microphone/hand and bounded by necklace/clothing.', 'unverified_glasses_fringe_microphone_boundaries'),
 '46795': ('Visible face detail is judgeable despite strong outdoor light/shadow, squint, bright background and slight softness.',
           'High collar and crop hide almost all neck; tiny predicted fragments are not proof of usable neck.', 'unverified_fringe_shadow_boundaries')}


def write(path,data):path.write_text(json.dumps(data,indent=2),encoding='utf-8')
def export(path,rows):
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    if OUT.exists():raise FileExistsError(OUT)
    source=ROOT/'outputs/ffhq_source_preparation_v1'
    latest=ROOT/'outputs/ffhq_distorted_input_support_v1'
    hashes=read(latest/'inference_plan.json')['input_sha256']
    for folder in [latest,ROOT/'outputs/ffhq_distorted_input_support_assessment_v1',source]:
        hashes.update({str(folder/p):h for p,h in read(folder/'sha256.json').items()})
        hashes[str(folder/'sha256.json')]=sha(folder/'sha256.json')
    mstpath=ROOT/'outputs/mst_subject_skin_study_import_v1/summary.json'
    for p in [Path(__file__),ROOT/'docs/ffhq-source-eligibility-protocol-2026-11-05.md',mstpath,
        ROOT/'docs/mst-subject-skin-study-results-2026-11-02.md',ROOT/'docs/faceocc-mst-feasibility-decision-2026-11-01.md']:
        hashes[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in hashes.items())
    attempts=read(source/'attempts.json');selected=read(source/'selected_before_pixels.json')['sources']
    support={r['id']:r for r in read(ROOT/'outputs/ffhq_mask_support_assessment_v1/assessment.json')['records']}
    actual=read(latest/'results.json')['records']
    assert {r['id'] for r in attempts}==set(NOTES)
    assert [r['id'] for r in attempts]==[r['id'] for r in selected]
    assert len({r['metadata']['photo_url'] for r in selected})==12
    assert len({r['pixel_md5'] for r in attempts})==12
    OUT.mkdir()
    write(OUT/'plan.json',dict(protocol_sha256=sha(ROOT/'docs/ffhq-source-eligibility-protocol-2026-11-05.md'),
        input_sha256=hashes,source_screen='assistant_all12_original1024px_images_inspected',
        inference=0,fits=0))
    records=[]
    for row,meta in zip(attempts,selected):
        sid=row['id'];photo=meta['metadata'];ref,neck,measurement=NOTES[sid]
        assert sha(ROOT/row['path'])==row['access']['sha256']
        records.append(dict(id=sid,source_path=row['path'],source_sha256=row['access']['sha256'],
            original_photo_url=photo['photo_url'],author=photo['author'],recorded_license=photo['license'],license_url=photo['license_url'],
            rights_scope='existing_recorded_local_research_role_NOT_new_terms_review_or_publication_clearance',
            reference_screen='usable_visible_face_reference_with_limits',reference_screen_pass=True,
            reference_scope='photographic_restoration_to_original_visible_pixels_NOT_intrinsic_colour_or_ideal_light',
            reference_observation=ref,neck_observation=neck,
            correction_support='experimental_unadmitted_not_blanket_rejected',
            correction_concern=support[sid]['correction_observation'],
            measurement_skin=measurement,measurement_concern=support[sid]['measurement_observation'],
            measurement_admitted=False,correction_training_support_admitted=False,
            identity_lineage='ffhq_photo_'+sid,person_id=None,independent_person_verified=False,
            leakage_holding_block=BLOCK,holding_block_is_person_identity=False,
            source_role='development_exposed_unallocated',unseen_final_evaluation_eligible=False,
            MST=None,matching_MST_available=False,full_pipeline_training_admitted=False,
            observer='assistant',human_approval=False))
    byid={r['id']:r for r in records};descendants=[]
    for row in actual:
        parent=byid[row['source_id']]
        descendants.append(dict(case_id=row['image_id'],source_id=row['source_id'],
            lineage=parent['identity_lineage'],leakage_holding_block=BLOCK,
            role='development_exposed_unallocated',layer=row['case']['layer'],
            technical_status=row['status'],full_pipeline_training_admitted=False,person_id=None))
    assert len(records)==12 and len(descendants)==168
    assert all(sum(x['source_id']==r['id'] for x in descendants)==14 for r in records)
    assert len({r['leakage_holding_block'] for r in descendants})==1
    mst=read(mstpath)
    mst_decision=dict(status='no_calibration_run_existing_admission_scope_gap_not_resolved_by_FFHQ_screen',
        reviewed_subjects=mst['attempts'],favourable_structured_reviews=mst['favourable_structured_visual_answers'],
        concern_or_uncertain=mst['structured_concern_or_uncertainty'],original_failures=mst['technical_failures'],
        matching_measurement_contract='89c7a3963dcc72bfa8c7b73433789b058093131662c88a6d30a7f25d791823fd',
        old393_features_compatible=False,FFHQ_labels_invented=False,
        next_evidence_needed=['exact_matching_labelled_photos_with_actual_skin_eligibility_and_retained_concerns',
            'justified_category_and_person_scope_with_adequacy_before_fitting',
            'one_subject_held_protocol_with_same_row_baseline_and_failure_denominators'],
        not_activated=['same_favourable_subset_fit','repeat19_subject_review','automatic755_batch','label_by_appearance','training_without_MST'])
    result=dict(records=records,reference_screen_passes=12,full_pipeline_training_admissions=0,
        lineage_keys=12,conservative_unsplit_development_blocks=1,verified_person_count=None,
        descendants=descendants,MST_decision=mst_decision,new_inference=0,new_fits=0,
        full_resolution_source_images_inspected=12,new_human_annotation_task=False)
    write(OUT/'eligibility.json',result);export(OUT/'sources.csv',records);export(OUT/'descendants.csv',descendants)
    with (OUT/'sources.csv').open(newline='',encoding='utf-8') as stream:csvsources=list(csv.DictReader(stream))
    with (OUT/'descendants.csv').open(newline='',encoding='utf-8') as stream:csvchildren=list(csv.DictReader(stream))
    assert [r['id'] for r in csvsources]==[r['id'] for r in records]
    assert [r['case_id'] for r in csvchildren]==[r['case_id'] for r in descendants]
    assert all(r['leakage_holding_block']==BLOCK for r in csvchildren)
    cards=[]
    for r in records:
        cards.append('<section><h2>'+r['id']+' — usable visible-face reference; training held</h2>'+
            '<img loading="lazy" src="../../'+r['source_path']+'"><p>'+html.escape(r['reference_observation'])+'</p><p>'+html.escape(r['neck_observation'])+
            '</p><p>Measurement: '+html.escape(r['measurement_skin'])+'. '+html.escape(r['measurement_concern'])+'</p><p>Correction: '+html.escape(r['correction_concern'])+
            '</p><p>Recorded attribution: '+html.escape(r['author'])+' · <a href="'+html.escape(r['original_photo_url'],quote=True)+'">Original photo</a> · '+
            '<a href="'+html.escape(r['license_url'],quote=True)+'">'+html.escape(r['recorded_license'])+'</a></p></section>')
    (OUT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Source eligibility decisions</title>'+
        '<style>body{font:18px system-ui;max-width:1100px;margin:auto;padding:20px}img{width:100%;max-width:650px}section{border-top:1px solid #aaa}</style>'+
        '<h1>12 source references: usability and separate holds</h1><p>Assistant full-resolution screen: all12 have judgeable visible-face pixels for photographic restoration. '+
        'No full-pipeline training admissions. Correction/measurement/MST/person-split gates remain separate. '+
        'All168 descendants stay in one unsplit development holding block; this does not assert one person or independent people. '+
        'No new inference, fits, contact or human annotation task.</p>'+''.join(cards),encoding='utf-8')
    assert all(sha(p)==h for p,h in hashes.items())
    write(OUT/'verification.json',dict(source_rows=12,descendant_rows=168,descendants_per_source=14,
        unique_photo_URLs=12,unique_original_pixel_hashes=12,verified_people=None,
        train_dev_test_split_created=False,CSV_JSON_membership_parity=True,
        all_input_and_historical_hashes_unchanged=True,new_fits=0,new_inference=0))
    write(OUT/'sha256.json',{p.name:sha(p) for p in OUT.iterdir() if p.is_file()})
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','descendants','MST_decision']},indent=2))


if __name__=='__main__':main()
