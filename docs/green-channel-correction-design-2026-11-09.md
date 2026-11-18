# Selected correction design: facial green-channel distribution

9 November 2026. Stage 1 of the [completion plan](model-completion-plan-2026-11-09.md).
User authorised selecting and specifying the correction design. This document
selects a single **input-representation change**, not another leaf repair or
an automatically executed fit.

## Decision and training-side rationale

Append four green-channel distribution measurements to the existing twelve
inputs. Retain facial Lab/ITA, matched calibrated MST, all seven scene inputs,
the constrained action-tree objective, depth four, saved actions/costs, roles,
reserved-clean veto and frozen facial exception. The matched parent is the
globally fitted colour-nonharm candidate, not the failed local-refinement tree.
It has the same fitting constraints that the proposed candidate will use.

The training audit established that colour-only transforms often lower facial
L, making low L an ambiguous cue. The actual generators supply a narrower,
testable distinction: core cool/warm transforms change R or B only; the additive
stress-colour transform also changes only R/B. All three colour-only recipes
leave each original green-channel value unchanged. Under/overexposure transforms
change green as well as R/B. This claim is about the synthetic generator, not
physical colour constancy in real photographs.

The existing facial inputs are Lab averages; the existing scene features use
whole-scene Lab quantiles and average channel ratios. They do not contain the
facial green-channel quantiles or their contrast ratio. This supplies additional
input information, rather than a new threshold on the old summary vector.

The two intended effects are hypotheses:

- Clean versus overexposed inputs: green brightness and within-skin contrast
  may distinguish some exposure changes that absolute facial L mixes with
  naturally different complexions. There is no invariant clean reference at
  inference, so low contrast/high brightness is not proof of overexposure.
- Colour-only versus underexposed inputs: green distribution may help the tree
  avoid treating an R/B cast's reduced Lab L as exposure loss. Existing chroma
  features remain to describe cast changes; recipe labels never enter inference.

**Important limitation:** actual-input masks/crops can change between variants,
so unchanged per-pixel green does not guarantee unchanged measured quantiles.
Natural skin variation, shading, camera processing and clipping can still make
exposure and colour ambiguous. This design does not promise separation or fix
missing masks. If the training-only preparation exposes such failure, record it
and stop under the readiness rules rather than selecting a different feature set.

## Why this is distinct from previous trials

| Previous route | What it tested | Difference here |
| --- | --- | --- |
| Facial brightness, 24 October | L quantiles/IQR and spatial half differences | Green values do not incorporate R/B shifts as Lab L does |
| Chroma distribution, 6 November | a/b IQR and L-a/L-b covariance | No green quantile or green contrast feature |
| Channel endpoints, 30 October | Per-channel exact 0/255 fractions | Quantiles/contrast use the interior distribution, not only endpoints |
| Face-local context, 8 November | Existing scene statistics moved to the face crop | These features use actual measured facial skin and a separate channel |
| Split heads/gates/restrictions | Different prediction objectives, controls or feature eligibility | Objective, controls, heads and gates stay fixed |
| Recent nonharm/local refinement | Constraints or splits on the existing twelve inputs | Adds previously absent input information, without relaxing constraints |

These distinctions do not establish superiority. The previous failures remain
part of the evidence and the unchanged aligned comparison remains binding.

## Frozen feature definition

Use each actual input's cached normalized BGR `input.png` and its finalized
normalized facial `measurement_mask.png`. Do not use native correction alpha,
scoring-union masks, clean/reference masks, or pixels from the photographic
reference. This is the same image/support used for the four existing facial
measurements, with the same minimum 1,000 normalized selected pixels.

Take RGB8 green values (BGR index 1), with no linear-light conversion or colour
enhancement. Using NumPy linear percentiles, append in this exact order:

1. `input_green_p10_codes`: tenth percentile, code values 0–255.
2. `input_green_p50_codes`: median, code values 0–255.
3. `input_green_p90_codes`: ninetieth percentile, code values 0–255.
4. `input_green_log_contrast`: natural log((p90 + 1)/(p10 + 1)).

The +1 is exactly one RGB8 code to define the log at zero, not a tuned margin.
Feature values enter the tree with the existing float32 routing contract.
No reference differences, distortion direction, source ID, recipe, score,
fitting cost or output error is an inference feature. No feature subsets,
alternative channels/quantiles, scaling choices or parameter search follow.

## Exact roles and fixed comparison

