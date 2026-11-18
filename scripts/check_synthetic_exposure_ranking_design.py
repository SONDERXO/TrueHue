"""Generated algebra and expected allocation only; no training or image I/O."""
import json
from fractions import Fraction as F
from pathlib import Path


SOURCES = ('16061', '29617', '32685', '39568', '46795', '48879',
           '49131', '52445', '53146', '54632', '59807')
ROLES = ('identity', 'colour_only', 'exposure_under', 'exposure_over',
         'combined_under', 'combined_over')
PREFERENCES = (('identity', 'exposure_under'),
               ('identity', 'exposure_over'),
               ('colour_only', 'combined_under'),
               ('colour_only', 'combined_over'))


def vector(exposure, cast=F(0), nuisance=F(0), curved=True):
    # These are invented mathematical coordinates, never encoder features.
    return (nuisance, cast, exposure,
            -exposure * exposure if curved else F(0)) + (F(0),) * 4092


def difference(a, b):
    return tuple(x - y for x, y in zip(a, b))


def main():
    out = Path('outputs/synthetic_exposure_ranking_design_v1')
    out.mkdir(parents=True, exist_ok=False)
    folds = []
    held_pairs = []
    for held in SOURCES:
        fit_sources = [s for s in SOURCES if s != held]
        fit = [(s, role) for s in fit_sources for role in ROLES]
        test = [(held, role) for role in ROLES]
        fit_pairs = [(s, a, b) for s in fit_sources for a, b in PREFERENCES]
        test_pairs = [(held, a, b) for a, b in PREFERENCES]
        assert not set(fit) & set(test)
        assert len(fit) == 60 and len(test) == 6
        assert len(fit_pairs) == 40 and len(test_pairs) == 4
        assert all(s != held for s, _, _ in fit_pairs)
        held_pairs.extend(test_pairs)
        folds.append(dict(held_source=held, fitting_sources=fit_sources,
                          fit_records=fit, held_records=test,
                          fit_preferences=fit_pairs, held_preferences=test_pairs))
    assert len(set(held_pairs)) == 44

    curved_margins = []
    for nuisance in (F(-7), F(0), F(13)):
        for cast in (F(0), F(3, 10)):
            clean = vector(F(0), cast, nuisance)
            for t in (F(-1, 2), F(1, 2)):
                edited = vector(t, cast, nuisance)
                # Fixed illustrative score selects coordinate 3; NO fitted head.
                margin = clean[3] - edited[3]
                assert margin == F(1, 4)
                curved_margins.append(str(margin))

    clean = vector(F(0), curved=False)
    low = vector(F(-1, 2), curved=False)
    high = vector(F(1, 2), curved=False)
    d_low, d_high = difference(clean, low), difference(clean, high)
    assert any(d_low) and all(a + b == 0 for a, b in zip(d_low, d_high))
    # Consequently w.d_low + w.d_high == 0 for EVERY linear w.
    # Both margins cannot be strictly positive.

    # Different acceptable source appearances can require opposite preferences
    # on identical features. NO deterministic scorer can satisfy both.
    a_original = vector(F(-1, 2))
    a_over = vector(F(0))
    b_original = vector(F(0))
    b_under = vector(F(-1, 2))
    assert a_original == b_under and a_over == b_original
    assert all(a + b == 0 for a, b in zip(
        difference(a_original, a_over), difference(b_original, b_under)))

    result = dict(
        status='GENERATED_DESIGN_CHECKS_PASS_NOT_MODEL_QUALITY',
        generated_fixture=True, feature_width=4096,
        actual_feature_reads=0, image_reads=0, trained_heads=0,
        actual_correction_fits=0, fixed_weight_examples_not_fits=True,
        expected_folds=len(folds), fit_records_per_fold=60,
        fit_preferences_per_fold=40, held_preferences_total=44,
        held_preferences_are_independent_votes=False,
        pair_order_is_explicit_synthetic_restoration_not_JOD=True,
        useful_curvature_example_margins=curved_margins,
        affine_response_opposing_margin_certificate=True,
        identical_feature_conflicting_preference_certificate=True,
        qualifies_real_encoder_curvature=False,
        actual_source_file_hash_binding_complete=False,
    )
    for name, data in (('expected_allocation.json', folds),
                       ('generated_verification.json', result)):
        (out / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
