"""Count matching labels/subjects and prospective scope; never measure or fit."""
from collections import Counter
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/faceocc_mst_feasibility_v1'
    if out.exists():raise FileExistsError(out)
    hashes={}
    def read(path):
        raw=(ROOT/path).read_bytes();hashes[path]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
    subjects=read('outputs/next_cycle_data_plan_v1/mst_subject_inventory.json')
    old=read('outputs/nostril_mst_measurement_v4/summary.json')
    first=read('outputs/faceocc_diagnostic_v1/summary.json')
    second=read('outputs/faceocc_light_comparison_v1/summary.json')
    readiness=read('outputs/faceocc_development_readiness_v1/summary.json')
    ledger=read('outputs/faceocc_development_readiness_v1/eligibility_ledger.json')
    labels={r['subject_id']:r['official_mst'] for r in subjects}
    rows=[]
    for cycle,data in [('first',first),('broader',second)]:
        for r in data['records']:
            if not r['image_id'].startswith('mst_e__'):continue
            subject=r['image_id'].split('__',1)[1].split('/')[0]
            rows.append(dict(image_id=r['image_id'],subject_id=subject,official_mst=labels[subject],
                evidence_cycle=cycle,technical_available=r['status']=='success',
                calibration_admitted=False,exposure='previously_exposed_development'))
    assert len(rows)==len({r['image_id'] for r in rows})==33
    successful=[r for r in rows if r['technical_available']]
    measured_subjects=sorted({r['subject_id'] for r in successful})
    support=Counter(labels[s] for s in measured_subjects)
    by_subject=[dict(subject_id=s,official_mst=labels[s],
        matching_attempts=sum(r['subject_id']==s for r in rows),
        matching_technical_measurements=sum(r['subject_id']==s for r in successful),
        same_category_other_measured_subjects=support[labels[s]]-1,
        admitted_calibration_rows=0) for s in measured_subjects]
    old_subjects={r['subject_id'] for r in old['records']}
    old_support=Counter(labels[s] for s in old_subjects)
    full_support=Counter(r['official_mst'] for r in subjects)
    table=[dict(official_mst=category,old_cycle_subjects=old_support[category],
        current_faceocc_subjects=support[category],full_inventory_subjects=full_support[category],
        full_inventory_has_separable_support=full_support[category]>=2) for category in range(1,11)]
    additional=[r for r in subjects if not r['in_completed_cycle']]
    upper_bound=old['attempts']+sum(r['unique_images'] for r in additional)
    assert len(successful)==23 and len(measured_subjects)==4 and upper_bound==755
    result=dict(decision='NO_GO_FOR_CALIBRATION_NOW',matching_mst_attempts=33,
        matching_technical_measurements=23,matching_failures=10,matching_subjects=4,
        matching_categories=sorted(support),current_matching_calibration_admitted=0,
        held_subject_rows_without_same_category_fit_support=len(successful),
        previous_parent_attempts=old['attempts'],previous_parent_successes=old['successes'],
        previous_parent_subjects=len(old_subjects),parent_features_compatible_with_faceocc=False,
        prospective_expanded_subjects=len(subjects),prospective_upper_bound_attempts=upper_bound,
        prospective_count_is_processing_authorization=False,
        prospective_categories_with_two_subjects=[k for k in range(1,11) if full_support[k]>=2],
        prospective_singleton_categories=[k for k in range(1,11) if full_support[k]==1],
        independent_final_validation_established=False,
        limited_exposed_development_question_possible_in_principle=True,
        current_blockers=['No evidence-backed actual-skin calibration admission manifest.',
            'Only4subjects/4singleton categories have current FaceOcc measurements.',
            '393older parent measurements cannot be mixed with FaceOcc-derived features.',
            'A prospective19subject study needs matching preparation/admission and a substantive predeclared rationale; no incremental same15fit.'],
        masks_or_features_generated=0,calibrator_fits=0,tree_fits=0,lookup_exported=False)
    assert readiness['reliable_matching_lookup_available'] is False
    assert not any(r['mst_calibration_admitted'] for r in ledger)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    out.mkdir()
    for name,value in [('decision.json',result),('matching_subjects.json',by_subject),
        ('matching_attempts.json',rows),('category_support.json',table),('input_sha256.json',hashes)]:
        (out/name).write_text(json.dumps(value,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
