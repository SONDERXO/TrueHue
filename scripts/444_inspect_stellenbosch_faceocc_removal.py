"""Saved FaceOcc removal boards and exact domain/model loss decomposition."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from scipy.io import loadmat
from src.skin_masking.faceocc_mediapipe_bridge import align_input
from src.skin_masking.faceocc_coordinates import map_visible_mask

BASE=ROOT/'outputs/stellenbosch_face_crop_v1'
PARENT=ROOT/'outputs/stellenbosch_parser_appearance_v1'
OUT=ROOT/'outputs/stellenbosch_faceocc_removal_v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def overlay(image,mask,color):
    result=image.copy();result[mask]=np.rint(.6*image[mask]+.4*np.array(color)).astype(np.uint8);return result

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for p in [Path(__file__),ROOT/'docs/stellenbosch-faceocc-removal-protocol-2026-11-05.md']:
        bound[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    template=loadmat(ROOT/'models/faceocc_candidate_v1/similarity_Lm3D_all.mat')['lm']
    records=[];boards=[]
    for row in read(PARENT/'results_PRIVATE.json')['records']:
        case=row['case_id'];folder=PARENT/case;source=BASE/case;image=cv2.imread(str(source/'input.png'))
        rec=dict(case_id=case,subject_key=row['subject_key'],condition=row['condition'],source_mst_exact_decimal=row['source_mst_exact_decimal'],
            final_status=row['status'],available='measurement_report' in row,admitted=False)
        empty=np.zeros(image.shape[:2],bool);parent=kept=removed=empty;model_panel=np.full_like(image,35)
        if rec['available']:
            points=np.load(source/'landmarks.npy',allow_pickle=False)
            aligned,matrix,_=align_input(image,points,template)
            assert np.array_equal(aligned,cv2.imread(str(folder/'aligned.png')))
            assert sha(row['logits_path'])==row['logits_sha256']
            logits=np.load(row['logits_path'],allow_pickle=False)
            prediction=(logits>0).astype(np.uint8)*255
            visible=map_visible_mask(prediction,image.shape[:2],matrix)>0
            coverage=map_visible_mask(np.full((256,256),255,np.uint8),image.shape[:2],matrix)>0
            parent=cv2.imread(str(folder/'parent_mask.png'),0)>0
            kept=parent&visible;removed=parent&~visible
            assert np.array_equal(kept,cv2.imread(str(folder/'measurement_mask.png'),0)>0)
            domain_loss=parent&~coverage;model_loss=removed&coverage
            assert np.array_equal(removed,domain_loss|model_loss) and not (domain_loss&model_loss).any()
            assert np.array_equal(parent,kept|removed) and not (kept&removed).any()
            rec.update(parent_pixels=int(parent.sum()),kept_pixels=int(kept.sum()),removed_pixels=int(removed.sum()),
                mapping_domain_loss=int(domain_loss.sum()),model_prediction_loss=int(model_loss.sum()),
                retained_fraction=float(kept.sum()/parent.sum()),aligned_positive_pixels=int(np.count_nonzero(prediction)))
            model_panel=overlay(aligned,prediction>0,[0,255,0])
            for name,mask in [('parent',parent),('kept',kept),('removed',removed),('mapping_loss',domain_loss),('model_loss',model_loss)]:
                assert cv2.imwrite(str(OUT/(case+'_'+name+'.png')),mask.astype(np.uint8)*255)
        else:rec['reason']=row.get('reason') or row['parent_report'].get('reason')
        panels=[image,overlay(image,parent,[0,255,0]),overlay(image,kept,[0,255,0]),overlay(image,removed,[0,0,255]),model_panel]
        label=np.full((26,1280,3),255,np.uint8)
        cv2.putText(label,case+' '+row['condition']+' '+('available '+row['status'] if rec['available'] else 'UNAVAILABLE parent/detector'),(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,np.hstack(panels)]));records.append(rec)
    for i in range(10):assert cv2.imwrite(str(OUT/f'contact_{i+1:02d}.png'),np.vstack(boards[3*i:3*i+3]))
    available=[r for r in records if r['available']]
    summary=dict(attempts=len(records),available=len(available),unavailable=len(records)-len(available),
        exact_alignment_and_mask_replays=len(available),
        **{name:sum(r[name] for r in available) for name in ['parent_pixels','kept_pixels','removed_pixels','mapping_domain_loss','model_prediction_loss']},
        empty_final_masks=sum(r['kept_pixels']==0 for r in available),new_forwards=0,new_fits=0,admissions=0)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private FaceOcc removal inspection</h1><p>Original; parent green; kept green; removed red; aligned original/model positives green. Red means removed, not certified skin. Unavailable stages are labelled. Research only; no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
