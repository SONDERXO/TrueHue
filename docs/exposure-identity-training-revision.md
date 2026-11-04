# Exposure and unchanged-image training revision — 23 October 2026

Before any training comparison, resolve the method checkpoint in
[thesis-method-alignment.md](thesis-method-alignment.md). This development table
does not implement the proposal's full MST-conditioned training procedure.

The separately versioned `controlled_training_v2` table is built. It contains
**30 eligible training pairs from the same seven training sources**, adding
14 checked inputs to the original16. No new learner was fitted or selected.

## What was added

Each training source received two fixed probes, specified before the build:

- **Unchanged control:** gamma1, red gain1, blue gain1. The decoded saved input
  is exactly equal to the decoded source. The target is `[1,1,1]`.
- **Mild exposure-only brightening:** gamma1.10, red gain1, blue gain1. The known
  inverse target is approximately `[0.90909,1,1]`.

These are the ordinary source photos as synthetic references, not calibrated
real-world color ground truth. An unchanged control means no synthetic transform,
not a human judgment that the photo never needs correction.

The original source-generation skin masks and binary generation scope are
unchanged. Features are recomputed from each saved input through the existing
estimator and `material_hair_veto_v1` runtime. Only the declared four input Lab/ITA
columns enter the model matrix. Existing tree predictions were ignored for target
construction; known inverse parameters supply targets. The frozen runtime was
called to check availability, features and masks, not to train or score a learner.

## Outcome

| Eligible training variant | Original | Revised |
| --- | ---: | ---: |
| Darkened | 7 | 7 |
| Color shift | 6 | 6 |
| Bright/warm | 3 | 3 |
| Mild exposure-only brightening | 0 | 7 |
| Unchanged control | 0 | 7 |
| Total | 16 | 30 |

All14 new attempts succeeded and introduced **zero clipped pixels**. Every
unchanged input matches its source exactly; mild inputs preserve all pixels
outside generation support and never darken a generated pixel. Applying known
inverse parameters on generation support reconstructs within one uint8 channel
level, including quantization. This is an operator check, not learned performance.

The original16 training rows retain their exact field values. The three
development-validation rows, four clipped-stress rows and one original excluded
row are copied byte-for-byte into the revised manifest directory. No stress row
was promoted into fitting, and no validation or reserved-test source was augmented.
The complete audit ledger contains38 original/new attempts.

The combined training table deliberately contains two generation-policy versions:
`controlled_skin_mask_v1` for original rows and `controlled_exposure_identity_v1`
for additions. Both retain the same transform and estimation-mask version. This
does not change historical provenance to pretend all examples used a new recipe.
The old prototype training runner is not silently redirected to these tables.

## Source-grouped checks prepared

Seven inner folds are written to `source_group_folds.json`. Each holds one known
duplicate/source group out of the training-source pool; all variants and known
duplicates stay together. Every eligible training pair is held out exactly once.
The external development source19 and clipped stress rows never enter these
folds. Subject identity separation remains unverified; source grouping is not a
claim that every group depicts a different person.

These are fold plans only. No models were fitted and no score improvement has
been claimed. A suitable next comparison is original versus revised data using
the same fixed tree settings and source-grouped checks. Report shared original
probes and new controls separately; do not choose settings by repeatedly checking
the one-source external development set.

## Review and remaining quality issues

The [new input/mask review index](../outputs/controlled_training_v2/review-index.md)
and [training coverage chart](../outputs/controlled_training_v2/training_coverage.png)
are available. Previews12288,22454,62331 and75027 were visually inspected. They
show saved inputs and mask overlays, not newly learned corrections or human
approval. Other new inputs received numerical and runtime checks.

The historical mask problems were not solved by this data revision. The review
pack includes `prior_mask_diagnostics.csv` for all16 original training pairs,
including22454/dark,12288/color-shift and62331/color-shift residuals. These are
historical diagnostics, not quality labels for the new mild/control inputs.
No original human decision or source eligibility was changed.

## Artifacts and verification

Tables and policy: `data/manifests/controlled_training_v2/`.
Saved inputs, masks, runtime checks and previews: `outputs/controlled_training_v2/`.
The summary records original input/model/human-label hashes and new table hashes.

Reproduce from the project root:

```text
venv/Scripts/python.exe scripts/46_build_exposure_identity_table.py
venv/Scripts/python.exe scripts/47_check_exposure_identity_table.py
```

Existing tables and reports are protected from overwrite.447 tests passed,
including prevention of validation/stress rows in inner folds, keeping known
duplicate sources together and rejecting inconsistent IDs. Actual checks verified
the30×4 feature matrix,30×3 targets, all14 saved inputs, exact identity controls,
fold separation, frozen-table byte equality and unchanged original hashes.

The correction mask option, four-feature schema, approved thesis scope, current
model weights, Android files and final test set remain unchanged. This is a small
development data revision, not a final thesis training set or evidence that the
exposure errors have already improved.
