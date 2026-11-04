"""Reconstruct40single-factor candidates and verify the8-source review packet."""
import hashlib
import json
import re
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.skin_mask import create_candidate_mask_bgr,keep_largest_connected_component
from src.evaluation.mask_support_quality import support_retention
from src.ita_estimation.square_measurement import contract


def main():
    out=ROOT/'outputs/color_cast_ycrcb_refinement_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    assert contract(ROOT)[1]==plan['old_measurement_contract_sha256']
    source=ROOT/'outputs/three_variant_training_candidates_v1'
    rows=[json.loads(x) for x in (source/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    keyed={(r['source_image_id'],r['variant']):r for r in rows}
    records=read(out/'attempts.json');count=0
    assert len(records)==20 and [r['image_id'] for r in records]==plan['selected_ids']
    for r in records:
        name=r['source_id'];support=cv2.imread(str(ROOT/keyed[(r['image_id'],'identity')]['reference_mask_path']),0)>0
        for frame,variant in [('reference','identity'),('color','color')]:
            original=keyed[(r['image_id'],variant)];metrics=r['frames'][frame]
            assert metrics['status']=='available'
            image=cv2.imread(str(ROOT/original['input_path']));baseline=cv2.imread(str(ROOT/original['input_mask_path']),0)
            x,y,w,h=metrics['face_box'];crop=image[y:y+h,x:x+w]
            colors=cv2.imread(str(out/'geometry'/f'{name}_{frame}_ycrcb_colors.png'),0)
            old_colors=cv2.imread(str(out/'geometry'/f'{name}_{frame}_and_colors.png'),0)
            excluded=cv2.imread(str(out/'geometry'/f'{name}_{frame}_excluded.png'),0)
            np.testing.assert_array_equal(colors,ycrcb_color_candidate(crop))
            np.testing.assert_array_equal(old_colors,create_candidate_mask_bgr(crop))
            expected=np.zeros((256,256),np.uint8);old_expected=np.zeros_like(expected)
            expected[y:y+h,x:x+w]=cv2.bitwise_and(keep_largest_connected_component(colors),cv2.bitwise_not(excluded))
            old_expected[y:y+h,x:x+w]=cv2.bitwise_and(keep_largest_connected_component(old_colors),cv2.bitwise_not(excluded))
            candidate=cv2.imread(str(out/'masks'/f'{name}_{frame}_candidate.png'),0)
            np.testing.assert_array_equal(expected,candidate);np.testing.assert_array_equal(old_expected,baseline)
            assert metrics['candidate_screen']==support_retention(support,candidate>0,candidate>0)
            assert metrics['candidate_pixels']==np.count_nonzero(candidate)
            count+=1
    shortlist=read(out/'review_selection.json')['selected_ids']
    assert len(shortlist)==len(set(shortlist))==8 and set(shortlist)<=set(plan['selected_ids'])
    page=(out/'review.html').read_text(encoding='utf-8')
    data=json.loads(re.search(r'<script id="review-data" type="application/json">(.*?)</script>',page,re.S)[1])
    assert [r['image_id'] for r in data['records']]==shortlist
    assert data['review_scope']=='candidate_reference_and_color_input_masks_only'
    assert len(data['panel_labels'])==6 and all(r['panel_count']==6 for r in data['records'])
    assert all((out/'boards'/f'{r["source_id"]}.png').exists() for r in data['records'])
    summary=read(out/'summary.json')
    assert summary['old_color_screen_pass']==5 and summary['new_color_screen_pass']==14
    assert summary['screen_regressions']==[]
    target.write_text(json.dumps(dict(status='pass',candidate_masks_reconstructed=count,baseline_parity_checks=count,
        review_ids_verified=8,original_contract_unchanged=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print('PASS:40candidate masks/screens reconstructed,40baseline parity checks,8review IDs and6panel labels verified.')


if __name__=='__main__':main()
