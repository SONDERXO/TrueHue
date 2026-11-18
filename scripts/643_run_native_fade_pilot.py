"""Fixed four-condition native fade pilot, no fits or inference."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from src.model_training.blended_recovery_targets import render_rgb8
from src.model_training.photographic_target_diagnostic import metrics
OUT=ROOT/'outputs/native_inward_fade_pilot_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve pilot')
    bound={}
    def bind(p):
        p=Path(p);bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p
    def read(p):return json.loads(bind(p).read_text())
    def rgb(p):return cv2.cvtColor(cv2.imread(str(bind(p))),cv2.COLOR_BGR2RGB)
    diagnosis=read(ROOT/'outputs/restored_mask_boundary_diagnosis_v1/diagnosis_PRIVATE.json')
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    ev={r['case_id']:r for r in read(ROOT/'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')['records']}
    OUT.mkdir();records=[]
    def edges(alpha,output,image):
        residual=output.astype(float)-image.astype(float);jumps=0;values=[]
        for axis in (0,1):
            jumps+=int((np.abs(np.diff(alpha,axis=axis))>=.5).sum())
            a=np.take(alpha,range(alpha.shape[axis]-1),axis=axis);b=np.take(alpha,range(1,alpha.shape[axis]),axis=axis)
            boundary=(a>0)!=(b>0);v=np.abs(np.diff(residual,axis=axis)).mean(axis=2);values.extend(v[boundary].tolist())
        return dict(alpha_jumps_at_least_half=jumps,support_boundary_residual_MAE=float(np.mean(values)),support_boundary_residual_max=float(max(values)))
    for item in diagnosis['records']:
        cid=item['case_id'];r=prep[cid];e=ev[cid];alpha=np.load(bind(r['alpha_path']));guard=cv2.imread(str(bind(r['protected_path'])),0)>0
        support=(alpha>0)&~guard;dist=cv2.distanceTransform(np.pad(support.astype(np.uint8),1),cv2.DIST_L2,cv2.DIST_MASK_PRECISE)[1:-1,1:-1]
        t=np.clip(dist/3.,0,1).astype(float);new=np.minimum(alpha,t*t*(3-2*t));new[~support]=0;new[guard]=0
        image=rgb(r['scene_path']);ref=rgb(r['reference_path']);old=rgb(e['output_path']);out=render_rgb8(image,new,e['candidate']['parameters'])
        assert (new<=alpha).all() and np.array_equal(out[guard|~support],image[guard|~support])
        scoring=cv2.imread(str(bind(r['scoring_path'])),0)>0
        folder=OUT/cid;folder.mkdir();np.save(folder/'alpha.npy',new);cv2.imwrite(str(folder/'output.png'),cv2.cvtColor(out,cv2.COLOR_RGB2BGR))
        l,top,right,bottom=r['input_bridge']['native_bounds']
        def row(arrays,zoom=False):
            panels=[]
            for a in arrays:
                if zoom:a=cv2.resize(a[top:bottom,l:right],(224,224),interpolation=cv2.INTER_NEAREST)
                panels.append(a)
            return np.hstack(panels)
        title=np.full((28,896,3),255,np.uint8);cv2.putText(title,cid+' ref|input|old blend|native fade',(3,19),cv2.FONT_HERSHEY_SIMPLEX,.42,(0,0,0),1)
        board=np.vstack([title,row([ref,image,old,out]),row([ref,image,old,out],True)])
        cv2.imwrite(str(folder/'board.png'),cv2.cvtColor(board,cv2.COLOR_RGB2BGR))
        records.append(dict(case_id=cid,parameters=e['candidate']['parameters'],old_alpha_path=r['alpha_path'],new_alpha_path=str(folder/'alpha.npy'),output_path=str(folder/'output.png'),board=str(folder/'board.png'),
            old_edges=edges(alpha,old,image),new_edges=edges(new,out,image),old_partial=int(((alpha>0)&(alpha<1)).sum()),new_partial=int(((new>0)&(new<1)).sum()),positive_support=int(support.sum()),
            old_metrics=metrics(old,ref,scoring),new_metrics=metrics(out,ref,scoring)))
    for p in (Path(__file__),ROOT/'docs/native-inward-fade-pilot-protocol-2026-11-08.md',ROOT/'src/model_training/blended_recovery_targets.py'):bind(p)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in bound.items())
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(records=records,input_sha256=bound,new_fits=0,new_inference=0,holdout_image_reads=0),indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
