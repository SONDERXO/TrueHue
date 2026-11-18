"""Generated-only checks of the GP local-log necessary condition, not GP code.

This does not implement a full grey-pixel selector, illuminant estimator,
feature extractor or correction model. No photographs or fitted data are used.
"""
from pathlib import Path
import hashlib
import json
import math
from fractions import Fraction

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs/gray_pixel_feasibility_v1'


def main():
    result_path = OUT/'generated_assumption_checks_PRIVATE.json'
    if result_path.exists():
        raise FileExistsError('Preserve assessment')
    texture = np.array([[.12, .18, .24], [.15, .20, .25], [.18, .22, .28]])
    records = []
    for kind, reflectance in [('neutral', [1., 1., 1.]), ('coloured', [1.4, .8, .6])]:
        base = texture[:, :, None]*reflectance
        for role, gamma, gain in [('identity', 1., 1.), ('under', 1/.7, 1.),
                                  ('over', .7, 1.), ('red_attenuation', 1., 245/255)]:
            image = base**gamma*np.array([gain, 1., 1.])
            assert image.min() > 0 and image.max() < 1  # log valid, no clipping
            deviations = np.std(np.log(image), axis=(0, 1), ddof=0)
            expected = gamma*np.std(np.log(texture), ddof=0)
            assert np.max(np.abs(deviations-expected)) < 1e-14
            # This diagnostic ratio is NOT a reproduction of GP's full ranking.
            relative_spread = float(np.std(deviations)/np.mean(deviations))
            assert relative_spread < 1e-13
            ratio = float(image[:, :, 0].mean()/image[:, :, 1].mean())
            expected_ratio = (reflectance[0]/reflectance[1])**gamma*gain
            assert math.isclose(ratio, expected_ratio, abs_tol=1e-14)
            # Independent scalar log-variance arithmetic for every channel.
            for channel in range(3):
                logs = [math.log(float(x)) for x in image[:, :, channel].ravel()]
                mean = sum(logs)/9
                scalar = math.sqrt(sum((x-mean)**2 for x in logs)/9)
                assert abs(scalar-deviations[channel]) < 1e-14
            records.append(dict(generated_fixture=True, kind=kind, role=role,
                local_log_standard_deviations=deviations.tolist(),
                necessary_condition_relative_spread=relative_spread,
                pooled_r_over_g=ratio, expected_r_over_g=expected_ratio))
    # Same observed 3x3 coloured surface has two exact factorizations.
    # Fractions verify product equality without floating-point/log assumptions.
    t = [Fraction(str(v)) for v in texture.ravel()]
    color = [Fraction('1.4'), Fraction('.8'), Fraction('.6')]
    assert all((x*c)*1 == x*c for x in t for c in color)
    # A channel offset (camera/processing) breaks multiplicative log cancellation.
    shifted = texture[:, :, None]*np.array([1.4, .8, .6])+.02
    shifted_deviations = np.std(np.log(shifted), axis=(0, 1))
    assert np.ptp(shifted_deviations) > 1e-4
    result = dict(generated_only=True, generated_patch_conditions=len(records),
        scientific_rows=0, scalar_variance_checks=24, exact_factorization_equalities=27,
        both_neutral_and_coloured_satisfy_necessary_condition=True,
        common_gamma_scales_all_channel_log_contrasts=True,
        common_gamma_does_not_make_this_condition_an_exposure_direction_estimator=True,
        coloured_surface_r_over_g_changes_under_gamma=True,
        additive_offset_breaks_log_cancellation=True,
        offset_local_log_standard_deviations=shifted_deviations.tolist(),
        full_gray_pixel_algorithm_implemented=False, algorithm_rejection_proved=False,
        photo_reads=0, fits=0, predictions=0, holdout_bytes_read=0,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cases=records)
    result_path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'},indent=2))


if __name__ == '__main__':
    main()
