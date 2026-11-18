"""Freeze nine-case label/group/screen policy without reading any photograph."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/scin_exploratory_policy_v1'


def main():
    if OUT.exists():raise FileExistsError('Preserve previous or partial policy')
    bound={}
    def read(p):
        p=Path(p);raw=p.read_bytes();bound[str(p)]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    prior=ROOT/'outputs/scin_nine_provenance_review_v1'
    receipt=read(prior/'review_PRIVATE.json');assert receipt['passed']
    for p,h in receipt['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    records=read(prior/'nine_case_reconciliation_PRIVATE.json')
    clarification=read(prior/'official_schema_clarification_PRIVATE.json')
    assert clarification['status']=='gradability_semantics_resolved_from_official_schema'
    local=read(ROOT/'outputs/local_labelled_photographic_source_review_v1/scin_nine_case_readiness_PRIVATE.json')
    bycase={r['case_id']:r for r in local}
    roster=[]
    for r in records:
        assert r['saved_selection']['intended_use']=='training_candidate'
        aliases=bycase[r['case_id']]['existing_local_paths']
        canonical=f"data/raw/scin/selected_candidates/{r['image_id']}.png"
        assert canonical in aliases
        states=[]
        for name in aliases:
            path=ROOT/name
            assert path.is_file() and path.stat().st_size>0
            states.append(dict(relative_path=name,bytes=path.stat().st_size))
        roster.append(dict(case_id=r['case_id'],image_id=r['image_id'],image_slot=r['image_slot'],
            official_image_path=r['official_image_path'],canonical_relative_path=canonical,local_alias_membership=states,
            reference_labels=dict(india=int(r['raw_india_label']),us=int(r['raw_us_label'])),
            raw_reference_labels=dict(india=r['raw_india_label'],us=r['raw_us_label']),
            raw_gradability=dict(india=r['india_gradability_raw'],us=r['us_gradability_raw']),
            label_status=r['label_status'],case_group='scin_case_'+r['case_id'],
            verified_person_id=None,role='exploratory_development_readiness_only',
            inherited_image_hash=None,hash_provenance='No trusted original image hash established by checked manifests.',
            training_admitted=False,calibration_admitted=False,heldout_validation=False))
    assert len(roster)==len({r['case_id'] for r in roster})==9
    policy=dict(status='prepared_not_executed',version='scin_nine_exploratory_policy_v1',
        purpose='Determine local image identity, duplicate/support and raw measurement readiness; not train calibration.',
        reference_policy=dict(preserve_both=True,preferred_annotator=None,average_labels=False,agreement_filter=False,
            disputed_labels_are_ground_truth=False,case_labels_not_per_image_physical_truth=True,
            future_reporting='If separately approved for scoring, report both annotator error series on all attempted cases; no best-of-two or fabricated consensus.',
            new_adjudication_requested=False),
        grouping=dict(unit='published_case_id',all_slots_and_aliases_stay_together=True,
            cross_case_person_independence_verified=False,
            exact_duplicate_rule='Merge exact-file or exact-decoded-image links conservatively; never count aliases as cases.',
            approximate_similarity_rule='Flag uncertain links for review; do not declare person identity or independence from a perceptual hash.',
            locked_overlap_rule='Use saved locked-allocation metadata/hashes only. Quarantine any established conflict; never read locked images.',
            future_person_held_claim_permitted=False),
        allocation=dict(all_nine='exploratory_development_readiness_only',new_calibration_fit=False,
            new_validation_split=False,no_partition_clearance_inferred_from_missing_record=True,
            all_failure_records_retained=True,no_success_only_subset=True),
        screen=dict(status='prepared_not_executed',roster='roster_PRIVATE.json',attempts=9,
            phase1='Check exact roster membership/byte sizes; hash all named aliases. Establish a new local baseline, not a publisher-authenticated checksum.',
            alias_conflict='If aliases differ, retain all hashes and block that case pending identity resolution; do not pick the nicer image.',
            phase2='Decode canonical images only after identity checks; cache exact RGB frames. Record exact duplicate groups and any overlap supported by existing saved hashes.',
            phase3='One unchanged native YuNet .85/NMS.3/topK5000 anchor per identity-clear canonical image; exactly one face required, no manual person switch.',
            pipeline='Existing native square1.5 bridge, original parser/landmark attempts and raw FaceOcc visibility, unchanged1000guard. Preserve every failure.',
            maximum_detector_calls=18,maximum_parser_calls=9,maximum_FaceOcc_calls=9,
            landmark_helper_calls='Record all existing parent attempts; no extra rescue.',
            allowed_outputs=['Source/alias hashes and provenance','Case/duplicate/support ledger','Cached RGB and masks','Raw Lab/ITA and seven existing full-frame scene summaries','All nine diagnostic boards, with label values hidden'],
            label_inputs_to_pipeline=False,MST_predictions=False,calibration_fits=False,correction_tree_fits=False,
            no_new_downloads=True,no_locked_image_reads=True,no_new_annotation_queue=True,
            stop='After independent cached-statistic/hash/projection replay and all-case support review; no automatic fit, label or mask admission.'),
        decision_rules=['Alias or allocation conflict: preserve and block; no replacement.',
            'Usable face/support or broad brightness is readiness only, not independent intrinsic-tone truth.',
            'Case-level independence limits and conflicting labels remain even if every technical screen passes.',
            'Only a separate justified calibration design could propose modelling; no weakened original-preservation gates.'],
        new_image_reads=0,new_image_hashes=0,new_fits=0,new_predictions=0,
        calibration_admitted=False,runtime_adopted=False)
    OUT.mkdir()
    for name,value in [('policy_PRIVATE.json',policy),('roster_PRIVATE.json',roster),('input_sha256_PRIVATE.json',bound)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(dict(cases=9,label_status=dict(Counter(r['label_status'] for r in roster)),
        local_alias_files=sum(len(r['local_alias_membership']) for r in roster),screen_status=policy['screen']['status'],image_reads=0,fits=0)))


if __name__=='__main__':main()
