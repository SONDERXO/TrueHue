"""Primary saved SCIN CSV/role joins; no photograph bytes or image hashing."""
from pathlib import Path
from collections import Counter
import csv,hashlib,io,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/scin_nine_provenance_review_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial reconciliation')
    bound={}
    def read(path,kind='json'):
        path=Path(path);raw=path.read_bytes();bound[str(path)]=hashlib.sha256(raw).hexdigest()
        return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))) if kind=='csv' else json.loads(raw)
    local=read(ROOT/'outputs/local_labelled_photographic_source_review_v1/scin_nine_case_readiness_PRIVATE.json')
    checkpoint=read(ROOT/'outputs/mst_retention_checkpoint_v1/summary.json')
    base=ROOT/'data/raw/scin/metadata'
    cases=read(base/'dataset_scin_cases.csv','csv');labels=read(base/'dataset_scin_labels.csv','csv')
    questions=read(base/'dataset_scin_label_questions.csv','csv')
    selection=read(ROOT/'data/manifests/scin_candidate_selection.csv','csv')
    downloads=read(ROOT/'data/manifests/scin_download_log.csv','csv')
    partitions=read(ROOT/'data/manifests/source_preparation_v1/source_audit_and_partitions.csv','csv')
    duplicates=read(ROOT/'data/manifests/source_preparation_v1/duplicate_candidate_pairs.csv','csv')
    correction=read(ROOT/'outputs/correction_data_redesign_v1/selection.json')['selected']
    dispositions=read(ROOT/'outputs/correction_duplicate_audit_v1/candidate_dispositions.json')
    for path in (base/'dataset_scin_cases.csv',base/'dataset_scin_labels.csv',base/'dataset_scin_label_questions.csv'):
        assert bound[str(path)]==checkpoint['input_sha256'][str(path)]
    records=[]
    for item in local:
        cid=item['case_id'];case_rows=[r for r in cases if r['case_id']==cid];label_rows=[r for r in labels if r['case_id']==cid]
        assert len(case_rows)==len(label_rows)==1
        case,label=case_rows[0],label_rows[0];slot=str(item['image_slot']);official=item['official_image_path']
        assert case['image_'+slot+'_path']==official
        raw_india,raw_us=label['monk_skin_tone_label_india'],label['monk_skin_tone_label_us']
        assert int(raw_india)==item['india_label'] and int(raw_us)==item['us_label']
        sel=[r for r in selection if r['case_id']==cid]
        exact=[r for r in sel if r['image_path']==official and r['image_slot']==slot]
        assert len(exact)==1 and exact[0]['intended_use']=='training_candidate'
        chosen=exact[0];image_id=chosen['image_id']
        assert int(chosen['source_mst_label'])==int(raw_india)
        logs=[r for r in downloads if r['case_id']==cid and r['image_path']==official]
        assert logs
        part=[{k:r.get(k) for k in ('image_id','partition','duplicate_group_id','subject_id','subject_separation_status')} for r in partitions if r['image_id']==image_id]
        allocation=[r for r in correction if r['image_id']==image_id]
        dup=[r for r in dispositions if r['image_id']==image_id]
        candidate_pairs=[r for r in duplicates if image_id in (r['image_a'],r['image_b'])]
        historical=[r for r in checkpoint['records'] if r['case_id']==cid]
        assert len(historical)==1 and historical[0]['status']==item['label_status']
        records.append(dict(case_id=cid,image_id=image_id,image_slot=item['image_slot'],official_image_path=official,
            raw_india_label=raw_india,raw_us_label=raw_us,india_gradability_raw=label['gradable_for_monk_skin_tone_india'],
            us_gradability_raw=label['gradable_for_monk_skin_tone_us'],label_status=item['label_status'],
            label_gap=abs(int(raw_india)-int(raw_us)),reference_policy='unselected_preserve_both_no_average',
            head_neck_tag=case['body_parts_head_or_neck'],shot_type=case['image_'+slot+'_shot_type'],
            saved_selection=chosen,selected_images_for_same_case=len(sel),
            download_log_statuses=[r['download_status'] for r in logs],
            partition_evidence=part,correction_allocation_evidence=allocation,duplicate_dispositions=dup,
            duplicate_candidate_pair_evidence=candidate_pairs,person_group_status='case_id_only_no_verified_cross_case_person_identity',
            training_admitted=False,calibration_admitted=False,pixel_screen_selected=False))
    wording=[r for r in questions if r['Related column family'] in ('monk_skin_tone_label','gradable_for_monk_skin_tone')]
    summary=dict(cases=9,primary_case_joins=9,primary_label_joins=9,selection_exact_image_joins=9,download_log_joins=9,
        label_status=dict(Counter(r['label_status'] for r in records)),label_gap_counts=dict(Counter(r['label_gap'] for r in records)),
        raw_gradability_values=dict(Counter(r[k] for r in records for k in ('india_gradability_raw','us_gradability_raw'))),
        explicit_partition_matches=sum(bool(r['partition_evidence']) for r in records),
        explicit_correction_allocation_matches=sum(bool(r['correction_allocation_evidence']) for r in records),
        duplicate_disposition_matches=sum(bool(r['duplicate_dispositions']) for r in records),
        duplicate_candidate_pair_matches=sum(bool(r['duplicate_candidate_pair_evidence']) for r in records),
        published_cross_case_person_identifier_available=False,provisional_case_groups_not_verified_person_groups=True,
        label_dictionary_wording=wording,
        gradability_caution='Raw flags are True but dictionary question uses negative cannot-rate wording. Preserve flags and historical interpretation; do not silently reverse/reinterpret. Clarify semantics before admission.',
        historical_selection_bias='Original selection prefers India label, then US fallback, for broad-group training candidates; not a newly justified calibration-reference policy.',
        ready_calibration_rows=0,ready_subject_disjoint_cohort=False,reference_policy_selected=False,
        new_image_reads=0,new_image_hashes=0,new_fits=0,new_predictions=0,holdout_reads=0)
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',summary),('nine_case_reconciliation_PRIVATE.json',records),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='label_dictionary_wording'},indent=2))


if __name__=='__main__':main()
