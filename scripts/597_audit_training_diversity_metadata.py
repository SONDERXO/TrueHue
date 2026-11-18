"""Existing publisher metadata/exposure plans only; never opens image files."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/training_diversity_metadata_audit_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed audit')
    bound={}
    def read(p):p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    subjects=read(ROOT/'outputs/stellenbosch_received_data_v1/subjects_PRIVATE.json')
    manifests={name:read(ROOT/'outputs'/name/'plan_PRIVATE.json') for name in (
        'stellenbosch_bounded_preparation_v1','stellenbosch_new_subjects_v1','frozen_split_subject_check_v1')}
    exposed=set();cohorts={}
    for name,plan in manifests.items():
        keys={r['subject_key'] for r in plan['selection']};exposed.update(keys);cohorts[name]=len(keys)
    # Count all exclusions recorded by the latest plan conservatively too.
    exposed.update(manifests['frozen_split_subject_check_v1']['excluded_exposed_keys_PRIVATE'])
    bands=('[1,3)','[3,5)','[5,7)','[7,9)','[9,10]')
    def band(r):
        v=Decimal(r['exact_decimal'])
        return bands[0] if v<3 else bands[1] if v<5 else bands[2] if v<7 else bands[3] if v<9 else bands[4]
    counts={b:dict(total=0,previously_selected_or_excluded=0,not_in_three_pixel_plans=0) for b in bands}
    for r in subjects:
        c=counts[band(r)];c['total']+=1;c['previously_selected_or_excluded' if r['subject_key'] in exposed else 'not_in_three_pixel_plans']+=1
    model=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    prep=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records'];byid={r['case_id']:r for r in prep}
    training=[byid[cid] for cid in model['full']['training_cases']]
    result=dict(total_publisher_groups=len(subjects),known_selected_or_excluded_keys=len(exposed),cohorts=cohorts,by_descriptive_interval=counts,
        current_full_model=dict(fitting_conditions=len(training),source_photos=len({r['source_case'] for r in training}),
            publisher_groups=len({r['subject_id'] for r in training}),clean_photos=sum(r['recipe']=='clean' for r in training)),
        audit_scope='Existing three Stellenbosch pixel-selection plans and latest exclusion list, not a universal exposure/identity certificate',
        interval_policy='Continuous-score descriptive intervals, not integer MST categories',
        new_image_reads=0,new_model_fits=0,new_source_selections=0,new_annotations=0)
    assert sum(c['total'] for c in counts.values())==285
    bound[str(Path(__file__))]=sha(Path(__file__));assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
