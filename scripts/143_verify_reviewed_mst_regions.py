"""Verify reviewed sparse-patch replay and report same-subject photo contrasts."""
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    folder=ROOT/'outputs/mst_region_quality_v2'
    result=json.loads((folder/'summary.json').read_text())
    references=json.loads((folder/'provisional_points.json').read_text())['records']
    manifest=json.loads((ROOT/'outputs/mst_region_quality_v1/inspection_manifest.json').read_text())['records']
    confirmation=json.loads((folder/'completion_confirmation.json').read_text())
    assert confirmation['reference_sha256']==digest(folder/'provisional_points.json')
    assert result['confirmation_sha256']==digest(folder/'completion_confirmation.json')
    with (ROOT/'data/manifests/mst_mapping_feasibility_v1/reviewed_included_rows.csv').open(encoding='utf-8-sig',newline='') as f:
        metadata={r['image_id']:r for r in csv.DictReader(f)}
    for row,reference,source in zip(result['records'],references,manifest):
        assert row['image_id']==reference['image_id']==source['image_id']
        assert digest(Path(source['source_path']))==source['original_sha256']
        assert digest(ROOT/source['mask_path'])==source['mask_sha256']
        square=cv2.resize(cv2.imread(source['source_path']),(256,256),interpolation=cv2.INTER_LINEAR)
        full=cv2.imread(str(ROOT/source['mask_path']),0)>0
        selected=np.zeros((256,256),bool);overlaps=[]
        for x,y in reference['points_square_xy']:
            selected[y-1:y+2,x-1:x+2]=True
            overlaps.append(int(full[y-1:y+2,x-1:x+2].sum()))
        assert overlaps==row['baseline_patch_selected']
        encoded=cv2.cvtColor(square,cv2.COLOR_BGR2LAB).astype(np.float32)
        lab=np.stack([encoded[:,:,0]*(100/255),encoded[:,:,1]-128,encoded[:,:,2]-128],axis=-1)[selected]
        means=[round(float(np.mean(lab[:,i])),4) for i in range(3)]
        stats=row['patch_statistics']
        assert means==[stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star']]
        assert round(math.degrees(math.atan((means[0]-50)/means[2])),4)==stats['ita_degrees']
    pairs=[]
    for a,b in itertools.combinations(result['records'],2):
        ma,mb=metadata[a['image_id']],metadata[b['image_id']]
        if ma['subject_id']!=mb['subject_id']:continue
        assert ma['source_mst_label']==mb['source_mst_label']
        pairs.append(dict(subject_id=ma['subject_id'],official_mst=int(ma['source_mst_label']),
            image_a=a['image_id'],lighting_a=ma['source_lighting'],
            image_b=b['image_id'],lighting_b=mb['source_lighting'],
            reviewed_patch_ita_difference=abs(a['patch_statistics']['ita_degrees']-b['patch_statistics']['ita_degrees']),
            baseline_ita_difference=abs(a['baseline_features']['input_ita_degrees']-b['baseline_features']['input_ita_degrees'])))
    assert len(pairs)==4
    report=dict(status='pass_reviewed_patch_accounting',images_checked=12,patches_checked=24,
        user_confirmed_revised_placement=True,same_subject_pairs=pairs,
        original_masks_sources_unchanged=True,new_fits=0,new_estimator_adopted=False,
        limitation='Sparse user-reviewed visible skin locations, not neutral lighting/calibrated complexion or subject-independent mapping validation.',
        input_sha256={p.name:digest(p) for p in [folder/'summary.json',folder/'provisional_points.json',folder/'completion_confirmation.json']})
    (folder/'reviewed_verification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
