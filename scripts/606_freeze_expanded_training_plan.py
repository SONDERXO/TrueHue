"""Freeze exact new-source roles, recipes and unchanged calibration choices; no fits."""
from pathlib import Path
from collections import Counter
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.photographic_target_diagnostic import case_matrix
OUT=ROOT/'outputs/expanded_correction_training_plan_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve frozen plan')
    bound={}
    def read(p):p=Path(p);bound[str(p)]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    old=read(ROOT/'outputs/aligned_action_tree_models_v1/models_PRIVATE.json')
    prep=read(ROOT/'outputs/group_diversity_final_masks_v1/results_PRIVATE.json')
    verification=read(ROOT/'outputs/group_diversity_final_masks_v1/verification_PRIVATE.json');assert verification['passed']
    roleplan=read(ROOT/'outputs/group_diversity_candidates_v1/plan_PRIVATE.json')
    admitted=[r for r in prep['records'] if r['status']=='available'] # technical availability only; scientific flags stay false.
    rejected=[r for r in prep['records'] if r['status']!='available']
    assert len(admitted)==80 and len(rejected)==16
    oldkeys={r['subject_id'] for r in old['predictions'] if r['cohort']=='development'}
    newkeys={r['subject_key'] for r in admitted};holdkeys={r['subject_key'] for r in roleplan['groups'] if r['role']=='closed_holdout_candidate'}
    assert len(oldkeys)==10 and len(newkeys)==32 and len(holdkeys)==8
    assert not oldkeys&newkeys and not (oldkeys|newkeys)&holdkeys
    calibrationkeys=set(old['calibrations'])
    for mapping in old['calibrations'].values():assert not set(mapping['training_keys'])&(newkeys|holdkeys)
    recipes=case_matrix();assert len(recipes)==14 and sum(r['layer']=='core' for r in recipes)==8
    pending=[]
    for r in admitted:
        assert r['role']=='development_candidate' and not r['training_admitted'] and not r['calibration_admitted']
        for recipe in recipes:
            if recipe['id']=='clean':continue
            pending.append(dict(case_id=r['case_id']+'__'+recipe['id'],source_case=r['case_id'],subject_key=r['subject_key'],
                source_path=r['source_path'],source_sha256=r['source_sha256'],source_score=r['source_score'],
                recipe=recipe,role='new_fitting_candidate',status='not_generated'))
    assert len(pending)==1040 and len({r['case_id'] for r in pending})==1040
    fits=[]
    for parent in old['folds']+[old['full']]:
        key=parent['held_key'];excluded=[] if key=='full' else [key];lookup='|'.join(excluded);assert lookup in calibrationkeys
        fits.append(dict(held_key=key,parent_training_cases=parent['training_cases'],
            new_row_MST_calibration_excluded_keys=excluded,new_row_own_key_absent_from_all_calibrations=True,
            frozen_actions=parent['model']['actions'],parent_clean_count=sum(parent['model']['clean'])))
    for p in (Path(__file__),ROOT/'docs/expanded-correction-training-protocol-2026-11-08.md',ROOT/'src/model_training/photographic_target_diagnostic.py'):
        bound[str(p)]=sha(p)
    result=dict(status='frozen_plan_only_no_inputs_or_fits',new_reference_sources=[dict(case_id=r['case_id'],subject_key=r['subject_key'],source_path=r['source_path'],source_sha256=r['source_sha256']) for r in admitted],
        new_clean_exclusions=[dict(case_id=r['case_id'],reason=r.get('reason'),disposition='no_derivatives_generated_no_regional_reference') for r in rejected],
        pending_distortions=pending,planned_fits=fits,recipes=recipes,
        counts=dict(old_clean_references=22,new_clean_references=80,total_clean_references=102,old_groups=10,new_groups=32,total_fitting_groups=42,
            closed_holdout_groups=8,closed_holdout_photos=24,new_nonlinear_input_attempts=1040,planned_tree_fits=11,new_MST_fits=0,fixed_old_evaluation_attempts=756),
        closed_holdout_keys=sorted(holdkeys),new_model_fits=0,new_image_reads=0,scientific_admissions=0,
        source_condition_counts=dict(Counter(r['condition'] for r in admitted)),
        feature_contract_gate='Must verify unchanged raw measurement semantics before frozen calibration reuse')
    assert all(sha(p)==h for p,h in bound.items());OUT.mkdir()
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    print(json.dumps(result['counts'],indent=2));print('Plan only: no image reads, generation or fits.')

if __name__=='__main__':main()
