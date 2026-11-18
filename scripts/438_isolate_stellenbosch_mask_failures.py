"""Private saved-pixel stage diagnosis; no new inference or target fitting."""
from collections import defaultdict,Counter
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.face_parsing_experiment import LABELS,facial_skin
from src.skin_masking.full_face_support import nostril_guard

PARENT=ROOT/'outputs/stellenbosch_face_crop_v1'
OUT=ROOT/'outputs/stellenbosch_mask_failure_isolation_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))

def main():
    if OUT.exists():raise FileExistsError(OUT)
    bound=read(PARENT/'inference_plan.json')['input_sha256']
    bound.update({str(PARENT/p):h for p,h in read(PARENT/'sha256.json').items()})
    for path in [Path(__file__),ROOT/'docs/stellenbosch-mask-failure-protocol-2026-11-05.md']:
        bound[str(path)]=sha(path)
    assert all(sha(p)==h for p,h in bound.items())
    OUT.mkdir();(OUT/'input_sha256_PRIVATE.json').write_text(json.dumps(bound,indent=2),encoding='utf-8')
    records=[];boards=[];replays=0;totals=defaultdict(Counter)
    for r in read(PARENT/'results_PRIVATE.json')['records']:
        folder=PARENT/r['case_id'];image=cv2.imread(str(folder/'input.png'))
        rec=dict(case_id=r['case_id'],subject_key=r['subject_key'],condition=r['condition'],sampling_stratum=r['sampling_stratum'],
            parent_status=r['parent_report']['status'],parent_stage=r['parent_report']['stage'],final_status=r['status'],admitted=False)
        panels=[image.copy()];probe=np.zeros(image.shape[:2],bool);skin=probe.copy();final=probe.copy()
        if (folder/'landmarks.npy').exists():
            points=np.load(folder/'landmarks.npy',allow_pickle=False);categories=cv2.imread(str(folder/'categories.png'),0)
            geometry=build_face_coverage(image,points);probe=(geometry.mask>0)&~nostril_guard(image.shape[:2],points)
            hist=np.bincount(categories[probe],minlength=19);assert len(hist)==19 and int(hist.sum())==int(probe.sum())
            skin=facial_skin(categories)&probe
            rec.update(probe_pixels=int(probe.sum()),parser_skin_nose_in_probe=int(skin.sum()),
                parser_skin_nose_fraction=float(skin.sum()/probe.sum()),parser_class_histogram=dict(zip(LABELS,map(int,hist))))
            totals[r['sampling_stratum']].update(dict(available=1,probe_pixels=int(probe.sum()),skin_nose_pixels=int(skin.sum())))
            try:
                semantic=build_semantic_face_coverage(image,points,categories)
                if (folder/'baseline_mask.png').exists():
                    expected=semantic.mask.copy()
                    if 'nostril_guard_removed_pixels' in r['parent_report']:expected[nostril_guard(expected.shape,points)]=0
                    assert np.array_equal(expected,cv2.imread(str(folder/'baseline_mask.png'),0));replays+=1
            except ValueError as error:
                rec['semantic_replay_failure']=str(error)
                assert r['parent_report']['stage']=='semantic_mask' and str(error)==r['parent_report']['reason']
        else:rec['unavailable']='Saved detector did not yield exactly one face; no replacement geometry'
        if (folder/'measurement_mask.png').exists():final=cv2.imread(str(folder/'measurement_mask.png'),0)>0
        for mask,color in [(probe,[255,180,0]),(skin,[0,255,0]),(final,[0,255,0])]:
            overlay=image.copy();overlay[mask]=np.rint(.6*image[mask]+.4*np.array(color)).astype(np.uint8);panels.append(overlay)
        board=np.hstack(panels);label=np.full((26,1024,3),255,np.uint8)
        cv2.putText(label,r['case_id']+' '+r['condition']+' '+r['status'],(5,18),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),1)
        boards.append(np.vstack([label,board]));records.append(rec)
    for i in range(10):assert cv2.imwrite(str(OUT/f'contact_{i+1:02d}.png'),np.vstack(boards[3*i:3*i+3]))
    summary=dict(attempts=30,geometry_category_pairs=sum('probe_pixels' in r for r in records),semantic_mask_exact_replays=replays,
        by_preexisting_stratum={k:dict(v,skin_nose_fraction=v['skin_nose_pixels']/v['probe_pixels']) for k,v in totals.items()},
        new_forwards=0,new_fits=0,admissions=0,probe_is_skin_truth=False)
    (OUT/'results_PRIVATE.json').write_text(json.dumps(dict(summary=summary,records=records),indent=2),encoding='utf-8')
    (OUT/'review_PRIVATE.html').write_text('<!doctype html><meta charset="utf-8"><h1>Private stage diagnosis</h1><p>Input; anatomical probe (not skin truth); parser skin/nose within probe; final mask if available. Missing masks are empty. Research only; no redistribution.</p>'+''.join(f'<img style="max-width:100%" src="contact_{i:02d}.png">' for i in range(1,11)),encoding='utf-8')
    assert all(sha(p)==h for p,h in bound.items())
    (OUT/'sha256.json').write_text(json.dumps({p.name:sha(p) for p in OUT.iterdir() if p.is_file()},indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
