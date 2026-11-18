"""Bind existing 336 distorted scenes then reuse frozen per-input mask pipeline."""
import json,hashlib,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/input_derived_mask_check_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
if not OUT.exists():
    parent=ROOT/'outputs/frozen_split_subject_evaluation_v1';sources={r['case_id']:r for r in read(ROOT/'outputs/frozen_split_subject_check_v1/results_PRIVATE.json')['records']}
    rows=[]
    for i,r in enumerate(read(parent/'results_PRIVATE.json')['records'],1):
        s=sources[r['source_case']];path=parent/r['source_case']/r['recipe']/'scene_input.png'
        rows.append(dict(case_id=r['case_id'],case_index=i,subject_key=s['subject_key'],condition=s['condition'],source_path=str(path),source_sha256=sha(path),sampling_stratum=s['sampling_stratum'],source_case=r['source_case'],recipe=r['recipe'],layer=r['layer'],calibration_admitted=False,training_admitted=False,MST=None))
    paths=[Path(__file__),ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py',ROOT/'docs/input-derived-mask-check-protocol-2026-11-06.md',ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json']
    bound={str(p):sha(p) for p in paths};bound.update({r['source_path']:r['source_sha256'] for r in rows})
    bound.update(read(ROOT/'outputs/stellenbosch_new_subjects_v1/inference_plan.json')['input_sha256'])
    OUT.mkdir();(OUT/'logits').mkdir();(OUT/'plan_PRIVATE.json').write_text(json.dumps(dict(selection=rows,input_sha256=bound),indent=2),encoding='utf-8')
source=(ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py').read_text()
source=source.replace('outputs/stellenbosch_new_subjects_v1','outputs/input_derived_mask_check_v1').replace('range(10)','range(112)').replace('range(1,11)','range(1,113)').replace('attempts=30,new_publisher_keys=10','attempts=336,new_publisher_keys=8')
exec(compile(source,str(ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py'),'exec'),{'__file__':__file__,'__name__':'__main__'})
