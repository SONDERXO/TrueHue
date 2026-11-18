"""Fixed acceptance, output replay and selected boards for depth-four comparison."""
from pathlib import Path
import runpy,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/depth_four_correction_comparison_v1'
M=ROOT/'outputs/depth_four_correction_models_v1/models_PRIVATE.json'
def main():
    ns=runpy.run_path(str(ROOT/'scripts/616_verify_expanded_correction_outputs.py'))
    fn=ns['main'];fn.__globals__.update(OUT=OUT,M=M);fn()
    ns=runpy.run_path(str(ROOT/'scripts/617_assess_expanded_correction.py'))
    fn=ns['main'];original=fn.__globals__['read']
    legacy=ROOT/'outputs/expanded_correction_models_v1/models_PRIVATE.json'
    fn.__globals__.update(OUT=OUT,read=lambda p:original(M if Path(p)==legacy else p));fn()
    d=json.loads((OUT/'results_PRIVATE.json').read_text())
    print('DEPTH FOUR SUMMARY')
    for cohort,layers in d['summary'].items():
        for layer,s in layers.items():print(cohort,layer,json.dumps(s['methods']['candidate']))
if __name__=='__main__':main()
