"""Replay saved geometry to separate color-rule coverage from missing landmarks."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.face_constrained_component import face_constrained_component


def main():
    old=ROOT/'outputs/rule_mask_ordering_v1';out=ROOT/'outputs/focused_ycrcb_diagnostic_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    for name,sha in read(old/'verification.json')['evidence_sha256'].items():assert digest(old/name)==sha
    rows=[json.loads(x) for x in (old/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    parent=ROOT/'outputs/correction_training_preparation_v1'
    paths=[Path(__file__),ROOT/'docs/focused-ycrcb-protocol.md',ROOT/'src/skin_masking/ycrcb_candidate.py',
        ROOT/'src/skin_masking/face_constrained_component.py',old/'verification.json',old/'plan.json']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir();(out/'masks').mkdir();(out/'boards').mkdir()
    def write(name,value):(out/name).write_text(json.dumps(value,indent=2),encoding='utf-8')
    write('plan.json',dict(input_sha256=hashes,ids=[r['image_id'] for r in rows],
        rule='existing Cr133..173,Cb77..127; saved geometry; no threshold tuning',existing_mst_lookup_applicable=False))
    def save(p,image):
        if not cv2.imwrite(str(p),image):raise OSError(p)
    def panel(im,title,mask=None):
        shown=im.copy()
        if mask is not None:
            selected=mask>0;shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,title,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.35,(255,255,255),1)
        return shown
    records=[]
    for r in rows:
        name=r['source_id'];im=cv2.imread(str(parent/'images'/f'{name}_reference.png'))
        and_mask=cv2.imread(str(old/'masks'/f'{name}_candidate.png'),0)
        candidate=np.zeros_like(and_mask)
        result=dict(image_id=r['image_id'],source_id=name,old_status=r['status'],source_suitability=r['source_suitability'],
            training_eligible=False,status='geometry_unavailable',reason=r.get('reason'))
        if 'face_box' in r:
            x,y,w,h=r['face_box']
            oval=cv2.imread(str(old/'geometry'/f'{name}_oval.png'),0)
            excluded=cv2.imread(str(old/'geometry'/f'{name}_excluded.png'),0)
            colors=cv2.imread(str(old/'geometry'/f'{name}_colors.png'),0)
            reconstructed=np.zeros_like(and_mask)
            reconstructed[y:y+h,x:x+w]=face_constrained_component(colors,oval,excluded)
            np.testing.assert_array_equal(and_mask,reconstructed)
            proposed_colors=ycrcb_color_candidate(im[y:y+h,x:x+w])
            proposed=face_constrained_component(proposed_colors,oval,excluded)
            candidate[y:y+h,x:x+w]=proposed
            assert not np.any((proposed>0)&((oval==0)|(excluded>0)))
            result.update(status='technical_support_available' if np.count_nonzero(candidate)>=1000 else 'insufficient_color_support',reason=None)
            save(out/'masks'/f'{name}_ycrcb_colors.png',proposed_colors)
        result.update(and_pixels=int(np.count_nonzero(and_mask)),ycrcb_pixels=int(np.count_nonzero(candidate)),
            added_pixels=int(np.count_nonzero((candidate>0)&(and_mask==0))),removed_pixels=int(np.count_nonzero((and_mask>0)&(candidate==0))))
        save(out/'masks'/f'{name}_ycrcb.png',candidate)
        save(out/'masks'/f'{name}_added.png',(((candidate>0)&(and_mask==0))*255).astype(np.uint8))
        save(out/'boards'/f'{name}.png',np.hstack([panel(im,name+' reference'),panel(im,'HSV AND YCrCb',and_mask),panel(im,'YCrCb-only diagnostic',candidate)]))
        records.append(result)
    write('attempts.json',records)
    summary=dict(status='diagnostic_complete_no_adoption',sources=24,statuses=dict(Counter(r['status'] for r in records)),
        old_insufficient_cases=[dict(source_id=r['source_id'],new_status=r['status'],new_pixels=r['ycrcb_pixels'],source_suitability=r['source_suitability']) for r in records if r['old_status']=='insufficient_support'],
        geometry_failures_not_rescued=[r['source_id'] for r in records if r['status']=='geometry_unavailable'],
        model_fits=0,candidate_ita_mst_calls=0,reserved_check_access=False)
    write('summary.json',summary)
    sections=''.join(f'<section><h2>{r["source_id"]}: {r["status"]}</h2><p>AND {r["and_pixels"]} → YCrCb {r["ycrcb_pixels"]} pixels. Source: {r["source_suitability"]}. Geometry issue: {r["reason"] or "none"}</p><img loading="lazy" src="boards/{r["source_id"]}.png"></section>' for r in records)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Color-rule diagnostic</title><style>body{font:16px system-ui;background:#151923;color:#eee;margin:24px}img{max-width:100%}section{border-top:1px solid #666;margin:24px 0}</style><h1>Same 24 training sources: color-rule diagnosis</h1><p>Saved geometry, unchanged YCrCb bounds. No new approvals, no mask replacement. Unavailable geometry stays unavailable. More selected pixels do not establish better masks.</p>'+sections,encoding='utf-8')
    assert all(digest(ROOT/p)==sha for p,sha in hashes.items())
    write('verification.json',dict(status='pass',all_saved_and_masks_reconstructed=True,anatomy_containment_checked=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
