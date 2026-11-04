"""Reuse fixed isolated CPU inference, changing output and plan paths only."""
from pathlib import Path

source = Path(__file__).with_name('369_run_faceocc_logits.py').read_text(encoding='utf-8')
assert source.count('outputs/faceocc_diagnostic_v1') == 1
assert source.count("out/'plan.json'") == 1
source = source.replace('outputs/faceocc_diagnostic_v1', 'outputs/mst_subject_skin_study_v1')
source = source.replace("out/'plan.json'", "out/'inference_plan.json'")
exec(compile(source, str(Path(__file__).with_name('369_run_faceocc_logits.py')), 'exec'), {'__file__': __file__, '__name__': '__main__'})
