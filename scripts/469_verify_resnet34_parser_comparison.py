"""Independent saved parser/mask/original-statistic/user-point verification."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.skin_masking.segmentation_appearance_probe import parser_input
from src.skin_masking.faceocc_coordinates import map_visible_mask
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
PARENT=ROOT/'outputs/resnet34_parser_comparison_v1'
SOURCE=ROOT/'outputs/stellenbosch_new_subjects_v1'
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
OUT=ROOT/'outputs/resnet34_parser_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'input_sha256_PRIVATE.json');bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    result=read(PARENT/'results_PRIVATE.json');source={r['case_id']:r for r in read(SOURCE/'results_PRIVATE.json')['records']}
    bindings=read(REVIEW/'prediction_bindings_PRIVATE.json');actual=read(IMPORTED/'actual_export_PRIVATE.json')
    counts=Counter();percase=[];stage_counts=defaultdict(Counter);checks=0
    for r in result['records']:
        folder=SOURCE/r['case_id'];target=PARENT/r['review_id'];image=cv2.imread(str(folder/'input.png'))
        assert np.array_equal(parser_input(image),cv2.imread(str(target/'parser_input.png')))
        categories=cv2.imread(str(target/'categories.png'),0)
        assert categories.shape==(256,256) and categories.dtype==np.uint8 and categories.max()<=18
        if r['case_id']=='case_29':
            assert r['status']=='failed' and not (target/'measurement_mask.png').exists();continue
        points=np.load(folder/'landmarks.npy',allow_pickle=False)
        parent=build_semantic_face_coverage(image,points,categories).mask.copy();parent[nostril_guard((256,256),points)]=0
        assert np.array_equal(parent,cv2.imread(str(target/'parent_mask.png'),0))
        assert compute_masked_lab_statistics(image,parent,1000)==r['parent_statistics']
        original=source[r['case_id']];logits=np.load(SOURCE/original['logits_path'],allow_pickle=False);M=np.array(read(folder/'matrix.json'))
        visible=map_visible_mask(np.where(logits>0,255,0).astype(np.uint8),(256,256),M)>0
        expected=(parent>0)&visible;mask=cv2.imread(str(target/'measurement_mask.png'),0)
        assert np.array_equal(mask>0,expected)
        assert compute_masked_lab_statistics(image,mask,1000)==r['measurement_report']['statistics'];checks+=1
        binding=bindings[r['review_id']];x0,y0,x1,y1=binding['native_bounds'];side=x1-x0
        grid=np.zeros((224,224),np.uint8);grid[y0:y1,x0:x1]=cv2.resize(mask,(side,side),interpolation=cv2.INTER_NEAREST)
        assert np.array_equal(grid,cv2.imread(str(target/'native_grid.png'),0))
        prediction=grid[y0:y1,x0:x1]>0;cell=Counter()
        row=next(a for a in actual['rows'] if a['review_id']==r['review_id'])
        for p in row['points']:
            if p['label']=='uncertain':continue
            sel=bool(prediction[p['y'],p['x']]);kind='skin' if p['label']=='skin' else 'unwanted'
            counts[kind+'_available']+=1;counts[kind+'_selected']+=sel;cell[kind+'_available']+=1;cell[kind+'_selected']+=sel
            if kind=='unwanted' and sel:counts[p['label']+'_selected']+=1
        percase.append(dict(review_id=r['review_id'],counts=dict(cell)))
    for k in ['skin_available','skin_selected','unwanted_available','unwanted_selected']:
        assert counts[k]==result['summary']['alternative_actual_points'][k]
    for p in read(PARENT/'parser_stage_points_PRIVATE.json'):
        if p['label']=='uncertain':continue
        kind='skin' if p['label']=='skin' else 'unwanted'
        if p['baseline_parser_skin_nose'] is not None:
            stage_counts['same_five_available_baseline_parser'][kind+'_points']+=1
            stage_counts['same_five_available_baseline_parser'][kind+'_selected']+=p['baseline_parser_skin_nose']
            stage_counts['same_five_alternative_parser'][kind+'_points']+=1
            stage_counts['same_five_alternative_parser'][kind+'_selected']+=p['alternative_parser_skin_nose']
    report=dict(cases=6,exact_transformed_inputs=6,category_maps_checked=6,semantic_final_statistics_native_replays=checks,
        actual_point_counts=dict(counts),per_case_PRIVATE=percase,parser_only_paired_point_counts={k:dict(v) for k,v in stage_counts.items()},
        all6boards_assistant_inspected=True,
        visual_findings='Glasses example gains broad cheek/chin and some forehead support but fine frames/reflection remain uncertain. Beard example gains central support while beard material is included. Dim forehead case remains sparse with new isolated patches. Warm dim case gains broad facial coverage; control changes mainly at chin/boundary. Landmark failure stays unavailable.',
        decision='retain_coverage_gain_but_do_not_adopt_due_to_worse_unwanted_inclusion_and_missing_beard_class',
        same_BiSeNet_family_not_architecture_independent=True,new_forwards=0,new_fits=0,admissions=0,
        parent_manifest_sha256=sha(PARENT/'sha256.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'assessment_PRIVATE.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'assessment_PRIVATE.json':sha(OUT/'assessment_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if 'PRIVATE' not in k},indent=2))

if __name__=='__main__':main()
