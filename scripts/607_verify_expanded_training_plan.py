"""Metadata/partition/calibration-role verification; no images, predictions or fits."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/expanded_correction_training_plan_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    d=read(OUT/'plan_PRIVATE.json');bound=read(OUT/'input_sha256_PRIVATE.json');assert all(sha(p)==h for p,h in bound.items())
    old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json');new=read(ROOT/'outputs/group_diversity_final_masks_v1/results_PRIVATE.json')
    records={r['case_id']:r for r in new['records']};oldkeys={r['subject_id'] for r in old['predictions'] if r['cohort']=='development'}
    newkeys={r['subject_key'] for r in d['new_reference_sources']};hold=set(d['closed_holdout_keys'])
    assert not oldkeys&newkeys and not (oldkeys|newkeys)&hold
    assert {r['case_id'] for r in d['new_reference_sources']}=={r['case_id'] for r in new['records'] if r['status']=='available'}
    assert {r['case_id'] for r in d['new_clean_exclusions']}=={r['case_id'] for r in new['records'] if r['status']!='available'}
    assert Counter(r['source_case'] for r in d['pending_distortions'])=={r['case_id']:13 for r in d['new_reference_sources']}
    assert Counter(r['recipe']['layer'] for r in d['pending_distortions'])=={'core':640,'composite_stress_design':400}
    assert all(r['status']=='not_generated' and r['subject_key'] not in hold for r in d['pending_distortions'])
    checks=0
    for fit,parent in zip(d['planned_fits'],old['folds']+[old['full']],strict=True):
        assert fit['held_key']==parent['held_key'] and fit['parent_training_cases']==parent['training_cases'] and fit['frozen_actions']==parent['model']['actions']
        mapping=old['calibrations']['|'.join(fit['new_row_MST_calibration_excluded_keys'])]
        assert not set(mapping['training_keys'])&(newkeys|hold)
        if fit['held_key']!='full':assert fit['held_key'] not in mapping['training_keys']
        for r in d['new_reference_sources']:
            assert r['subject_key']!=fit['held_key'] and r['subject_key'] not in mapping['training_keys'];checks+=1
    nb=read(ROOT/'outputs/group_diversity_final_masks_v1/final_input_sha256_PRIVATE.json');ob=old['input_sha256']
    common={p:h for p,h in nb.items() if p in ob and ('src' in Path(p).parts or 'models' in Path(p).parts)}
    assert len(common)==32 and all(ob[p]==h and sha(p)==h for p,h in common.items())
    oldprep=read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')
    available=[r for r in new['records'] if r['status']=='available']
    old_available=next(r for r in oldprep['records'] if r['status']=='available')
    for r in available:
        assert r['input_bridge']['version']==old_available['input_bridge']['version'] and r['input_bridge']['context_scale']==1.5
        assert r['measurement_report']['version']==old_available['measurement_report']['version']
        assert r['raw_features']=={k:r['measurement_report']['features'][k] for k in r['raw_features']}
    result=dict(passed=True,new_source_calibration_role_checks=checks,unchanged_runtime_model_bindings=len(common),
        clean_preparation_semantics_checked=80,planned_inputs=1040,planned_fits=11,new_MST_fits=0,
        planned_core_inputs=640,planned_stress_inputs=400,closed_holdout_groups=8,closed_holdout_image_reads=0,
        new_predictions=0,new_fits=0,new_source_image_reads=0,
        compatibility_limit='Checked existing clean-preparation semantics; future distorted-input preparation must reproduce and verify the same implementation.',
        plan_sha256=sha(OUT/'plan_PRIVATE.json'),verifier_sha256=sha(Path(__file__)))
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
