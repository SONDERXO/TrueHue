"""Verify saved logits/masks/features without another model forward."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.skin_masking.anatomical_face_coverage import build_face_coverage
from src.skin_masking.full_face_support import nostril_guard
from src.ita_estimation.compute_ita import compute_masked_lab_statistics
from src.model_training.facial_endpoint_features import facial_endpoint_features


def main():
    out=ROOT/'outputs/faceocc_diagnostic_v1';target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    plan=read(out/'plan.json');summary=read(out/'summary.json');inference=read(out/'inference.json')
    assert all(digest(Path(p))==h for p,h in plan['input_sha256'].items())
    assert inference['plan_sha256']==digest(out/'plan.json')
    assert [r['image_id'] for r in summary['records']]==[r['image_id'] for r in plan['attempts']]
    byid={r['image_id']:r for r in inference['records']};attempts={r['image_id']:r for r in plan['attempts']}
    checked=0;non_skin_selected=0;skin_retained=0
    for r in summary['records']:
        if 'candidate_sha256' not in r:continue
        row=attempts[r['image_id']];i=row['case_index']
        pred=byid[r['image_id']];lp=out/pred['logits_path'];assert digest(lp)==pred['logits_sha256']
        logits=np.load(lp,allow_pickle=False);matrix=np.array(row['matrix'])
        baseline=cv2.imread(row['baseline_mask'],0);image=cv2.imread(row['input_path'])
        # Reconstruct the two warps directly, independently of combine_saved/map_visible_mask.
        valid=cv2.warpAffine(np.full(baseline.shape,255,np.uint8),matrix,(256,256),
            flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        aligned=np.where((logits>0)&(valid>0),255,0).astype(np.uint8)
        visible=cv2.warpAffine(aligned,cv2.invertAffineTransform(matrix),(baseline.shape[1],baseline.shape[0]),
            flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        expected=cv2.bitwise_and(baseline,visible)
        path=out/('case_'+str(i))/'candidate_mask.png';assert digest(path)==r['candidate_sha256']
        candidate=cv2.imread(str(path),0);assert np.array_equal(candidate,expected)
        folder=Path(row['baseline_mask']).parent
        cats=cv2.imread(str(folder/'categories.png'),0);points=np.load(folder/'landmarks.npy')
        exclusion=build_face_coverage(image,points).exclusion_mask>0
        forbidden=(~np.isin(cats,[1,10]))|exclusion|nostril_guard(baseline.shape,points)
        assert not candidate[forbidden].any() and not candidate[baseline==0].any()
        stats=compute_masked_lab_statistics(image,candidate,1000);assert stats==r['statistics']
        assert np.count_nonzero(candidate)==r['candidate_pixels']
        assert (np.count_nonzero(baseline)-np.count_nonzero(candidate))==r['removed_pixels']
        if r['status']=='success':
            features={f'input_{k}':stats[k] for k in ['mean_l_star','mean_a_star','mean_b_star','ita_degrees']}
            features.update(facial_endpoint_features(image,candidate>0)['features']);assert features==r['features']
        else:assert r['features'] is None
        for category,points in r.get('sparse_mark_results',{}).items():
            for p in points:
                assert bool(candidate[p['y'],p['x']])==p['candidate_selected']
                if category=='non_skin':non_skin_selected+=int(p['candidate_selected'])
                if category=='skin':skin_retained+=int(p['candidate_selected'])
        checked+=1
    assert checked==17 and len(summary['records'])==25
    result=dict(status='saved_reconstruction_passed_not_quality_validation',mask_feature_replays=checked,
        all_attempts_retained=25,parent_failures_retained=8,added_selected_pixels=0,
        selected_programmed_forbidden_pixels=0,known_non_skin_marks_still_selected=non_skin_selected,
        known_skin_marks_retained=skin_retained,parent_and_correction_hashes_unchanged=True,
        additional_model_forwards=0,fits=0,adopted=False)
    target.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
