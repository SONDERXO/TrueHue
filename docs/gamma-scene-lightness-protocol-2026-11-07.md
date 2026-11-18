# Fixed gamma scene-lightness restriction

7 November 2026. User says “Okay lets do that” after the completed saved-trace
diagnosis and recommendation to repair exposure grouping. This specifies one
bounded comparison before fitting; no sweep, new cohort or app adoption.

## Hypothesis and change

Two clean failures were routed by whole-scene lightness to strongly non-neutral
gamma leaves. The latest surviving clean route uses scene median lightness at
all three splits despite passing leaf ranges. Test whether gamma can recover
exposure without the three absolute scene lightness percentiles: scene_l_p10,
scene_l_p50, scene_l_p90. This is not a claim that all remaining inputs are free
of scene or acquisition cues, nor a proof of background causality.

Set these three columns to zero in gamma fitting only, preserving the full
12-feature interface and forbidding these indices in exported gamma splits.
Keep original facial Lab, ITA, estimated MST, scene chroma ratios and clipping
fractions. Reuse original gain-head artifacts unchanged. Same gamma-target
standardization, unweighted depth3, random_state42, min_samples_leaf1 and all
other existing SETTINGS. Fit exactly ten saved held-publisher folds plus one
full model. No gain/gate/MST/target refits or nested correction fits.

## Fixed control and support policy

Apply the previously frozen joint-neutral-support policy to the revised gamma
tree and unchanged gain tree: exact neutral output per leaf with a fitting clean
member; full identity if either query lies outside its leaf's inclusive float32
fitting range on ANY of all 12 original axes. Recompute only leaf membership and
derived metadata, using original, unzeroed fitting features. The three excluded
gamma axes remain in this pre-existing support guard. This isolates predictor
restriction from a simultaneous support-rule relaxation. No margins or tuning.

Keep original gate coefficients, scores and decisions. Gate transfer mismatch
is a limitation; this is NOT a matched-gate training study. Verify held-key
exclusion of both predictor and gate. Report ungated and retained-gate paths
separately, never select the ungated path after observing its results.

## Frozen comparisons

Use all 1,428 saved attempts across working256 folds and borrowed, actual-input
and fallback native224 masks. Preserve original features, targets, images,
reference regions, masks, recipes, measurement failures and no-op handling.
Compare no correction, original retained split model, previous joint policy,
and revised joint policy. Report clean/core/stress separately: RGB MAE and
relative CIEDE2000, photo/equal-key means, harm/changed counts, support abstentions,
missing features and lost useful actions. The main isolated contrast is against
the previous joint policy, not only the older retained model. Save previous
policy aggregates/record bindings alongside the comparison.

The clean screen remains zero altered scored clean photos. Also explicitly
report changes to the remaining ungated clean failure and previous severe
darkening case, plus the recovered warm fallback case without claiming a
missing facial reference. A clean pass alone is insufficient: judge whether
core and stress recovery improve versus the previous policy and retained model.
All cohorts are exposed development data; repeated conditions from 54 originals
are not independent photos or people.

## Verification and stop

Test feature invariance and frozen gains on generated fixtures before real fits.
Verify all 11 saved fits: normalization, raw leaf target means, exclusions,
forbidden splits and gain equality. Independently reconstruct support metadata,
all decisions and RGB8 outputs/metrics, outside-mask protection and input hashes.
Review all 63 fixed prior boards with the revised output: all scored clean
photos in the two nonduplicate contexts, first available core/stress per context,
and the recovered warm case. Report any additional outcome-selected boards.

Save new private outputs, preserve old artifacts, and stop after this comparison.
No automatic next feature/weight/loss/threshold/capacity/range/gate fit, annotation,
dataset search, scientific admission, sharing, contact, commit or deployment.
