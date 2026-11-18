"""Report the frozen acceptance screen and gate-only invariance; never refit."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model_training.signed_benefit_gate import signed_benefit_decision
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    E=ROOT/'outputs/mst_excluded_clean_gate_comparison_v1';O=ROOT/'outputs/mst_excluded_clean_gate_assessment_v1'
    target=O/'acceptance_PRIVATE.json'
    if target.exists():raise FileExistsError(target)
    m=read(ROOT/'outputs/mst_excluded_clean_gate_models_v1/models_PRIVATE.json');v=read(E/'results_PRIVATE.json')
    prior=read(ROOT/'outputs/clean_constrained_gate_models_v1/models_PRIVATE.json')
    checks=[]
    for new,old in zip([f['model'] for f in m['folds']]+[m['full_signed']], [f['model'] for f in prior['folds']]+[prior['full_signed']]):
        for k in ['mean','scale','weights','alpha','training_keys','fitting_rows','clean_indices','constraint_margin']:
            assert new[k]==old[k],k
        assert new['coefficient'][4]==0 and new['fixed_zero_coefficient_indices']==[4]
        checks.append(len(new['clean_indices']))
    assert sum(checks)==290
    folds={f['held_key']:f['model'] for f in m['folds']};invariance=0
    for r in v['records']:
        if r['features'] is None:continue
        gate=folds[r['subject_id']] if r['suite']=='fold_working256' else m['full_signed']
        a=list(r['features']);b=list(r['features']);a[4]=1.;b[4]=10.
        assert signed_benefit_decision(gate,a)==signed_benefit_decision(gate,b)==r['signed_decision']
        invariance+=1
    s=v['summary'];fold=s['fold_working256'];later=s['fallback_native224']
    assertions=dict(zero_development_clean_edits=fold['clean']['methods']['signed']['changed_cases']==0,
        zero_later_clean_edits=later['clean']['methods']['signed']['changed_cases']==0,
        lower_development_core_mae=fold['core']['methods']['signed']['reference_metrics_rgb8_mae_codes']<fold['core']['methods']['frozen']['reference_metrics_rgb8_mae_codes'],
        lower_later_fallback_core_mae=later['core']['methods']['signed']['reference_metrics_rgb8_mae_codes']<later['core']['methods']['frozen']['reference_metrics_rgb8_mae_codes'])
    focal=[r for r in v['records'] if r['case_id']=='eval_22__colour_warm']
    focal_result=[dict(suite=r['suite'],decision=r['signed_decision'],reference_available=r['reference_available'],
        input_scene=r['input_scene_metrics'],output_scene=r['paths']['signed']['scene_metrics']) for r in focal]
    result=dict(criteria=assertions,screen_passed=all(assertions.values()),production_adopted=False,
        new_gate_fits=11,other_photographic_fits=0,mst_gate_invariance_checks=invariance,
        zero_coefficient_models=11,fitting_clean_constraint_occurrences=sum(checks),
        focal_case=focal_result,summary=s,comparison_sha256=sha(E/'results_PRIVATE.json'),
        protocol_sha256=sha(ROOT/'docs/mst-excluded-gate-protocol-2026-11-07.md'))
    target.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(dict(criteria=assertions,screen_passed=result['screen_passed'],mst_invariance_checks=invariance),indent=2))
    for suite in s:
        print(suite)
        for layer in ['clean','core','composite_stress_design']:
            print(layer,{method:dict(mae=round(s[suite][layer]['methods'][method]['reference_metrics_rgb8_mae_codes'],5),
                changed=s[suite][layer]['methods'][method]['changed_cases'],harms=s[suite][layer]['methods'][method]['reference_harms'])
                for method in ['frozen','previous_constrained','signed']})


if __name__=='__main__':main()
