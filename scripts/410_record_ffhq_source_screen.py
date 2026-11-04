"""Record assistant contact-sheet observations, never human approval or MST labels."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/ffhq_source_preparation_v1'
OUT=ROOT/'outputs/ffhq_source_visual_assessment_v1'
NOTES={
 '54632':'Cap/head covering and prominent beard; lower face/neck near crop edge.',
 '39568':'Hair at face edge and directional facial shadows; cropped lower neck.',
 '29617':'Sunglasses obscure eyes; hand covers cheek/jaw; pose and tight crop require support checks.',
 '29863':'Dim/uneven facial appearance, prominent beard and head covering.',
 '16061':'Eyeglasses with reflections; lower neck partly clothing/crop.',
 '52445':'Tight face crop with clothing at lower edge; visible-neck coverage must be checked.',
 '32685':'Downward head pose and fringe; neck partly collar/clothing.',
 '53146':'Strong directional sunlight/shadows and squint; head covering; tight lower crop.',
 '48879':'Strong profile/oblique pose and hair near face; pose-specific support checks needed.',
 '49131':'Relatively frontal unobstructed face; facial support/neck still unverified.',
 '59807':'Eyeglasses and microphone near lower face; object exclusion needed for measurement.',
 '46795':'Strong outdoor lighting and bright background; pose/neck crop require checking.'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if (OUT/'assistant_assessment.json').exists():
        raise FileExistsError('Do not overwrite recorded observations')
    manifest=json.loads((PARENT/'sha256.json').read_text())
    assert all(sha(PARENT/k)==v for k,v in manifest.items())
    selected=json.loads((PARENT/'selected_before_pixels.json').read_text())['sources']
    attempts=json.loads((PARENT/'attempts.json').read_text())
    assert set(NOTES)=={r['id'] for r in selected}
    assert [r['id'] for r in selected]==[r['id'] for r in attempts]
    records=[]
    for row,attempt in zip(selected,attempts):
        assert attempt['access']['success'] and sha(ROOT/attempt['path'])==attempt['access']['sha256']
        records.append(dict(id=row['id'],source_path=attempt['path'],source_sha256=attempt['access']['sha256'],
            observation=NOTES[row['id']],observer='assistant',
            evidence_scope='all12_on_saved_contact_sheet_not_full_resolution_quality_or_mask_review',
            disposition='retain_source_candidate_with_concerns_no_replacement',
            human_review_requested=False,photographic_quality_admitted=False,
            measurement_mask_admitted=False,correction_mask_admitted=False,
            person_independence_verified=False,MST=None,training_admitted=False))
    result=dict(status='bounded_source_acquisition_and_contact_sheet_screen_complete',
        user_scope='FFHQ source work authorised; ITA-to-MST deferred, not omitted from retained model',
        records=records,raw_photos=12,inference=0,fits=0,training_admissions=0,
        identity_recognition_performed=False,manual_annotation_batch_activated=False,
        source_photo_groups=12,person_count=None,tone_coverage=None,
        metadata_sha256=json.loads((PARENT/'metadata_access.json').read_text())['result']['sha256'],
        parent_manifest_sha256=sha(PARENT/'sha256.json'))
    (OUT/'assistant_assessment.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    headers=['ffhq_id','author','photo_url','licence','licence_url','source_path','source_sha256',
             'publisher_role','TrueHue_role','original_pixel_md5','person_group','MST','modifications']
    with (OUT/'attribution_and_source_ledger.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=headers);writer.writeheader()
        for row,attempt in zip(selected,attempts):
            meta=row['metadata']
            writer.writerow(dict(ffhq_id=row['id'],author=meta['author'],photo_url=meta['photo_url'],
                licence=meta['license'],licence_url=meta['license_url'],source_path=attempt['path'],
                source_sha256=attempt['access']['sha256'],publisher_role=row['publisher_category'],
                TrueHue_role='development_exposed_not_unseen_final',
                original_pixel_md5=row['in_the_wild']['pixel_md5'],person_group='',MST='',
                modifications='publisher_alignment_crop;TrueHue_bytes_unmodified;gallery_scaled_display_only'))
    text='# Assistant source screen — not training admission\n\n'
    text+='All12 selected sources retained. Observations are from the contact sheet, not dense mask or full-resolution reference approval. No MST labels were assigned.\n\n'
    text+='| FFHQ ID | Observation |\n|---|---|\n'
    text+='\n'.join('| '+r['id']+' | '+r['observation']+' |' for r in records)
    (OUT/'source-screen.md').write_text(text+'\n',encoding='utf-8')
    with (OUT/'attribution_and_source_ledger.csv').open(newline='',encoding='utf-8') as stream:
        assert [r['ffhq_id'] for r in csv.DictReader(stream)]==[r['id'] for r in records]
    plan=ROOT/'outputs/integrated_correction_plan_v1'
    plan_sources=json.loads((plan/'source_hashes.json').read_text())
    plan_parents=json.loads((plan/'parent_manifest_hashes.json').read_text())
    assert all(sha(ROOT/k)==v for k,v in plan_sources.items())
    assert all(sha(ROOT/'outputs'/k/'sha256.json')==v for k,v in plan_parents.items())
    (OUT/'verification.json').write_text(json.dumps(dict(parent_manifest_unchanged=True,
        source_files_verified=12,attribution_CSV_JSON_membership=True,
        distinct_photo_urls=len({r['metadata']['photo_url'] for r in selected}),
        distinct_original_pixel_hashes=len({r['in_the_wild']['pixel_md5'] for r in selected}),
        independent_people_not_established=True,integrated_plan_sources_unchanged=len(plan_sources),
        integrated_parent_manifests_unchanged=len(plan_parents),
        source_hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [
            ROOT/'scripts/408_prepare_ffhq_sources.py',ROOT/'scripts/409_build_ffhq_source_gallery.py',
            ROOT/'scripts/410_record_ffhq_source_screen.py',ROOT/'tests/test_ffhq_source_download.py']}
        ),indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()
        if p.is_file()},indent=2),encoding='utf-8')
    print('12sources retained; attribution/source hashes and unchanged plan evidence verified; MST deferred.')


if __name__=='__main__':
    main()
