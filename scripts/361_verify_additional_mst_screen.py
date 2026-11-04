"""Replay saved screen evidence; record agent visual diagnostics, not approvals."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.nostril_measurement import contract
from src.skin_masking.semantic_face_coverage import build_semantic_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features


def main():
    folder = ROOT / 'outputs/additional_mst_eligibility_v1'
    target = folder / 'verification.json'
    if target.exists():
        raise FileExistsError(target)
    summary = json.loads((folder / 'summary.json').read_text())
    plan = json.loads((folder / 'plan.json').read_text())
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    assert contract(ROOT)[1] == summary['measurement_contract_sha256']
    assert all(digest(p) == h for p,h in plan['input_sha256'].items())
    assert [r['image_id'] for r in summary['records']] == [r['image_id'] for r in plan['selected']]
    notes = {
        1:'Hairline/eyebrow vicinity is ambiguous at square256; no actual-skin approval.',
        2:'Profile and hair boundary need exact review; no apparent large exterior selection.',
        4:'Clear selected neck and garment pixels; hold measurement.',
        5:'Partial profile support; boundary/exclusions need exact review.',
        6:'Hair boundary and small brow-adjacent patches remain uncertain.',
        7:'Profile; no apparent worn face mask despite recorded mask=1; retain metadata, no relabeling.',
        10:'Clear beard/chin hair selected as skin; dark illumination also limits inspection.',
        11:'Beard-adjacent cheek boundary uncertain; hold pending exact review.',
        14:'Clear worn face-covering pixels selected as skin; hold measurement.',
        15:'Strong warm cast; no apparent large exterior selection, not colour-reference evidence.',
        16:'Strong warm cast and hair-adjacent boundary; no reference-colour approval.',
        17:'Curly hair near forehead boundary needs exact review.',
        18:'Curly hair near forehead boundary needs exact review.',
        19:'Curly hair boundary; conflicting recorded mask=0|1 retained, no relabeling.',
        23:'Dark illumination and mouth-adjacent pixels require review.',
        24:'Profile; hairline/ear boundary needs exact review.',
        25:'No obvious large non-skin region at diagnostic scale; not an approved mask.',
    }
    observations = []; subjects = defaultdict(Counter); checked = 0
    for i,r in enumerate(summary['records'],1):
        subjects[r['subject_id']]['attempts'] += 1
        subjects[r['subject_id']][r['status']] += 1
        assert digest(r['source_path']) == r['source_sha256']
        if r['status'] != 'success':
            continue
        case = folder / Path(r['board_path']).parent
        assert all(digest(case / name) == h for name,h in r['saved_sha256'].items())
        image = cv2.imread(str(case / 'input.png')); mask = cv2.imread(str(case / 'mask.png'),0)
        cats = cv2.imread(str(case / 'categories.png'),0); points = np.load(case / 'landmarks.npy')
        replay = build_semantic_face_coverage(image,points,cats).mask
        replay[nostril_guard(mask.shape,points)] = 0
        assert np.array_equal(replay,mask)
        stats = compute_masked_lab_statistics(image,mask,1000)
        assert stats == r['statistics']
        features = {f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
        features.update(facial_endpoint_features(image,mask>0)['features'])
        assert features == r['features']
        observations.append(dict(image_id=r['image_id'], case_index=i, diagnostic_note=notes[i],
            reviewer='assistant_visual_diagnostic_not_user_approval',
            clear_contamination=i in {4,10,14}, admitted=False))
        checked += 1
    assert checked == len(observations) == 17
    for subject in subjects:
        subjects[subject]['not_assessed'] = sum(r['subject_id']==subject for r in plan['universe']) - subjects[subject]['attempts']
    (folder / 'visual_diagnostics.json').write_text(json.dumps(observations,indent=2))
    result = dict(status='replay_passed_eligibility_not_established', replays=checked,
        subject_counts={k:dict(v) for k,v in subjects.items()},
        clear_contamination_diagnostics=3, diagnostics_inspected=17, admitted=0,
        input_hashes_unchanged=True, fits=0, automatic_expansion=False)
    target.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
