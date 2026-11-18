# Fitting-only green-feature preparation — 9 November 2026

Preparation passed for the selected
[green-channel design](green-channel-correction-design-2026-11-09.md).
All 890 fitting and twenty reserved-clean inputs are verified and feature-ready.
The mask-provenance gap is resolved by cached reconstruction, without changing
any mask or running a parser/FaceOcc forward. This completes a preparation
checkpoint; it is not a new model-performance result.

## Provenance and exact preservation

Scripts 682–684 use the exact 910 fitting/reserved case IDs from the approved
metadata preflight, in a new `outputs/fitting_green_features_v1` folder.
No image directory scan, source expansion or evaluation-only row was used.
The full fitting union includes cases used in existing outer-fold development
evaluation; their original configuration-specific exclusions remain intact.
No fitting use of later evaluation photos or final holdout was introduced.

The 227 normalized masks with inherited hashes passed direct verification.
The remaining 683 normalized masks match exact reconstructions from inherited
hash-bound parent masks, landmarks, alignment template, cached aligned images
and FaceOcc logits. Recomputed alignment matrices match the saved matrices.
No model was loaded for inference; cached logits were read with allow_pickle=False.

All 910 native mask projections match. Only 227 of those native masks also have
inherited hashes; the other 683 projections are corroborating equality checks,
not retroactive historical hash proof. Their normalized support provenance comes
from the reconstruction above. This clarifies the earlier readiness document's
expectation of a bound native projection: one must not assume a native hash
exists merely because the normalized hash was absent.

All 3,640 original facial Lab/ITA values reproduce exactly, with the same
normalized image, mask and 1,000-pixel guard. No clean/reference mask, correction
alpha or scoring-union mask was substituted. Newly recorded hashes bind the
prepared assets going forward; original artifacts were not rewritten.

## Training-only behaviour

Each fitting variant was paired with its fitting clean source for diagnostics
only: 808 pairs from 82 originals. These deltas will never be inference inputs.
The table reports median-green deltas in RGB8 codes (variant minus own clean).

| Fitting condition | Pairs | Median delta | Observed range |
| --- | ---: | ---: | ---: |
| Cool colour only | 73 | 0 | -5 to +3 |
| Warm colour only | 78 | 0 | -2 to +5 |
| Stress colour only | 71 | 0 | -11 to +10 |
| Core exposure under | 72 | -29 | -37 to -14 |
| Core exposure over | 71 | +32 | +24 to +41 |
| Stress exposure under | 28 | -80 | -87 to -47 |
| Stress exposure over | 57 | +75 | +66 to +83 |

The combined recipes retain the expected median direction as well: all their
underexposure pairs decrease green median and all overexposure pairs increase
it. Full four-feature summaries for every recipe are saved privately.

Of the 222 colour-only fitting pairs, 119 have exactly unchanged green median;
only 55 have all four features unchanged. This confirms that generator-level
green invariance does not imply actual-input measurement invariance. Changed
crop/normalization and selected support remain confounders. Log contrast is
not a uniformly reliable exposure-direction signal, especially under clipping.

These observations retain the training-side rationale for testing the feature
family: paired green median reacts much more strongly to these synthetic
exposure conditions than to R/B-only casts, despite the actual-input pipeline.
They do not establish a deployable discriminator: the clean reference is absent
at inference, absolute green values vary across complexions and lighting, and
cross-source feature ranges can still overlap. No threshold was fitted or
selected from these deltas and no numerical separability cutoff was invented.

## Independent checks and prepared vectors

- Four focused extractor tests passed in 0.34 seconds: exact green selection and
  percentile formulas, zero-valued finite contrast, insufficient support without
  imputation, and rejection of wrong/nonbinary support.
- The authoritative independent verifier passed 2,730 scalar quantile checks,
  910 log-contrast checks, 3,640 raw-statistic checks, 683 direct affine mask
  reconstructions and 910 native projections.
- All 808 pair deltas and recipe summaries were recomputed. All 5,482 selected
  metadata/code/asset bindings were verified. This reads only fitting/reserved
  assets, not all historical image bindings indiscriminately.
- Packaged eleven exact fitting configurations: 9,563 repeated training vectors
  and 220 repeated reserved-clean vectors. Original twelve columns, including
  nested calibrated MST, are copied exactly; only the four fixed features are
  appended. No pair deltas enter the sixteen-column schema.

The verifier was strengthened with direct comparisons to original metadata
while its first execution was in progress. That first receipt is retained for
provenance; a clean rerun of the completed verifier is authoritative, saved as
`verification_with_metadata_PRIVATE.json`. Its source hash is checked by the
packaging script. No source mask or feature artifact was changed between runs.

Private artifacts include `features_PRIVATE.json`, individual row receipts,
`verification_with_metadata_PRIVATE.json`, `prepared_vectors_PRIVATE.json`
and `assessment_PRIVATE.json`. The older `verification_PRIVATE.json` is the
superseded first-run receipt, not the authoritative preparation gate.

## Readiness decision and stopping boundary

**Technical fitting-side preparation passes, and the training-side rationale
remains sufficient for the one predeclared comparison.** Source-held benefit,
clean preservation and harmful-edit reduction are still unproven for these
features. No new model has been fitted and no candidate is adopted.

Next, if proceeding with the specifically defined comparison, append the same
features to permitted evaluation inputs and reserved vectors, preserving all
failures and the frozen extraction contract. Fit exactly eleven depth-four
colour-nonharm trees under the fixed design, with no feature/quantile/channel,
objective/depth/weight or recipe sweep. Independently verify fitting choices,
roles, final constraints, veto/exception, all 756 predictions, protected pixels
and metrics; review every changed output against global nonharm. The original
aligned joint acceptance criteria remain unchanged. A failed result ends the
cycle and is preserved, rather than triggering a rescue fit.

This user-approved continuation completed preparation only. Zero correction or
MST fits, new image-model forwards, evaluation-only feature rows, correction
renders or holdout reads occurred. DINO remains unused; final 24 photos remain
byte-unread. No app integration, new annotation, external contact/upload,
scientific admission, commit or push occurred. Full-face mask qualification
remains a separate unresolved completion requirement.
