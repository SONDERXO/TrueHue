"""Bind completed private thirty-board qualitative assessment to frozen outputs."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'outputs/stellenbosch_parser_appearance_v1'
VERIFY=ROOT/'outputs/stellenbosch_parser_appearance_verification_v1'
OUT=ROOT/'outputs/stellenbosch_parser_appearance_assessment_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
NOTES={
 1:'Broad facial mask retained; added hairline/mouth-border pixels need caution; no precise hair/rim accuracy claim.',
 2:'Substantial central-face holes reduced but nose/forehead gaps remain; condition-dependent facial support.',
 3:'Cool-condition lower-face omission increases despite technical pass; other two conditions similar. Availability is not mask-quality nonregression.',
 4:'Substantial forehead/nose/central support restored; remaining small nasal exclusions and boundaries require validation.',
 5:'Some forehead improvement; lower-face and right-side omissions persist after original-pixel veto.',
 6:'Glasses/reflections remain problematic. Two warm conditions gain technical passes but final support is sparse cheek patch or partial rim-shaped facial regions, not qualified broad skin.',
 7:'Cool condition still fails parser. Middle parent gains skin but final veto removes all. Last condition gains a pass with only sparse forehead/cheek islands.',
 8:'More central support but large condition-dependent holes remain. Fine eye/brow/glasses/hair boundaries not certified.',
 9:'Parser recognizes new forehead or facial regions; original-input FaceOcc leaves none or a small forehead patch below guard; all three remain failures.',
 10:'Two detector failures retained without synthetic geometry; middle condition has very little predicted skin and fails unchanged parent minimum.'}

def main():
    if OUT.exists():raise FileExistsError(OUT)
    for root in [BASE,VERIFY]:
        assert all(sha(root/p)==h for p,h in read(root/'sha256.json').items())
    rows=read(BASE/'results_PRIVATE.json')['records']
    assert len(rows)==30 and len({r['subject_key'] for r in rows})==10
    gained=[r['case_id'] for r in rows if r['status']=='success' and r['baseline_status']!='success']
    assert len(gained)==3
    report=dict(observer='assistant',all30boards_inspected=True,labels_hidden=True,observations_by_subject_index=NOTES,
        gained_case_ids_PRIVATE=gained,technical_nonregression_is_not_mask_quality_nonregression=True,
        decision='partial_recognition_gain_not_calibration_admission_or_runtime_adoption',
        remaining_highest_stratum_final_successes=0,complete_subject_keys=6,
        native_adequacy_established=False,no_pixel_ground_truth=True,new_forwards=0,new_fits=0,admissions=0,
        source_manifest_sha256=sha(BASE/'sha256.json'),verification_manifest_sha256=sha(VERIFY/'sha256.json'),script_sha256=sha(Path(__file__)))
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print('30 boards / 10 subject notes bound; no calibration admission or new inference.')

if __name__=='__main__':main()
