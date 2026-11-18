"""Saved-evidence admission decision; no pixels, inference, fitting or score bins."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_face_crop_v1'
ASSESS=ROOT/'outputs/stellenbosch_face_crop_assessment_v1'
OUT=ROOT/'outputs/stellenbosch_calibration_admission_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    inputs={}
    for root in (PARENT,ASSESS):
        for name,digest in read(root/'sha256.json').items():
            path=root/name;assert sha(path)==digest;inputs[str(path)]=digest
        inputs[str(root/'sha256.json')]=sha(root/'sha256.json')
    for path,digest in read(PARENT/'inference_plan.json')['input_sha256'].items():
        assert sha(path)==digest;inputs[path]=digest
    rows=read(PARENT/'results_PRIVATE.json')['records']
    subjects=defaultdict(list)
    for r in rows:subjects[r['subject_key']].append(r)
    assert len(rows)==30 and len(subjects)==10 and all(len(v)==3 for v in subjects.values())
    coverage={};ranges=[];private=[]
    for key,group in subjects.items():
        assert len({r['source_mst_exact_decimal'] for r in group})==1
        ok=[r for r in group if r['status']=='success']
        stratum=group[0]['sampling_stratum']
        cell=coverage.setdefault(stratum,dict(selected_subjects=0,attempts=0,technical_passes=0,complete_subjects=0))
        cell['selected_subjects']+=1;cell['attempts']+=3;cell['technical_passes']+=len(ok);cell['complete_subjects']+=len(ok)==3
        values=[r['measurement_report']['features']['input_ita_degrees'] for r in ok]
        spread=max(values)-min(values) if len(values)==3 else None
        if spread is not None:ranges.append(spread)
        private.append(dict(subject_key=key,technical_passes=len(ok),ita_range_degrees=spread,
            source_mst_exact_decimal=group[0]['source_mst_exact_decimal'],admitted=False))
    summary=dict(decision='hold_current30_for_calibration',selected_subjects=10,attempts=30,
        technically_complete_subjects=sum(len([r for r in g if r['status']=='success'])==3 for g in subjects.values()),
        coverage_by_preexisting_descriptive_sampling_stratum=coverage,
        complete_subject_ITA_range_degrees_min_median_max=[min(ranges),statistics.median(ranges),max(ranges)],
        range_is_descriptive_not_accuracy_or_acceptance_cutoff=True,
        admissions=0,calibration_fits=0,tree_fits=0,new_model_forwards=0,
        reasons=['Actual-skin support remains unverified, with documented substantial facial omissions.',
            'Normalized guard is not native-resolution qualification; no validated native adequacy threshold exists.',
            'Technical availability is uneven across the preselected descriptive score strata.',
            'Integer-only retained calibrator cannot consume preserved decimal targets unchanged.'],
        evaluation_scope='Development feasibility only; all30development-exposed, no untouched final set allocated.',
        next_requirement='Establish externally justified skin-support/native adequacy and decimal-compatible subject-held evaluation before any fit; no automatic new batch.',
        script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in inputs.items())
    OUT.mkdir()
    for name,value in [('summary.json',summary),('subjects_PRIVATE.json',private),('input_sha256_PRIVATE.json',inputs)]:
        (OUT/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
