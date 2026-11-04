"""Metadata-only MST support audit, preserving both SCIN annotator columns."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/mst_retention_checkpoint_v1'
    if out.exists():raise FileExistsError(out)
    metadata=ROOT/'data/raw/scin/metadata'
    paths=[metadata/'dataset_scin_cases.csv',metadata/'dataset_scin_labels.csv',
           metadata/'dataset_scin_label_questions.csv',ROOT/'data/manifests/scin_candidate_selection.csv',
           ROOT/'docs/mst-retention-data-audit-protocol.md',Path(__file__),
           ROOT/'src/ita_estimation/mst_lookup.py',
           Path('C:/Users/NYTHAN/Downloads/Thesis Proposal Document.pdf')]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    def read(p):
        with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
    cases=read(paths[0]);labels=read(paths[1]);by_case={r['case_id']:r for r in labels}
    assert len(by_case)==len(labels) and len({r['case_id'] for r in cases})==len(cases)
    def label(row,side):
        raw=row.get('monk_skin_tone_label_'+side,'')
        valid=row.get('gradable_for_monk_skin_tone_'+side,'').strip().lower()=='true'
        return int(raw) if valid and raw in {str(i) for i in range(1,11)} else None
    records=[];pool=[]
    for case in cases:
        row=by_case.get(case['case_id'],{});india=label(row,'india');us=label(row,'us')
        status=('agree' if india==us else 'disagree') if india is not None and us is not None else ('one_sided' if india is not None or us is not None else 'unavailable')
        slots=[i for i in (1,2,3) if case.get(f'image_{i}_path') and case.get(f'image_{i}_shot_type')=='AT_DISTANCE'] if case['body_parts_head_or_neck']=='YES' else []
        record=dict(case_id=case['case_id'],india_label=india,us_label=us,
            raw_india_label=row.get('monk_skin_tone_label_india',''),raw_us_label=row.get('monk_skin_tone_label_us',''),
            india_gradable=row.get('gradable_for_monk_skin_tone_india',''),us_gradable=row.get('gradable_for_monk_skin_tone_us',''),
            status=status,head_neck_at_distance_slots=slots,training_eligible=False)
        records.append(record)
        for slot in slots:
            image_path=case[f'image_{slot}_path']
            options=[ROOT/'data/raw/scin/selected_candidates'/f"scin__{case['case_id']}__{slot}.png",
                     ROOT/'data/raw/scin/selected_candidates'/Path(image_path).name]
            pool.append(dict(case_id=case['case_id'],image_slot=slot,official_image_path=image_path,
                label_status=status,india_label=india,us_label=us,
                existing_local_paths=[p.relative_to(ROOT).as_posix() for p in options if p.is_file()],
                face_suitability='not_assessed_by_this_metadata_audit',training_eligible=False))
    status_counts=dict(Counter(r['status'] for r in records))
    selected_cases={r['case_id'] for r in pool}
    pool_cases=[r for r in records if r['case_id'] in selected_cases]
    summary=dict(status='metadata_audit_no_fit_or_admission',case_count=len(cases),label_row_count=len(labels),
        case_ids_missing_label_row=sum(r['case_id'] not in by_case for r in cases),
        annotator_status_counts=status_counts,
        head_neck_at_distance_cases=len(pool_cases),head_neck_at_distance_images=len(pool),
        pool_case_label_status_counts=dict(Counter(r['status'] for r in pool_cases)),
        pool_cases_with_agreement_by_mst=dict(Counter(r['india_label'] for r in pool_cases if r['status']=='agree')),
        locally_available_pool_images=sum(bool(r['existing_local_paths']) for r in pool),
        records=records,metadata_candidate_images=pool,input_sha256=before,
        new_image_exposures=0,new_model_fits=0,new_training_admissions=0,
        mapping_exported=False,final_model_ready=False,
        note='Both recorded annotations retained. Metadata agreement does not establish image-level usable facial skin, independent subjects or neutral-color truth. Proposal MST-E calibration/evaluation roles still need explicit separation.')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
    out.mkdir();(out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k not in ['records','metadata_candidate_images','input_sha256']},indent=2))


if __name__=='__main__':main()
