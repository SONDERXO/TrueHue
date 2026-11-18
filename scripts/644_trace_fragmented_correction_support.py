"""Reconstruct saved support stages and attribute exclusions; no inference or edits."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.skin_masking.full_face_support import build_full_face_support
from src.skin_masking.continuous_correction import continuous_support
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.correction_preview import render_preview
OUT=ROOT/'outputs/fragmented_correction_support_trace_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve trace')
    bound={}
    def bind(p):
        p=Path(p);bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p
    def read(p):return json.loads(bind(p).read_text())
    def image(p):return cv2.imread(str(bind(p)))
    def mask(p):return cv2.imread(str(bind(p)),0)
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    ids=[r['case_id'] for r in read(ROOT/'outputs/restored_mask_boundary_diagnosis_v1/diagnosis_PRIVATE.json')['records']]
    OUT.mkdir();records=[]
    labels={0:'background',6:'glasses',9:'earring',15:'necklace',16:'clothing',17:'hair',18:'hat'}
    for cid in ids:
        r=prep[cid];p=Path(r['alpha_path']).parent;im=image(p/'input.png');parent=mask(p/'parent_mask.png');cats=mask(p/'categories.png');points=np.load(bind(p/'landmarks.npy'));visible=mask(p/'visible_face.png')
        outline=build_face_coverage(im,points).face_outline>0
        initial=build_full_face_support(im,parent,cats,points,face_count=1)
        filled=continuous_support(initial)
        preview=render_preview(im,parent,cats,points,visible,glasses='uncertain',parameters=(1.,1.,1.))
        saved=mask(p/'correction_mask_normalized.png');guard=mask(p/'protected_normalized.png')>0
        assert np.array_equal(saved,preview.support.correction_mask) and np.array_equal(guard,preview.protected)
        a=filled.correction_mask>0;semantic=np.isin(cats,list(labels));occ=(outline|(a&(filled.neck_mask==0)))&(visible==0)
        assert np.array_equal(a&~(semantic|occ),saved>0)
        loss=outline&~(saved>0);reason=np.zeros(outline.shape,np.uint8);reason[outline]=1;reason[outline&semantic&~occ]=2;reason[outline&occ&~semantic]=3;reason[outline&semantic&occ]=4
        palette=np.array([[0,0,0],[80,200,80],[30,30,240],[240,150,30],[220,30,220]],np.uint8);reasonim=palette[reason]
        def panel(a,title):
            if a.ndim==2:a=cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)
            h=np.full((28,256,3),255,np.uint8);cv2.putText(h,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);return np.vstack([h,a])
        board=np.vstack([np.hstack([panel(im,'Saved input'),panel(outline.astype(np.uint8)*255,'Geometric face'),panel(parent,'Measurement parent'),panel(saved,'Final correction')]),np.hstack([panel(semantic.astype(np.uint8)*255,'Semantic hard protection'),panel(visible,'Face visibility prediction'),panel(reasonim,'Green kept/red semantic'),panel(reasonim,'Blue visibility/purple both')])])
        dest=OUT/(cid+'.png');assert cv2.imwrite(str(dest),board)
        records.append(dict(case_id=cid,face_outline_pixels=int(outline.sum()),face_retained=int((outline&(saved>0)).sum()),face_excluded=int(loss.sum()),
            semantic_only=int((outline&semantic&~occ).sum()),visibility_only=int((outline&occ&~semantic).sum()),both=int((outline&semantic&occ).sum()),
            excluded_by_predicted_class={labels[k]:int((outline&(cats==k)).sum()) for k in labels},
            normalized_support_replay_exact=True,board=str(dest)))
    for p in (Path(__file__),ROOT/'src/skin_masking/object_protected_correction.py',ROOT/'src/skin_masking/full_face_support.py'):bind(p)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in bound.items())
    (OUT/'trace_PRIVATE.json').write_text(json.dumps(dict(records=records,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0),indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
