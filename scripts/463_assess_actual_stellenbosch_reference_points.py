"""Independent actual-user sparse-point accounting and stage diagnosis."""
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
REVIEW=ROOT/'outputs/stellenbosch_reference_points_v1'
IMPORTED=ROOT/'outputs/stellenbosch_reference_points_import_v1'
SOURCE=ROOT/'outputs/stellenbosch_new_subjects_v1'
OUT=ROOT/'outputs/stellenbosch_actual_reference_assessment_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(REVIEW/'input_sha256_PRIVATE.json')
    for root in [REVIEW,IMPORTED]:bound.update({str(root/p):h for p,h in read(root/'sha256.json').items()})
    assert all(sha(p)==h for p,h in bound.items())
    actual=read(IMPORTED/'actual_export_PRIVATE.json');comparison=read(IMPORTED/'comparison_PRIVATE.json')
    assert sha(IMPORTED/'actual_export_PRIVATE.json')==comparison['export_sha256']
    bindings=read(REVIEW/'prediction_bindings_PRIVATE.json');source={r['case_id']:r for r in read(SOURCE/'results_PRIVATE.json')['records']}
    totals=Counter();details=[];images=[];boards=[]
    for row in actual['rows']:
        binding=bindings[row['review_id']];folder=SOURCE/binding['case_id'];rec=source[binding['case_id']]
        native=cv2.imread(binding['native_crop_path']);height,width=native.shape[:2]
        masks=None;counts=Counter()
        if binding['native_grid_path'] is not None:
            x0,y0,x1,y1=binding['native_bounds'];grid=cv2.imread(binding['native_grid_path'],0)
            final=grid[y0:y1,x0:x1]>0
            parent=cv2.resize(cv2.imread(str(folder/'parent_mask.png'),0),(width,height),interpolation=cv2.INTER_NEAREST)>0
            points=np.load(folder/'landmarks.npy',allow_pickle=False);image=cv2.imread(str(folder/'input.png'))
            geometry=build_face_coverage(image,points)
            excluded=(geometry.exclusion_mask>0)|nostril_guard((256,256),points)
            excluded=cv2.resize(excluded.astype(np.uint8),(width,height),interpolation=cv2.INTER_NEAREST)>0
            masks=(parent,final,excluded)
        for p in row['points']:
            label=p['label'];x,y=p['x'],p['y'];totals['points']+=1;counts[label+'_points']+=1
            selected=None if masks is None else bool(masks[1][y,x]);parent_selected=None if masks is None else bool(masks[0][y,x])
            stage='uncertain_excluded' if label=='uncertain' else 'prediction_unavailable' if masks is None else 'included' if selected else 'removed_by_faceocc' if parent_selected else 'parent_anatomical_exclusion' if masks[2][y,x] else 'not_selected_by_parent_other'
            if label!='uncertain':
                if masks is None:totals['definite_unavailable']+=1;counts['definite_unavailable']+=1
                else:
                    kind='skin' if label=='skin' else 'unwanted'
                    totals[kind+'_available']+=1;totals[kind+'_selected']+=selected
                    counts[kind+'_available']+=1;counts[kind+'_selected']+=selected
                    if label=='skin' and not selected:totals[stage]+=1;counts[stage]+=1
                    if label!='skin' and selected:totals[label+'_selected']+=1
            else:totals['uncertain_excluded']+=1
            details.append(dict(review_id=row['review_id'],**p,parent_selected=parent_selected,final_selected=selected,stage=stage,admitted=False))
        images.append(dict(review_id=row['review_id'],case_id=binding['case_id'],review_status=row['status'],notes=row['notes'],prediction_available=masks is not None,counts=dict(counts)))
        original=cv2.resize(native,(512,512),interpolation=cv2.INTER_NEAREST)
        selected_panel=original.copy();point_panel=original.copy()
        if masks is not None:
            enlarged=cv2.resize(masks[1].astype(np.uint8),(512,512),interpolation=cv2.INTER_NEAREST)>0
            selected_panel[enlarged]=np.rint(.6*original[enlarged]+.4*np.array([0,255,0])).astype(np.uint8)
        else:selected_panel[:]=35
        colours={'skin':(0,255,0),'hair_or_beard':(0,220,255),'object_or_other':(255,0,255),'uncertain':(255,255,0)}
        for p in row['points']:
            xy=(int((p['x']+.5)*512/width),int((p['y']+.5)*512/height))
            cv2.circle(point_panel,xy,5,(0,0,0),3);cv2.circle(point_panel,xy,5,colours[p['label']],1)
        title=np.full((28,1536,3),255,np.uint8)
        cv2.putText(title,row['review_id']+' original | frozen final mask '+('available' if masks is not None else 'UNAVAILABLE')+' | actual user points',(5,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(0,0,0),1)
        boards.append((row['review_id'],np.vstack([title,np.hstack([original,selected_panel,point_panel])])))
    summary=dict(totals)
    for key in ['points','skin_available','skin_selected','unwanted_available','unwanted_selected','definite_unavailable']:
        assert summary[key]==comparison['summary'][key]
    assert totals['skin_available']-totals['skin_selected']==sum(totals[k] for k in ['removed_by_faceocc','parent_anatomical_exclusion','not_selected_by_parent_other'])
    summary.update(images=6,skin_point_inclusion=totals['skin_selected']/totals['skin_available'],unwanted_point_inclusion=totals['unwanted_selected']/totals['unwanted_available'],
        actual_export_sha256=comparison['export_sha256'],manifest_sha256=comparison['manifest_sha256'],
        reviewer='actual_user_export_not_assistant_annotations',independent_or_blinded=False,
        segmentation_accuracy=False,whole_mask_truth=False,calibration_admissions=0,new_forwards=0,new_fits=0,
        decision='reference_points_show_skin_omission_and_some_unwanted_inclusion_no_calibration_admission',script_sha256=sha(__file__))
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir()
    for name,board in boards:assert cv2.imwrite(str(OUT/(name+'.png')),board)
    (OUT/'assessment_PRIVATE.json').write_text(json.dumps(dict(summary=summary,images=images,points=details),indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Actual user point comparison · private</h1><p>Original native zoom; frozen final mask; actual user points (skin green, hair/beard yellow, object pink). Not added detail or dense truth. Failed prediction unavailable. No redistribution.</p>'+''.join(f'<img style="max-width:100%" src="{name}.png">' for name,_ in boards),encoding='utf-8')
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(dict(summary=summary,images=images),indent=2))

if __name__=='__main__':main()
