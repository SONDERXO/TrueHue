"""Independent mask/statistics replay and private qualitative assessment."""
import hashlib
import json
from pathlib import Path
import sys
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.segmentation_appearance_probe import parser_input
BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PRIOR=ROOT/'outputs/stellenbosch_parser_appearance_v1'
PARENT=ROOT/'outputs/stellenbosch_faceocc_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_faceocc_appearance_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NOTES={
 1:'Mostly small boundary shifts; original hair lock exclusion retained; some additional hairline pixels require caution.',
 2:'Some forehead skin restored while original central parser holes remain; lower boundary shifts include losses.',
 3:'Substantial apparently visible chin/lower-face coverage restored in warm conditions; cool parser hole remains.',
 4:'Mostly boundary/forehead changes; no obvious broad new object region at this scale, not complete-object accuracy.',
 5:'Broad apparent cheek/chin skin restored in warm conditions; outer forehead/jaw and lower-face material still uncertain.',
 6:'Large forehead/cheek restoration in middle warm glasses case; fine frame, lens and reflection contamination remains uncertain. Other warm case retains patchy parser support; cold parent failure unchanged.',
 7:'Two warm parents now retain much more available forehead/cheek support; still fragmented because parser misses other areas. Cold parser failure retained.',
 8:'Mostly narrow boundary changes; central parser omissions remain. Hair/sideburn boundaries not certified.',
 9:'All three now technically pass, with forehead-only support in first two and fragmented broader face in third; very dim native source prevents reliable skin/admission claim.',
 10:'All three remain earlier detector/parent failures; no replacement image or final measurement fabricated.'}

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    data=read(PARENT/'results_PRIVATE.json');old={r['case_id']:r for r in read(PRIOR/'results_PRIVATE.json')['records']}
    assert len(data['records'])==30
    checks=0;native_counts=[];groups=defaultdict(list);added=lost=0;counts=[]
    for r in data['records']:
        previous=old[r['case_id']]
        for k in ['source_path','subject_key','condition','source_mst_exact_decimal','source_mst_raw_value','source_mst_raw_type','parent_report','input_bridge']:
            assert r[k]==previous[k]
        assert not r['calibration_admitted'] and not r['training_admitted'] and r['MST'] is None
        if r['parent_report']['status']!='success':
            assert r['status']=='failed' and 'measurement_report' not in r;continue
        folder=PARENT/r['case_id'];original=BASE/r['case_id'];prior=PRIOR/r['case_id']
        image=cv2.imread(str(original/'input.png'));aligned=cv2.imread(str(folder/'aligned_original.png'))
        assert np.array_equal(aligned,cv2.imread(str(prior/'aligned.png')))
        assert np.array_equal(parser_input(aligned),cv2.imread(str(folder/'aligned_candidate.png')))
        matrix=np.array(read(folder/'matrix.json'));logits=np.load(r['logits_path'],allow_pickle=False)
        assert sha(r['logits_path'])==r['logits_sha256']
        valid=cv2.warpAffine(np.full((256,256),255,np.uint8),matrix,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        positive=np.where((logits>0)&(valid>0),255,0).astype(np.uint8)
        inverse=cv2.warpAffine(positive,cv2.invertAffineTransform(matrix),(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        parent=cv2.imread(str(prior/'parent_mask.png'),0)
        expected=np.where((parent>0)&(inverse>0),255,0).astype(np.uint8)
        mask=cv2.imread(str(folder/'measurement_mask.png'),0)
        assert np.array_equal(expected,mask)
        stats=compute_masked_lab_statistics(image,mask,1000)
        assert stats==r['measurement_report']['statistics']
        oldmask=cv2.imread(str(prior/'measurement_mask.png'),0)
        a=int(((mask>0)&(oldmask==0)).sum());l=int(((oldmask>0)&(mask==0)).sum())
        assert r['mask_change']==dict(added=a,lost=l);added+=a;lost+=l
        x0,y0,x1,y1=r['input_bridge']['native_bounds'];side=x1-x0
        projected=np.zeros(r['input_bridge']['source_shape'][:2],np.uint8)
        projected[y0:y1,x0:x1]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
        assert np.array_equal(projected,cv2.imread(str(folder/'native_grid.png'),0))
        n=int(np.count_nonzero(projected));assert n==r['native_accounting']['selected_native_grid_locations']
        checks+=1
        if r['status']=='success':
            assert stats['valid'];native_counts.append(n);counts.append(stats['skin_pixels']);groups[r['subject_key']].append(stats['ita_degrees'])
    assert added==data['summary']['added_normalized_pixels'] and lost==data['summary']['lost_normalized_pixels']
    ranges=[max(v)-min(v) for v in groups.values() if len(v)==3]
    report=dict(all30boards_assistant_inspected=True,labels_hidden=True,notes_by_subject_index_PRIVATE=NOTES,
        original_label_parent_contract_parities=30,manual_mapping_mask_replays=checks,original_statistics_native_projection_checks=checks,
        recognition_input_parities=checks,complete_subject_keys=len(ranges),successful_normalized_pixels_range=[min(counts),max(counts)],
        successful_native_grid_range=[min(native_counts),max(native_counts)],complete_subject_ITA_range_min_median_max=[min(ranges),float(np.median(ranges)),max(ranges)],
        within_subject_ITA_range_is_descriptive_not_accuracy=True,
        actual_skin_and_native_adequacy_established=False,calibration_admissions=0,new_forwards=0,new_fits=0,
        decision='retain_as_promising_isolated_recognition_candidate_not_default_or_calibration_admission',
        parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if 'PRIVATE' not in k},indent=2))

if __name__=='__main__':main()
