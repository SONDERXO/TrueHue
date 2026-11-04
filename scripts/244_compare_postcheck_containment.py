"""One fixed contour rule on exposed check cases; not independent evaluation."""
import hashlib
import importlib
import json
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np
from src.utilities.config import get_config
from src.ita_estimation.ycrcb_measurement import measure as old_measure
from src.ita_estimation.contour_ycrcb_measurement import measure as new_measure,contract
from src.skin_masking.face_outline_experiment import restrict_to_face_outline


def main():
    out=ROOT/'outputs/postcheck_contour_development_v1'
    if out.exists():raise FileExistsError(out)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    parent=ROOT/'outputs/ycrcb_training_check20_v1'
    prior=[json.loads(x) for x in (parent/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    final=ROOT/'outputs/ycrcb_training_check_final_reviews_v1'
    for name,sha in read(final/'verification.json')['evidence_sha256'].items():assert digest(final/name)==sha
    judgments={r['image_id']:r for r in read(final/'reconciled_reviews.json')}
    old_hashes=read(parent/'verification.json')['evidence_sha256']
    definition,identity=contract(ROOT)
    paths=[Path(__file__),ROOT/'docs/ycrcb-contour-development-protocol.md',final/'reconciled_reviews.json',parent/'attempts.jsonl']
    hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    out.mkdir()
    for folder in ['images','geometry','boards']:(out/folder).mkdir()
    def write(name,data):(out/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    write('plan.json',dict(status='frozen_before_new_candidate',source_ids=[r['image_id'] for r in prior],
        candidate_contract=definition,candidate_contract_sha256=identity,input_sha256=hashes,
        evidence_role='post-check development only; cases exposed and cannot be independent candidate evaluation',
        mst_lookup_applicable=False))
    prepare=importlib.import_module('11_prepare_training_manifests');config=get_config()
    detector=lambda im:prepare._detect_face_boxes(im,ROOT/config.FACE_MODEL_PATH,.85)
    provider=lambda im,box:prepare.detect_landmarks_with_margin(im,box,ROOT/config.FACE_LANDMARKER_MODEL_PATH)[0]
    records=[];parity=0
    def save(p,im):
        if not cv2.imwrite(str(p),im):raise OSError(p)
    def panel(im,label,mask=None):
        shown=im.copy()
        if mask is not None:
            selected=mask>0;shown[selected]=np.rint(.65*shown[selected]+.35*np.array([0,255,0])).astype(np.uint8)
        shown=cv2.copyMakeBorder(shown,26,0,0,0,cv2.BORDER_CONSTANT)
        cv2.putText(shown,label,(3,18),cv2.FONT_HERSHEY_SIMPLEX,.32,(255,255,255),1)
        return shown
    for source in prior:
        name=source['source_id'];review=judgments[source['image_id']];frames={};panels=[]
        with (out/'access_ledger.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(dict(image_id=source['image_id'],phase='postcheck_exposed_training_development'))+'\n')
        for frame in ['reference','color']:
            relative=f'images/{name}_{frame}.png';image_path=parent/relative
            assert digest(image_path)==old_hashes[relative]
            image=cv2.imread(str(image_path));old=old_measure(image,detector,provider)
            assert old.report==source['frames'][frame]['candidate'];parity+=1
            captured={}
            def capture(im,box):
                points=provider(im,box);captured['points']=points;captured['box']=box;return points
            new=new_measure(image,detector,capture)
            oval=np.zeros((256,256),np.uint8)
            if captured.get('points') is not None:
                x,y,w,h=captured['box']
                _,local=restrict_to_face_outline(np.full((h,w),255,np.uint8),captured['points'])
                oval[y:y+h,x:x+w]=local
                np.save(out/'geometry'/f'{name}_{frame}_landmarks.npy',captured['points'])
                save(out/'geometry'/f'{name}_{frame}_oval.png',oval)
            old_mask=old.mask if old.mask is not None else np.zeros_like(oval)
            new_mask=new.mask if new.mask is not None else np.zeros_like(oval)
            if new.report['status']=='success':assert not np.any((new_mask>0)&(oval==0))
            common=int(np.count_nonzero((old_mask>0)&(new_mask>0)));old_count=int(np.count_nonzero(old_mask))
            frames[frame]=dict(old_report=old.report,new_report=new.report,
                old_pixels=old_count,new_pixels=int(np.count_nonzero(new_mask)),
                old_outside_oval_pixels=int(np.count_nonzero((old_mask>0)&(oval==0))) if oval.any() else None,
                new_outside_oval_pixels=int(np.count_nonzero((new_mask>0)&(oval==0))) if oval.any() else None,
                old_mask_retained_fraction=common/old_count if old_count else None,
                removed_pixels=int(np.count_nonzero((old_mask>0)&(new_mask==0))),added_pixels=int(np.count_nonzero((new_mask>0)&(old_mask==0))))
            save(out/'images'/f'{name}_{frame}_new_mask.png',new_mask)
            panels.extend([panel(image,name+' '+frame),panel(image,'Frozen YCrCb v1',old.mask),panel(image,'Contour candidate',new.mask)])
        save(out/'boards'/f'{name}.png',np.hstack(panels))
        records.append(dict(image_id=source['image_id'],source_id=name,prior_check_decision=review['decision'],
            exact_original_notes=review['notes'],clarified_reason=review.get('clarified_reason'),
            frames=frames,new_human_review='not_requested_or_inferred',training_eligible=False))
    assert contract(ROOT)[1]==identity and all(digest(ROOT/p)==sha for p,sha in hashes.items())
    write('attempts.json',records)
    summary=dict(status='development_comparison_complete_no_promotion',sources=20,prior_check_accept=4,prior_check_reject=16,
        original_report_parity=parity,evidence_role='exposed-development, not independent test',frames={})
    for frame in ['reference','color']:
        values=[r['frames'][frame] for r in records]
        summary['frames'][frame]=dict(old_statuses=dict(Counter(v['old_report']['status'] for v in values)),
            new_statuses=dict(Counter(v['new_report']['status'] for v in values)),
            old_outside_oval_pixels=sum(v['old_outside_oval_pixels'] or 0 for v in values),
            new_outside_oval_pixels=sum(v['new_outside_oval_pixels'] or 0 for v in values),
            removed_pixels=sum(v['removed_pixels'] for v in values))
    summary.update(prior_acceptance_not_transferred=True,mst_calls=0,tree_fits=0,training_admissions=0,final_validation_test_access=False)
    write('summary.json',summary)
    sections=''.join(f'<section><h2>{r["source_id"]} — previous decision {r["prior_check_decision"]}</h2><p>Original note: {r["exact_original_notes"] or "none"}</p><img loading="lazy" src="boards/{r["source_id"]}.png"></section>' for r in records)
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Post-check containment development</title><style>body{font:17px system-ui;background:#171923;color:#eee;margin:28px}img{max-width:100%}section{margin:24px 0;border-top:1px solid #666}</style><h1>Post-check development: same exposed20sources</h1><p>Not independent evaluation or an adoption request. Fixed containment before component selection. Hair/hands/objects inside the face contour remain possible. Previous labels apply only to the old masks.</p>'+sections,encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
