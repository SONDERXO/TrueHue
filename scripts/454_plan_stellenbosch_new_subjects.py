"""Freeze unused publisher subjects/source bytes before any photo decode."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.data_preparation.stellenbosch_preparation import select_subjects,CONDITIONS
OUT=ROOT/'outputs/stellenbosch_new_subjects_v1'
RECEIPT=ROOT/'outputs/stellenbosch_received_data_v1'
BASE=ROOT/'outputs/stellenbosch_bounded_preparation_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    previous=read(BASE/'plan_PRIVATE.json')['selected_subjects'];excluded={r['subject_key'] for r in previous}
    subjects=read(RECEIPT/'subjects_PRIVATE.json');remaining=[r for r in subjects if r['subject_key'] not in excluded]
    selected=select_subjects(remaining);assert len(selected)==10 and not excluded&{r['subject_key'] for r in selected}
    assert select_subjects(list(reversed(remaining)))==selected
    receipt=read(RECEIPT/'protocol.json');data=Path(receipt['dataset_location'])
    files={r['path']:r for r in read(RECEIPT/'files_PRIVATE.json')}
    bound=read(ROOT/'outputs/stellenbosch_faceocc_appearance_v1/inference_plan.json')['input_sha256']
    for p in [BASE/'plan_PRIVATE.json',RECEIPT/'subjects_PRIVATE.json',RECEIPT/'files_PRIVATE.json',Path(__file__),
        ROOT/'scripts/455_prepare_stellenbosch_new_subjects.py',ROOT/'scripts/456_run_stellenbosch_new_subject_logits.py',
        ROOT/'docs/stellenbosch-new-subject-protocol-2026-11-05.md']:
        bound[str(p)]=sha(p)
    rows=[]
    for index,r in enumerate(selected,1):
        label=data/r['publisher_folder']/'monk_scale_value.json';assert sha(label)==r['label_sha256'];bound[str(label)]=r['label_sha256']
        for c in CONDITIONS:
            path=data/r['publisher_folder']/'front-facing'/(c+'.jpeg');expected=files[path.relative_to(data).as_posix()]['sha256']
            assert sha(path)==expected;bound[str(path)]=expected
            rows.append(dict(case_id=f'case_{len(rows)+1:02d}',case_index=len(rows)+1,subject_index=index,
                subject_key=r['subject_key'],condition=c,source_path=str(path),source_sha256=expected,
                source_mst_exact_decimal=r['exact_decimal'],source_mst_raw_type=r['raw_type'],source_mst_raw_value=r['raw_value'],
                sampling_stratum=r['sampling_stratum'],calibration_admitted=False,training_admitted=False,MST=None))
    assert len(rows)==30 and all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'logits').mkdir()
    plan=dict(status='frozen_before_photo_decode',excluded_subject_keys_PRIVATE=sorted(excluded),selected_subjects_PRIVATE=selected,
        selection=rows,input_sha256=bound,source_score_policy='continuous_decimal_no_rounding',
        scope='bounded_development_preparation_NOT_training_or_final_test',unused_highest_interval_keys_after_selection=0)
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    print('Frozen10 new publisher keys /30photos; no pixel decode, admission or fit.')

if __name__=='__main__':main()
