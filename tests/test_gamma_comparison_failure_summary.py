import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/531_compare_gamma_scene_chroma_restriction_v3.py'
spec=importlib.util.spec_from_file_location('gamma_comparison_summary',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_missing_outputs_stay_in_attempts_without_scores():
    failure=dict(reference_available=False,features=None,paths={},input_scene_metrics=None)
    scored=dict(reference_available=True,features=[1],subject_id='fictional',paths={n:dict(changed_channels=1,reference_metrics=dict(rgb8_mae_codes=1.,relative_deltaE00_mean=2.),scene_metrics=None) for n in ['old_ungated','old_gated','new_ungated','new_gated']},input_reference_metrics=dict(rgb8_mae_codes=0.),input_scene_metrics=None)
    result=module.summarize([failure,scored]);assert result['attempts']==2 and result['reference_scored']==1
    for p in result['paths'].values():assert p['reference_metrics_rgb8_mae_codes']==1 and p['scene_metrics_rgb8_mae_codes'] is None and p['changed_cases']==1
    empty=module.summarize([failure]);assert empty['reference_scored']==0 and all(p['reference_metrics_rgb8_mae_codes'] is None for p in empty['paths'].values())
