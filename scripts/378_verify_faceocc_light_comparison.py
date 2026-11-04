"""Saved-output verification and explicit assistant-only qualitative observations."""
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.ita_estimation.faceocc_veto_candidate import combine_saved
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard


def main():
    out=ROOT/'outputs/faceocc_light_comparison_v1'
    if (out/'verification.json').exists():raise FileExistsError('Already verified')
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    summary=read(out/'summary.json');ip=read(out/'inference_plan.json');run=read(out/'inference.json')
    assert all(digest(Path(p))==h for p,h in ip['input_sha256'].items())
    prior=read(ROOT/'outputs/faceocc_diagnostic_v1/plan.json')
    reused=ROOT/'scripts/369_run_faceocc_logits.py';assert digest(reused)==prior['input_sha256'][str(reused)]
    notes={3:'Face-edge support reduced; blurred original limits skin-boundary judgment.',
        4:'Masks largely similar; facial-hair/stubble vicinity still selected, not resolved.',
        5:'New excluded patch near mouth/cheek appears to remove useful skin; potential harm.',
        6:'Masks broadly similar; no obvious large new loss at diagnostic scale.',
        7:'Masks broadly similar; no actual-skin accuracy established.',
        10:'Face/hair boundary trims; irregular parent coverage remains.',
        11:'Small face-edge reduction; no obvious major change.',
        12:'Glasses vicinity remains ambiguous; do not claim all frames excluded.',
        13:'Small edge differences; unusual pose/exclusions remain.',
        14:'Masks broadly similar; dark lighting limits boundary judgment.',
        15:'Small forehead-edge reduction, otherwise largely preserved.',
        16:'Larger profile/neck-edge removal; mixed skin loss and neck exclusion cannot be quantified visually.',
        19:'Hairline/forehead trims; curls remain an ambiguous boundary.',
        20:'Cheek/hairline trimming in warm light; no independent colour/reference claim.',
        21:'Facial-hair concern largely unchanged; not a beard solution.',
        22:'Masks nearly identical; existing outer-forehead gap not repaired by a removal-only veto.',
        23:'Mouth/shadow protrusion reduced, some adjacent skin may also be lost.',
        24:'Glasses/outer-face area trimmed, bridge/frame vicinity still needs human judgment.'}
    predictions={r['image_id']:r for r in run['records']};observations=[];checked=0
    for row in summary['records']:
        i=row['case_index']
        if 'candidate_report' not in row:
            observations.append(dict(image_id=row['image_id'],case_index=i,status=row['status'],
                note=row.get('reason'),reviewer='assistant_diagnostic_not_user_judgment'));continue
        folder=out/('case_'+str(i));prediction=predictions[row['image_id']]
        lp=out/prediction['logits_path'];assert digest(lp)==prediction['logits_sha256']
        image=cv2.imread(str(folder/'input.png'));base=cv2.imread(str(folder/'baseline_mask.png'),0)
        saved=cv2.imread(str(folder/'candidate_mask.png'),0);assert digest(folder/'candidate_mask.png')==row['candidate_sha256']
        replay,_,report=combine_saved(image,base,np.load(lp),np.array(row['matrix']))
        assert np.array_equal(replay,saved) and report==row['candidate_report']
        assert compute_masked_lab_statistics(image,base,1000)==row['parent_report']['statistics']
        cats=cv2.imread(str(folder/'categories.png'),0);points=np.load(folder/'landmarks.npy')
        forbidden=(~np.isin(cats,[1,10]))|(build_face_coverage(image,points).exclusion_mask>0)|nostril_guard(base.shape,points)
        assert not saved[forbidden].any() and not saved[base==0].any()
        observations.append(dict(image_id=row['image_id'],case_index=i,status=row['status'],note=notes[i],
            reviewer='assistant_diagnostic_not_user_judgment',ground_truth=False));checked+=1
    assert len(observations)==24 and checked==18
    (out/'assistant_observations.json').write_text(json.dumps(observations,indent=2))
    result=dict(status='saved_checks_passed_qualitative_only',attempts=24,paired_outputs=18,
        remaining_failures=6,candidate_new_failures=0,mask_feature_replays=18,
        median_parent_retention=statistics.median(r['candidate_report']['retained_fraction'] for r in summary['records'] if 'candidate_report' in r),
        lanes={lane:dict(attempts=sum(r['lane']==lane for r in summary['records']),
            available=sum(r['lane']==lane and r['status']=='success' for r in summary['records'])) for lane in {r['lane'] for r in summary['records']}},
        source_and_correction_hashes_unchanged=True,user_judgments_pending=4,
        polygon_annotations_not_assumed=True,adopted=False,fits=0)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
