"""Metadata-only prospective selection; freeze raw hashes before any new pixels."""
from decimal import Decimal
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/frozen_split_subject_check_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    receipt=ROOT/'outputs/stellenbosch_received_data_v1'
    old=ROOT/'outputs/stellenbosch_bounded_preparation_v1/plan_PRIVATE.json';new=ROOT/'outputs/stellenbosch_new_subjects_v1/plan_PRIVATE.json'
    excluded={r['subject_key'] for r in read(old)['selected_subjects']}|{r['subject_key'] for r in read(new)['selected_subjects_PRIVATE']}
    assert len(excluded)==20
    subjects=read(receipt/'subjects_PRIVATE.json');remaining=[r for r in subjects if r['subject_key'] not in excluded]
    assert len(remaining)==265 and not any(Decimal(r['exact_decimal'])>=9 for r in remaining)
    selected=[]
    for low,high in [(1,3),(3,5),(5,7),(7,9)]:
        band=[r for r in remaining if low<=Decimal(r['exact_decimal'])<high]
        band.sort(key=lambda r:hashlib.sha256(('TrueHue-frozen-split-subject-check-v1:'+r['subject_key']).encode()).hexdigest())
        assert len(band)>=2
        selected.extend(dict(r,sampling_stratum=f'[{low},{high})') for r in band[:2])
    location=Path(read(receipt/'protocol.json')['dataset_location']);files={r['path']:r['sha256'] for r in read(receipt/'files_PRIVATE.json')}
    bindings={str(p):sha(p) for p in [old,new,receipt/'subjects_PRIVATE.json',receipt/'files_PRIVATE.json',Path(__file__),ROOT/'docs/frozen-split-subject-check-protocol-2026-11-06.md']}
    rows=[]
    for i,r in enumerate(selected,1):
        label=location/r['publisher_folder']/'monk_scale_value.json';assert sha(label)==r['label_sha256'];bindings[str(label)]=r['label_sha256']
        for condition in ['F_cool_600','H_warm_600','L_warm_600']:
            path=location/r['publisher_folder']/'front-facing'/(condition+'.jpeg');expected=files[path.relative_to(location).as_posix()];assert sha(path)==expected;bindings[str(path)]=expected
            rows.append(dict(case_id=f'eval_{len(rows)+1:02d}',case_index=len(rows)+1,subject_index=i,subject_key=r['subject_key'],condition=condition,
                source_path=str(path),source_sha256=expected,source_mst_exact_decimal=r['exact_decimal'],sampling_stratum=r['sampling_stratum'],
                calibration_admitted=False,training_admitted=False,MST=None))
    assert len(rows)==24 and len({r['source_sha256'] for r in rows})==24
    training=read(ROOT/'outputs/stellenbosch_new_subjects_v1/results_PRIVATE.json')['records']
    assert not {r['source_sha256'] for r in rows}&{r['source_sha256'] for r in training}
    OUT.mkdir();(OUT/'logits').mkdir()
    plan=dict(status='frozen_before_pixel_decode',selection=rows,selected_keys_PRIVATE=[r['subject_key'] for r in selected],excluded_exposed_keys_PRIVATE=sorted(excluded),
        original_attempts=24,synthetic_attempts=336,highest_interval_unexposed_keys=0,input_sha256=bindings,scope='prospective_development_fixed_support_NOTfinal_validation')
    (OUT/'plan_PRIVATE.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    print('Frozen8recorded-unexposed publisher keys/24photos/336planned attempts; no new pixels decoded.')


if __name__=='__main__':main()
