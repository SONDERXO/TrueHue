"""Reconstruct rule masks and verify color/geometry/exclusion invariants."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.face_constrained_component import face_constrained_component
from src.skin_masking.skin_mask import create_candidate_mask_bgr
from src.ita_estimation.square_measurement import contract


def main():
    out=ROOT/'outputs/rule_mask_ordering_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');definition=plan['contract']
    assert hashlib.sha256(json.dumps(definition,sort_keys=True).encode()).hexdigest()==plan['contract_sha256']
    assert contract(ROOT)[1]==definition['baseline_measurement_contract']
    for name,sha in definition['input_sha256'].items():assert digest(ROOT/name)==sha
    rows=[json.loads(x) for x in (out/'attempts.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in rows]==plan['selected_ids'] and len(rows)==24
    access=[json.loads(x) for x in (out/'access_ledger.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [r['image_id'] for r in access]==plan['selected_ids']
    parent=ROOT/'outputs/correction_training_preparation_v1'
    old=read(parent/'verification.json')['evidence_sha256'];checked=0
    for r in rows:
        name=r['source_id'];reference=parent/'images'/f'{name}_reference.png'
        assert digest(reference)==old[f'images/{name}_reference.png']
        baseline=parent/'images'/f'{name}_reference_mask.png'
        if baseline.exists():assert digest(baseline)==old[f'images/{name}_reference_mask.png']
        candidate=cv2.imread(str(out/'masks'/f'{name}_candidate.png'),0)
        assert candidate.shape==(256,256) and set(np.unique(candidate))<={0,255}
        assert np.count_nonzero(candidate)==r['candidate_pixels']
        if 'face_box' in r:
            x,y,w,h=r['face_box'];image=cv2.imread(str(reference))
            color=cv2.imread(str(out/'geometry'/f'{name}_colors.png'),0)
            oval=cv2.imread(str(out/'geometry'/f'{name}_oval.png'),0)
            excluded=cv2.imread(str(out/'geometry'/f'{name}_excluded.png'),0)
            np.testing.assert_array_equal(color,create_candidate_mask_bgr(image[y:y+h,x:x+w]))
            reconstructed=np.zeros_like(candidate)
            reconstructed[y:y+h,x:x+w]=face_constrained_component(color,oval,excluded)
            np.testing.assert_array_equal(candidate,reconstructed)
            crop=candidate[y:y+h,x:x+w]>0
            assert not np.any(crop&((color==0)|(oval==0)|(excluded>0)))
            checked+=1
        else:assert not candidate.any() and r['status']=='unavailable'
        assert r['training_eligible'] is False
        if name=='55166':assert r['source_suitability']=='reject_monochrome_reference'
    target.write_text(json.dumps(dict(status='pass',attempts=24,reconstructed_color_and_geometry_cases=checked,
        old_measurement_contract_unchanged=True,no_reserved_check_access=True,
        evidence_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2),encoding='utf-8')
    print(f'PASS: 24 attempts; {checked} color/contour/anatomy reconstructions; original contract intact.')


if __name__=='__main__':main()
