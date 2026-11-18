# Expanded training inputs prepared — 8 November 2026

Prepared and verified all **1,040 planned distorted inputs**. Of these, **810
have available measurements and correction support**. No correction tree or MST
estimator was fitted in this stage. The 24 holdout photos remain unopened.

## What was prepared

- Used the fixed 13 non-clean conditions for each of the 80 new reference photos.
- Generated each distortion on the original full scene, then detected and masked
  that actual distorted input. No original-photo anchor or mask was borrowed.
- Kept the raw parser, landmarks, occlusion model, thresholds, protection and
  blending unchanged. No contrast enhancement, fallback or new weights.
- Ran 933 parser forwards and 842 local CPU occlusion forwards. All 842 occlusion
  runs completed; passing inference is separate from passing measurement.
- Reused the 96 existing clean records: 80 technical passes and 16 failures.
  No derivatives were generated from the 16 sources without a usable reference.
  They are excluded-before-generation records, not fabricated detector failures.

The ledger contains 1,136 records: 1,040 generated conditions and 96 cached clean
records. The 810 available distorted inputs plus 80 clean references give **890
new fitting candidates**, not 890 independent photos or people. Combined with
the parent's 227 fitting rows, the full fit can have at most 1,117 rows if all
feature and contract checks remain satisfied. There are still only 102 proposed
reference photos across 42 fitting publisher groups.

## Availability and failures

| Input condition | Available / 80 attempts |
| --- | ---: |
| Ordinary underexposure | 73 |
| Ordinary overexposure | 71 |
| Cool colour cast | 72 |
| Warm colour cast | 76 |
| Cool cast + underexposure | 73 |
| Cool cast + overexposure | 68 |
| Warm cast + underexposure | 73 |
| Warm cast + overexposure | 69 |
| Additive colour stress | 72 |
| Underexposure stress | 28 |
| Overexposure stress | 57 |
| Combined underexposure stress | 21 |
| Combined overexposure stress | 57 |

Core conditions provide 575/640 available measurements; stress conditions provide
235/400. Strong darkening remains particularly difficult. The 230 failures are
88 initial-anchor failures, 110 parent-measurement failures and 32 final-masking
failures. None was replaced or counted as successful correction or clean safety.

Only 15 of the 80 sources retain measurements for every one of their 13 distorted
conditions. Every source retains at least one. Selected native measurement areas
range from 39 to 979 original-image grid locations. Passing the processing-frame
pixel minimum does not establish measurement adequacy or correct skin selection.

## Regions, features and diagnostic masks

Measurements use the original distorted pixels. The four facial features and
seven whole-scene summaries keep the aligned pipeline's definitions. MST remains
uncomputed here; the planned fit will use the frozen matching calibrations.
The 32 shared runtime/model bindings checked against the aligned parent are
unchanged, and the saved actual-input pipeline replays passed.

Each generated condition has its clean-reference support available for regional
supervision. The scoring region is the union of that clean support and the
**usable** actual-input correction support. A failed input's saved diagnostic
alpha is not applied and is not added to that union. Failed rows are excluded
from fitting; their masks remain labelled diagnostic. This does not alter the
old 756-attempt evaluation regions, which remain frozen for the comparison.

No clean-reference mask enters input features or applied correction. The support
renderer was exercised with identity controls only, not a learned correction.
Protected pixels have zero alpha; correction beyond the saved crop is unavailable.
Glasses handling stays explicitly uncertain and does not establish rim/lens accuracy.

## Verification and inspection

Scripts 608–612 prepare, run, finalize, verify and assess the inputs. Independent
saved-artifact verification checked:

- 80 original source decodes and all 1,040 distortion pixel/recipe replays;
- 952 actual-input crop/resize replays and 903 saved parent mask/statistic replays;
- 842 cached occlusion-service and native support/protection projection replays;
- all 1,040 scoring regions and regional RGB input-error calculations;
- all 1,136 role/status records and 9,193 bound source hashes.

Verification adds no model forwards or fits. Generated artifacts are separately
hashed. The focused recipe/measurement/projection suite passed **33 tests in
10.28 seconds**, using software fixtures rather than research-model fitting.

Inspected all **92 fixed review boards in 23 contact sheets**: underexposure for
each of the 80 sources, plus the first frozen source for each other condition.
This is not a claim that all 1,040 inputs were visually reviewed. The selection
does not depend on results. All inputs were numerically verified.

The boards show broad support in some cases, but forehead-only or fragmented
support, missed skin and uncertain beard/glasses boundaries in others. Assistant
inspection is not a new annotation set or skin ground truth. None of these
technical passes automatically enables scientific admission.

Private artifacts: `outputs/expanded_correction_inputs_v1`, including
`review_PRIVATE.html`, the full ledger, assessment and verification receipts.
No holdout image reads, new annotations, app changes, uploads, contact, publication,
commit or push occurred. Earlier artifacts are preserved.

## Next step

The preparation gate is technically satisfied for the fixed exploratory
comparison. Next is the already specified **11 correction-tree fits**, using
frozen MST calibrations and action libraries, followed by verification and the
same 756-attempt evaluation. Keep the new holdout closed during this work.

Zero unwanted clean edits and retained distortion benefit remain joint
requirements. More prepared rows do not establish better correction, true skin
colour, independent all-tone fairness or a finished model. The common-severity
14-condition development matrix is not the proposal's exact three tone-dependent
recipes; that methods distinction remains documented.
