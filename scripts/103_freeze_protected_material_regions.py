"""Freeze original-image-only region QA before candidate inference."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
import cv2
import numpy as np

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    folder=ROOT/'data/manifests/paint_protection_validation_v1'
    target=folder/'frozen_manifest.json'
    if target.exists():raise FileExistsError(target)
    draft=folder/'draft_manifest.json';data=json.loads(draft.read_text())
    assert all(digest(ROOT/p)==h for p,h in data['input_sha256'].items())
    replacements={
      '67436_R1':[[48,62],[57,59],[66,60],[72,63],[68,66],[57,65],[49,67]],
      '67436_R2':[[138,65],[148,62],[158,63],[164,66],[161,69],[150,67],[141,69]],
      '67436_R3':[[84,144],[96,140],[106,140],[115,143],[121,146],[114,145],[104,144],[94,146]],
      '67436_R4':[[87,184],[98,187],[113,187],[125,182],[122,187],[111,189],[98,188]]}
    changes=[];raster=importlib.import_module('90_score_face_boundary_references')
    for f in data['frames']:
        regions=f['annotation'].get('regions',[])
        if not regions:continue
        image=cv2.imread(str(ROOT/f['source_path']));shown=cv2.resize(image,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
        for r in regions:
            if r['region_id'] in replacements:
                changes.append(dict(region_id=r['region_id'],original_points=r['points'],frozen_points=replacements[r['region_id']],reason='Narrow to visible purple cosmetic interior; remove adjacent ordinary skin/teeth/mouth ambiguity before inference'))
                r['points']=replacements[r['region_id']]
            a=np.asarray(r['points'],np.float32)
            independent=np.array([[cv2.pointPolygonTest(a,(float(x),float(y)),False)>=0 for x in range(f['width'])] for y in range(f['height'])])
            mask=raster.polygon_pixels(r['points'],f['width'],f['height']);assert np.array_equal(mask,independent) and mask.any()
            r['pixels']=int(mask.sum());r['interior_pixels']=int(cv2.erode(mask.astype(np.uint8),np.ones((3,3),np.uint8)).sum())
            polygon=np.rint(a*3).astype(np.int32);cv2.polylines(shown,[polygon],True,(0,0,255),2)
            x,y=polygon.mean(axis=0).astype(int);cv2.putText(shown,r['region_id'].split('_')[-1],(x,y),cv2.FONT_HERSHEY_SIMPLEX,.4,(0,255,255),1)
        assert cv2.imwrite(str(ROOT/'outputs/paint_protection_inventory_v1/regions'/(f['frame_id']+'_frozen.png')),shown)
    qa=dict(status='Original five overlays inspected before any new candidate inference',draft_sha256=digest(draft),changes=changes,
        limitation='Codex provisional protected interiors, not user/expert validation or exhaustive material truth',unchanged_user_annotations=True)
    (folder/'region_qa.json').write_text(json.dumps(qa,indent=2))
    data.update(status='frozen_before_candidate_inference',region_qa=qa)
    data['input_sha256'].update({str(p.relative_to(ROOT)):digest(p) for p in [draft,folder/'region_qa.json',Path(__file__)]})
    target.write_text(json.dumps(data,indent=2));print(dict(frames=len(data['frames']),changes=len(changes),sha256=digest(target)))
if __name__=='__main__':main()
