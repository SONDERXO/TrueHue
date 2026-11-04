"""Reconstruct fixed contour candidates and preserve exposed-development labels."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.contour_ycrcb_measurement import build_mask,contract


def main():
    out=ROOT/'outputs/postcheck_contour_development_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');assert contract(ROOT)[1]==plan['candidate_contract_sha256']
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    for path,sha in plan['candidate_contract']['dependency_sha256'].items():assert digest(ROOT/path)==sha
    rows=read(out/'attempts.json');assert len(rows)==20 and [r['image_id'] for r in rows]==plan['source_ids']
    parent=ROOT/'outputs/ycrcb_training_check20_v1'
    judgments={r['image_id']:r for r in read(ROOT/'outputs/ycrcb_training_check_final_reviews_v1/reconciled_reviews.json')}
    reconstructed=0;failures=0
    for row in rows:
        name=row['source_id'];old=judgments[row['image_id']]
        assert row['prior_check_decision']==old['decision'] and row['exact_original_notes']==old['notes']
        assert not row['training_eligible'] and row['new_human_review']=='not_requested_or_inferred'
        for frame in ['reference','color']:
            metrics=row['frames'][frame];image=cv2.imread(str(parent/'images'/f'{name}_{frame}.png'))
            mask=cv2.imread(str(out/'images'/f'{name}_{frame}_new_mask.png'),0)
            assert mask.shape==(256,256) and np.count_nonzero(mask)==metrics['new_pixels']
            points_path=out/'geometry'/f'{name}_{frame}_landmarks.npy'
            if points_path.exists():
                x,y,w,h=metrics['new_report']['face_box'];points=np.load(points_path)
                expected=np.zeros_like(mask);expected[y:y+h,x:x+w]=build_mask(image[y:y+h,x:x+w],points).mask
                np.testing.assert_array_equal(mask,expected)
                oval=cv2.imread(str(out/'geometry'/f'{name}_{frame}_oval.png'),0)
                assert not np.any((mask>0)&(oval==0))
                reconstructed+=1
            else:
                assert not mask.any() and metrics['new_report']['status']=='failed'
                failures+=1
    assert reconstructed+failures==40
    target.write_text(json.dumps(dict(status='pass',geometry_available_masks_reconstructed=reconstructed,
        missing_geometry_frames_explicit=failures,all40frames_accounted=True,
        prior20decisions_and_notes_unchanged=True,new_human_acceptances_inferred=0,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(f'PASS:{reconstructed}geometry masks reconstructed,{failures}missing-geometry frames retained;all40accounted;labels unchanged.')


if __name__=='__main__':main()
