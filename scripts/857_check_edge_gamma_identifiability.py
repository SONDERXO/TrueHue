"""Generated scalar edge counterexamples only; no photo/CRF estimator or fit."""
from pathlib import Path
import hashlib,json,math

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/edge_response_cue_feasibility_v1'

def main():
    if OUT.exists():raise FileExistsError('Preserve candidate check')
    irradiance_codes=list(range(20,221,10));examples=[]
    for exponent in [.7,1/.7]:
        # World A: an acceptable source already has this camera/rendering response.
        acceptable_A=[round(255*(k/255)**exponent) for k in irradiance_codes]
        input_A=acceptable_A.copy()  # No added distortion; desired controls identity.
        # World B: a different acceptable source uses the identity response.
        acceptable_B=irradiance_codes.copy()
        input_B=[round(255*(k/255)**exponent) for k in acceptable_B]
        assert input_A==input_B and acceptable_A!=acceptable_B
        # The observable total response exponent is the same in both worlds.
        assert math.isclose(exponent*1.,1.*exponent)
        examples.append(dict(total_response_exponent=exponent,edge_input_codes=input_A,
            world_A=dict(source_response_exponent=exponent,added_gamma=1.,reference_codes=acceptable_A,nominal_inverse_gamma=1.),
            world_B=dict(source_response_exponent=1.,added_gamma=exponent,reference_codes=acceptable_B,nominal_inverse_gamma=1/exponent),
            exact_identical_observed_RGB8_codes=True,different_reference_targets=True))
    OUT.mkdir()
    (OUT/'generated_counterexamples_ONLY.json').write_text(json.dumps(examples,indent=2)+'\n')
    files=['docs/oblique-identity-route-diagnosis-2026-11-12.md',
        'docs/source-transfer-repair-review-2026-11-12.md',
        'scripts/857_check_edge_gamma_identifiability.py']
    (OUT/'verification_PRIVATE.json').write_text(json.dumps(dict(passed=True,
        status='EDGE_CRF_AS_STANDALONE_ADDED_GAMMA_REPAIR_NOT_QUALIFIED',generated_world_pairs=2,
        scalar_edge_samples_per_world=21,identical_observed_codes=42,scientific_rows=0,
        caveat='Counterexamples are permitted response/source models, not demonstrated contradictions in actual TrueHue data; no claim all edge-derived features fail.',
        estimator_implemented=False,photos_read=0,real_fits=0,predictions=0,weights_downloaded=False,
        input_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}),indent=2)+'\n')
    print('PASS: two generated21sample pairs have identical RGB8 inputs and different correct restoration targets. No dataset reads.')

if __name__=='__main__':main()
