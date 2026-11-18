# Correction model and paper realignment — 11 November 2026

**Current direction: stop the calibration-source expansion and return to the
correction model.** The user requested this audit before further source work.
STW/CHROMA-FIT checks are deferred, not prerequisites. This document supersedes
older next-step recommendations where they make stronger intrinsic-tone or
lighting-invariance claims necessary for the photographic-restoration study.
It does not change historical outcomes or authorize a new fit.

## Source of scope

Rechecked the original 111-page proposal's SHA256 against its existing page-text
extraction: `1426f3769ba771daadf9b6e0e0b1e347729c8f04919c214e6fedc3df272e7b8a`.
Read PDF pages10–14,62–63,65–67 from that matching extraction. No new rendering or
proposal editing is claimed. Also checked the completion specification, proposal
tracker, actual reviewed-data records and the manual-refinement implementation.

The proposal asks whether an ITA/MST-informed decision tree improves synthetically
distorted photographs against their original references, relative to uncorrected
input, across tone groups. Page14 explicitly excludes proof of recovering actual
skin colour or real camera bias. Pages63 and65 identify original photographs as
restoration targets. This was already clarified on3November; recent guidance
drifted back toward a stronger calibration-data requirement.

## Retain the requirements that actually matter

- The final correction predictor remains a decision tree, with ITA, an honestly
  described MST estimate and facial statistics. Outputs remain gamma and red/blue
  gains with an explicit rendering convention. Do not hide another correction
  predictor behind the tree or claim tone conditioning merely from a named column.
- Single-photo, local processing and Android remain the intended deliverable.
  The user's face/visible-neck extension stays; facial measurement and correction
  support remain separate. The user's optional manual-refinement choice is
  authorized and supersedes older prohibitions on manual mask assistance.
- Use permitted sources, consistent measurements and train/inference features,
  matched targets, nonleaking source/group allocation and honest failure counts.
  Preserve final24 and older locked allocations. Do not invent MST labels.
- Evaluate corrected versus uncorrected input using the same target/regions,
  report RGB/DeltaE, controls where meaningful, harms, coverage and supported
  tone-group results. Actual photographer MOS and on-device checks remain later
  deliverables; assistant reviews and software parity do not replace them.

## Requirements I allowed to become too strong

| Added expectation | Correct scope |
|---|---|
| Physically measured intrinsic skin colour before further correction work | Not required by the paper. Ordinary photographic originals can be synthetic-restoration targets. Colorimeter datasets are optional evidence. |
| Exactly illumination-invariant MST | Not a proposal requirement. Quantify sensitivity and uncertainty; do not make the exact-affine rank diagnostic an impossibility claim or new adoption gate. |
| Every photographic target needs an independent MST label | Not needed to learn paired correction targets or compute an external input-derived MST feature. Reference MST labels are needed for defensible calibration accuracy and tone-stratified claims. |
| Any marginal feature-range mismatch blocks all development | A risk to report, not a new automatic rejection/abstention threshold. It does not prove failure or forbid a clearly labelled developmental comparison. It also does not prove transfer. |
| Perfect dense masks or proven cross-case identity everywhere | Not established and not newly required for an exploratory run. Preserve reviewed support, group what is known, report uncertainty, and do not claim independent person-level validation without evidence. |
| A varying/accurate MST feature guarantees better correction | It does not. Correction outputs must demonstrate benefit; a better calibrator alone does not fix action direction or the too-bright demo. |

This correction does not reverse failed calibration tests, approve unqualified
maps, drop the user's MST requirement or silently loosen previously fixed gates.
It removes unsupported reasons to keep expanding the project before testing the
actual correction question.

## What the recent work contributed

