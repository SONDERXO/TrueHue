"""Independent scalar adjacency counts and native projection replay."""
from pathlib import Path
import json,hashlib
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'outputs/restored_mask_boundary_diagnosis_v1';d=json.loads((out/'diagnosis_PRIVATE.json').read_text())
    prep={r['case_id']:r for r in json.loads((ROOT/'outputs/aligned_correction_preparation_v1/results_PRIVATE.json').read_text())['records']}
    pairs=0
    for item in d['records']:
        r=prep[item['case_id']];p=Path(r['alpha_path']).parent;norm=np.load(p/'correction_alpha_normalized.npy');alpha=np.load(r['alpha_path']);g=cv2.imread(r['protected_path'],0)>0;l,t,rr,b=r['input_bridge']['native_bounds'];a=alpha[t:b,l:rr];guard=g[t:b,l:rr]
        expected=cv2.resize(norm,(rr-l,b-t),interpolation=cv2.INTER_LINEAR);raw=expected.copy();expected[guard]=0
        assert np.array_equal(expected,a) and not alpha[g].any()
        assert item['projected_guard_removes_nonzero_alpha']==int(((raw>0)&guard).sum())
        assert item['native_alpha_pixels']==int((a>0).sum()) and item['native_partial_alpha_pixels']==int(((a>0)&(a<1)).sum())
        for name,dy,dx in [('horizontal',0,1),('vertical',1,0)]:
            jumps=touches=0
            for y in range(a.shape[0]-dy):
                for x in range(a.shape[1]-dx):
                    if abs(float(a[y,x])-float(a[y+dy,x+dx]))>=.5:
                        jumps+=1;touches+=bool(guard[y,x] or guard[y+dy,x+dx])
                    pairs+=1
            assert item['adjacent_alpha_jumps'][name]==dict(jumps_at_least_half=jumps,touching_protected=touches)
        assert hashlib.sha256(Path(item['board']).read_bytes()).hexdigest()==item['board_sha256']
    for p,h in d['input_sha256'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    result=dict(passed=True,fixed_conditions=4,scalar_adjacent_pair_checks=pairs,new_fits=0,new_inference=0,holdout_image_reads=0)
    (out/'verification_PRIVATE.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
