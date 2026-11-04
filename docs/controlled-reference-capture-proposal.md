# Proposed controlled photographic-reference collection

30 October 2026 · Discussion draft, not an approved study or collection order.
Supports [the adviser decision brief](adviser-decision-brief-2026-10-30.md).
This specifies a new data direction, not another test of the same32 sources.

## Purpose and method boundary

Create better documented photographic targets for the retained single-image
ITA + calibrated MST + facial-statistics decision-tree gamma/red/blue method.
A chart is an **offline acquisition/reference aid**, not a proposed runtime
input. It must not supply held-out lighting labels, reference ITA/MST or target
statistics to the correction tree. A photographic reference is not a direct
measurement of intrinsic skin reflectance. No additional model family, parser,
beard detector, reconstruction operator or camera-profiling runtime is adopted.

## Decisions to freeze before recruitment or captures

- Participant availability, consent and institutional requirements for collection,
  retention and thesis use of identifiable portraits; any permission to show
  examples must be explicit. Use coded IDs and restrict original-photo access.
- Available smartphone/camera controls, target/card, fixed light and support;
  no equipment purchase is assumed. Decide whether the device permits locking
  exposure, white balance, focus and computational modes. Log unsupported locks.
- Intended range of participants and photographic conditions, feasible numbers,
  and a sample-size rationale. Repeated photos are not independent people.
  Do not infer MST from race or claim ten-category coverage without evidence.
- Participant-level training/development/final-test roles, allocation rule and
  access ledger before measuring or fitting. Separate correction and MST roles;
  newly collected portraits do not acquire official MST labels automatically.
- Reference acceptance, repeatability, stopping and evaluation criteria. Agree
  meaningful thresholds and denominators before looking at model outcomes;
  this draft deliberately supplies no invented success threshold.

## Capture sequence for each participant/session

1. Use a stable camera position, distance, pose and diffuse lighting arrangement.
   Record device, app/version, lens, light setup and background. Avoid mixed
   lighting where practical. Keep makeup, facial hair, glasses and other
   occlusions in the record; they are not automatically rejected or approved.
2. Photograph a suitable neutral/color target in the subject's lighting without
   glare or blocked patches. Record target identity and placement, camera
   settings and file metadata. Recheck after lighting/settings change. A neutral
   reference supports white balance; color profiling requires the appropriate
   chart and documented workflow. [Manufacturer guidance](https://calibrite.com/us/why-you-need-to-calibrate/?noredirect=en-US)
   and [camera-profile workflow](https://calibrite.com/us/learning-centre/calibrite-profiler-camera-dng/?noredirect=en-US).
   These sources support the acquisition principle, not validation of TrueHue.
3. Capture the target-free reference portrait under the same recorded settings
   and lighting, plus repeat reference frames. Preserve originals; record any
   target-based processing as a separate derived file with settings, tool/version
   and hashes. Do not choose edits by whichever makes TrueHue score best.
   A chart-to-portrait change in light/pose invalidates the assumed match and
   must be logged rather than silently corrected.
4. Inspect reference quality separately from the skin mask: focus/motion,
   illumination consistency, reflections, clipping and color-pipeline settings.
   Record skin and chart clipping separately. A zero-clipping condition alone
   is not reference approval and must not silently bias selection toward lighter
   captures. Retain every attempt and reason for a hold.
5. Keep the whole-frame square256 preprocessing and original masking contract
   fixed for algorithm measurements. Chart diagnostic frames stay out of normal
   input features. Never crop/resize differently or insert old lookups under a
   changed support. Facial/neck coverage and exclusions require explicit review;
   this collection does not solve the existing neck requirement.

## Two distinct evidence lanes

**Known synthetic lane:** after a reference is independently accepted, generate
only the recipes and settings declared before generation. Keep exact gamma
convention, transforms/order, quantization, clipping and inverse-target lineage.
Inputs share the reference's geometry, supporting fixed-reference-mask pixel
metrics. Untouched copies are identity controls: the existing zero-changed-pixel
gate applies to these exact-image controls. Every input mask still needs its
own technical/review admission; reference approval does not propagate.

**Real capture lane:** if approved, capture a fixed, declared set of changed
lighting/exposure conditions with the same device/pose and repeated controls.
These are not exact synthetic inverses; motion, shadows and camera processing
can change geometry and appearance. Do not assign inverse gamma targets from
exposure settings alone or score full-face pixels as though they are aligned.
Declare valid region matching/registration and scoring before model evaluation,
or retain these captures as a separately labeled qualitative robustness lane.
Do not add a registration model or reference-guided runtime by implication.

Reference repeats estimate acquisition variability; they must not be judged
against an exact zero-pixel-difference criterion. Spatial lighting changes may
also exceed what the retained three-parameter operator can reproduce. Report
that mismatch rather than introduce an unapproved recovery operation.

## Data records and calibration plan

Each record needs person/session/capture IDs, assigned role, file/hash lineage,
settings/lighting/target metadata, reference-quality decision and notes, mask
decision, transform/target provenance, clipping/support outcomes and exposure
history. Keep photo paths private; use aggregate tables in the brief.

Retain the [existing MST evaluation design](mst-calibration-evaluation-design.md)
and the previously agreed limited scope. Audit official labels, subject support
and historical exposure in metadata first; keep all photos of a subject together.
Freeze an adviser-agreed calibration/validation plan with the exact masking
contract before fitting. Report exact/within-one accuracy, ordinal error,
baseline comparison, failures and unsupported categories with explicit counts.
Do not refit repeatedly on historically exposed subjects or call resplitting
them an untouched test. New photo color charts do not independently validate
MST categories, and the experimental lookup remains unvalidated until the
appropriate evidence exists.

## Progression and stop rule

Agree the brief's decisions, then freeze this collection protocol and manifests.
An acquisition feasibility stage should have a declared size and exit conditions
before capture; it checks reference quality and repeatability, not tree settings.
Do not recruit a large batch or train on feasibility captures to chase a result.
If acquisition is feasible, collect the approved cohort and perform one separately
predeclared comparison. Keep final-test subjects locked until the method and
acceptance criteria are frozen. If reference repeatability/support is inadequate,
record that finding and return to the agreed scope decision instead of cycling
through mask, feature, depth, weight or source-specific tweaks.

No photos were collected, no participant contacted, no equipment purchased and
no model or calibration fitted while preparing this proposal. The current demo
and parser/beard hold remain unchanged.