- Parent: verified `outputs/colour_nonharm_models_v1/models_PRIVATE.json`.
- Use its exact ten held-publisher configurations and full configuration, exact
  training case IDs/features/cost matrices/action libraries and nested MST
  calibrations. No source additions, new distortions or new target/MST fits.
- Full fitting has 890 conditions from 82 originals across 34 publisher groups;
  keep 82 clean, 228 exposure-only, 222 colour-only and 358 combined conditions.
- Keep all reserved groups and 227 reserved conditions out of tree fitting;
  append features to the same twenty usable reserved-clean vectors only for
  recomputing the same veto. No calibration of the new features on those rows.
- The later cohort remains evaluation only. In development, each outer held
  publisher remains absent from its fit, including upstream calibration as in
  the verified parent. The full configuration retains its existing training
  roles; do not reinterpret all exposed development rows as fitting material.
- Preserve all 756 evaluation attempts and their failures/scoring availability.
  New extraction is permitted only after fitting-side readiness; evaluation
  outcomes never select the feature family or recipe parameters.
- The 24-photo final holdout stays closed. Source paths/group names recorded in
  old exclusion metadata do not authorise reading its images.

## Readiness before spending the one model cycle

1. Check the parent verification binding, training/reserved roles and cached
   image/mask paths using metadata only. Record inherited hash coverage without
   reading image bytes. Do not label path existence as feature correctness.
2. Check all fourteen generators on artificial RGB ramps only: colour-only
   green exact identity, exposure changes green, deterministic outputs. This is
   software evidence, not a real-photo model result.
3. In a subsequent fixed preparation, extract these exact four features for
   fitting rows first, including the same-source fitting clean pairs. Verify
   original four facial values against the saved raw-feature records to ensure
   exact image/mask identity; bind every accessed cached input/mask. Report
   availability and mask-induced colour-only changes without tuning.
4. If any fitting or reserved-clean asset is missing, inconsistent, nonfinite,
   undersized or mismatched, stop and preserve the failed preparation. Do not
   drop/replace rows, borrow clean masks or impute a feature. Source integrity
   repairs must be documented before proceeding. Original measurement failures
   remain failures throughout.
5. At fitting-only readiness review, explicitly distinguish generator invariance
   from measured actual-input behaviour. If actual-input behaviour supplies no
   defensible additional exposure/colour information, do not fit merely because
   extraction succeeded. No new numerical separability cutoff is invented here.

Current authorisation covers this design/readiness record and synthetic checks.
Actual-photo extraction, the model cycle and evaluation have not run. No new
mask policy/parser is introduced; full-face qualification remains separately
blocked as described in the completion plan.

## Candidate construction once readiness and comparison are approved

Exactly eleven full depth-four colour-nonharm action-tree fits, using the
existing `colour_nonharm_action_tree.fit_action_tree` and the sixteen fixed
features. Same equal-row saved RGB objective, fourteen actions, exact clean and
colour-only feasibility, greedy tie rules and terminal identity handling.
Recompute veto membership using augmented reserved vectors. Keep the frozen
facial exception based on its original bound feature names/ranges; do not add
green-based exceptions or refit those bounds.

Require final postprocessing constraints before evaluation. Independently verify
all tree choices, original twelve columns and costs/roles/calibrations, four
new feature formulas, veto/exception routing and 756 predictions. Reuse unchanged
source receipts only under exact bindings. Preserve partial and previous output
folders; use a new versioned folder and never rerun blindly over partials.

Render the same 756 attempts and independently check native RGB/DE metrics,
source hashes, protection/zero-alpha invariants and exact identity outputs.
Report clean/core/stress, exposure-only/colour-only/combined separately in both
cohorts, equal-group results, harm/benefit counts and missing measurements.
Compare to aligned for acceptance and global nonharm for attribution. Inspect
every output changed from global nonharm; reuse review only for exact output
and metric matches. Do not claim repeated conditions/folds as independent photos.

## Acceptance and stopping

The original joint criteria remain unchanged: zero usable clean edits; no
increase versus aligned in either cohort's core/stress RGB/DE mean error or
harms; no reduction in benefit counts. All independent protection/replay checks
must pass. Numerical acceptance does not establish dense mask quality, real-world
naturalness or true skin-colour recovery. Known harms remain explicitly reported.

One feature family, one preparation, eleven fits, one fixed evaluation. No
second family/channel, recipe expansion, objective/depth/weight sweep, guard
retuning or rescue fit. Failure freezes the result and returns to the completion
decision, not another incremental suggestion. No automatic adoption, final
holdout access, DINO inference, app changes, contact, upload, commit or push.