| Work | Direct use now | What it does not establish |
|---|---|---|
| Thirty original plus thirty brighter reviewed captures | Reproducible labelled measurement/calibration development and lighting-sensitivity evidence | A finished correction tree or full photographic MST coverage |
| Fourteen reviewed photographic source/target roles, seven usable pairs; two904 roles retained blocked | Existing paired correction targets, edited support, identity controls, native operator costs and grouped development inputs | Independent final accuracy, neutral physical truth or all-case availability |
| Shared measurement core and fixed action-cost package | Concrete bridge between measurement, features and rendering; reusable development evidence | Automatic scientific admission or old-model compatibility |
| Scalar/contextual calibration assessments | Document limitations; retain exact saved outputs and failed preservation checks | Permission for parameter sweeps or mandatory new source acquisition |
| Scene diagnostics, SCIN screen and source searches | Dated limitations/appendix evidence | A new dependency for the main correction study |

No learned correction tree or corrected-image prediction has yet been produced
from the newly reviewed photographic package. The saved fourteen development
vectors are complete, but their isotonic MST feature is constant. This prevents
a claim of demonstrated MST conditioning on that batch; it does not prohibit
using that immutable package for a bounded correction-development diagnostic.
The original synthetic study and supported tone-group evaluation must remain
distinct from such a diagnostic.

The manual editor currently rerenders with captured historical controls; edited
measurement is display-only. It does not retrain or recompute the tree/MST.
Therefore the user's better mask but still too-bright result is consistent with
the implementation. More mask reviews alone will not repair those controls.

## Evaluation gates: keep their authority and purpose straight

The paper requires improvement versus uncorrected input, per-MST evidence and
honest feasibility limitations. Exact zero clean edits and no regression versus
the old aligned comparator are later engineering/adoption checks, not verbatim
proposal claims. They remain binding for the comparisons in which they were
frozen; do not change them after seeing failures. Calibration preservation gates
likewise remain the criteria for their completed comparisons, not universal
prerequisites for every correction diagnostic.

Do not apply old synthetic-cohort numerical thresholds directly to a different
PPR target cohort: targets, regions and sample counts differ. A new comparison
needs a prospective, task-matched protocol. Promotion still requires the retained
correction requirements, coverage and compatible runtime evidence; a positive
small diagnostic would not overturn earlier failures or authorize final testing.

## Narrow next work

Prepare **one correction-focused experiment specification using the existing
reviewed photographic package**, not another dataset/calibration project. Its
question is whether the reviewed source/reference supervision can teach the
retained tree useful correction while preserving defined reference/identity
roles. Use already frozen input-derived features and mapping artifacts as explicit
development evidence; do not refit a mapper just to obtain feature variation.

The specification must name the single supervision change, attempted eight-group
ledger/seven usable pairs, exact tree/action/operator contract, held publisher
groups, input baseline, defined identity controls and prospective acceptance/stop
rules. Include how it tests both harmful brightening and missed useful correction.
If the small cohort cannot support that question, state the precise missing
correction evidence in that specification instead of initiating a generic search.
Do not manufacture new controls, tune a failed recipe, or execute a tree fit under
this audit's authority. This is a new photographic-supervision design review,
not a restart of the closed synthetic feature/leaf search.

For the paper, keep synthetic-original restoration as the primary proposed
experiment. Photographic editor supervision is an explicit development extension,
not silently the proposed target definition. Describe contextual MST versus a
lookup, finite-action versus direct parameter regression, manual assistance,
neck support and changed source roles as actual method differences. The unresolved
MST-E calibration/evaluation wording, three distortion recipes and disparity
definition need clear methods treatment, not a new physical-colour project.

No new calibration fits, datasets, model families, feature sweeps, annotation
rounds, forced acquisition/contact steps or parser training are selected. Keep
all completed reviews. No future work should become a prerequisite without naming
the correction/paper requirement it serves, the bounded deliverable and a stop
condition. Do not repeatedly re-audit already settled artifacts.

## Audit effects and limits

This audit updates project direction and records scope corrections only. It does
not edit the submitted proposal, assert adviser approval, accept a failed model,
change the app, or guarantee completion. Existing source investigations and all
negative results remain preserved, with their old next-step directions superseded
by this document. No photo bytes, image-model calls, fits, predictions, downloads,
contacts, uploads, commits, pushes or final/locked accesses occurred. Original
proposal bytes were hashed only; matching saved extracted text was reviewed.
