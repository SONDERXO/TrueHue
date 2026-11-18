# Paper-aligned condition, target and evaluation decision

14 November 2026. Specification only. No source admission, image generation,
target optimization, correction-tree fitting, new review or adoption occurred.
The model remains unfinished; paper editing remains paused. Deadline: November25,
exact submission time unspecified; model completion remains the priority.

## Decision and reason

Use the already documented directional Table2 interpretation as the proposed
paper-composite evaluation lane. Do not multiply predicted correction gains or
replace the existing mild diagnostic inputs. This is a coverage and recoverability
decision, not a new learning method or permission to restart closed experiments.

The latest review contained44 fresh identity/colour cases and22 carried exposure
cases. The mild colour cases changed primary-region RGB by approximately1.22–1.53
codes on average; the saved exposure corrections changed it by23.93–26.16.
The user's broader report that the reviewed differences were too small remains
valid qualitative feedback. Existing individual ratings and closed assessments
remain unchanged. Neither these magnitudes nor stronger inputs prove usefulness.

Table2 does not define executable slider units, pivots or operation order. However,
this project already declared those engineering choices. We must distinguish
paper ambiguity from an absence of local definitions. The November3 directional
implementation is an explicitly authorized experimental departure, not literal
paper parity, panel approval or a training-ready recipe.

## One condition contract

Reuse `directional_exposure_pivot_gamma_offset_rgb8_v1` from
`src/distortion_generation/directional_exposure_recipe.py`; preserve its existing
implementation and evidence. No new strength, pivot, warm-cast variant or grid.

| Recorded tone group | Table2 gamma g | brightness | contrast | red offset | blue offset |
| --- | ---: | ---: | ---: | ---: | ---: |
| light, MST1–3 | .85 | -20 | +5 | -6 | +6 |
| medium, MST4–7 | .70 | -35 | +8 | -10 | +10 |
| dark, MST8–10 | .60 | -45 | +10 | -14 | +14 |

For encoded RGB x in[0,1], let c=1+contrast/100 and b=abs(brightness)/255.
Underexposure is `c*(x**(1/g)-1)+1-b`; overexposure is `c*x**g+b`.
Colour adds `[red_offset,0,blue_offset]/255`. Combined cases apply exposure
before colour. Clip once, blend with supplied distortion alpha, round once using
the existing implementation. Clean is an exact unchanged reference.

The prospective primary roster has six roles per eligible source: identity,
colour-only, exposure-under, exposure-over, combined-under and combined-over.
Each source receives its recorded group's setting, not all three severity rows.
With N admitted sources, the budget is6N condition records and at most5N local
target optimizations, with no automatic correction-tree fits. N and source IDs
are deliberately unbound: this is not an executable roster or acquisition request.

For this prospective lane, distortion alpha is1 across the supplied photographic
crop, modeling a capture error. Correction uses only the existing approved skin
application alpha and protection vetoes. This explicit evaluation choice does
not authorize any current image regeneration or mask change. Outside corrected
skin, equality is required to the distorted input, not to the original reference.
Whole-crop error therefore describes context that the correction is not intended
to restore and must not replace the primary-region result.

## Target contract: achievable restoration before learned prediction

The reference is the original accepted photograph, not physical skin truth or a
lighter target complexion. Retain gamma/red/blue outputs and the current direct
gamma renderer `encoded_rgb_direct_gamma_then_gain_v1`: power, red/blue gains,
clip, approved correction-alpha blend, RGB8 rounding. Identity target is[1,1,1].

Reuse the existing `direct_gamma_rgb_three_control_blended_target_v1` fitter in
`src/model_training/blended_recovery_targets.py`, not the older reciprocal-gamma
target convention. Its fixed policy is one identity-start bounded local fit,
each control in[.25,4], SciPy TRF linear squared RGB loss, tolerances1e-10 and
max_nfev500. Fit support is the explicitly sealed primary scoring support within
positive application alpha; reference access is supervision-only. Record rank,
convergence, active bounds, clipping, float residual and actual RGB8 residual.
No alternate starts, relaxed bounds, clipped-case deletion or threshold tuning.

Composite targets are approximate local recovery controls. They are not exact
inverses, global optima or automatic predictions. Additive brightness/contrast
and clipping can leave substantial residual even with reference-aware fitting.
The existing November3 ramp results already demonstrate this limitation; do not
repeat those generated probes merely to rename them a new experiment.

Before selecting a new learner, the bound source roster must support a separate,
bounded recoverability assessment: compare original input with reference-aware
three-control recovery on every declared role. If substantial residual remains,
report the renderer/condition mismatch; do not assume a better tree can remove it.
Good local recovery would justify investigating prediction, not qualify a model.
No new numerical pass threshold or model-training continuation is selected here.

## Source and tone eligibility

No independent tone-labelled correction cohort is currently admitted. The11
reviewed FFHQ sources lack eligible official tone labels for these group claims.
Do not substitute predicted MST, apparent darkness, race or the severity name.
Do not reuse them as independent qualification sources.

The existing nine-source SCIN shortlist is only a metadata shortlist. Preserve
both annotators: three agreements and six disagreements, including two
medium/dark group disagreements. Neither agreement-only selection nor whichever
annotation gives a favorable result is permitted. Person duplication, usable
reference, measurement/application support and source-role eligibility remain
unresolved. No new file inventory or image access is authorized by this design.

The next concrete prerequisite is one source-eligibility decision using the
already saved shortlist records: enumerate the unresolved admission fields and
decide whether a bounded non-locked development roster can be formed. Bind source
IDs, source count, both-label handling and exact target-fit budget before any
image generation. If it cannot be formed, record that gap; do not quietly switch
to unlabelled sources or open the locked holdouts. Any needed new annotation or
source acquisition requires a separately scoped task, not an automatic queue.

## Evaluation and claim boundaries

Seal source identities, support, conditions and analysis before target optimization
or prediction. Keep all variants of a source in one partition, preserve exposure
and colour families separately, and count people/sources rather than variants.
Target fitting may use training references; a future automatic held-source
prediction must not use its reference, oracle controls or optimized residuals.

Report input and restored primary-region CIEDE2000 and RGB8 MAE, paired benefits,
individual regressions, clipping and unavailable targets. Include whole-crop
descriptive results and exact preservation outside application alpha/protection.
Use equal source weights within each role and report all six roles separately.
Report tone strata with actual independent source denominators and annotation
ambiguity; do not pool away darker-skin regressions. If coverage is absent, say so.
The paper's disparity criterion needs a denominator fixed before qualification;
this document does not invent one or claim the cohort supports a fairness result.

No new user rating batch is selected. Any later usefulness review needs an
explicit prospective protocol and must distinguish an appropriate restoration
from a merely visible change. Existing mild cases and failed/closed recipes stay
part of the evidence; stronger cases cannot retroactively rescue their results.

## Stop and next action

This design resolves operators, condition roles and compatible target semantics.
It does not supply a distinct learning repair, an eligible cohort, a final
predictor, Android parity, expert MOS or a completed thesis. Next: resolve the
saved shortlist's source/tone admission gaps and bind one exact recoverability
roster/budget before any new fits. Do not launch another open-ended method queue.

Existing artifacts, locked final24/older holdouts and their manifests, approved
ear/manual support, runtime and manuscript remain untouched.

Evidence: `reviewed-correction-magnitude-audit-results-2026-11-14.md`,
`directional-exposure-revision-results-2026-11-03.md`,
`correction-training-contract-2026-11-11.md`,
`qualification-eligibility-blue-check-results-2026-11-13.md`, and
`delivery-readiness-review-2026-11-14.md`.
