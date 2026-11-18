# Skin support, lighting and calibration decision — 5 November 2026

**Decision: retain the recognition improvements, but do not calibrate the current
method across these lighting conditions.** The masks remain unvalidated as skin,
and large ITA changes persist when measurements use shared facial locations.
This concerns the current method/sample, not rejection of the Stellenbosch release.

The user authorised mask review and separation of support changes from recorded
colour changes. Scripts449–450 followed the [frozen protocol](stellenbosch-support-lighting-protocol-2026-11-05.md),
using all30saved cases,25technical measurements and seven complete subject keys.
No new inference, image variants, targets, calibration/tree fits or admissions.

## Comparing more consistent locations

For each complete subject's three photos, the existing final masks were mapped
to their common aligned face coordinates and intersected. That intersection
was inverse-mapped to each original photo and restricted to its own final mask.
All21shared-region measurements passed the unchanged1000normalized-pixel guard.
The other three subject keys remain incomplete; they receive no substitute
shared region. Original pixels supply every statistic.

This reduces variation in the sampled face locations but does not establish
dense anatomical correspondence, actual skin or causal isolation of lighting.
Landmarks, pose, resampling and tiny native faces remain limitations. The common
region is a diagnostic probe only, not a new runtime measurement mask.

| Within-person three-condition ITA range, same seven keys | Minimum | Median | Maximum |
|---|---:|---:|---:|
| Existing final mask for each photo | 102.62° | 107.81° | 165.67° |
| Shared aligned-location probe | 102.65° | 106.29° | 165.35° |

Six of seven individual ranges decrease, but the reductions are only0.32–3.03°;
one increases0.03°. These are descriptive feature ranges, not calibrated errors,
accuracy, statistical significance or acceptance thresholds. They show that
changing selected regions does not explain all of the large ITA variation.

## Recorded colour and the existing formula

For the25available full-mask measurements, all seven cool-condition b* means
are negative and all18warm-condition means are positive. The same pattern remains
in the shared probes:7/7cool negative,14/14warm positive. Under the existing
`atan((L* - 50) / b*)` formula, changing the sign of b* can change the sign of
the ratio and angle. This is observable arithmetic behaviour, not proof of a
code bug, ground-truth colour, or a physically isolated lighting effect.

No arctan2 replacement, b* cutoff, colour normalisation or calibrated white
balance was introduced. The enhanced images used for recognition were not used
for these statistics. No intrinsic-skin-colour requirement is being added.

ITA is expected to reflect a distorted photograph and may remain useful to the
correction tree; invariance is not required of every correction input feature.
The unresolved issue is treating that value as a dependable basis for a
subject-level MST mapping across these casts. This diagnostic does not test or
rule out every possible mapping, nor establish that the source labels are wrong.

## Review of all30masks

The assistant inspected all30new boards with source scores hidden. Some subjects
have broad apparently facial support; others have central-face holes, fragmented
cheek regions or missing lower face. The shared region for one subject shrinks
to forehead/upper cheek because of a cool-condition omission. Another becomes
disconnected forehead/cheek/chin patches. The highest-interval complete subject
has only a small common forehead strip in very dim original pixels.

Hairline/feature boundaries, fine glasses/rims/reflections and native detail
remain uncertain. Neither assistant inspection nor a shared region certifies
actual skin; no pixel truth or independent expert acceptance exists here.
The five early failures and three incomplete subject groups remain visible.
For incomplete groups the gallery's shared region is labelled unavailable;
their red outside-probe panel is not evidence that those pixels are bad skin
or were removed by a model. No masks were repaired or replaced.

## Consequence for correction development

The25technical passes are a software availability result, not25admitted training
examples or a justified calibration cohort. Retain the fixed recognition candidates
and their baselines, but close this same30mask/lighting diagnostic sequence.
Another enhancement sweep or successful-only fit would not resolve the current
evidence gaps.

Before MST calibration, specify and evaluate how the retained ITA-to-MST design
handles lighting-dependent colour, while preserving supplied decimal targets,
subject separation, actual-skin evidence and failure coverage. A lighting-aware
mapping or a justified reference-condition policy would be a substantive design
decision requiring explicit definition and an independent evaluation scope;
neither is chosen or implemented here. Do not silently select the most favourable
lighting, change the ITA formula, drop MST, reuse old thresholds or train on
the seven complete subjects. The full retained correction model remains untrained.

The dataset remains useful for exposing lighting/measurement failure modes.
This decision does not declare all285subjects unusable, require new participants,
or imply adviser approval or physical skin-colour recovery.

## Verification and evidence

All bound source, parent/model/history and artifact hashes remained unchanged.
Thirty label/membership checks,25independent original full-mask statistics,
seven manual common-region reconstructions and21original-pixel shared-statistic/
projection checks passed. Independent reduction matched the existing per-channel
float32 averaging order; the initial verification attempt used a different mean
reduction order and failed exact rounding parity. The verifier was corrected;
no saved measurements or production formula were changed.

Seven focused shared-support/coordinate tests passed in0.37seconds, including
translated-region mapping, no additions, source immutability, disjoint supports
without fallback and incomplete/singular-input rejection. Not a new full-suite
run or scientific validation.

Private gallery: `outputs/stellenbosch_support_lighting_v1/review_PRIVATE.html`.
Checks/qualitative notes: `outputs/stellenbosch_support_lighting_assessment_v1/assessment_PRIVATE.json`.
Data, scores, identifiers and manifests remain ignored local evidence under the
author's research/noncommercial+citation/no-redistribution conditions. No dataset
sharing, contacts, recruitment, training, runtime/Android adoption or submitted/
working-thesis edits occurred.
