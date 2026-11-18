"""Reuse exact gate comparison contexts; add the prior unconstrained comparator."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/535_compare_signed_benefit_gates.py').read_text()
source=source.replace('outputs/signed_benefit_gate_comparison_v1','outputs/clean_constrained_gate_comparison_v1').replace('outputs/signed_benefit_gate_models_v1','outputs/clean_constrained_gate_models_v1').replace('docs/signed-benefit-gate-protocol-2026-11-07.md','docs/clean-constrained-gate-protocol-2026-11-07.md')
source=source.replace("for name in ['frozen','matched_binary','signed']:","for name in ['frozen','matched_binary','previous_signed','signed']:")
source=source.replace("    paths=[MP,C,S,Path(__file__)","    previous_path=ROOT/'outputs/signed_benefit_gate_comparison_v1/results_PRIVATE.json'\n    previous={(r['suite'],r['case_id']):r for r in read(previous_path)['records']}\n    paths=[previous_path,ROOT/'scripts/535_compare_signed_benefit_gates.py',MP,C,S,Path(__file__)")
source=source.replace("        r['paths']['frozen']=dict(c['paths']['old_gated'])","        r['paths']['frozen']=dict(c['paths']['old_gated'])\n        r['paths']['previous_signed']=dict(previous[suite,cid]['paths']['signed'])")
source=source.replace("newimages['matched_binary'],newimages['signed']","rgb(ROOT/'outputs/signed_benefit_gate_comparison_v1'/suite/cid/'signed.png'),newimages['signed']")
source=source.replace('ref|input|frozen|binary|signed','ref|input|frozen|previous signed|constrained').replace('Private signed-benefit gate comparison','Private clean-constrained gate comparison')
exec(compile(source,str(ROOT/'scripts/535_compare_signed_benefit_gates.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
