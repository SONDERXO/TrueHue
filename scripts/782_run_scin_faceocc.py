"""Reuse established CPU batch worker on one fixed native-readiness package."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/scin_nine_support_screen_v1'
marker=OUT/'worker_started_PRIVATE.json'
if marker.exists():raise FileExistsError('Worker already started; preserve partial output')
source=ROOT/'scripts/369_run_faceocc_logits.py'
raw=source.read_text(encoding='utf-8')
assert raw.count('outputs/faceocc_diagnostic_v1')==1
assert raw.count("out/'plan.json'")==1
with marker.open('x',encoding='utf-8') as f:
    json.dump(dict(worker_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),inference_plan_sha256=hashlib.sha256((OUT/'inference_plan.json').read_bytes()).hexdigest()),f)
adapted=raw.replace('outputs/faceocc_diagnostic_v1','outputs/scin_nine_support_screen_v1').replace("out/'plan.json'","out/'inference_plan.json'")
exec(compile(adapted,str(source),'exec'),{'__file__':__file__,'__name__':'__main__'})
