# Can the existing features distinguish clean and overexposed photos?

8 November 2026. A saved-training-data audit, without fitting another model.

**Partly.** Some useful overexposed training conditions have feature values outside the clean-photo ranges. Many remain inside every range. A simple range guard would therefore leave much of the lost recovery unresolved.

## What was checked

We examined the eight distinct fitting branches implicated by the [lost-benefit diagnosis](expanded-lost-benefit-diagnosis-2026-11-08.md): one full-model branch and seven branches across the existing development folds. These branches were selected from previously observed failures, so this is exploratory diagnosis.

For each branch, we took the minimum and maximum of each of the 12 existing features across its clean fitting rows. We checked which useful overexposed fitting rows fell strictly outside those ranges. The ranges came only from fitting clean rows. No thresholds were optimised, no split was selected, and no new model or evaluation prediction was produced.

“Useful” here means at least one existing action has lower saved RGB training cost than identity on that row. It is an optimistic action-availability check using the training reference, not a deployable decision or a naturalness assessment.

## Results

| Full model's affected branch | Training-condition count |
| --- | ---: |
| All conditions | 562 |
| Clean conditions | 102 |
| Useful overexposure conditions | 174 |
| Outside at least one clean feature range | 75 (43.1%) |
| Inside every clean feature range | 99 (56.9%) |

The 174 conditions include repeated distortions of originals; they are not 174 independent photos or people. Within this branch, facial brightness alone puts none of these 174 outside the clean brightness range. Whole-scene median brightness puts 47 outside its clean range; feature-specific counts overlap and must not be added.

Across the seven affected fold branches, the corresponding totals are 1,174 useful overexposure row occurrences: 508 outside at least one range and 666 inside all ranges. These repeatedly reuse training originals and are not additional independent evidence.

No useful overexposed row exactly matches a clean row on all 12 float32 feature values in these branches. That does **not** establish a robust separating rule. Likewise, being inside all individual ranges does **not** prove that combinations of features cannot separate the rows.

## Implication and next step

This supports checking the decision structure rather than automatically discarding the existing correction controls or loosening clean protection. Every lost-benefit case already reaches the current depth limit of three, while the saved rows contain some remaining separation information.

A justified next experiment is **one fixed comparison allowing depth four instead of three**, retaining the expanded training rows, frozen MST calibrations, features, actions, clean constraints and old evaluation cases. It should use the same 11 fitting configurations and unchanged joint acceptance requirements. This is a proposed single change, not a depth sweep or an assurance that one extra decision will solve the problem. The audit does not authorise starting that fit automatically.

The candidate remains frozen and unadopted. The separate eight-group, 24-photo holdout remains byte-unread. Any next candidate must pass the existing development requirements before that holdout is opened. Mask quality and visible correction boundaries remain separate unresolved issues.

## Verification

Script 620 produced the fixed-range audit. Script 621 independently recomputed the float32 clean ranges and row classifications using scalar comparisons: **4,384 row occurrences across eight leaves passed**, with bound source hashes unchanged. No new fits, image-model inference, source-image reads or holdout reads occurred. Private artifacts remain in `outputs/expanded_training_separability_v1`.
