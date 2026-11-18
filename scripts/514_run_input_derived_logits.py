"""CPU visibility inference on actual distorted input crops."""
from pathlib import Path
source=Path(__file__).with_name('369_run_faceocc_logits.py').read_text()
assert source.count('outputs/faceocc_diagnostic_v1')==1 and source.count("out/'plan.json'")==1
source=source.replace('outputs/faceocc_diagnostic_v1','outputs/input_derived_mask_check_v1').replace("out/'plan.json'","out/'inference_plan.json'")
exec(compile(source,str(Path(__file__).with_name('369_run_faceocc_logits.py')),'exec'),{'__file__':__file__,'__name__':'__main__'})
