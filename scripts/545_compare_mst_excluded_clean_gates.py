"""Fixed saved-output comparison with both prior signed and constrained gates."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/535_compare_signed_benefit_gates.py').read_text()
def replace(old,new):
    global source
    assert old in source,old
    source=source.replace(old,new)
replace('outputs/signed_benefit_gate_comparison_v1','outputs/mst_excluded_clean_gate_comparison_v1')
replace('outputs/signed_benefit_gate_models_v1','outputs/mst_excluded_clean_gate_models_v1')
replace('docs/signed-benefit-gate-protocol-2026-11-07.md','docs/mst-excluded-gate-protocol-2026-11-07.md')
replace("for name in ['frozen','matched_binary','signed']:","for name in ['frozen','matched_binary','previous_signed','previous_constrained','signed']:")
replace("    paths=[MP,C,S,Path(__file__)",
    "    previous_signed_path=ROOT/'outputs/signed_benefit_gate_comparison_v1/results_PRIVATE.json'\n"
    "    previous_constrained_path=ROOT/'outputs/clean_constrained_gate_comparison_v1/results_PRIVATE.json'\n"
    "    previous_signed={(r['suite'],r['case_id']):r for r in read(previous_signed_path)['records']}\n"
    "    previous_constrained={(r['suite'],r['case_id']):r for r in read(previous_constrained_path)['records']}\n"
    "    paths=[previous_signed_path,previous_constrained_path,ROOT/'scripts/535_compare_signed_benefit_gates.py',MP,C,S,Path(__file__)")
replace("        r['paths']['frozen']=dict(c['paths']['old_gated'])",
    "        r['paths']['frozen']=dict(c['paths']['old_gated'])\n"
    "        r['paths']['previous_signed']=dict(previous_signed[suite,cid]['paths']['signed'])\n"
    "        r['paths']['previous_constrained']=dict(previous_constrained[suite,cid]['paths']['signed'])")
replace("newimages['matched_binary'],newimages['signed']",
    "rgb(ROOT/'outputs/clean_constrained_gate_comparison_v1'/suite/cid/'signed.png'),newimages['signed']")
replace('ref|input|frozen|binary|signed','ref|input|frozen|prior constraint|MST excluded')
replace('Private signed-benefit gate comparison','Private MST-excluded clean gate comparison')
replace('Reference | input | frozen gate | matched binary | signed benefit.','Reference | input | frozen gate | previous clean-constrained | MST excluded.')
exec(compile(source,str(ROOT/'scripts/535_compare_signed_benefit_gates.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
