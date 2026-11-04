# Proposed31-pair controlled-development stage

24 October2026. Follow-up to [candidate variant checks](candidate-variant-checks.md).
Status: staged and verified, **not fitted**, not the final thesis dataset.

## Staged data

- Existing22 rows are preserved with exactly the same field values.
- Proposed additions:14272's five fixed variants and84897's four unclipped
  variants, nine pairs from two new training sources.
- Combined31 pairs represent eight source/known-duplicate groups, with eight
  leave-one-group-out fold plans. No models were fitted from these plans.
- Combined variants: six dark, five color shift, four bright/warm, eight
  unchanged and eight mild brightening.

The new rows reference existing saved256 images/masks rather than duplicating
datasets. The same baseline HSV/YCrCb Lab/ITA measurements are recomputed from
distorted inputs; no YCrCb-only feature substitutions or clean-reference features
enter X. Inverse gamma/red/blue targets come from the fixed generation settings.
All nine additions are unclipped, feature-valid and pass the existing exploratory
retention screen. The existing additions-only correction-support policy is fixed.

## Eligibility and exclusions

This is a separately versioned **development proposal**, not a change to the
master training cohort or human labels. The new sources remain human-pending
and final `training_ready=False` in the master audit.14272's facial-hair/jaw/
lighting and84897's pose/boundary caveats remain documented. Numerical screening
does not certify calibrated reference color or pixel-accurate skin selection.

All20 prior screening attempts remain in the ledger:

| Disposition | Attempts |
| --- | ---: |
| Proposed additions | 9 |
| Held/not staged | 9 |
| Clipped stress/not staged | 2 |

Neither3705 nor39108 enters the proposed stage. Their issues are preserved;
84897/bright and39108/bright stay stress-only. The original eight held training
pairs remain excluded. Source20555's color failure is also preserved in its
separate follow-up report; it is not quietly added here.

All selected sources retain their TRAIN allocation and original duplicate-group
IDs. An additional eight-source decoded-pixel/dHash check found no candidate
links at Hamming distance<=4. This does not establish subject independence.
The new sources were already recorded as development-exposed; they cannot be
presented as a fresh final holdout. No reserved-test or external validation
image was processed for staging.

## Fixed next comparison plan

For each of eight source-group folds, evaluate the **same held-source probes**
using no correction and two depth3/seed42 trees:

1. Fit the baseline only on the remaining original22 IDs.
2. Fit the expansion on the remaining31 IDs.

Exclude every variant/duplicate of the held source from both fits. Keep features,
targets, correction support and scoring regions identical. Report original22
probes and new9 probes separately, alongside per-variant and equal-source results.
This is a fixed development data-coverage comparison, not independent final
validation or an automatic replacement-model selection.

No changes to the runtime model, feature schema or neck behavior follow from
staging. The [face-and-neck requirement](face-and-neck-correction-requirement.md)
and unresolved MST/dataset/method distinctions remain recorded separately.

## Files and checks

- `data/manifests/controlled_expansion31_v1/staged_train.csv`
- `proposed_additions.csv`, `all_twenty_attempts.json`, `source_group_folds.json`
  and `comparison_plan.json` in that same directory.
- [Stage summary](../outputs/controlled_expansion31_v1/summary.json)
- [Readiness checks](../outputs/controlled_expansion31_v1/readiness_checks.json)
- [Source evidence links](../outputs/controlled_expansion31_v1/review-index.md)
- Script68: `scripts/68_stage_development_expansion.py` (refuses overwrite).

Verified31x4 features,31x3 targets,22 original row strings unchanged, nine exact
saved-input generation recipes/clipping counts, all31 recomputed feature vectors,
eight disjoint folds covering every row once, no original-held overlap and
unchanged input/model/table/review artifacts. No production runner was redirected.

Existing full suite: **464 passed**.

Follow-up: [completed source-group comparison](development-expansion-comparison.md). The expanded set did not improve overall performance; runtime model unchanged.
