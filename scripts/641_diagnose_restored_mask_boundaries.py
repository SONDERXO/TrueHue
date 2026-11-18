"""Four fixed restored cases: saved mask/projection/blend diagnosis, no inference."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/restored_mask_boundary_diagnosis_v1'
def main():
    if OUT.exists():raise FileExistsError('Preserve diagnosis')
    bound={}
    def bind(p):
        p=Path(p);bound[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return p
    def read(p):return json.loads(bind(p).read_text())
    def load(p):return np.load(bind(p),allow_pickle=False)
    def im(p,gray=False):return cv2.imread(str(bind(p)),0 if gray else 1)
    model=read(ROOT/'outputs/facial_veto_exception_models_v1/models_PRIVATE.json')
    ids=[t['case_id'] for t in model['exception_trace'] if t['restored']];assert len(ids)==4
    prep={r['case_id']:r for r in read(ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json')['records']}
    evaluation={r['case_id']:r for r in read(ROOT/'outputs/facial_veto_exception_comparison_v1/results_PRIVATE.json')['records']}
    OUT.mkdir();records=[]
    def panel(a,label,heat=False):
        if a.ndim==2:a=cv2.applyColorMap(np.uint8(np.clip(a,0,1)*255),cv2.COLORMAP_VIRIDIS) if heat else cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)
        a=cv2.resize(a,(256,256),interpolation=cv2.INTER_NEAREST);title=np.full((28,256,3),255,np.uint8);cv2.putText(title,label,(3,19),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);return np.vstack([title,a])
    def components(a):
        n,_,stats,_=cv2.connectedComponentsWithStats(a.astype(np.uint8),8);return sorted(stats[1:,cv2.CC_STAT_AREA].astype(int).tolist(),reverse=True)
    for cid in ids:
        r=prep[cid];folder=Path(r['alpha_path']).parent;alpha=load(r['alpha_path']);norm=load(folder/'correction_alpha_normalized.npy');support=im(folder/'correction_mask_normalized.png',True)>0;guard=im(r['protected_path'],True)>0
        ng=im(folder/'protected_normalized.png',True)>0;parent=im(folder/'parent_mask.png',True);visible=im(folder/'visible_face.png',True);inputnorm=im(folder/'input.png')
        left,top,right,bottom=r['input_bridge']['native_bounds'];raw=cv2.resize(norm,(right-left,bottom-top),interpolation=cv2.INTER_LINEAR);g=guard[top:bottom,left:right];local=alpha[top:bottom,left:right]
        expected=raw.copy();expected[g]=0;assert np.array_equal(local,expected) and not alpha[guard].any()
        width=r['correction_report']['blend_report']['edge_width_pixels'];eqwidth=width*(right-left)/256
        edgecounts={}
        for name,a,b,pa,pb in [('horizontal',local[:,:-1],local[:,1:],g[:,:-1],g[:,1:]),('vertical',local[:-1],local[1:],g[:-1],g[1:])]:
            jump=np.abs(a-b)>=.5;edgecounts[name]=dict(jumps_at_least_half=int(jump.sum()),touching_protected=int((jump&(pa|pb)).sum()))
        output=im(evaluation[cid]['output_path'])[top:bottom,left:right]
        panels=[panel(inputnorm,'Actual-input crop'),panel(parent,'Parent facial mask'),panel(support.astype(np.uint8)*255,'Final permitted support'),panel(norm,'Normalized alpha',True),panel(visible,'Predicted visible face'),panel(ng.astype(np.uint8)*255,'Protected pixels'),panel(local,'Native alpha (nearest zoom)',True),panel(output,'Native output (nearest zoom)')]
        board=OUT/(cid+'.png');assert cv2.imwrite(str(board),np.vstack([np.hstack(panels[:4]),np.hstack(panels[4:])]))
        records.append(dict(case_id=cid,source_case=r['source_case'],native_crop_side=right-left,normalized_feather_width=width,native_equivalent_feather_width=eqwidth,
            parent_pixels=int((parent>0).sum()),final_support_pixels=int(support.sum()),normalized_alpha_components=components(norm>0),native_alpha_components=components(local>0),
            native_alpha_pixels=int((local>0).sum()),native_partial_alpha_pixels=int(((local>0)&(local<1)).sum()),
            projected_guard_removes_nonzero_alpha=int(((raw>0)&g).sum()),projected_guard_removes_alpha_at_least_half=int(((raw>=.5)&g).sum()),
            adjacent_alpha_jumps=edgecounts,board=str(board),board_sha256=hashlib.sha256(board.read_bytes()).hexdigest(),
            limitation='Predicted masks are not ground truth; excluded regions may be intentional protection or missed skin. No pixel inclusion accuracy inferred.'))
    for p in [Path(__file__),ROOT/'src/correction/seamless_blend.py',ROOT/'src/model_training/aligned_correction_support.py']:bind(p)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in bound.items())
    result=dict(records=records,input_sha256=bound,new_fits=0,new_inference=0,new_candidate_renders=0,holdout_image_reads=0,selection='All four restored conditions, two originals; fixed before this diagnosis')
    (OUT/'diagnosis_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
