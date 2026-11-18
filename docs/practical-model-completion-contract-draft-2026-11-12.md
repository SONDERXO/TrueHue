# Practical correction-model completion contract - draft for researcher choices

12 November 2026. The user prioritizes finishing the correction model BEFORE editing the paper. Paper/prototype drafts remain preserved and paused. This is an operating-requirements draft, not paper editing, a model proposal, an experiment, or a passing decision. No model, photo, mask or holdout is processed.

## What we are trying to finish

A single-photo correction model that makes useful exposure and colour improvements while avoiding unwanted edits to an already acceptable photograph. Its final control predictor remains one decision tree using input-derived ITA/MST and lightweight traditional features. Outputs retain gamma and red/blue adjustment. Face/visible-neck correction and optional manual refinement stay; measurement/correction supports and protected areas remain separate. Existing segmentation assistance is not revoked by the traditional correction-feature constraint.

The target is photographic restoration, not intrinsic physical skin-colour recovery. The model need not perfectly invert clipped information, have a perfectly illumination-invariant MST estimate or achieve perfect segmentation before any development. Those are not invented prerequisites. It must report limitations and failures honestly.

## Recommended practical choices - not yet accepted

| Choice | Recommended direction | Alternative requiring an explicit choice |
|---|---|---|
| Correction strength | Prefer conservative useful improvements; leaving some distorted inputs unchanged can be acceptable when reported as missed corrections. | Prefer stronger recovery while accepting a greater risk of unwanted edits. |
| Already acceptable photographs | Permit tiny changes only if a prospective assessment finds no visible unwanted alteration. | Require exact pixel-for-pixel preservation of every usable identity output. |
| Main success comparator | Require useful restoration versus the uncorrected input; report the old aligned comparator as an additional benchmark. | Additionally require retaining all specified recovery/error/benefit results of the old comparator. |

These are objectives, not authority to invent an uncertainty score, identity veto, strength slider, new confidence threshold or fallback. A conservative objective cannot be satisfied merely by returning every image unchanged. No fixed numerical perceptual tolerance, allowed harm rate or required improvement percentage is invented here. If small identity changes are allowed, the exact assessment and tolerances must be defined prospectively; neither visual invisibility nor an acceptable harm rate can be inferred from an aggregate mean or a universal DeltaE cutoff.

## Proposed model-readiness evidence

1. **Useful restoration:** compare held-source corrected and uncorrected inputs against the same reference and region. Report exposure directions and red/blue colour conditions separately, plus combined conditions where declared. CIEDE2000 is the paper's primary reconstruction measure; also report RGB error, individual harms, worst failures, missed useful corrections and control errors where targets are defined. Exposure gains must not conceal colour regression. The exact acceptance margins/denominators belong in the prospective task-specific protocol before new results, not in a posthoc rule.
2. **Preservation matching the selected policy:** evaluate usable unchanged references as a separate control set. Do not turn failed measurement or unavailable outputs into learned preservation. Preserve all failures in attempted-source/condition counts. Do not claim safety from averages alone.
3. **Protected pixels and compatible processing:** preserve protected/outside-alpha pixels relative to actual input, and bind one measurement geometry, masks, Lab/ITA/MST calculation, feature order, tree and renderer. Better displayed measurement must influence any newly qualified predictor through its declared compatible path; current historical-control demonstrations do not establish this. Manual mask edits must not be described as retraining. Whether a particular edit changes a tree's controls depends on its actual route, not on a promise that every edit must change the prediction.
4. **Transfer beyond fitting:** all derivatives of a source stay together. Fit calibration and supervised choices only in eligible fitting roles. Validate a frozen method on legitimately disjoint sources under a predeclared protocol and report person-group uncertainty. A perfect training score or repeatedly exposed development result alone is insufficient. Keep final24/older locked allocations byte-unread until a separately specified final-evaluation stage; this draft authorizes no final read.
5. **Honest tone scope:** retain ITA/MST and test/report behavior across eligible supported tone evidence. A named MST feature, altered MST from an exposure change or constant original estimates do not prove useful tone conditioning. Do not invent labels, complexion boundaries, accuracy or fairness. Missing subgroup coverage is reported and limits claims; no new physical-reference acquisition or endless calibration search is implied.
6. **An executable frozen model:** qualification ultimately concerns a particular saved tree and processing contract, with reproducible controls and rendered outputs. Fold trees and software checks alone are not a deployed final model. No all-data fit or existing rejected-model promotion is selected by this document.

## Model completion versus later deliverables

Model-ready means the chosen frozen predictor/pipeline has satisfied its prospectively agreed quality, preservation, coverage and independent validation requirements. Android integration, phone performance, final exports/user-interface verification and the manuscript are later deliverables. Genuine expert MOS remains a separate study requirement; no opinions or scores are fabricated. If visual appraisal is used to define acceptable unchanged outputs, its assessment method must be specified before that particular evaluation. No adviser approval is imposed; researchers make the decisions.

## Historical checks remain intact

Exact zero identity edits and no regression against the aligned comparator were binding rules for their completed comparisons. Their results stay FAIL/CLOSED/NOTADOPTED. They are not universally verbatim proposal requirements. Changing a future requirement does not change a historical result, qualify the current app, justify selecting a favorable old subset or permit reopening a closed trial. This draft is based on user requirements and the proposal distinction, not a threshold fitted to saved scores. No candidate is retested or rescored against proposed policies here.

## What happens after the choices

Record the selected requirements as a prospective operating target, then assess any substantive future correction-learning proposal against that target. There is still no supported new training campaign ready, and accepting a practical definition does not create one. If no credible proposal can meet the agreed target within the retained scope, say so rather than propose another summary, data expansion or paper substitution. No correction family is dropped and no completion date is promised.

Pending user input: correction-strength priority, identity-preservation policy and comparator policy. An additional numerical validation protocol is not selected or run. Existing data-only constraint, no neural correction features/new captures, PPRpause, completed reviews, old failures and unread locks remain.

## Provenance

Based on completion-specification-2026-11-09.md, correction-model-and-paper-realignment-2026-11-11.md, correction-training-contract-2026-11-11.md and consolidated-training-design-decision-2026-11-12.md. This draft supersedes only the near-term priority to edit paper drafts: the user's later request explicitly returns priority to model completion. No manuscript, original protocol, model, runtime or Android asset is changed.
