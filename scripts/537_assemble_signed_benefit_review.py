"""Fixed clean/focal/context boards, plus four explicitly outcome-selected harms."""
import json,hashlib
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'outputs/signed_benefit_gate_comparison_v1';O=ROOT/'outputs/signed_benefit_gate_review_v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    if O.exists():raise FileExistsError(O)
    v=read(E/'results_PRIVATE.json');assert len(v['boards'])==61;O.mkdir();cards=[]
    for suite,cid in v['boards']:
        a=cv2.imread(str(E/suite/cid/'board.png'));cards.append(cv2.copyMakeBorder(a,0,282-a.shape[0],0,1280-a.shape[1],cv2.BORDER_CONSTANT,value=(35,35,35)))
    for i in range(0,len(cards),4):assert cv2.imwrite(str(O/f'contact_{i//4+1:02d}.png'),np.vstack(cards[i:i+4]))
    extra=[]
    for suite in ['fold_working256','fallback_native224']:
        for layer in ['core','composite_stress_design']:
            rr=[r for r in v['records'] if r['suite']==suite and r['layer']==layer and r['reference_available']]
            r=max(rr,key=lambda r:r['paths']['signed']['reference_metrics']['rgb8_mae_codes']-r['paths']['frozen']['reference_metrics']['rgb8_mae_codes']);cid=r['case_id'];context=next(c for c in read(ROOT/'outputs/gamma_scene_chroma_comparison_v3/results_PRIVATE.json')['records'] if c['suite']==suite and c['case_id']==cid)
            panels=[cv2.imread(r['reference_path']),cv2.imread(r['image_path']),cv2.imread(context['old_output_paths']['old_gated']),cv2.imread(str(E/suite/cid/'matched_binary.png')),cv2.imread(str(E/suite/cid/'signed.png'))];title=np.full((26,panels[0].shape[1]*5,3),255,np.uint8);cv2.putText(title,'Outcome-selected '+suite+' '+cid,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,0,0),1);a=np.vstack([title,np.hstack(panels)]);file=f'extra_{len(extra)+1}.png';assert cv2.imwrite(str(O/file),a);extra.append(dict(suite=suite,case_id=cid,layer=layer,file=file))
    clean={}
    for r in v['records']:
        if r['recipe']=='clean' and r['reference_available'] and r['suite']!='fold_working256':
            clean.setdefault(r['case_id'],[]).append(sha(E/r['suite']/r['case_id']/'signed.png'))
    assert len(clean)==23 and all(len(x)==3 and len(set(x))==1 for x in clean.values())
    (O/'selection_PRIVATE.json').write_text(json.dumps(dict(fixed_boards=v['boards'],additional_outcome_selected=extra,native_clean_duplicate_checks=23),indent=2),encoding='utf-8');print('Prepared61fixed boards +4outcome-selected harm boards;23native clean duplicates verified.')
if __name__=='__main__':main()
