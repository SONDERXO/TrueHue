# Remaining correction error: compressed contrast and colour differences

2 November2026. In response to the user's request to keep improving, script393
analysed the existing six saved results without new fitting or changing methods.
All prior artifact hashes verified. Existing check blocks and face polygons were
used unchanged; no new dataset, pixels, parser/model inference or user review.

## What the evidence says

Every fitted face shows the same descriptive pattern: its darkest source-green
quartile is too bright relative to editor A, while its brightest quartile is
too dark. The wedding faces also have a positive Lab a* residual consistent with
the pink shift seen in the previous visual inspection.

|Frame|Darkest quartile mean L* error|Brightest quartile mean L* error|Whole-region mean a* error|
|---|---:|---:|---:|
|1398_0|+4.24|-4.42|+4.08|
|1398_1|+3.79|-3.95|+3.66|
|1398_2|+3.97|-4.37|+4.60|
|1487_0|+2.17|-2.00|+1.00|
|1487_1|+2.58|-1.30|+0.10|
|1487_2|+3.20|-2.27|+2.15|

Errors are fitted-minus-editor on the saved check blocks, not actual measured
skin error. Quartiles are defined by source green within those blocks; they
are intensity strata, not annotated anatomical shadows/highlights. Approximate
face regions include mixed facial features and makeup. Registration uncertainty,
quantisation and source conditions remain possible contributors. These data
support contrast compression as a working explanation; they do not prove a
unique cause or that a fourth control will fix it.

Machine-readable results also preserve per-channel residuals, fixed-gamma
per-pixel required-gain distributions and clipping counts. They were computed
algebraically from saved arrays, without estimating a new operator. Required
gains vary across pixels, which can reflect target curves/local edits as well
as mixed features and alignment; do not infer that adding green gain alone
would solve the residuals.

## Concrete proposed improvement — not executed

Recommend considering **one explicit contrast control** in addition to gamma,
red gain and blue gain. This is a candidate research change, not an adopted
model or guaranteed improvement. It changes the retained correction-output
design and therefore needs an explicit user decision before implementation.
ITA/calibrated MST/facial statistics and decision-tree model family would stay.
Original proposal wording/pages would need checking before any formal panel
amendment; no submitted paper or letter changed here.

If explicitly chosen, a single isolated comparison can be frozen as follows:

- Same six exact source/editor-A pairs, selected faces, polygons, fit/check
  blocks and source precision. All original three-control results retained.
- One four-control candidate: shared gamma, scalar contrast about fixed encoded
  midpoint0.5, red/blue gain; final clip. Explicit formula:
  `clip((0.5 + contrast * (source**(1/gamma) - 0.5)) * [red,1,blue], 0,1)`.
  Contrast1 reproduces the current operator. No local edits or skin smoothing.
- One identity-start squared-sRGB fit per photo with existing gamma/gain bounds,
  contrast fixed to a declared bounded range[0.5,2]. Same solver tolerances.
  No objective/bounds/midpoint/start sweep or second candidate.
- Compare check-block relative DeltaE, RGB residuals, darkest/brightest residuals,
  clipping and all six visual outputs against the saved baseline. Keep every
  degradation, failure and colour issue. No automatic perceptual success threshold.
- End after this representational diagnostic. No tree fit, new labels/MST,
  runtime/demo integration, cohort admission or automatic larger batch.

The alternative is retaining exactly three outputs and accepting the demonstrated
approximation limit while pursuing the missing MST/reference evidence. Repeated
three-control tuning on these same six photos is not recommended.

Artifacts: `outputs/ppr10k_residual_diagnosis_v1/{protocol,results}.json` and
`review.html`. Parent results and immutable delivery snapshots preserved.
No new fitted results or improved rendered images produced in this diagnosis.
