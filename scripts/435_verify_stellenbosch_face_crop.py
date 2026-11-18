"""Verify private fixed-crop evidence without inference, fitting or admission."""
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics

BASE=ROOT/'outputs/stellenbosch_bounded_preparation_v1'
PARENT=ROOT/'outputs/stellenbosch_face_crop_v1'
OUT=ROOT/'outputs/stellenbosch_face_crop_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    manifest=read(PARENT/'sha256.json')
    assert all(sha(p)==h for p,h in bound.items())
    assert all(sha(PARENT/p)==h for p,h in manifest.items())
    old={r['case_id']:r for r in read(BASE/'results_PRIVATE.json')['records']}
    rows=read(PARENT/'results_PRIVATE.json')['records'];counts=[];sides=[];failures=Counter();checks=0
    assert len(rows)==30 and set(old)=={r['case_id'] for r in rows}
    for r in rows:
        previous=old[r['case_id']];folder=PARENT/r['case_id'];bridge=r['input_bridge']
        for key in ['subject_key','condition','source_path','source_mst_exact_decimal','source_mst_raw_type','source_mst_raw_value']:
            assert r[key]==previous[key]
        source=cv2.imread(r['source_path']);x,y,w,h=previous['parent_report']['face_box']
        side=int(np.ceil(1.5*max(w*source.shape[1]/256,h*source.shape[0]/256)))
        left=min(max(int(np.floor((x+w/2)*source.shape[1]/256-side/2)),0),source.shape[1]-side)
        top=min(max(int(np.floor((y+h/2)*source.shape[0]/256-side/2)),0),source.shape[0]-side)
        assert bridge['native_bounds']==[left,top,left+side,top+side]
        assert np.array_equal(source[top:top+side,left:left+side],cv2.imread(str(folder/'native_crop.png')))
        sides.append(side)
        if 'measurement_report' in r:
            mask=cv2.imread(str(folder/'measurement_mask.png'),0);image=cv2.imread(str(folder/'input.png'))
            assert compute_masked_lab_statistics(image,mask,1000)==r['measurement_report']['statistics']
            native=np.zeros(source.shape[:2],np.uint8)
            native[top:top+side,left:left+side]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
            assert np.array_equal(native,cv2.imread(str(folder/'measurement_native_grid.png'),0))
            accounting=r['native_accounting'];n=int(np.count_nonzero(mask));k=int(np.count_nonzero(native))
            assert n==accounting['normalized_selected_pixels'] and k==accounting['selected_native_grid_locations']
            assert accounting['source_area_equivalent_pixels']==n*(side/256)**2
            if r['status']=='success':counts.append(k)
            checks+=1
        if r['status']!='success':failures[r.get('reason') or r.get('measurement_report',{}).get('reason','unspecified')]+=1
        assert not r['calibration_admitted'] and not r['training_admitted'] and r['MST'] is None
    assessment=dict(all30_boards_assistant_inspected=True,labels_hidden_on_boards=True,
        observations='Small native faces throughout. Cases 1-3 mostly contiguous facial support; 4-6 central skin holes; 7-9 condition-dependent lower-face loss; 10-12 forehead/nose and central gaps; 13-15 substantial condition-dependent cheek/chin loss; 16-18 glasses/reflections and sparse or failed support; 19-21 dim face and all failures; 22-24 large central-face omissions; 25-30 dim low-signal faces and all failures. No intrinsic tone or pixel-accuracy claim.',
        cases=30,exact_native_crop_checks=30,decimal_label_parities=30,
        independent_statistics_and_native_projection_checks=checks,
        native_crop_side_range=[min(sides),max(sides)],
        successful_mask_native_grid_locations_range=[min(counts),max(counts)],
        success_by_condition={c:dict(successes=sum(r['condition']==c and r['status']=='success' for r in rows),attempts=sum(r['condition']==c for r in rows)) for c in sorted({r['condition'] for r in rows})},
        subjects_with_three_successes=sum(all(r['status']=='success' for r in rows if r['subject_key']==s) for s in {r['subject_key'] for r in rows}),
        failure_reasons=dict(failures),new_forwards=0,new_fits=0,admissions=0,native_adequacy_established=False,
        parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items()) and all(sha(PARENT/p)==h for p,h in manifest.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(assessment,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps(assessment,indent=2))

if __name__=='__main__':main()
