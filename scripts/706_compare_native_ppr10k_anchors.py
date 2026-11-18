"""One native-size YuNet call per frozen PPR source; detector only."""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np,tifffile
from PIL import ImageCms
from src.utilities.config import get_config
BASE=ROOT/'outputs/ppr10k_new_group_comparison_v1'
OLD=ROOT/'outputs/ppr10k_automatic_support_v1'
OUT=ROOT/'outputs/ppr10k_native_anchor_comparison_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False),encoding='utf-8')
def save(p,a):
    if not cv2.imwrite(str(p),a):raise IOError(str(p))

def main():
    if OUT.exists():raise FileExistsError('Preserve partial/completed native comparison')
    bound={}
    def bind(p):bound[str(p)]=sha(p)
    sample=read(BASE/'frozen_sample.json');audit=read(BASE/'image_audit.json')
    prior=read(OLD/'results_PRIVATE.json');verification=read(OLD/'verification_PRIVATE.json')
    assert verification['passed'] and verification['results_sha256']==sha(OLD/'results_PRIVATE.json')
    oldplan=read(OLD/'plan_PRIVATE.json');model=(ROOT/get_config().FACE_MODEL_PATH).resolve()
    assert model.is_file() and sha(model)==oldplan['input_sha256'][str(model)]
    bind(model);images={};regions=read(BASE/'source_regions.json')
    oldrows={r['frame']:r for r in prior['records']}
    for frame in sample['frames']:
        a=next(r for r in audit if r['frame']==frame and r['role']=='source')
        p=BASE/a['file'];assert sha(p)==a['sha256'];bind(p)
        rgb=tifffile.imread(p);assert list(rgb.shape)==a['shape'] and str(rgb.dtype)==a['dtype']=='uint16'
        with tifffile.TiffFile(p) as tf:icc=tf.pages[0].tags[34675].value
        assert hashlib.sha256(icc).hexdigest()==a['icc_sha256']
        assert 'sRGB' in ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(BytesIO(icc)))
        images[frame]=cv2.cvtColor(np.rint(rgb.astype(float)/257).astype(np.uint8),cv2.COLOR_RGB2BGR)
    for p in [Path(__file__),ROOT/'src/face_detection/detect_faces.py',
              ROOT/'docs/ppr10k-native-anchor-comparison-protocol-2026-11-09.md',
              BASE/'frozen_sample.json',BASE/'image_audit.json',BASE/'source_regions.json',
              OLD/'results_PRIVATE.json',OLD/'verification_PRIVATE.json',OLD/'plan_PRIVATE.json']:
        bind(p)
    OUT.mkdir();write(OUT/'plan_PRIVATE.json',dict(frames=sample['frames'],model=str(model),
        threshold=.85,nms=.3,topK=5000,input='native RGB16 round(/257) to BGR8',
        opencv_version=cv2.__version__,input_sha256=bound,maximum_detector_forwards=8))
    rows=[];calls=0
    try:
        for frame in sample['frames']:
            image=images[frame];h,w=image.shape[:2];folder=OUT/frame;folder.mkdir()
            # Marker precedes the only call; never retry on a partial run.
            write(folder/'started_PRIVATE.json',dict(frame=frame,input_shape=list(image.shape)))
            detector=cv2.FaceDetectorYN.create(str(model),'',(w,h),.85,.3,5000)
            calls+=1;retval,faces=detector.detect(image)
            raw=[] if faces is None else faces.tolist();boxes=[];scores=[]
            if faces is not None:
                assert faces.ndim==2 and faces.shape[1]==15 and np.isfinite(faces).all()
                for face in faces:
                    if face[14]<.85:continue
                    x,y,bw,bh=face[:4].astype(int)
                    x=max(0,min(x,w));y=max(0,min(y,h))
                    bw=max(1,min(bw,w-x));bh=max(1,min(bh,h-y))
                    boxes.append([int(x),int(y),int(bw),int(bh)]);scores.append(float(face[14]))
            ordered=sorted(zip(boxes,scores),key=lambda z:z[0][2]*z[0][3],reverse=True)
            boxes=[x[0] for x in ordered];scores=[x[1] for x in ordered]
            comparator=[[b[0]*w/256,b[1]*h/256,b[2]*w/256,b[3]*h/256] for b in oldrows[frame]['anchors_256']]
            r=dict(frame=frame,shape=list(image.shape),raw_return_value=int(retval),raw_faces=raw,
                candidate_boxes=boxes,candidate_scores=scores,candidate_face_count=len(boxes),
                exactly_one_eligible=len(boxes)==1,previous_boxes_native_display=comparator,
                previous_available=oldrows[frame]['status']=='available',historical_polygon=regions[frame]['polygon'])
            write(folder/'detection_PRIVATE.json',r);rows.append(r)
            shown=image.copy();cv2.polylines(shown,[np.array(regions[frame]['polygon'],np.int32)],True,(0,255,0),1)
            for b in comparator:
                x,y,bw,bh=b;cv2.rectangle(shown,(round(x),round(y)),(round(x+bw),round(y+bh)),(255,255,0),1)
            for b,s in zip(boxes,scores):
                x,y,bw,bh=b;cv2.rectangle(shown,(x,y),(x+bw,y+bh),(0,255,255),2)
                cv2.putText(shown,f'{s:.3f}',(x,max(12,y-3)),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
            save(folder/'overlay.png',shown)
            write(OUT/'progress_PRIVATE.json',dict(completed=len(rows),detector_forwards=calls))
            print(frame,'old',len(comparator),'native',len(boxes),'scores',scores,flush=True)
        assert calls==len(rows)==8 and all(sha(p)==h for p,h in bound.items())
        write(OUT/'results_PRIVATE.json',dict(records=rows,detector_forwards=calls,parser_forwards=0,
            landmarker_calls=0,FaceOcc_forwards=0,new_fits=0,target_reads=0,holdout_reads=0,
            input_sha256=bound,visual_review_pending=True,training_admitted=False))
        write(OUT/'artifact_sha256_PRIVATE.json',{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()})
    except Exception:
        write(OUT/'failure_PRIVATE.json',dict(completed=len(rows),detector_forwards=calls,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
