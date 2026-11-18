"""Saved-output/new-source verification without inference or calibration."""
from decimal import Decimal
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
PARENT=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/stellenbosch_new_subject_verification_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    plan=read(PARENT/'plan_PRIVATE.json');bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    previous={r['subject_key'] for r in read(ROOT/'outputs/stellenbosch_bounded_preparation_v1/plan_PRIVATE.json')['selected_subjects']}
    selected=plan['selected_subjects_PRIVATE'];assert not previous&{r['subject_key'] for r in selected}
    metadata=read(ROOT/'outputs/stellenbosch_received_data_v1/subjects_PRIVATE.json')
    expected=[]
    for low,high in [(1,3),(3,5),(5,7),(7,9),(9,10)]:
        candidates=[r for r in metadata if r['subject_key'] not in previous and Decimal(low)<=Decimal(r['exact_decimal']) and (Decimal(r['exact_decimal'])<high or high==10 and Decimal(r['exact_decimal'])==10)]
        candidates.sort(key=lambda r:hashlib.sha256(('TrueHue-Stellenbosch-preparation-v1:'+r['subject_key']).encode()).digest())
        expected.extend(r['subject_key'] for r in candidates[:2])
    assert expected==[r['subject_key'] for r in selected] and len(set(expected))==10
    result=read(PARENT/'results_PRIVATE.json');index={r['case_id']:r for r in plan['selection']}
    crops=parents=finals=0;native_counts=[];sides=[]
    for r in result['records']:
        folder=PARENT/r['case_id'];source=cv2.imread(r['source_path']);initial=index[r['case_id']]
        for k,v in initial.items():assert r[k]==v
        assert sha(Path(r['source_path']))==r['source_sha256']==sha(folder/'source.jpeg')
        assert not r['calibration_admitted'] and not r['training_admitted'] and r['MST'] is None
        if 'input_bridge' in r:
            bridge=r['input_bridge'];x,y,w,h=bridge['source256_face_box'];side=int(np.ceil(1.5*max(w,h)*224/256))
            left=min(max(int(np.floor((x+w/2)*224/256-side/2)),0),224-side)
            top=min(max(int(np.floor((y+h/2)*224/256-side/2)),0),224-side)
            assert bridge['native_bounds']==[left,top,left+side,top+side]
            native=cv2.imread(str(folder/'native_crop.png'));assert np.array_equal(source[top:top+side,left:left+side],native)
            image=cv2.imread(str(folder/'input.png'));assert np.array_equal(image,cv2.resize(native,(256,256),interpolation=cv2.INTER_LINEAR));crops+=1;sides.append(side)
        if r.get('parent_report',{}).get('status')=='success':
            assert np.array_equal(parser_input(image),cv2.imread(str(folder/'parser_input.png')))
            points=np.load(folder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
            expected_mask=build_semantic_face_coverage(image,points,categories).mask.copy();expected_mask[nostril_guard((256,256),points)]=0
            parent=cv2.imread(str(folder/'parent_mask.png'),0);assert np.array_equal(parent,expected_mask)
            assert compute_masked_lab_statistics(image,parent,1000)==r['parent_report']['statistics'];parents+=1
        if 'measurement_report' in r:
            aligned=cv2.imread(str(folder/'aligned_original.png'));assert np.array_equal(parser_input(aligned),cv2.imread(str(folder/'aligned_candidate.png')))
            logits=np.load(PARENT/r['logits_path'],allow_pickle=False);assert sha(PARENT/r['logits_path'])==r['logits_sha256']
            M=np.array(read(folder/'matrix.json'))
            valid=cv2.warpAffine(np.full((256,256),255,np.uint8),M,(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            positive=np.where((logits>0)&(valid>0),255,0).astype(np.uint8)
            inverse=cv2.warpAffine(positive,cv2.invertAffineTransform(M),(256,256),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
            expected_mask=np.where((parent>0)&(inverse>0),255,0).astype(np.uint8)
            mask=cv2.imread(str(folder/'measurement_mask.png'),0);assert np.array_equal(mask,expected_mask)
            assert compute_masked_lab_statistics(image,mask,1000)==r['measurement_report']['statistics'];finals+=1
            native=np.zeros((224,224),np.uint8);native[top:top+side,left:left+side]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
            assert np.array_equal(native,cv2.imread(str(folder/'native_grid.png'),0))
            assert int(np.count_nonzero(native))==r['native_accounting']['selected_native_grid_locations']
            if r['status']=='success':native_counts.append(int(np.count_nonzero(native)))
    assert len(result['records'])==30 and len(index)==30
    assert sum(r['status']=='success' for r in result['records'])==result['summary']['final_successes']
    assert all(sha(p)==h for p,h in bound.items())
    report=dict(source_and_decimal_memberships=30,new_subject_keys_disjoint=10,selection_hash_order_verified=True,
        native_crop_and_original_input_checks=crops,parent_original_statistics_and_semantic_replays=parents,
        manual_final_mapping_statistics_native_checks=finals,native_crop_side_range=[min(sides),max(sides)],
        successful_native_grid_range=[min(native_counts),max(native_counts)] if native_counts else None,
        new_forwards=0,new_fits=0,admissions=0,parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    OUT.mkdir();(OUT/'verification_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'verification_PRIVATE.json':sha(OUT/'verification_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
