"""Replay saved semantic masks/exclusions; no parser or correction refitting."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.face_parsing_experiment import LABELS
from src.ita_estimation.square_measurement import contract


def main():
    folder=ROOT/'outputs/semantic_face_coverage_v1'
    if (folder/'verification.json').exists():raise FileExistsError('Verification already exists')
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(folder/'plan.json');rows=read(folder/'records.json')
    assert len(rows)==24 and contract(ROOT)[1]==plan['old_measurement_contract_sha256']
    for p,sha in plan['input_sha256'].items():assert digest(ROOT/p)==sha
    forbidden_before=Counter();forbidden_after=Counter();boards=[]
    for r in rows:
        assert r['status']=='candidate_available' and not r['candidate_approved'] and not r['training_admitted']
        assert digest(ROOT/r['image_path'])==r['source_sha256']
        assert digest(ROOT/r['baseline_path'])==r['baseline_sha256']
        assert digest(ROOT/r['landmarks_path'])==r['landmarks_sha256']
        assert digest(folder/r['category_path'])==r['category_sha256']
        image=cv2.imread(str(ROOT/r['image_path']));old=cv2.imread(str(ROOT/r['baseline_path']),0)>0
        points=np.load(ROOT/r['landmarks_path']);cats=cv2.imread(str(folder/r['category_path']),0)
        geometry=build_face_coverage(image,points)
        allowed=(cats==1)|(cats==10)
        count,labels=cv2.connectedComponents(allowed.astype(np.uint8),connectivity=8)
        expected=np.zeros_like(allowed)
        components=0
        for label in range(1,count):
            component=labels==label
            if (component&(geometry.face_outline>0)).any():expected|=component;components+=1
        expected &= ~(geometry.exclusion_mask>0)
        mask=cv2.imread(str(folder/r['mask_path']),0)
        assert digest(folder/r['mask_path'])==r['mask_sha256']
        np.testing.assert_array_equal(mask,expected.astype(np.uint8)*255)
        alpha=cv2.imread(str(folder/'masks'/f'{r["case_id"]}_alpha.png'),0)
        expected_alpha=cv2.GaussianBlur(mask,(3,3),0);expected_alpha[~expected]=0
        np.testing.assert_array_equal(alpha,expected_alpha)
        assert not mask[~allowed|(geometry.exclusion_mask>0)].any()
        assert not alpha[~allowed|(geometry.exclusion_mask>0)].any()
        assert components==r['report']['associated_components']
        assert r['added_pixels']==int((expected&~old).sum()) and r['removed_pixels']==int((old&~expected).sum())
        for value,label in enumerate(LABELS):
            if value in [1,10]:continue
            forbidden_before[label]+=int((old&(cats==value)).sum())
            forbidden_after[label]+=int((expected&(cats==value)).sum())
        boards.append(cv2.imread(str(folder/r['board_path'])))
    # Six source-labeled contact sheets permit full visual inspection.
    for i in range(0,len(boards),4):
        assert cv2.imwrite(str(folder/f'contact_{i//4+1}.png'),np.vstack(boards[i:i+4]))
    smoke=ROOT/'outputs/semantic_face_mask_cli_smoke_v1'
    np.testing.assert_array_equal(cv2.imread(str(smoke/'mask.png'),0),cv2.imread(str(folder/'masks/25517__additional_gamma_darken.png'),0))
    result=dict(status='pass',saved_mask_replays=24,hard_exclusion_checks=24,inward_alpha_replays=24,
        CLI_smoke_matches_pack=True,old_measurement_contract_unchanged=True,
        baseline_selected_predicted_non_skin=dict(forbidden_before),candidate_selected_predicted_non_skin=dict(forbidden_after),
        interpretation='Predicted-class exclusion invariants, not independently measured segmentation accuracy.',
        old_masks_replaced=0,new_mask_approvals=0,correction_model_fits=0,ITA_MST_calls=0,
        verifier_sha256=digest(Path(__file__)),
        evidence_sha256={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()})
    (folder/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['evidence_sha256','baseline_selected_predicted_non_skin','candidate_selected_predicted_non_skin']},indent=2))


if __name__=='__main__':main()
