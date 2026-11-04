# Source screening follow-up

24 October2026. Follow-up to [the coverage audit](training-coverage-audit.md).
Development checks only: no training admissions, model fitting or runtime changes.

## 20555: fixed five-variant check

Generated the same dark, bright/warm, color-shift, unchanged and mild-brightening
probes from the saved256 source, using a freshly computed hair-clean generation
region. Features and experimental correction support were measured from each
saved distorted input. No clean features were substituted into failed inputs.

| Variant | Processing | Clipped pixels | Retention screen |
| --- | --- | ---: | --- |
| Dark | Pass | 0 | Pass |
| Bright/warm | Pass | 0 | Pass |
| Color shift | Pass | 0 | **Hold: estimation loss** |
| Unchanged | Pass | 0 | Pass |
| Mild brightening | Pass | 0 | Pass |

The color-shift estimation mask contains1,788 pixels, exceeding the old1,000
minimum, but retains only4.57% of the known generation region. Experimental
correction support retains86.0%. A good-looking correction mask therefore does
not establish trustworthy Lab/ITA features for parameter learning. This is the
same failure class identified in earlier held cases, now on a newly inspected
source. It is not resolved by collecting more sources alone.

Codex inspected all five rows. The color-shift estimator selects mainly the
mouth-adjacent region while broader correction support covers much more face.
The other four variants have substantially broader estimation support. No human
acceptance label was assigned;20555 remains a follow-up candidate, with its
color-shift probe held rather than silently omitted from the record.

## Second bounded batch

Screened18 additional TRAIN-only sources from the remaining266 eligible pool
IDs, using the same six native-photo-lightness rank bins and seed42 hash order.
All prior18 exposure IDs were excluded. Sampling is not MST stratification,
intrinsic skin-tone labeling or group-dependent distortion severity.

All18 passed fresh256 processing. Codex inspected every source/mask row:

- **14272,39108,3705,84897:** promising for fixed-variant follow-up only. These
  show comparatively usable detail and broad visible-face coverage; facial
  hair/jaw boundaries, jewelry/edges or downward pose still need checks.
- **The other14:** held for shadows, blur, heavy occlusion, glasses, severe
  pose, fragmented support, strong rendering or outer-region contamination.
  Reasons are saved per source, separately from original human decisions.

Neither processing success nor this Codex visual assessment establishes clean
reference truth or final training eligibility. No source was selected for
improving a learned score; no model predictions were used to screen these photos.
Natural skin appearance, wrinkles or skin-tone darkness are not rejection rules.

Across the two batches,36 new training-pool sources have been inspected:35
processing successes and one landmark failure. This is a selected development
sample, not a dataset-wide acceptance rate. No reserved-test image or external
development-validation source was inspected in this follow-up.

## Decision and next step

Completed follow-up: [all20 probes on the four candidates](candidate-variant-checks.md).
14272 passes all five;84897 has four unclipped passes and one stress case.
3705/color and39108's lower-left reference region remain held for review.
No pairs were admitted and no model was fitted.

Keep the current22-row training selection and model unchanged. Log20555's failed
color variant and retain the four new source candidates as pending, not accepted.
Do not compensate for estimator failure by admitting weak features or using a
clean-source mask during inference. Do not cherry-pick easy variants and hide
the missing color-shift coverage.

Next, apply the same fixed variant checks to14272,39108,3705 and84897 and assess
**estimation** consistency, not only correction coverage. Compare the paper's
YCrCb-only candidate as a separately versioned measurement policy if appropriate;
it would require recomputed features and its own evaluation, not silent reuse
of the old tree. Thresholds must not be tuned just until these cases pass.
Defer another model revision until enough suitable sources and reliable input
measurements are established. The face-and-neck requirement remains recorded;
no neck localization or correction was implemented by these source checks.

## Evidence and checks

- [20555 variants and six new-source sheets](../outputs/source_screening_followup_v1/review-index.md)
- [Full measurements](../outputs/source_screening_followup_v1/summary.json)
- [Per-source/variant disposition](../data/manifests/source_screening_followup_v1/candidate_disposition.json)
- [Verification](../outputs/source_screening_followup_v1/verification.json)
- Script66: `scripts/66_continue_source_screening.py` (refuses overwrite).

All18 new IDs were added to the append-only development-exposure ledger before
processing; the prior ledger snapshot is preserved with the selection policy.
They cannot become fresh evaluation sources later. Original human pending labels,
source partitions, model and old manifests remain unchanged.

Verified exact saved generation pixels, five inverse targets/clipping counts,
18 new mask shapes/counts/removal-only hair masks, source/ledger disjointness
and tracked original hashes. All seven boards were visually inspected.

Existing full suite: **464 passed**.
