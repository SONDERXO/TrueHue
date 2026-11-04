"""Score frozen sparse provisional interiors against saved masks; no new estimator."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    folder=ROOT/'outputs/mst_region_quality_v1'
    if (folder/'summary.json').exists():raise FileExistsError('Scoring exists')
    manifest=json.loads((folder/'inspection_manifest.json').read_text())
    reference=json.loads((folder/'provisional_points.json').read_text())
    assert reference['inspection_manifest_sha256']==digest(folder/'inspection_manifest.json')
    original=json.loads((ROOT/'outputs/mst_square256_measurement_v1/summary.json').read_text())
    by_id={r['image_id']:r for r in original['records']};points={r['image_id']:r for r in reference['records']}
    tracked=[folder/'inspection_manifest.json',folder/'provisional_points.json',Path(__file__),ROOT/'docs/mst-region-quality-protocol.md']
    hashes={str(p):digest(p) for p in tracked};results=[];(folder/'point_boards').mkdir(exist_ok=True)
    for r in manifest['records']:
        assert digest(Path(r['source_path']))==r['original_sha256'] and digest(ROOT/r['mask_path'])==r['mask_sha256']
        image=cv2.resize(cv2.imread(r['source_path']),(256,256),interpolation=cv2.INTER_LINEAR)
        baseline=cv2.imread(str(ROOT/r['mask_path']),0)>0
        ref=points[r['image_id']];patch=np.zeros((256,256),np.uint8);checks=[]
        shown=cv2.resize(image,(768,768),interpolation=cv2.INTER_NEAREST)
        for index,(x,y) in enumerate(ref['points_square_xy']):
            assert 1<=x<255 and 1<=y<255
            patch[y-1:y+2,x-1:x+2]=255
            selected=int(baseline[y-1:y+2,x-1:x+2].sum())
            checks.append(dict(point=index,square_xy=[x,y],baseline_selected_pixels=selected,patch_pixels=9))
            cv2.rectangle(shown,((x-2)*3,(y-2)*3),((x+2)*3,(y+2)*3),(0,255,255),1)
        stats=compute_masked_lab_statistics(image,patch,minimum_skin_pixels=1)
        old=by_id[r['image_id']]['features']
        results.append(dict(image_id=r['image_id'],checks=checks,
            patch_pixels=int((patch>0).sum()),baseline_selected_patch_pixels=int((baseline&(patch>0)).sum()),
            provisional_patch_statistics=stats,baseline_features=old,
            patch_minus_baseline_ita=stats['ita_degrees']-old['input_ita_degrees'] if stats['valid'] else None,
            notes=ref['notes'],measurement_contract_used_for_mapping=False))
        assert cv2.imwrite(str(folder/'point_boards'/f"{r['index']:02d}.png"),shown)
    assert all(digest(Path(p))==h for p,h in hashes.items())
    summary=dict(status='sparse_provisional_QA_only_no_new_mask',records=results,
        points=24,total_patch_pixels=sum(r['patch_pixels'] for r in results),
        selected_patch_pixels=sum(r['baseline_selected_patch_pixels'] for r in results),
        fully_selected_points=sum(p['baseline_selected_pixels']==9 for r in results for p in r['checks']),
        wholly_missed_points=sum(p['baseline_selected_pixels']==0 for r in results for p in r['checks']),
        input_sha256=hashes,new_fits=0,masks_changed=0,lookup_exported=False,
        limitation='Codex provisional sparse visible cheek interiors; not expert labels, exhaustive mask accuracy or validated alternative measurement. Local lighting/anatomy differences confound ITA contrasts.')
    (folder/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({k:v for k,v in summary.items() if k not in ['records','input_sha256']},indent=2))


if __name__=='__main__':main()
