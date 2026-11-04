# Stop small tweaks; complete one controlled model-development cycle

30 October 2026. User direction: improve the implementation without going back
in circles. Pause additional feature, tree-depth, mask-cleanup and per-case
experiments on the same 47 development rows. Preserve all evidence, but use
this checkpoint as the next-work entry point rather than another incremental
experiment chosen from the newest failure.

## What the evidence supports

The endpoint candidate is the strongest current research candidate, not the
default demo model. On the shared 47 cases its mean CIEDE2000 is 5.300 versus
8.013 for the stronger matched baseline. One of 26 clean inputs still changes.
Full-path JPEG checks retain benefit but expose substantial mask-coverage
changes in some cases. Saved recovery targets still produce patchy output on
the highlighted damaged input. More unit tests do not establish image quality.

The current candidate contains 26 approved clean rows and 21 approved distorted
rows across 26 source groups. All 21 distorted rows have some recorded generation
clipping. This does **not** mean all are unusable: clipping ranges from a small
fraction to severe damage, and the authorized clipped-input development route
remains valid as research. It does mean there is no approved unclipped distorted
row in this particular fitting plan, and the candidate depends on a narrow,
repeatedly exposed synthetic stress set.

The earlier three-variant preparation reports six unclipped, support-screen-
passing, target-available variants (two exposure, four color, zero combined).
Their exact distorted masks are still unreviewed. They are candidates, not
automatically admitted rows or a sufficient dataset for a completed thesis.
These are variant counts, not necessarily six independent subjects. Original
reference acceptance does not approve another variant mask.

Metadata checkpoint: `outputs/correction_readiness_checkpoint_v1/readiness.json`,
produced by script 276 without opening images, fitting models or touching reserved
roles. The count concerns this current plan, not every historical dataset.

## One next cycle, in order

1. **Prepare the primary training set before fitting again.** Use existing
   source-approved photographs first. Separate unchanged controls, recoverable
   correction examples and clipped stress examples. Audit clipping, approximate
   target quality and exact input masks; do not equate zero clipping with an
   exact inverse or reliable skin mask. Expand beyond six pending variants
   before representing this as adequate model data. Report source/tone/severity
   selection bias, including the lack of independently validated MST groups.
2. **Freeze one measurement and augmentation specification.** Keep the thesis
   face-mask → ITA → calibrated MST → facial statistics → gamma/red/blue tree
   architecture. Preserve Table 2 values and existing stress artifacts. Do not
   silently weaken Table 2 or substitute a CNN, new segmentation method,
   smoothing, generative reconstruction or another correction operator. Any
   additional recovery-oriented recipe must be documented as an engineering
   addition before use, with exact equations/units/order and target semantics.
   A changed estimation mask requires matching MST calibration/validation;
   do not apply the old lookup to an incompatible mask contract.
3. **Freeze data roles and evaluation before the next fit.** Existing repeatedly
   exposed sources remain development. Build source/known-duplicate-separated
   fitting and development checks using explicit mask eligibility. Keep reserved
   validation/test roles locked until deliberate evaluation activation. Do not
   use them to choose features, thresholds, recipes or which cases to exclude.
4. **Run one predeclared model comparison.** Retain the strongest endpoint
   baseline and one fully specified candidate. Report clean safety, distorted
   benefit, mask failures, clipping and results by source/severity. No new
   feature/depth/weight sweep after inspecting the result. A failure triggers
   a written blocker and a data/method decision, not another small tweak.
5. **Adopt only after the gates pass.** Require zero correction-induced changes
   on the held clean controls under the current conservative gate, benefit
   versus unchanged on distorted inputs, and source-held end-to-end evidence
   with explicit failures. Mask support needs quality evidence; better overlap
   alone does not approve non-skin additions. Check encoding sensitivity, then
   integrate the frozen candidate into the demo with reproducible lineage.
   Photographer evaluation uses the user's existing Google Form only after
   the correction model is finished. Android remains paused while Python is
   prioritized.

## Stopping rules

- Do not launch another small same-cohort model or mask trial while the primary
  data/measurement specification above remains unresolved.
- Do not claim that removing every clipped row solves the problem; it could
  discard useful data and bias tone/severity coverage. Preserve stress results
  separately and predeclare which rows enter the next candidate's fitting loss.
- Do not use the known 68453 clean failure to invent an input threshold or
  source exception. It remains exposed development evidence.
- Do not request another large manual photo-review batch as the default next
  action. Prepare a concrete eligible set first, then identify only the minimum
  missing judgments and explain their role.
- No perfection claim: the retained operator cannot recreate arbitrary clipped
  color information. Report those limits separately from avoidable model error.

Immediate action is training-data/specification preparation, not another model
fit. This plan does not itself approve new images, masks, recipes, calibration
or reserved-data access, and it does not replace the working demo.
