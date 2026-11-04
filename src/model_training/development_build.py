"""Fail-closed data contract and activation evidence for development tree builds."""
import math
from src.data_preparation.controlled_training_table import FEATURES, TARGETS
from src.model_training.control_recipe_comparison import plan_control_folds
from src.distortion_generation.generate_distortions import inverse_parameters

SETTINGS = dict(max_depth=3, random_state=42, min_samples_leaf=1)


def validate_build_rows(rows, eligible_ids, held_ids):
    """Return a fixed-order fitting set after exact routing/target validation."""
    # Reuses source/group consistency checks and retains diagnostic-only groups.
    plan_control_folds(rows, eligible_ids, held_ids)
    if len({r['pair_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate pair ID')
    for row in rows:
        for key in FEATURES + TARGETS:
            value = row[key]
            if isinstance(value, bool) or not math.isfinite(float(value)):
                raise ValueError('Finite numeric features and targets required')
        targets = [float(row[k]) for k in TARGETS]
        if min(targets) <= 0:
            raise ValueError('Positive correction targets required')
        gamma, red, blue = [float(row['distortion_' + k]) for k in ('gamma', 'red_gain', 'blue_gain')]
        if not all(math.isfinite(v) and v > 0 for v in (gamma, red, blue)):
            raise ValueError('Positive finite distortion metadata required')
        inverse = list(inverse_parameters(gamma, red, blue).values())
        if any(not math.isclose(a, b, rel_tol=0, abs_tol=1e-12) for a, b in zip(targets, inverse)):
            raise ValueError('Targets disagree with known inverse distortion')
    eligible = set(eligible_ids)
    fitting = sorted((dict(r) for r in rows if r['pair_id'] in eligible), key=lambda r: r['pair_id'])
    if len({r['source_image_id'] for r in fitting}) < 2:
        raise ValueError('At least two fitting sources required')
    return fitting


def activation_gate(aggregate):
    """Use held-source recipe metrics only; never score all-row fit as CV."""
    def one(method, variant):
        matches = [r for r in aggregate if r['scope'] == 'primary' and r['method'] == method and r['variant'] == variant]
        if len(matches) != 1 or matches[0]['evaluation_kind'] != 'source_held_out':
            raise ValueError('Unique source-held-out evidence required')
        row = matches[0]
        for key in ('mean_ciede2000', 'equal_source_mean_ciede2000'):
            if not math.isfinite(float(row[key])) or row[key] < 0:
                raise ValueError('Valid error evidence required')
        if not isinstance(row['pairs'], int) or row['pairs'] <= 0:
            raise ValueError('Nonempty evidence required')
        if not isinstance(row['worsened_pairs'], int) or not 0 <= row['worsened_pairs'] <= row['pairs']:
            raise ValueError('Invalid harm denominator')
        return row
    baseline = one('no_correction', 'all')
    candidate = one('with_controls', 'all')
    if candidate['pairs'] != baseline['pairs'] or candidate['sources'] != baseline['sources']:
        raise ValueError('Baseline and candidate denominators differ')
    unchanged, mild = one('with_controls', 'identity_control'), one('with_controls', 'mild_bright_exposure')
    checks = dict(pair_mean_improves=candidate['mean_ciede2000'] < baseline['mean_ciede2000'],
                  equal_source_mean_improves=candidate['equal_source_mean_ciede2000'] < baseline['equal_source_mean_ciede2000'],
                  no_unchanged_harm=unchanged['worsened_pairs'] == 0,
                  no_mild_harm=mild['worsened_pairs'] == 0)
    return dict(status='passes_development_quality_gate' if all(checks.values()) else 'held_quality_failure',
                checks=checks, production_ready=False,
                source_held_out_evidence=dict(baseline=baseline, candidate=candidate,
                                              unchanged=unchanged, mild=mild),
                limitation='Even numerical success would not establish MST, final data/mask/reference validity or final thesis evaluation.')
