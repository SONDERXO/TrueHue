"""Private saved-output verification/assessment; no forwards, refits or relabelling."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.data_preparation.stellenbosch_preparation import select_subjects,CONDITIONS

PARENT=ROOT/'outputs/stellenbosch_bounded_preparation_v1'
OUT=ROOT/'outputs/stellenbosch_bounded_preparation_assessment_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
NOTES={
 1:'Small full-scene face; baseline extends below face; veto leaves small facial region; colour differs across conditions.',
 2:'Small face and condition-dependent partial coverage; first parent fails, other masks below pixel minimum.',
 3:'Small face; parent includes neck and, in one warm condition, much of light shirt; veto removes much of that region.',
 4:'All three parent attempts fail; selected face/skin incomplete or absent; no candidate masks are fabricated.',
 5:'Small face; hair/top-of-head or neck enters parent support; some candidate masks lose large facial regions.',
 6:'Small face with glasses and high hair; parent includes hair; veto leaves sparse facial fragments, sometimes none.',
 7:'Small dim facial region; only middle condition reaches FaceOcc; sparse retained skin and other two parent failures.',
 8:'Small face with hair/clothing boundaries; candidate coverage changes markedly with condition and remains below guard.',
 9:'Small dim face; first parent fails; remaining candidate masks contain tiny patches rather than sufficient skin support.',
 10:'Small dark-looking/low-signal face in these photos; only middle condition reaches FaceOcc, then retains no pixels; no intrinsic tone inference.'}


def main():
    if OUT.exists():raise FileExistsError(OUT)
    plan=read(PARENT/'plan_PRIVATE.json');bound=read(PARENT/'inference_plan.json')['input_sha256']
    manifest=read(PARENT/'sha256.json')
    assert all(sha(p)==h for p,h in bound.items())
    assert all(sha(PARENT/p)==h for p,h in manifest.items())
    selection=select_subjects(read(ROOT/'outputs/stellenbosch_received_data_v1/subjects_PRIVATE.json'))
    assert selection==plan['selected_subjects']
    result=read(PARENT/'results_PRIVATE.json');rows=[];candidate_counts=[];retentions=[];widths=[];heights=[];checked=0
    expected={x['case_id']:x for x in plan['selection']}
    for rec in result['records']:
        folder=PARENT/rec['case_id'];selected=expected[rec['case_id']]
        assert rec['source_mst_exact_decimal']==selected['source_mst_exact_decimal']
        assert rec['source_mst_raw_type']==selected['source_mst_raw_type'] and rec['integer_category'] is None
        assert sha(Path(rec['source_path']))==sha(folder/'source.jpeg')
        box=rec['parent_report']['face_box'];widths.append(box[2]);heights.append(box[3])
        measurement=rec.get('measurement_report',{});candidate=measurement.get('candidate_pixels')
        if measurement:
            image=cv2.imread(str(folder/'input.png'));mask=cv2.imread(str(folder/'measurement_mask.png'),0)
            stats=compute_masked_lab_statistics(image,mask,1000)
            assert stats==measurement['statistics'] and candidate==int(np.count_nonzero(mask))
            assert not measurement['calibration_admitted'] and measurement['mst'] is None
            candidate_counts.append(candidate);retentions.append(measurement['retained_fraction']);checked+=1
        rows.append(dict(case_id=rec['case_id'],subject_key=rec['subject_key'],condition=rec['condition'],
            source_mst_exact_decimal=rec['source_mst_exact_decimal'],integer_category=None,
            parent_status=rec['parent_report']['status'],measurement_status=rec['status'],
            failure_reason=rec.get('reason') or measurement.get('reason'),candidate_pixels=candidate,
            retention=measurement.get('retained_fraction'),calibration_admitted=False))
    assert len(rows)==30 and len({r['subject_key'] for r in rows})==10
    assert all(Counter(r['condition'] for r in rows if r['subject_key']==s)==Counter(CONDITIONS) for s in {r['subject_key'] for r in rows})
    OUT.mkdir()
    with (OUT/'cases_PRIVATE.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    with (OUT/'cases_PRIVATE.csv').open(newline='',encoding='utf-8') as stream:csvrows=list(csv.DictReader(stream))
    assert len(csvrows)==30 and all(a['source_mst_exact_decimal']==b['source_mst_exact_decimal'] for a,b in zip(csvrows,rows))
    assessment=dict(summary=result['summary'],observer='assistant',all30_native_original_and_mask_boards_inspected=True,
        label_scores_not_displayed_on_boards=True,observations_by_subject_index=NOTES,
        face_box_working_width_min_median_max=[min(widths),statistics.median(widths),max(widths)],
        face_box_working_height_min_median_max=[min(heights),statistics.median(heights),max(heights)],
        candidate_pixels_min_max=[min(candidate_counts),max(candidate_counts)],
        retention_min_median_max=[min(retentions),statistics.median(retentions),max(retentions)],
        saved_measurement_statistics_checks=checked,CSV_JSON_decimal_parity=True,
        parent_manifest_sha256=sha(PARENT/'sha256.json'),assessment_script_sha256=sha(Path(__file__)),
        new_model_forwards=0,new_fits=0,admissions=0,
        next_candidate='fixed_face_framing_bridge_same30_with_native_resolution_accounting_NOT_activated',
        population_failure_rate_claim=False,entire_dataset_unusable_claim=False)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(assessment,indent=2),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items()) and all(sha(PARENT/p)==h for p,h in manifest.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2))
    print(json.dumps(dict(selected_cases=30,decimal_parities=30,statistics_checks=checked,new_forwards=0,new_fits=0,admissions=0),indent=2))


if __name__=='__main__':main()
