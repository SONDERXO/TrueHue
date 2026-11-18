"""Saved source/label/allocation readiness; no photograph bytes or fits."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/local_labelled_photographic_source_review_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve prior or partial review')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    scin=read(ROOT/'outputs/independent_source_inventory_v1/scin_inventory.json')
    retention=read(ROOT/'outputs/mst_retention_checkpoint_v1/summary.json')
    mst=read(ROOT/'outputs/additional_mst_eligibility_v1/summary.json')
    inventory=read(ROOT/'outputs/independent_source_inventory_v1/summary.json')
    current=read(ROOT/'outputs/combined_reviewed_mst_design_v1/rows_PRIVATE.json')
    subjects=read(ROOT/'outputs/stellenbosch_received_data_v1/subjects_PRIVATE.json')
    groups=read(ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')['groups']
    final={r['subject_key'] for r in groups if r['role']=='closed_holdout_candidate'}
    local=[]
    for r in scin:
        if not r['existing_local_paths']:continue
        assert r['role']=='historical_training_candidate' and not r['training_admitted']
        # Only already-declared training candidates: existence/size, never hash/decode.
        paths=[]
        for relative in r['existing_local_paths']:
            path=ROOT/relative
            paths.append(dict(path=relative,exists=path.is_file(),bytes=path.stat().st_size if path.is_file() else None))
        local.append(dict(r,current_file_membership=paths))
    assert len(local)==9 and len({r['case_id'] for r in local})==9
    good=[r for r in mst['records'] if r['status']=='success']
    mst_range=[min(r['features']['input_mean_l_star'] for r in good),max(r['features']['input_mean_l_star'] for r in good)]
    stats=dict(scin_inventory_images=len(scin),scin_recorded_local_cases=len(local),
        scin_local_label_status=dict(Counter(r['label_status'] for r in local)),
        scin_local_cases_with_at_least_one_existing_path=sum(any(p['exists'] for p in r['current_file_membership']) for r in local),
        scin_agree_case_labels=[r['india_label'] for r in local if r['label_status']=='agree'],
        scin_pool_label_status=retention['pool_case_label_status_counts'],
        historical_MSTE_attempts=len(mst['records']),historical_MSTE_successes=len(good),historical_MSTE_l_star_range=mst_range,
        MSTE_not_assessed=mst['not_assessed'],current_reviewed_rows=len(current),current_subjects=len({r['subject_id'] for r in current}),
        Stellenbosch_inventory_subjects=len(subjects),final_locked_groups=len(final),
        FairFace_additional_screen_clear=inventory['additional_screen_clear_sources'],
        currently_ready_additional_photographic_MST_rows=0)
    ledger=[dict(source='SCIN existing nine training-candidate cases',label='Both India and US MST annotations preserved; six disagree, three agree.',
        readiness='Best concrete local natural-photograph lead, not admitted. No agree-only subset.',
        gaps=['Primary annotation/gradability provenance and label policy','Person/duplicate and allocation reconciliation','Face/support adequacy','Current-method brightness and colour coverage'],
        action='Metadata-only nine-case provenance/allocation/duplicate readiness before any pixel screen; preserve all nine outcomes.'),
        dict(source='MST-E old25 screen',label='Four official subject labels:2/4/5/9.',readiness='Closed, not admitted; technical passes do not reopen eligibility.',
        gaps=['Historical support contamination','Protected evaluation/subject-role reconciliation','Current manual/native method mismatch'],
        action='Do not repurpose evaluation subjects, retry25, or expand312 under this review.'),
        dict(source='Stellenbosch release',label='Publisher decimal score per subject.',readiness='Current60/10people already reviewed; additional subjects/conditions not a new photographic domain by themselves.',
        gaps=['Rendered224px domain','No verified neutral reference in current evidence','Current cross-lighting error/photographic transfer'],
        action='No automatic new-subject/condition expansion; final eight groups remain locked.'),
        dict(source='FairFace / FFHQ',label='No independent MST reference established by these inventories.',
        readiness='Old mapped MST/race/appearance approvals are not ground-truth labels.',gaps=['Independent MST reference'],action='Do not relabel old predictions or use race as MST.'),
        dict(source='PPR10K / local FiveK edits',label='Editor appearance targets, not MST labels.',
        readiness='Correction targets cannot substitute for intrinsic-tone references.',gaps=['Independent MST labels and compatible input/reference evidence'],
        action='Retain existing correction artifacts; no inferred MST labels or evaluation-role reuse.')]
    OUT.mkdir()
    for name,value in [('summary_PRIVATE.json',dict(statistics=stats,source_ledger=ledger,image_reads=0,model_calls=0,fits=0,
        training_admitted=False,calibration_admitted=False,holdout_reads=0)),('scin_nine_case_readiness_PRIVATE.json',local),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
