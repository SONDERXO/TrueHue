"""Prepare provisional source splits and failure audit; no pairs/model generated."""
import csv
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
from src.data_preparation.source_partition import connected_groups,allocate_group,classify_pair


def main():
    common=importlib.import_module('16_compare_face_outline')
    pilot=importlib.import_module('21_synthetic_pair_pilot')
    checks=importlib.import_module('15_prepare_fairface_mask_review')
    manifests=ROOT/'data/manifests'
    output=manifests/'source_preparation_v1'
    if output.exists():
        raise FileExistsError('Refusing overwrite of partition decisions')
    source_path=manifests/'v2_complete_mouth_v1/fairface_candidate_processed_manifest.csv'
    selection_path=manifests/'fairface_candidate_selection.csv'
    rows=common.read(source_path)
    selection={r['image_id']:r for r in common.read(selection_path)}
    if len(rows)!=len({r['image_id'] for r in rows}) or {r['image_id'] for r in rows}!=set(selection):
        raise ValueError('Source IDs do not match candidate selection exactly')
    source_splits={k:r['source_split'] for k,r in selection.items()}
    reviews={r['image_id']:r for r in common.read(manifests/'fairface_candidate_mask_quality_review.csv')}
    reviews.update({r['image_id']:r for r in common.read(manifests/'fairface_random50_review_seed42.csv')})
    audits={r['image_id']:r for r in common.read(ROOT/'outputs/accepted_exclusion_audit/audit.csv')}
    evidence=[ROOT/'outputs'/p/'comparison.csv' for p in ('complete_mouth_experiment_v1','complete_mouth_fresh30_seed42')]
    exposed=set()
    for path in evidence:
        exposed.update(r['image_id'] for r in common.read(path))
    smoke=manifests/'fairface_smoke_test_selection.csv'
    exposed.update(r['image_id'] for r in common.read(smoke))
    pilot_pairs=ROOT/'outputs/synthetic_pair_pilot_v1/pairs.csv'
    exposed.update(r['source_image_id'] for r in common.read(pilot_pairs))
    fingerprints={str(p):checks.digest(p) for p in [source_path,selection_path,smoke,pilot_pairs]+evidence}
    # Exact decoded-pixel equality plus conservative dHash candidate links.
    hashes={}
    for r in rows:
        image=cv2.imread(r['image_path'])
        if image is None:
            raise ValueError('Unreadable source while deduplicating: '+r['image_id'])
        gray=cv2.cvtColor(cv2.resize(image,(9,8)),cv2.COLOR_BGR2GRAY)
        dhash=sum(int(bit)<<i for i,bit in enumerate((gray[:,1:]>gray[:,:-1]).ravel()))
        exact=hashlib.sha256(str(image.shape).encode()+image.tobytes()).hexdigest()
        hashes[r['image_id']]=(exact,dhash)
    ids=sorted(hashes)
    links=[]; pair_records=[]
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            exact=hashes[a][0]==hashes[b][0]
            distance=(hashes[a][1]^hashes[b][1]).bit_count()
            if exact or distance<=4:
                links.append((a,b))
                pair_records.append(dict(image_a=a,image_b=b,decoded_exact_duplicate=exact,dhash_distance=distance,
                    match_status='exact' if exact else 'unconfirmed_near_duplicate_candidate'))
    partitions={}; group_ids={}; group_sizes={}
    for group in connected_groups(ids,links):
        split=allocate_group(group,source_splits,exposed,42)
        key=hashlib.sha256('|'.join(group).encode()).hexdigest()[:16]
        for image_id in group:
            partitions[image_id]=split;group_ids[image_id]=key;group_sizes[image_id]=len(group)
    for r in rows:
        image_id=r['image_id']
        review=reviews.get(image_id,{})
        decision=review.get('visual_review','pending').strip().lower()
        decision={'deny':'reject'}.get(decision,decision)
        audit=audits.get(image_id,{}).get('exclusion_audit','not_audited')
        if r['processing_status']!='success':
            suitability='excluded_automated_failure'
        elif decision=='reject' or audit=='misplaced_geometry':
            suitability='excluded_review_or_known_geometry'
        elif audit=='uncertain':
            suitability='hold_uncertain_geometry'
        elif decision=='accept':
            suitability='provisional_reviewed_candidate'
        else:
            suitability='hold_unreviewed_source'
        r.update(source_split=source_splits[image_id],partition=partitions[image_id],
            duplicate_group_id=group_ids[image_id],duplicate_group_size=group_sizes[image_id],
            decoded_pixel_sha256=hashes[image_id][0],dhash64=f'{hashes[image_id][1]:016x}',
            known_pipeline_development_exposure=image_id in exposed,subject_id='',
            subject_separation_status='identity_ids_unavailable_not_verified',
            original_visual_decision=decision,exclusion_audit=audit,source_suitability=suitability,
            training_ready=False,readiness_reason='reference suitability and current-version review remain required; grouping/severity unresolved')
    pair_policy=[]
    features={r['image_id']:r for r in common.read(ROOT/'outputs/synthetic_pair_pilot_v1/distorted_input_features.csv')}
    for pair in common.read(pilot_pairs):
        feature=features[pair['pilot_id']]
        pair_policy.append(dict(pilot_id=pair['pilot_id'],source_image_id=pair['source_image_id'],
            processing_status=feature['processing_status'],exclusion_reason=feature['exclusion_reason'],
            clipped_pixel_count=pair['clipped_pixel_count'],
            failure_policy=classify_pair(feature['processing_status'],int(pair['clipped_pixel_count'])),
            intended_use='pilot_only_not_training'))
    output.mkdir()
    pilot.write_csv(output/'source_audit_and_partitions.csv',rows)
    pilot.write_csv(output/'pilot_pair_failure_audit.csv',pair_policy)
    if pair_records:
        pilot.write_csv(output/'duplicate_candidate_pairs.csv',pair_records)
    else:
        (output/'duplicate_candidate_pairs.csv').write_text('image_a,image_b,decoded_exact_duplicate,dhash_distance,match_status\n',encoding='utf-8')
    from collections import Counter
    summary=dict(source_count=len(rows),seed=42,train_group_validation_fraction=.2,
        partitions=dict(Counter(r['partition'] for r in rows)),
        suitability=dict(Counter(r['source_suitability'] for r in rows)),
        duplicate_candidate_pairs=len(pair_records),exact_duplicate_pairs=sum(r['decoded_exact_duplicate'] for r in pair_records),
        pipeline_exposed_source_count=len(exposed&set(ids)),
        pilot_failure_policy=dict(Counter(r['failure_policy'] for r in pair_policy)),
        input_sha256=fingerprints,
        note='Provisional allocations only; reserved_test not a subject-independent or guaranteed untouched benchmark; no final training eligibility.')
    assert all(checks.digest(Path(p))==h for p,h in fingerprints.items())
    (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))


if __name__=='__main__':
    main()
