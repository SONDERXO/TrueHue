"""Existing one-forward CPU batch path, on raw actual-input aligned images."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'outputs/aligned_correction_preparation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
binding=out/'worker_binding_PRIVATE.json'
if binding.exists():raise FileExistsError('Worker already bound; no automatic repeat')
paths=[Path(__file__),ROOT/'scripts/369_run_faceocc_logits.py',ROOT/'scripts/420_run_preview_faceocc.py',out/'inference_plan.json']
for folder in (out/'cases').iterdir():
    paths.extend(p for p in folder.iterdir() if p.is_file())
binding.write_text(json.dumps(dict(input_sha256={str(p):sha(p) for p in paths},new_fits=0),indent=2),encoding='utf-8')
source=(ROOT/'scripts/369_run_faceocc_logits.py').read_text(encoding='utf-8')
assert source.count('outputs/faceocc_diagnostic_v1')==1
source=source.replace('outputs/faceocc_diagnostic_v1','outputs/aligned_correction_preparation_v1').replace("out/'plan.json'","out/'inference_plan.json'")
exec(compile(source,str(ROOT/'scripts/369_run_faceocc_logits.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
