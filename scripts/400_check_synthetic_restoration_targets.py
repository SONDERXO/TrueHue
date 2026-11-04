"""Paper-scope synthetic target checks; generated arrays only, no fits/adoption."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import cv2
import numpy as np
from src.distortion_generation.paper_gamma import transform_rgb
from src.correction.seamless_blend import inward_alpha, apply_blended

OUT = ROOT / 'outputs/synthetic_restoration_target_check_v1'


def inverse_direct(parameters):
    gamma, red, blue = parameters
    return [1/gamma, red**(-1/gamma), blue**(-1/gamma)]


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    OUT.mkdir()
    sources = ['Thesis Proposal Document.pdf', 'src/distortion_generation/paper_gamma.py',
               'src/correction/seamless_blend.py', 'scripts/398_ppr10k_smooth_boundary_check.py']
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
    protocol = dict(task='synthetic distorted-original photographic restoration, not intrinsic colour',
        input='deterministic generated RGB ramps, no dataset photos',
        baseline='three direct-exponent paper controls only',
        parameters=[[1.,1.,1.],[1.4,.85,1.05],[.7,1.5,.8]],
        scope='arithmetic diagnostics; not Table2 augmentation adoption, target labels or ML training',
        questions=['unclipped float inverse','clipping loss','RGB8 quantisation','blended inverse residual','exact neutral identity','frozen smooth candidate neutral alteration'],
        source_sha256=hashes)
    (OUT/'protocol.json').write_text(json.dumps(protocol, indent=2))
    yy, xx = np.indices((96,96))
    reference = np.stack([xx/95, yy/95, ((xx+yy)%96)/95], axis=2)
    mask = np.zeros((96,96),np.uint8);mask[8:88,8:88]=255
    alpha, _ = inward_alpha(mask, face_width=80)
    fractional = (alpha>0)&(alpha<1)
    reference8 = np.rint(reference*255).astype(np.uint8)
    original = reference.copy(); rows=[]
    for parameters in protocol['parameters']:
        inv = inverse_direct(parameters)
        raw = transform_rgb(reference,*parameters,clip=False)
        distorted = np.clip(raw,0,1)
        restored = transform_rgb(distorted,*inv)
        valid = np.all((raw>=0)&(raw<=1),axis=2)
        float_error = np.abs(restored-reference)
        assert np.max(float_error[valid]) < 1e-12
        distorted_blend = reference*(1-alpha[...,None])+distorted*alpha[...,None]
        restored_blend = distorted_blend*(1-alpha[...,None])+transform_rgb(distorted_blend,*inv)*alpha[...,None]
        distorted8 = np.rint(distorted*255).astype(np.uint8)
        restored8 = np.rint(transform_rgb(distorted8.astype(float)/255,*inv)*255).astype(np.uint8)
        result = dict(parameters=parameters,inverse=inv,
            clipped_channel_samples=int(((raw<0)|(raw>1)).sum()),
            float_unclipped_max_error=float(float_error[valid].max()),
            float_all_mean_error=float(float_error.mean()),
            RGB8_reconstruction_MAE_codes=float(np.abs(restored8.astype(float)-reference8).mean()),
            fractional_edge_mean_error=float(np.abs(restored_blend-reference)[fractional].mean()),
            outside_alpha_exact=bool(np.array_equal(restored_blend[alpha==0],reference[alpha==0])))
        assert result['outside_alpha_exact']
        if parameters==[1.,1.,1.]:
            neutral,_,_=apply_blended(cv2.cvtColor(reference8,cv2.COLOR_RGB2BGR),mask,parameters,face_width=80)
            assert np.array_equal(neutral,cv2.cvtColor(reference8,cv2.COLOR_RGB2BGR))
        rows.append(result)
    assert np.array_equal(reference,original)
    spec=importlib.util.spec_from_file_location('saved_smooth',ROOT/sources[-1])
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    neutral_smooth=module.soft_boundary(reference)
    neutral_smooth8=np.rint(neutral_smooth*255).astype(np.uint8)
    assert not np.array_equal(neutral_smooth8,reference8)
    assert any(r['fractional_edge_mean_error']>1e-5 for r in rows[1:])
    report=dict(cases=rows,baseline_neutral_RGB8_exact_identity=True,
        frozen_four_control_smooth_neutral_exact_identity=False,
        smooth_neutral_changed_channel_codes=int(np.count_nonzero(neutral_smooth8!=reference8)),
        decision='Analytic inverse only verified for unclipped unblended float baseline. Not valid full blended/quantised labels.',
        correction_training_ready=False,new_fits=0,new_photo_access=0,new_inference=0,
        no_candidate_or_runtime_change=True)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (OUT/'results.json').write_text(json.dumps(report,indent=2))
    (OUT/'sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()},indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
