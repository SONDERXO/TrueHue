"""Freeze known evidence/holds for the next method decision; no processing/fits."""
from collections import Counter
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/faceocc_development_readiness_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(path):
        raw=(ROOT/path).read_bytes();hashes[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    first=read('outputs/faceocc_diagnostic_v1/summary.json')
    later=read('outputs/faceocc_light_comparison_v1/summary.json')
    human=read('outputs/faceocc_four_review_import_v1/decisions.json')
    observations=read('outputs/faceocc_light_comparison_v1/assistant_observations.json')
    subjects=read('outputs/next_cycle_data_plan_v1/mst_subject_inventory.json')
    references=read('outputs/reference_readiness_r1_import/decisions.json')
    checkpoint=read('models/faceocc_candidate_v1/acquisition.json')
    review={r['image_id']:r for r in human};notes={r['image_id']:r for r in observations}
    known_holds={'fairface__train/7316.jpg':'assistant_possible_cheek_skin_loss',
        'fairface__train/39083.jpg':'historical_facial_hair_concern_not_revoked_by_similar_review',
        'fairface__train/74882.jpg':'earlier_source_measurement_rejection_preserved_despite_new_preference',
        'fairface__train/29321.jpg':'earlier_source_quality_rejection_preserved_despite_new_preference',
        'fairface__train/77101.jpg':'outer_coverage_gap_unresolved_by_removal_only_veto'}
    rows=[]
    for cycle,data in [('first_diagnostic',first),('broader_qualitative',later)]:
        for r in data['records']:
            identity=r['image_id'];available=r['status']=='success'
            extra=[]
            if identity in known_holds:extra.append(known_holds[identity])
            if cycle=='first_diagnostic' and r['case_index']==10:extra.append('known_beard_point_remains_selected')
            rows.append(dict(image_id=identity,evidence_cycle=cycle,technical_status=r['status'],
                technical_features_available=available,explicit_concerns=extra,
                human_review=review.get(identity),assistant_observation=notes.get(identity),
                intended_role='exposed_measurement_diagnostics_only',
                eligibility='technical_failure' if not available else ('hold_known_concern' if extra else 'actual_skin_eligibility_not_established'),
                correction_training_admitted=False,mst_calibration_admitted=False))
    assert len(rows)==len({r['image_id'] for r in rows})==49
    summary=dict(status='experimental_candidate_selected_training_not_ready',
        preferred_experimental_candidate='current_parser_anatomy_nostril_plus_fixed_FaceOcc_veto',
        active_runtime_changed=False,evidence_attempts=49,
        feature_available=sum(r['technical_features_available'] for r in rows),
        dispositions=dict(Counter(r['eligibility'] for r in rows)),
        human_cases=4,reference_review_records=len(references),
        full_official_subjects=len(subjects),
        singleton_categories=sorted(k for k,v in Counter(r['official_mst'] for r in subjects).items() if v==1),
        independent_validation_subjects_established=0,
        reliable_matching_lookup_available=False,calibration_fits=0,tree_fits=0,
        checkpoint_sha256=next(r['sha256'] for r in checkpoint['evidence'] if r['file']=='model.safetensors'),
        decision='One readiness/design cycle only; calibration activation requires separate evidence manifest, no same-subject tweak.')
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    out.mkdir()
    for name,value in [('eligibility_ledger.json',rows),('summary.json',summary),('input_sha256.json',hashes)]:
        (out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
