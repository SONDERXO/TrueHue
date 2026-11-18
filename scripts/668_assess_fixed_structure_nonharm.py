"""Independent output replay, fixed acceptance and both reserved comparators."""
from pathlib import Path
import runpy,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/fixed_structure_nonharm_comparison_v1';M=ROOT/'outputs/fixed_structure_nonharm_models_v1/models_PRIVATE.json'
def main():
    ns=runpy.run_path(str(ROOT/'scripts/616_verify_expanded_correction_outputs.py'));fn=ns['main'];fn.__globals__.update(OUT=OUT,M=M);fn()
    ns=runpy.run_path(str(ROOT/'scripts/617_assess_expanded_correction.py'));fn=ns['main'];read=fn.__globals__['read'];legacy=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
    fn.__globals__.update(OUT=OUT,read=lambda p:read(M if Path(p)==legacy else p));fn()
    d=json.loads((OUT/'results_PRIVATE.json').read_text());comparators={stage:json.loads((ROOT/path/'results_PRIVATE.json').read_text()) for stage,path in [('pre','outputs/reserved_clean_veto_pre_comparison_v1'),('veto','outputs/reserved_clean_veto_comparison_v1'),('previous_exception','outputs/facial_veto_exception_comparison_v1'),('global_nonharm','outputs/colour_nonharm_comparison_v1')]}
    report={}
    for co in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            item={stage:data['summary'][co][layer]['methods']['candidate'] for stage,data in comparators.items()}
            item['exception']=d['summary'][co][layer]['methods']['candidate'];report[co+'_'+layer]=item
    (OUT/'attribution_PRIVATE.json').write_text(json.dumps(report,indent=2));print('ATTRIBUTION',json.dumps(report,indent=2))
if __name__=='__main__':main()
