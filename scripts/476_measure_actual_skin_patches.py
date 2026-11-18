"""Actual user patch reference: strict import, native measurements and mask overlap."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.evaluation.skin_patch_review import validate_export,rasterize
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
REVIEW=ROOT/'outputs/stellenbosch_skin_patch_review_v2'
OUT=ROOT/'outputs/stellenbosch_skin_patch_import_v2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():raise FileExistsError(OUT)
    actual=REVIEW/'truehue_skin_patch_review.json';manifest=read(REVIEW/'manifest.json')
    rows=validate_export(read(actual),manifest,sha(REVIEW/'manifest.json'))
    bound={str(actual):sha(actual)}
    for package in [REVIEW,ROOT/'outputs/stellenbosch_new_subjects_v1',ROOT/'outputs/resnet34_parser_comparison_v1']:
        bound.update({str(package/p):h for p,h in read(package/'sha256.json').items()})
    bindings=read(ROOT/'outputs/stellenbosch_reference_points_v1/prediction_bindings_PRIVATE.json')
    for b in bindings.values():bound[b['source_path']]=b['source_sha256']
    for rel in ['scripts/476_measure_actual_skin_patches.py','src/evaluation/skin_patch_review.py','src/ita_estimation/compute_ita.py']:
        bound[str(ROOT/rel)]=sha(ROOT/rel)
    assert all(sha(Path(p))==h for p,h in bound.items())
    OUT.mkdir();(OUT/'actual_export_PRIVATE.json').write_bytes(actual.read_bytes())
    records=[];boards=[]
    totals=dict(images=len(rows),marked=0,unavailable=0,polygons=0,native_patch_pixels=0)
    for row in rows:
        key=row['review_id'];b=bindings[key];image=cv2.imread(str(REVIEW/(key+'.png')))
        h,w=image.shape[:2];mask=rasterize(row['polygons'],w,h);patch=mask>0
        count=int(patch.sum());totals['polygons']+=len(row['polygons']);totals['native_patch_pixels']+=count;totals[row['status']]+=1
        cv2.imwrite(str(OUT/(key+'_patch.png')),mask)
        stats=compute_masked_lab_statistics(image,mask,minimum_skin_pixels=1)
        panels=[image.copy(),image.copy()];panels[1][patch]=(panels[1][patch]*.6+np.array([0,255,0])*.4).astype(np.uint8)
        models={}
        for name,path in [('baseline',Path(b['native_grid_path']) if b['native_grid_path'] else None),
            ('resnet34',ROOT/'outputs/resnet34_parser_comparison_v1'/key/'native_grid.png')]:
            if path is None or not path.exists():
                models[name]=dict(status='unavailable',patch_pixels=count,patch_selected=None,statistics=None)
                panels.append(np.zeros_like(image));continue
            full=cv2.imread(str(path),0);x0,y0,x1,y1=b['native_bounds'];prediction=full[y0:y1,x0:x1]>0
            assert prediction.shape==patch.shape
            overlap=int((prediction&patch).sum())
            models[name]=dict(status='available',patch_pixels=count,patch_selected=overlap,
                patch_selection_fraction=overlap/count if count else None,
                selected_native_pixels=int(prediction.sum()),statistics=compute_masked_lab_statistics(image,prediction.astype(np.uint8)*255,minimum_skin_pixels=1),
                overlap_statistics=compute_masked_lab_statistics(image,(prediction&patch).astype(np.uint8)*255,minimum_skin_pixels=1))
            panel=image.copy();panel[prediction]=(panel[prediction]*.6+np.array([255,180,0])*.4).astype(np.uint8);panels.append(panel)
        records.append(dict(review_id=key,status=row['status'],notes=row['notes'],polygons=len(row['polygons']),
            native_patch_pixels=count,patch_statistics=stats,models=models,admitted=False))
        board=np.concatenate([cv2.resize(p,(240,240),interpolation=cv2.INTER_NEAREST) for p in panels],axis=1)
        title=np.full((35,960,3),255,np.uint8);cv2.putText(title,key+' | original | user patches | baseline | ResNet34',(5,24),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,0,0),1)
        board=np.concatenate([title,board]);cv2.imwrite(str(OUT/(key+'_board.png')),board);boards.append(board)
    aggregate={}
    for name in ['baseline','resnet34']:
        available=[r for r in records if r['status']=='marked' and r['models'][name]['status']=='available']
        denominator=sum(r['native_patch_pixels'] for r in available);selected=sum(r['models'][name]['patch_selected'] for r in available)
        aggregate[name]=dict(paired_images=len(available),patch_pixels=denominator,selected=selected,fraction=selected/denominator if denominator else None)
    result=dict(actual_export_sha256=sha(actual),manifest_sha256=sha(REVIEW/'manifest.json'),totals=totals,aggregate=aggregate,records=records,
        contract=dict(coordinates='native original crop',raster='OpenCV fillPoly integer vertices including boundary; polygon union',statistics='retained original BGR OpenCV Lab/ITA',minimum_pixel_admission_rule=None,arithmetic_minimum_pixels=1,manual_reference_only=True),
        limitation='Exposed reviewer-selected patches, not full-face truth/independent accuracy/admission; native pixels not independent samples.')
    (OUT/'results_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    cv2.imwrite(str(OUT/'all_boards_PRIVATE.png'),np.concatenate(boards))
    assert all(sha(Path(p))==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir()},indent=2),encoding='utf-8')
    print(json.dumps(dict(totals=totals,aggregate=aggregate),indent=2))


if __name__=='__main__':main()
