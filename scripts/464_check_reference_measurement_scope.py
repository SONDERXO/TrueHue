"""Keep all user marks; separately describe the face-only geometry scope."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
PRIOR=ROOT/'outputs/stellenbosch_actual_reference_assessment_v1'
SOURCE=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/stellenbosch_reference_scope_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound={}
    for root in [IMPORTED,PRIOR,REVIEW]:bound.update({str(root/p):h for p,h in read(root/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    bindings=read(REVIEW/'prediction_bindings_PRIVATE.json');rows=read(IMPORTED/'actual_export_PRIVATE.json')['rows']
    counts=Counter();details=[]
    for row in rows:
        binding=bindings[row['review_id']]
        if binding['native_grid_path'] is None:continue
        folder=SOURCE/binding['case_id'];image=cv2.imread(str(folder/'input.png'));points=np.load(folder/'landmarks.npy',allow_pickle=False)
        outline=build_face_coverage(image,points).face_outline
        x0,y0,x1,y1=binding['native_bounds'];outline=cv2.resize(outline,(x1-x0,y1-y0),interpolation=cv2.INTER_NEAREST)>0
        final=cv2.imread(binding['native_grid_path'],0)[y0:y1,x0:x1]>0
        for p in row['points']:
            if p['label']!='skin':continue
            inside=bool(outline[p['y'],p['x']]);selected=bool(final[p['y'],p['x']]);prefix='inside_geometric_face' if inside else 'outside_geometric_face'
            counts[prefix+'_skin_points']+=1;counts[prefix+'_selected']+=selected
            details.append(dict(review_id=row['review_id'],**p,inside_geometric_face=inside,predicted_selected=selected))
    assert sum(counts[k] for k in ['inside_geometric_face_skin_points','outside_geometric_face_skin_points'])==113
    assert counts['inside_geometric_face_selected']+counts['outside_geometric_face_selected']==54
    report=dict(counts,geometry_subset_is_not_new_skin_truth=True,original_all_point_summary_preserved=True,
        observation='Actual point overlays include neck skin; measurement is face-only. Outside-oval points also include uncertain contour mapping and must not all be called neck.',
        new_forwards=0,new_fits=0,admissions=0,actual_export_sha256=sha(IMPORTED/'actual_export_PRIVATE.json'),script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'scope_PRIVATE.json').write_text(json.dumps(dict(summary=report,points=details),indent=2),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({'scope_PRIVATE.json':sha(OUT/'scope_PRIVATE.json')},indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
