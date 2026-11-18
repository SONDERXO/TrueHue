"""Pinned unchanged batch worker, one forward per aligned development parent."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/group_diversity_final_masks_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
binding=OUT/'worker_binding_PRIVATE.json'
if binding.exists():raise FileExistsError('Worker already bound; do not repeat forwards')
paths=[Path(__file__),ROOT/'scripts/369_run_faceocc_logits.py',OUT/'inference_plan.json',OUT/'preparation_PRIVATE.json']
binding.write_text(json.dumps(dict(input_sha256={str(p):sha(p) for p in paths},new_fits=0),indent=2),encoding='utf-8')
source=(ROOT/'scripts/369_run_faceocc_logits.py').read_text(encoding='utf-8')
assert source.count('outputs/faceocc_diagnostic_v1')==1 and source.count("out/'plan.json'")==1
source=source.replace('outputs/faceocc_diagnostic_v1','outputs/group_diversity_final_masks_v1').replace("out/'plan.json'","out/'inference_plan.json'")
exec(compile(source,str(ROOT/'scripts/369_run_faceocc_logits.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
