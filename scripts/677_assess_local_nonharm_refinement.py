"""Independent native replay, unchanged acceptance, all recent comparators."""
from pathlib import Path
import runpy,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/local_nonharm_refinement_comparison_v1'
M=ROOT/'outputs/local_nonharm_refinement_models_v1/models_PRIVATE.json'

def main():
    assert not (OUT/'verification_PRIVATE.json').exists()
    ns=runpy.run_path(str(ROOT/'scripts/616_verify_expanded_correction_outputs.py'));fn=ns['main'];fn.__globals__.update(OUT=OUT,M=M);fn()
    ns=runpy.run_path(str(ROOT/'scripts/617_assess_expanded_correction.py'));fn=ns['main'];read=fn.__globals__['read'];legacy=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
    fn.__globals__.update(OUT=OUT,read=lambda p:read(M if Path(p)==legacy else p));fn()
    paths=dict(previous_exception='facial_veto_exception_comparison_v1',global_nonharm='colour_nonharm_comparison_v1',fixed_structure='fixed_structure_nonharm_comparison_v1')
    data={stage:json.loads((ROOT/'outputs'/path/'results_PRIVATE.json').read_text()) for stage,path in paths.items()}
    data['local_refinement']=json.loads((OUT/'results_PRIVATE.json').read_text())
    report={co+'_'+layer:{stage:d['summary'][co][layer]['methods']['candidate'] for stage,d in data.items()} for co in ('development','later') for layer in ('clean','core','composite_stress_design')}
    (OUT/'attribution_PRIVATE.json').write_text(json.dumps(report,indent=2));print('Attribution saved')
if __name__=='__main__':main()
