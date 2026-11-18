"""Independent frozen-roster/policy checks, without opening images."""
from pathlib import Path
from collections import Counter
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/scin_exploratory_policy_v1'
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest=OUT/'verification_PRIVATE.json'
    if dest.exists():raise FileExistsError('Preserve verification')
    bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    roster=read(OUT/'roster_PRIVATE.json');policy=read(OUT/'policy_PRIVATE.json')
    original=read(ROOT/'outputs/scin_nine_provenance_review_v1/nine_case_reconciliation_PRIVATE.json')
    bycase={r['case_id']:r for r in original}
    assert len(roster)==len({r['case_id'] for r in roster})==len(bycase)==9
    assert {r['case_id'] for r in roster}==set(bycase)
    assert Counter(r['label_status'] for r in roster)=={'agree':3,'disagree':6}
    for r in roster:
        old=bycase[r['case_id']]
        assert r['image_id']==old['image_id'] and r['official_image_path']==old['official_image_path'] and r['image_slot']==old['image_slot']
        assert r['raw_reference_labels']=={'india':old['raw_india_label'],'us':old['raw_us_label']}
        assert r['reference_labels']=={k:int(v) for k,v in r['raw_reference_labels'].items()}
        assert r['verified_person_id'] is None and r['inherited_image_hash'] is None
        assert not any(r[k] for k in ('training_admitted','calibration_admitted','heldout_validation'))
        assert r['canonical_relative_path'] in {p['relative_path'] for p in r['local_alias_membership']}
    labels=policy['reference_policy'];assert labels['preserve_both'] and labels['preferred_annotator'] is None
    assert not any(labels[k] for k in ('average_labels','agreement_filter','disputed_labels_are_ground_truth','new_adjudication_requested'))
    assert not policy['grouping']['cross_case_person_independence_verified'] and not policy['grouping']['future_person_held_claim_permitted']
    screen=policy['screen'];assert screen['status']=='prepared_not_executed' and screen['attempts']==9
    assert not any(screen[k] for k in ('label_inputs_to_pipeline','MST_predictions','calibration_fits','correction_tree_fits'))
    assert screen['maximum_detector_calls']==18 and screen['maximum_parser_calls']==screen['maximum_FaceOcc_calls']==9
    assert policy['new_image_reads']==policy['new_image_hashes']==policy['new_fits']==policy['new_predictions']==0
    result=dict(passed=True,exact_cases=9,disputed_cases_retained=6,agreement_cases_retained=3,
        original_label_pairs_unchanged=9,case_groups_not_claimed_person_groups=True,
        aliases_not_counted_as_extra_cases=True,screen_executed=False,new_image_reads=0,new_image_hashes=0,new_fits=0,
        input_sha256={str(p):sha(p) for p in OUT.iterdir() if p.is_file()},verifier_sha256=sha(Path(__file__)))
    dest.write_text(json.dumps(result,indent=2)+'\n');print('PASS:exact9/all6disputes/bothlabels;no person-independence or fitting claim;screen not executed.')


if __name__=='__main__':main()
