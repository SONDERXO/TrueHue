"""Reuse the frozen joint-policy evaluator with only revised gamma artifacts."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/551_compare_joint_neutral_support.py').read_text(encoding='utf-8')

def replace(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)

replace('outputs/joint_neutral_support_v1','outputs/gamma_scene_lightness_comparison_v1')
replace("    folds=read(S)['folds'];full=read(F);table=", "    M=ROOT/'outputs/gamma_scene_lightness_models_v1/models_PRIVATE.json'\n"
    "    PREV=ROOT/'outputs/joint_neutral_support_v1/results_PRIVATE.json'\n"
    "    revised=read(M);assert all(sha(p)==h for p,h in revised['input_sha256'].items())\n"
    "    previous=read(PREV);previous_rows={(r['suite'],r['case_id']):r for r in previous['records']}\n"
    "    folds=revised['folds'];full=read(F);full['split']=revised['full_model'];table=")
replace("for p in [S,F,T,C,Path(__file__),", "for p in [S,F,T,C,M,PREV,ROOT/'scripts/551_compare_joint_neutral_support.py',ROOT/'src/model_training/gamma_scene_lightness_restriction.py',Path(__file__),")
replace('docs/joint-neutral-support-protocol-2026-11-07.md','docs/gamma-scene-lightness-protocol-2026-11-07.md')
replace("('input','retained','policy_ungated','policy_gated')", "('input','retained','previous_policy_ungated','previous_policy_gated','policy_ungated','policy_gated')")
replace("if vector is not None:assert predict_split(payloads[key],vector)==c['paths']['old_ungated']['parameters']", "if vector is not None:assert predict_split(payloads[key],vector)[1:]==c['paths']['old_ungated']['parameters'][1:]")
replace("        r['paths']['retained']=c['paths']['old_gated']", "        r['paths']['retained']=c['paths']['old_gated']\n"
    "        for name in ['policy_ungated','policy_gated']:r['paths']['previous_'+name]=previous_rows[c['suite'],c['case_id']]['paths'][name]\n"
    "        for path in previous_rows[c['suite'],c['case_id']]['output_paths'].values():bind(path)")
replace("rgb(c['old_output_paths']['old_gated']),images['policy_ungated']", "rgb(previous_rows[c['suite'],c['case_id']]['output_paths']['policy_gated']),images['policy_ungated']")
replace('ref | input | retained | policy no gate | policy gated','ref | input | previous gated | new ungated | new gated')
replace('new_fits=0,new_mask_forwards=0', 'new_fits=0,upstream_new_gamma_fits=11,new_mask_forwards=0')
replace('retained | joint policy without gate | joint policy with retained gate','previous policy gated | revised policy without gate | revised policy with retained gate')
exec(compile(source,str(ROOT/'scripts/551_compare_joint_neutral_support.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
