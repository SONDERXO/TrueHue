# First real photographic correction-tree result — 6 November 2026

The authorized nested experiment is complete. Ten actual correction trees were
fitted and evaluated on held publisher keys. They improve average distorted
image error but harm every scored clean image. **This candidate fails clean
preservation and is not adopted.** This is learned prediction evidence, unlike
the earlier reference-aware operator fits.

## Exact experimental scope

Thirty fixed Stellenbosch photos,10publisher keys,14existing cases each:
420attempts. One failed original contributes14unavailable attempts, retained
without invented image-error scores. For29available originals, the saved
measurement mask is borrowed as fixed binary synthesis/application/scoring
support. This is explicitly a restricted measured-region diagnostic, not the
whole-face/neck app policy, a new automatic mask or an actual-input mask test.
Masks may still contain beard/objects; unchanged pixels outside them do not
establish object protection. Hard mask boundaries are visible in the outputs.

Every distorted image's own RGB provides Lab/ITA statistics on that support.
All29clean measurements exactly replay saved original features; the automatic
1000normalized-pixel guard remains. No source-statistic substitution. One common
engineering severity is used across all sources, unrelated to source MST labels.

There were377nonclean target-fit calls and29neutral shortcuts. Targets were
available for328nonclean cases plus29clean cases. Forty-nine stress inputs were
degenerate for target fitting and have no valid target. These are retained,
excluded from supervised fitting and displayed as unchanged target-fit fallbacks;
the fallback is not an oracle success. Nine stress measurements had undefined
ITA and also remain unchanged predictive fallbacks. In total397rows have
features,357have both features and targets, and406have scoring support.

## Nested fitting and outputs

For every outer held key, a contextual ridge uses clean measurements from other
keys only. Each correction-training key's MST features come from a ridge that
excludes both that key and the outer key. Identical exclusion sets are cached:
55actual MST ridge fits, not an all-data deployed estimator. Input features are
the four Lab/ITA values plus continuous predicted MST. Across held predictions,
113contextual estimates require explicit clipping to1–10, showing a distribution
shift from the earlier clean-only experiment; no rounded index is introduced.

Ten depth3/seed42/minleaf1 target-standardized trees fit three controls. There
are397held predictions and nine unchanged feature-failure outputs on406scored
cases;14original failures lack support. No own-key score enters its outer model
or its inner training estimate. All fitting normalization uses fitting targets
only. Reference pixels supply supervision/scoring, not inference features.

## Errors and harm

RGB8 MAE uses a0–255channel scale on the full fixed support. Means below use
scored operational outcomes, including unchanged feature failures. Original
failures without support stay in the attempt counts, not the MAE denominator.

| Layer | Scored / attempts | Predicted | Input MAE | Tree MAE | Target-fit-or-fallback MAE |
| --- | ---: | ---: | ---: | ---: | ---: |
| Clean |29/30|29|0|10.369|0|
| Core |232/240|232|20.739|18.843|0.114|
| Stress |145/150|136|52.565|34.035|21.008|

Equal-key input→tree MAE: clean0→10.382, core20.657→18.976,
stress52.283→34.180. Relative CIEDE2000 input→tree means: clean0→3.706,
core7.678→6.724, stress19.773→12.843. These are development descriptive
averages, not accuracy percentages, significance or independent generalization.

All29scored clean photos change and worsen. Ninety-eight of232core cases and
28of145stress operational outputs also worsen in RGB error. Mean improvement
does not outweigh or conceal these regressions. The fixed tree is not a usable
automatic correction model merely because some averages improve.

The read-only leaf audit finds all29held clean inputs route to leaves containing
nonclean training rows. Their predicted controls are pooled with distortion
targets rather than remaining neutral. This describes the fitted behavior; it
does not prove that deeper trees, new weights or a heuristic identity gate will
solve it. No such repair/search was run.

## Verification and visual findings

Script480generated/saved the experiment. Script481verified3213inner training
feature traces, all10outer exclusions and fitting-only target means/stds.
All406scored renderer/metric outputs replay without refitting; predicted controls
match the portable trees. Original sources and bound prior artifacts remain
hash-identical. Sixty focused existing continuous-interface, tree, target and
recipe tests pass in6.77seconds; no full-suite or phone check is claimed.

All58preselected available combined-cool-under/core and stress-combined-under
boards plus two explicit original-failure boards were inspected. Many core
tree outputs remain visibly dark relative to references despite the target-fit
column recovering them. Severe stress shadows/patches often remain in both
tree and target-fit fallback outputs. Sparse forehead-only support and glasses/
beard boundary uncertainty persist. These are assistant development observations,
not human ratings or full inspection of all420individual outputs.

Private gallery: `outputs/nested_correction_assessment_v1/review_PRIVATE.html`.
Saved rows/models/images/hashes: `outputs/nested_correction_diagnostic_v1/`.
No private photos, labels or artifacts were shared or published. All original
admission flags remain false; no production refit, Android change or final-method
adoption occurred. Author research/noncommercial, citation and no-redistribution
terms remain.

## Next substantive model question

The first real correction-tree fit now exists, and its failure is concrete:
clean preservation and separation of distortion from ordinary recorded colour.
Before proposing one bounded repair, inspect whether the current inference
features distinguish clean and distorted cases sufficiently and whether the
target/role design causes conflicting controls. Reuse these saved traces and
targets; do not start with another dataset, mask review, generated arithmetic
test, depth sweep, automatic identity threshold or favorable-subset refit.
This comparison is closed; a new fitting intervention needs its own explicit
fixed design and must retain clean, core and stress harm reporting.
