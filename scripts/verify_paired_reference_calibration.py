"""Independent source/data joins and projection-span/prototype/pixel verification."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.evaluation.paired_reference_prototype_pixel_verification import verify_run
from src.model_training.reiqa_frozen_features import sha
OUT=ROOT/'outputs/paired_reference_calibration_prediction_v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    destination=OUT/'verification_PRIVATE.json'
    if destination.exists():raise FileExistsError(destination)
    for p,h in read(OUT/'bindings_PRIVATE.json').items():assert sha(ROOT/p)==h
    rows=read(OUT/'prepared_rows.json');assert rows==read(ROOT/'outputs/camera_halfstop_prediction_v1/prepared_rows.json')
    assert len(rows)==66 and all(r['generated_fixture'] is False and r['parent_training_admitted'] is False for r in rows)
    for r in rows:
        assert sha(ROOT/r['input_pack'])==r['input_pack_sha256']
        with np.load(ROOT/r['input_pack'],allow_pickle=False) as original, np.load(OUT/'evaluation'/(r['case_id']+'.npz'),allow_pickle=False) as evaluated:
            for key in ['input','reference','alpha','protected']:np.testing.assert_array_equal(original[key],evaluated[key])
    result=verify_run(OUT)
    assert read(OUT/'completion_PRIVATE.json')['calibration_models']==11
    result.update(calibration_models=11,reference_prototypes=66,target_fits=0,held_reference_used_for_calibration=False,
        prior_condition_task='unchanged_camera_halfstop',old_severe_stress_requalified=False,
        artifact_sha256={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    destination.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('PASS independent spans/prototypes660fit66held132render; status='+result['numeric_status'],flush=True)
if __name__=='__main__':main()
