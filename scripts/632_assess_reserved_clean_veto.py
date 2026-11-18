"""Independent output checks, attribution summary and fixed joint acceptance."""
from pathlib import Path
import runpy,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/reserved_clean_veto_comparison_v1'
MODELS=ROOT/'outputs/reserved_clean_veto_models_v1'
def main():
    for stage in ('pre','final'):
        out=ROOT/('outputs/reserved_clean_veto_pre_comparison_v1' if stage=='pre' else 'outputs/reserved_clean_veto_comparison_v1')
        model=MODELS/('pre_veto_models_PRIVATE.json' if stage=='pre' else 'models_PRIVATE.json')
        ns=runpy.run_path(str(ROOT/'scripts/616_verify_expanded_correction_outputs.py'));fn=ns['main'];fn.__globals__.update(OUT=out,M=model);fn()
    ns=runpy.run_path(str(ROOT/'scripts/617_assess_expanded_correction.py'));fn=ns['main'];original=fn.__globals__['read'];legacy=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
    fn.__globals__.update(OUT=OUT,read=lambda p:original(MODELS/'models_PRIVATE.json' if Path(p)==legacy else p));fn()
    final=json.loads((OUT/'results_PRIVATE.json').read_text());pre=json.loads((ROOT/'outputs/reserved_clean_veto_pre_comparison_v1/results_PRIVATE.json').read_text());depth=json.loads((ROOT/'outputs/depth_four_correction_comparison_v1/results_PRIVATE.json').read_text())
    summary={}
    for cohort in ('development','later'):
        for layer in ('clean','core','composite_stress_design'):
            summary[cohort+'_'+layer]={stage:data['summary'][cohort][layer]['methods']['candidate'] for stage,data in (('unreserved_depth_four',depth),('reserved_pre_veto',pre),('reserved_post_veto',final))}
    (OUT/'attribution_PRIVATE.json').write_text(json.dumps(summary,indent=2));print('ATTRIBUTION',json.dumps(summary,indent=2))
if __name__=='__main__':main()
