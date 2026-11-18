"""Independent saved-mask/original-pixel checks; no model forwards or refits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.segmentation_appearance_probe import parser_input

BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PARENT=ROOT/'outputs/stellenbosch_parser_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_parser_appearance_verification_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    prior={r['case_id']:r for r in read(BASE/'results_PRIVATE.json')['records']}
    data=read(PARENT/'results_PRIVATE.json');parents=finals=transforms=0
    assert len(data['records'])==30
    native_counts=[];ranges={}
    for r in data['records']:
        old=prior[r['case_id']];folder=PARENT/r['case_id'];original=BASE/r['case_id']
        for key in ['source_path','subject_key','condition','source_mst_exact_decimal','source_mst_raw_type','source_mst_raw_value','input_bridge']:
            assert r[key]==old[key]
        image=cv2.imread(str(original/'input.png'))
        assert not r['calibration_admitted'] and not r['training_admitted'] and r['MST'] is None
        if (folder/'parser_input.png').exists():
            enhanced=cv2.imread(str(folder/'parser_input.png'));assert np.array_equal(parser_input(image),enhanced);transforms+=1
            points=np.load(original/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
            try:
                expected=build_semantic_face_coverage(image,points,categories).mask.copy()
                expected[nostril_guard(expected.shape,points)]=0
                assert np.array_equal(expected,cv2.imread(str(folder/'parent_mask.png'),0))
                assert compute_masked_lab_statistics(image,expected,1000)==r['parent_report']['statistics'];parents+=1
            except ValueError as error:
                assert r['parent_report']['stage']=='semantic_mask' and str(error)==r['parent_report']['reason']
        if 'measurement_report' in r:
            mask=cv2.imread(str(folder/'measurement_mask.png'),0)
            stats=compute_masked_lab_statistics(image,mask,1000)
            assert stats==r['measurement_report']['statistics'];finals+=1
            assert not mask[cv2.imread(str(folder/'parent_mask.png'),0)==0].any()
            x0,y0,x1,y1=r['input_bridge']['native_bounds'];side=x1-x0
            projected=np.zeros(r['input_bridge']['source_shape'][:2],np.uint8)
            projected[y0:y1,x0:x1]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
            assert np.array_equal(projected,cv2.imread(str(folder/'native_grid.png'),0))
            assert int(np.count_nonzero(projected))==r['native_accounting']['selected_native_grid_locations']
            if r['status']=='success':
                native_counts.append(int(np.count_nonzero(projected)))
                ranges.setdefault(r['subject_key'],[]).append(stats['ita_degrees'])
    assert sum(r['status']=='success' for r in data['records'])==data['summary']['candidate_final_successes']
    assert all(sha(p)==h for p,h in bound.items())
    report=dict(attempts=30,decimal_membership_parities=30,parser_copy_exact_checks=transforms,
        semantic_mask_and_original_parent_stats_checks=parents,original_final_stats_and_native_projection_checks=finals,
        successful_native_grid_range=[min(native_counts),max(native_counts)],
        complete_subject_keys=sum(len(v)==3 for v in ranges.values()),
        complete_subject_ita_ranges_PRIVATE={k:max(v)-min(v) for k,v in ranges.items() if len(v)==3},
        original_sources_and_parent_artifacts_unchanged=True,new_forwards=0,new_fits=0,admissions=0,
        script_sha256=sha(__file__),parent_manifest_sha256=sha(PARENT/'sha256.json'))
    OUT.mkdir();(OUT/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'verification_PRIVATE.json':sha(OUT/'verification_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if 'PRIVATE' not in k},indent=2))

if __name__=='__main__':main()
