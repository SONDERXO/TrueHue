"""Reuse frozen source preparation with a separately bound 24-photo selection."""
from pathlib import Path
source=Path(__file__).with_name('455_prepare_stellenbosch_new_subjects.py').read_text()
source=source.replace("outputs/stellenbosch_new_subjects_v1","outputs/frozen_split_subject_check_v1").replace('range(10)','range(8)').replace('range(1,11)','range(1,9)').replace('attempts=30,new_publisher_keys=10','attempts=24,new_publisher_keys=8').replace("+'/30; parser forwards '","+'/24; parser forwards '")
source=source.replace("bound=plan['input_sha256']","bound=dict(plan['input_sha256']); bound.update(read(ROOT/'outputs/stellenbosch_new_subjects_v1/inference_plan.json')['input_sha256']); bound[str(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')]=sha(ROOT/'outputs/frozen_split_candidate_v1/model_PRIVATE.json')")
exec(compile(source,str(Path(__file__).with_name('455_prepare_stellenbosch_new_subjects.py')),'exec'),{'__file__':__file__,'__name__':'__main__'})
