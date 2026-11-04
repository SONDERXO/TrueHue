"""Reconstruct every rule-factor mask and its support diagnostics."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.skin_mask import keep_largest_connected_component,create_candidate_mask_bgr
from src.skin_masking.ycrcb_candidate import ycrcb_color_candidate
from src.skin_masking.face_constrained_component import face_constrained_component
from src.evaluation.mask_support_quality import support_retention
from src.ita_estimation.square_measurement import contract


def main():
    out=ROOT/'outputs/table2_input_mask_robustness_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json')
    for path,sha in plan['input_sha256'].items():assert digest(ROOT/path)==sha
    assert contract(ROOT)[1]==plan['original_measurement_contract']
    records=[json.loads(x) for x in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    access=[json.loads(x) for x in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(records)==20 and [r['image_id'] for r in records]==plan['selected_ids']
    assert len(access)==40 and {r['image_id'] for r in access}==set(plan['selected_ids'])
    parent=ROOT/'outputs/correction_training_preparation_v1';old=read(parent/'verification.json')['evidence_sha256']
    reconstructed=0;baseline_parity=0
    for r in records:
        name=r['source_id'];ref_mask=cv2.imread(str(parent/'images'/f'{name}_reference_mask.png'),0)>0
        for frame in ['reference','input']:
            report=r['frames'][frame];assert report['status']=='available'
            x,y,w,h=report['face_box'];key=name+'_'+frame
            image_path=parent/'images'/f'{key}.png';baseline_path=parent/'images'/f'{key}_mask.png'
            assert digest(image_path)==old[f'images/{key}.png']
            assert digest(baseline_path)==old[f'images/{key}_mask.png']
            image=cv2.imread(str(image_path));crop=image[y:y+h,x:x+w]
            colors={c:cv2.imread(str(out/'geometry'/f'{key}_{c}_colors.png'),0) for c in ['and','ycrcb']}
            np.testing.assert_array_equal(colors['and'],create_candidate_mask_bgr(crop))
            np.testing.assert_array_equal(colors['ycrcb'],ycrcb_color_candidate(crop))
            excluded=cv2.imread(str(out/'geometry'/f'{key}_excluded.png'),0)
            oval=cv2.imread(str(out/'geometry'/f'{key}_oval.png'),0)
            for arm in plan['arms']:
                color_name,ordering=arm.split('_')
                native=(cv2.bitwise_and(keep_largest_connected_component(colors[color_name]),cv2.bitwise_not(excluded))
                    if ordering=='original' else face_constrained_component(colors[color_name],oval,excluded))
                expected=np.zeros((256,256),np.uint8);expected[y:y+h,x:x+w]=native
                actual=cv2.imread(str(out/'masks'/f'{key}_{arm}.png'),0)
                np.testing.assert_array_equal(actual,expected)
                metrics=report['arms'][arm]
                assert metrics['selected_pixels']==np.count_nonzero(actual)
                assert metrics['support_screen']==support_retention(ref_mask,actual>0,actual>0)
                if ordering=='oval':assert not np.any((native>0)&(oval==0))
                if arm=='and_original':
                    np.testing.assert_array_equal(actual,cv2.imread(str(baseline_path),0));baseline_parity+=1
                reconstructed+=1
        assert r['training_eligible'] is False
    summary=read(out/'summary.json')
    for arm in plan['arms']:
        values=[r['frames']['input']['arms'][arm] for r in records]
        assert summary['arms'][arm]['support_screen_pass']==sum(v['support_screen']['screen_pass'] for v in values)
        assert summary['arms'][arm]['total_outside_oval_pixels']==sum(v['outside_oval_pixels'] for v in values)
    assert summary['clipped_inputs']==sum(r['clipping']['clipped_pixels']>0 for r in records)==19
    target.write_text(json.dumps(dict(status='pass',reconstructed_masks=reconstructed,baseline_parity_checks=baseline_parity,
        unchanged_measurement_contract=True,all_diagnostics_recomputed=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(f'PASS: {reconstructed} masks reconstructed, {baseline_parity} baseline parity checks; metrics and source hashes match.')


if __name__=='__main__':main()
