"""Independent class accounting and private visual-assessment record."""
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/'outputs/stellenbosch_mask_failure_isolation_v1'
OUT=ROOT/'outputs/stellenbosch_mask_failure_verification_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    inputs=read(PARENT/'input_sha256_PRIVATE.json')
    inputs.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in inputs.items())
    result=read(PARENT/'results_PRIVATE.json');rows=result['records'];assert len(rows)==30
    totals={};checked=0
    for r in rows:
        if 'probe_pixels' not in r:continue
        hist=r['parser_class_histogram']
        assert sum(hist.values())==r['probe_pixels']
        assert hist['skin']+hist['nose']==r['parser_skin_nose_in_probe']
        assert r['parser_skin_nose_fraction']==r['parser_skin_nose_in_probe']/r['probe_pixels']
        t=totals.setdefault(r['sampling_stratum'],[0,0,0]);t[0]+=1;t[1]+=r['probe_pixels'];t[2]+=r['parser_skin_nose_in_probe'];checked+=1
    for key,(count,den,num) in totals.items():
        aggregate=result['summary']['by_preexisting_stratum'][key]
        assert [aggregate['available'],aggregate['probe_pixels'],aggregate['skin_nose_pixels']]==[count,den,num]
    high=[r for r in rows if r['sampling_stratum']=='[9,10]' and 'probe_pixels' in r]
    assert len(high)==4 and all(r['parser_class_histogram']['background']==r['probe_pixels'] for r in high)
    for i in range(1,11):assert cv2.imread(str(PARENT/f'contact_{i:02d}.png')).shape==(846,1024,3)
    report=dict(cases=30,class_accounting_checks=checked,aggregate_strata_checks=len(totals),
        high_stratum_available_all_background=4,high_stratum_missing_detector=2,
        all30_boards_assistant_inspected=True,labels_hidden=True,
        qualitative_observations='Probe generally tracks facial surface but includes glasses, hair edge or other non-skin in some cases; it is not an admissible replacement mask. Parser holes precede final veto on many faces. Some additional losses follow FaceOcc, including lower-face and reflected-glasses regions. Dim high-score sample faces have no parser skin despite available face geometry. Two detector failures retained.',
        no_skin_accuracy_claim=True,no_causal_bias_or_population_rate_claim=True,
        new_forwards=0,new_fits=0,admissions=0,parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in inputs.items())
    OUT.mkdir();(OUT/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'verification_PRIVATE.json':sha(OUT/'verification_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='qualitative_observations'},indent=2))

if __name__=='__main__':main()
