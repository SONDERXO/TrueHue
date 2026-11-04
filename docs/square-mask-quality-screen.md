# Development mask-quality screen

23 October 2026. Follow-up to [fresh square dataset](square-development-dataset.md).

## Decision

Follow-up: [removal-only hair-clean generation experiment](hair-clean-generation-results.md)
explains three reference-related holds and confirms five remaining training
mask-loss cases. No held pair was automatically promoted into the22-row manifest.

Do not widen the masking thresholds or fill missing regions automatically to
force the flagged examples through. Keep the masks unchanged and hold suspect
pairs in a separate development manifest. This screening does not revise human
review labels, the original 30-candidate table, runtime behavior or final scope.

The screen checks every one of the 38 generated attempts, rather than only the
four examples already flagged by visual inspection. It retains 22 of 30 training
candidates and holds eight. Six training sources remain; all four training
variants of source12288 are held. No learner was fitted.

## Explicit rule and its limitations

For the whole generation region and each of its bounding-box quadrants with
at least 100 generation pixels, require:

- Estimation retains at least 50% of that region.
- Experimental correction support retains at least 80% of that region.
- Existing visual concerns also trigger a hold, even if the numerical rule passes.

These cutoffs are **exploratory**, selected after seeing development failures
and frozen before this batch was scored. They are not validated segmentation
standards or an independent test. No cutoff search or learned-score selection
was performed. Regions smaller than the minimum are reported but not scored.

The reference is the known synthetic generation mask, not annotated true skin.
Missing its pixels can indicate skin loss **or correct removal of mistakenly
included hair**. Therefore this is a consistency/reference-suitability screen,
not proof that correction should restore every reference pixel. Clean references
are used only in this development audit, never as runtime inputs or model features.
Passing also cannot detect every hair, paint or background error.

## Cases held

| Source | Training variants held | Reason |
| --- | --- | --- |
| 12288 | dark, color shift, unchanged, mild brightening | Upper-region support disagreement; color shift also loses substantial estimation coverage. Inspection confirms hair included in the generation region. Hair-veto removal is not itself a defect to undo. |
| 22211 | dark, color shift | Large upper-right estimation/correction loss; identified by applying the same rule to all pairs. |
| 22454 | dark | Sparse central/lower-face seed cannot support broad facial correction. |
| 62331 | color shift | Substantial estimation loss and incomplete correction coverage. |

Source19/color-shift is flagged too, but stays in development-validation, with
all three development attempts retained. Do not remove a difficult validation
case to improve a score. All four clipped stress attempts and the one original
exclusion retain their roles. No reserved-test source was examined.

Raw HSV/YCrCb checks on missed generation pixels show that color thresholds
account for much of the lost support. Other missed pixels pass raw thresholds
but disappear later; the audit does not isolate morphology, component selection,
crop geometry and anatomical exclusions from one another. Removing only one
threshold would neither solve all losses nor guarantee material exclusion.

## Selection effects

| Variant | Before screen | Screen-pass candidates |
| --- | ---: | ---: |
| Dark | 7 | 4 |
| Color shift | 6 | 3 |
| Bright/warm | 3 | 3 |
| Unchanged | 7 | 6 |
| Mild brightening | 7 | 6 |
| Total | 30 | 22 |

This favors inputs the current pipeline handles well. Do not present subsequent
results on this subset as results on all 30 examples, as representative skin-tone
performance, or as proof of a better algorithm. Preserve and report the held
cases separately. MST categories and subject independence remain unresolved.

## Artifacts and checks

- [All 38 screening previews](../outputs/square_mask_quality_v1/review-index.md)
- [Per-pair flags and threshold diagnostics](../outputs/square_mask_quality_v1/summary.json)
- `data/manifests/square_mask_quality_v1/screen_policy.json`
- `screen_pass_train.csv`: 22 original rows, unchanged field values.
- `held_train.csv`: eight original rows, unchanged field values.
- `source_group_folds.json`: six inner source-group plans, no fitting.

The two training manifests form an exact, disjoint partition of the original
30 rows; no validation/stress/excluded pair enters either. Hash checks preserve
original artifacts. Seven new tests cover regional loss despite a sufficient
pixel count, estimation failure hidden by correction expansion, additions outside
the reference, sparse regions and invalid masks. Full suite: **454 passed**.

Reproduction: `venv/Scripts/python.exe scripts/53_screen_square_mask_quality.py`
(refuses to overwrite existing outputs).

The immediate quality disposition is now recorded: hold the eight pairs, retain
22 as exploratory screen-pass candidates, and leave all historical evidence
intact. Before final training, resolve reference-mask contamination and confirm
a final eligibility policy; these exploratory cutoffs do not supply approval.
Any later mask-fix experiment should be versioned and evaluated on held cases
as well as retained ones, including paint/hair regression checks. Do not tune
until the same reviewed cases pass or silently promote held cases into fitting.
