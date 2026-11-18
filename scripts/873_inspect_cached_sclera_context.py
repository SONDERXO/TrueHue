"""Three frozen exposed cached frames only; no learner or raw-photo access."""
from pathlib import Path
import json,hashlib,math,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.sclera_context import extract_sclera_context
from src.skin_masking.landmark_exclusion import FEATURE_INDICES
OUT=ROOT/'outputs/sclera_context_cached_inspection_v1'
IDS=['16061','29617','54632']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if OUT.exists():raise FileExistsError('Preserve completed/partial inspection')
    parent=ROOT/'outputs/ffhq_mask_support_v1';inventory=json.loads((parent/'sha256.json').read_text())
    files=['docs/sclera-context-cache-inspection-protocol-2026-11-13.md','src/model_training/sclera_context.py',
        'src/skin_masking/landmark_exclusion.py','scripts/873_inspect_cached_sclera_context.py',
        'outputs/sclera_context_generated_v1/verification_PRIVATE.json','outputs/ffhq_mask_support_v1/sha256.json']
    bindings={name:sha(ROOT/name) for name in files}
    for ident in IDS:
        for name in ['input.png','categories.png','landmarks.npy']:
            rel=f'outputs/ffhq_mask_support_v1/{ident}/{name}'
            assert sha(ROOT/rel)==inventory[ident+'/'+name];bindings[rel]=inventory[ident+'/'+name]
    OUT.mkdir();(OUT/'execution_plan_PRIVATE.json').write_text(json.dumps(dict(ordered_sources=IDS,input_sha256=bindings,raw_original_reads=0,models_or_fits=0),indent=2)+'\n')
    records=[];boards=[]
    for ident in IDS:
        folder=parent/ident;image=cv2.imread(str(folder/'input.png'));cat=cv2.imread(str(folder/'categories.png'),0);points=np.load(folder/'landmarks.npy',allow_pickle=False)
        result=extract_sclera_context(image[:,:,::-1].copy(),cat,points);mask=result.pop('mask')
        assert not (mask&~np.isin(cat,[4,5])).any()
        if result['valid']:
            pixels=image[:,:,::-1][mask].tolist();means=[math.fsum(p[j] for p in pixels)/len(pixels) for j in range(3)]
            expected=[1.,math.log((means[0]+1)/(means[1]+1)),math.log((means[2]+1)/(means[1]+1))]
            assert all(math.isclose(a,b,abs_tol=1e-12,rel_tol=1e-12) for a,b in zip(result['features'].values(),expected))
        else:assert not mask.any() and list(result['features'].values())==[0.,0.,0.]
        shown=image.copy();shown[mask]=[0,255,0];crops=[];eyeinfo=[]
        for name,center,ring,label in [('right_eye',468,[469,470,471,472],5),('left_eye',473,[474,475,476,477],4)]:
            contour=points[FEATURE_INDICES[name],:2];binary=np.zeros((256,256),np.uint8);cv2.fillPoly(binary,[np.rint(contour).astype(np.int32)],255)
            eroded=cv2.erode(binary,np.ones((3,3),np.uint8))>0
            info=dict(eye=name,contour_pixels=int((binary>0).sum()),eroded_pixels=int(eroded.sum()),
                categories_inside_eroded={str(k):int((cat[eroded]==k).sum()) for k in np.unique(cat[eroded])})
            if len(points)>=478:
                origin=points[center,:2];radius=math.ceil(float(np.linalg.norm(points[ring,:2]-origin,axis=1).max()))+1
                yy,xx=np.indices((256,256));iris=(xx-origin[0])**2+(yy-origin[1])**2<=radius**2
                info['post_iris_matching_class_pixels']=int((eroded&~iris&(cat==label)).sum());info['iris_guard_radius']=radius
            eyeinfo.append(info)
            x0=max(0,int(np.floor(contour[:,0].min()))-4);x1=min(256,int(np.ceil(contour[:,0].max()))+5)
            y0=max(0,int(np.floor(contour[:,1].min()))-4);y1=min(256,int(np.ceil(contour[:,1].max()))+5)
            crop=np.hstack([image[y0:y1,x0:x1],shown[y0:y1,x0:x1]])
            target=np.full((128,512,3),230,np.uint8)
            if crop.size:
                factor=min(512/crop.shape[1],128/crop.shape[0]);zoom=cv2.resize(crop,None,fx=factor,fy=factor,interpolation=cv2.INTER_NEAREST)
                target[:zoom.shape[0],:zoom.shape[1]]=zoom
            crops.append(target)
        header=np.full((34,512,3),255,np.uint8)
        cv2.putText(header,ident+' available='+str(result['valid'])+' selected='+str(int(mask.sum())),(4,14),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1)
        cv2.putText(header,result['reason'][:65],(4,29),cv2.FONT_HERSHEY_SIMPLEX,.35,(0,0,0),1)
        board=np.vstack([header,np.hstack([image,shown]),*crops]);dest=OUT/ident;dest.mkdir()
        assert cv2.imwrite(str(dest/'inspection.png'),board);assert cv2.imwrite(str(dest/'selected_mask.png'),mask.astype(np.uint8)*255)
        records.append(dict(source_id=ident,landmark_shape=list(points.shape),selected_pixels=int(mask.sum()),result=result,eye_geometry_diagnostics=eyeinfo))
        boards.append(board)
    assert cv2.imwrite(str(OUT/'inspection_all.png'),np.vstack(boards))
    assert all(sha(ROOT/p)==h for p,h in bindings.items())
    (OUT/'records_PRIVATE.json').write_text(json.dumps(records,indent=2)+'\n')
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,sources=3,available=sum(r['result']['valid'] for r in records),
        scalar_and_class_checks_passed=True,input_sha256=bindings,source_hashes_unchanged=True,raw_original_reads=0,
        source_images_loaded=3,categories_loaded=3,landmark_arrays_loaded=3,final_locked_reads=0,fits=0,predictions=0),indent=2)+'\n')
    print(json.dumps(records,indent=2))

if __name__=='__main__':main()
