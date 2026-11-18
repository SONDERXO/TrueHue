"""Fixed visual subset and exact change counts for one gamma comparison."""
import json,hashlib
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'outputs/gamma_scene_chroma_comparison_v3';O=ROOT/'outputs/gamma_scene_chroma_review_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if O.exists():raise FileExistsError(O)
    v=read(E/'results_PRIVATE.json');chosen=[(s,c) for s,c in v['boards'] if not c.endswith('__clean') or s in ['fold_working256','fallback_native224']];assert len(chosen)==61;O.mkdir();cards=[]
    for s,c in chosen:
        a=cv2.imread(str(E/s/c/'board.png'));cards.append(cv2.copyMakeBorder(a,0,282-a.shape[0],0,1024-a.shape[1],cv2.BORDER_CONSTANT,value=(35,35,35)))
    for i in range(0,len(cards),4):assert cv2.imwrite(str(O/f'contact_{i//4+1:02d}.png'),np.vstack(cards[i:i+4]))
    changes={}
    for suite in v['summary']:
        rr=[r for r in v['records'] if r['suite']==suite and r['image_path'] is not None]
        changes[suite]={layer:{name:sum(not r['paths'][name]['byte_identical_old'] for r in rr if r['layer']==layer) for name in ['new_ungated','new_gated']} for layer in ['clean','core','composite_stress_design']}
    result=dict(selected_boards=chosen,counts=dict(fold_clean=29,native_clean=23,other_fixed=9),changed_outputs=changes)
    (O/'review_selection_PRIVATE.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(O/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in O.iterdir() if p.is_file()},indent=2),encoding='utf-8');print(json.dumps(changes,indent=2))
if __name__=='__main__':main()
