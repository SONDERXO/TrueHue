"""One fixed hard/soft edge comparison on saved support; no inference/fits."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2
import numpy as np
from src.correction.seamless_blend import apply_blended
from src.skin_masking.face_neck_support import FaceNeckSupport,apply_shared_parameters
from src.ita_estimation.nostril_measurement import contract
from src.ita_estimation.compute_ita import compute_masked_lab_statistics


def main():
    parent=ROOT/'outputs/whole_face_support_v4';out=ROOT/'outputs/seamless_support_v5'
    if out.exists():raise FileExistsError(out)
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    old=json.loads((parent/'records.json').read_text());refrows=json.loads((ROOT/'outputs/preferred_support_cohort_v2/records.json').read_text())
    ids=[Path(r['image_id']).stem for r in refrows if r['measurement']['status']=='success']
    identity=contract(ROOT)[1];assert len(old)==len(ids)==16
    inputs=[Path(__file__),ROOT/'src/correction/seamless_blend.py',ROOT/'docs/seamless-support-protocol-2026-11-01.md',parent/'records.json']
    hashes={str(p):digest(p) for p in inputs}
    out.mkdir();(out/'cases').mkdir()
    (out/'plan.json').write_text(json.dumps(dict(status='fixed_before_comparison',cases=ids,parameters=[.85,1.05,.95],
        edge_rule='inward_smoothstep_max2_ceil3percent_facewidth',input_sha256=hashes,
        measurement_contract_sha256=identity,model_fits=0),indent=2))
    records=[];cards=[]
    for sid,previous in zip(ids,old):
        source=parent/'cases'/sid;folder=out/'cases'/sid;folder.mkdir()
        image=cv2.imread(str(source/'input.png'));mask=cv2.imread(str(source/'correction_mask.png'),0)
        measurement=cv2.imread(str(source/'measurement_mask.png'),0);neck=cv2.imread(str(source/'neck_mask.png'),0)
        _,xx=np.nonzero(measurement);width=int(xx.max()-xx.min()+1)
        before=compute_masked_lab_statistics(image,measurement,1000)
        assert before==previous['statistics']
        base=FaceNeckSupport(measurement,neck,mask,{})
        hard=apply_shared_parameters(image,base,.85,1.05,.95)
        soft,alpha,report=apply_blended(image,mask,[.85,1.05,.95],face_width=width)
        identity_output,_,_=apply_blended(image,mask,[1,1,1],face_width=width)
        assert np.array_equal(identity_output,image) and np.array_equal(soft[mask==0],image[mask==0])
        assert not alpha[mask==0].any() and np.all((alpha[mask>0]>0)&(alpha[mask>0]<=1))
        assert np.array_equal(soft[alpha==1],hard[alpha==1])
        assert compute_masked_lab_statistics(image,measurement,1000)==before
        for name,array in [('input.png',image),('measurement_mask.png',measurement),('correction_mask.png',mask),
            ('alpha.png',np.rint(alpha*255).astype(np.uint8)),('hard.png',hard),('soft.png',soft),
            ('board.png',np.hstack((image,cv2.cvtColor(np.rint(alpha*255).astype(np.uint8),cv2.COLOR_GRAY2BGR),hard,soft)))]:assert cv2.imwrite(str(folder/name),array)
        records.append(dict(case_id=sid,blend_report=report,measurement_statistics=before,
            binary_correction_mask_sha256=digest(source/'correction_mask.png'),
            measurement_mask_sha256=digest(source/'measurement_mask.png'),
            changed_hard_vs_soft_pixels=int(np.any(hard!=soft,axis=2).sum()),
            quality_approved=False,board_path=(folder/'board.png').relative_to(out).as_posix()))
        cards.append('<h2>'+sid+'</h2><img src="cases/'+sid+'/board.png">')
    assert contract(ROOT)[1]==identity and all(digest(Path(p))==h for p,h in hashes.items())
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Seamless edge preview</title><style>body{font:18px system-ui;max-width:1400px;margin:25px auto;padding:20px}img{width:100%}</style><h1>Whole-face edge blending</h1><p>Panels: original; correction alpha (white full strength); hard-edge operator; inward-blended operator. Same illustrative settings, not a learned correction result. Binary support and ITA measurement remain unchanged; no blending outside support.</p>'+''.join(cards),encoding='utf-8')
    result=dict(status='fixed_blending_checks_passed',cases=16,measurement_contract_sha256=identity,
        measurement_masks_statistics_unchanged=True,binary_support_unchanged=True,
        all_identity_outputs_exact=True,all_outside_support_pixels_exact=True,
        full_strength_interior_matches_hard_operator=True,no_internal_zero_alpha_on_selected_pixels=True,
        parser_inferences=0,model_fits=0,calibration_fits=0,demo_changed=False)
    (out/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
