# Integrated correction development plan — 3 November 2026

## Decision and scope

The generated-image formula checks are complete. Use this single plan as the
next reference; do not start another formula sweep or readiness-inventory loop.
The user authorised combining the recipes, admission and evaluation requirements.
This is planning, not permission or evidence for photo processing, calibration,
tree training, runtime replacement or panel approval.

The task matches the actual proposal: restore synthetically distorted photographs
toward their original photographic references. It does not require or establish
intrinsic skin-colour recovery. Original photo quality/support must still be
appropriate for that photographic task. No mandatory instrument, new participants
or DAST access is imposed. Proposal PDF10–14/printed3–7 and63–66/56–59 were verified
in `proposal-scope-validation-2026-11-03.md`; submitted PDF remains unchanged.

Retain ITA + calibrated MST + facial statistics → decision-tree gamma/red/blue
correction, on-device Android, one selected face. The three-output development
renderer uses direct-exponent gamma. This does not switch the older runtime.
The frozen four-control contrast/soft-boundary PPR experiment from script399 is
a separate experimental comparison, not the operator of this three-output plan.
Neither its parameters nor its smooth-neutral behaviour transfer here.

## Saved definitions to use, without further tuning

| Component | Saved implementation | Important limitation |
|---|---|---|
| Exposure-only core | `development_roles.core_exposure`: direct power1/g under or g over | Quantisation/blended recovery is not exact; omits Table2 offsets/extra contrast |
| Colour/combined core | `core_colour_recipe.render_rgb`: attenuate red for cool, blue for warm; optional power exposure | Also darkens; not additive-slider equivalence or calibrated white balance |
| Composite stress design | `directional_exposure_recipe.render_rgb`: directional gamma, offset, contrast and additive colour | Deliberately retains clipping/unrepresentable cases; actual clipping must be measured |
| Technical roles | `development_roles.assign_role` | No-clipping role alone is not source, mask or target admission |
| Three-output target construction | `blended_recovery_targets.fit_target` | One bounded local fit, not exact inverse, prediction or global optimum |
| Three-output rendering | `blended_recovery_targets.render_rgb8`, checked against `apply_blended` | Supplied alpha must represent the admitted whole-face/neck design |

Full formulas, constants and checks are saved in the script401/403/404/405 reports.
The new plan artifact pins implementation hashes. Do not overwrite old snapshots.
The paper's Table2 values inform experimental strengths; departures in formulas,
variants, contrast pivots, gain conversion and target construction remain explicit
in `panel-change-register.md` (C09/C10). These are development decisions, not
claims that the submitted paper specified those implementations.

## Proposed case matrix for a future authorised source cycle

Fix source/person roles and an approved source severity assignment first. One
source uses one severity group, not every group chosen after seeing corrections.
The existing broad grouping is lightMST1–3, medium4–7, dark8–10; group provenance
must be recorded. Do not infer a reliable label from filename, race, appearance,
an incompatible lookup or a generated ramp's name.

| Layer | Cases per source in the proposed diagnostic matrix |
|---|---|
| Clean | One unchanged original, not repeated per group/cast |
| Core exposure | Under, over:2 |
| Core colour | Cool, warm:2 |
| Core combined | Under/over × cool/warm:4 |
| Composite stress design | Exposure under/over, additive colour-only, combined under/over:5 |

This is a proposed complete14-case **diagnostic** matrix, not an adopted training
sample distribution, count of participants, cohort size, class weight or final
split. The clean/core/stress-design layers remain separate. A stress-design case
stays in that layer even if its particular photograph does not clip; observed
technical clipping/role is an additional field, never a reason to move favourable
stress cases into normal training. Core cases with unexpected clipping/support
errors remain failed attempts, not automatic replacements.

Before a real cycle, justify training proportions/weights, uncertainty/adequacy,
label coverage and split allocation using admitted identities, then freeze them
before any fit. The proposal's70/15/15 split (PDF62/55) remains an academic baseline;
this plan does not fabricate achievable counts or claim those proportions are
person-disjoint in the present data. Any actual departure must be recorded.

## Admission: evidence needed per source and pair

1. **Photographic source.** Bind exact source hash, permitted intended use and
   provenance; inspect usable facial detail, lighting/colour limitations, selected
   face and eligibility. Ordinary original references are allowed; acceptance
   does not certify ideal illumination or physical skin reflectance. PPR editor
   targets are a different supervision choice, not automatically admitted here.
2. **People, duplicates and exposure.** Bind person/scene/duplicate relationships
   and existing dataset roles. Keep connected people/duplicate groups and every
   synthetic descendant in one partition. Unknown identity is a hold, not proof
   of independence. Preserve all14 exposed PPR diagnostics and reserved locks.
3. **Measurement skin.** Bind the exact input measurement contract and actual-skin
   evidence, including hair/beard/glasses/covering concerns. FaceOcc is preferred
   experimental, not automatically admitted. Existing18 exact MST image reviews
   are complete but limited; do not repeat them or fit only favourable cases.
4. **Correction/scoring support.** Bind selected whole face plus visible neck,
   protections, hole handling and combined-boundary alpha independently of skin
   measurement. Specify scoring region before target fitting. Fixed source alpha
   used for synthesis cannot be assumed to equal support found from distorted
   input: verify/recompute actual correction alpha and measure mismatch. Generated
   ramps did not validate actual face/neck association, occlusion or neck edges.
5. **MST and features.** Bind compatible calibration version, subject-held evidence
   and adequacy. No reliable mapping has been adopted. Source labels/grouping can
   define augmentation/evaluation roles only with justified provenance. Model
   features must use measured distorted-input ITA, its matching mapped MST and a
   frozen list of distorted-input facial statistics; never reference/official
   MST substituted for predicted MST. No fabricated MST, fallback omission or old
   lookup reuse. The complete feature schema still needs a versioned freeze.
6. **Exact pair and target.** Bind original/distorted hashes, recipe/version,
   group/cast/direction, forward clipping, input measurements, actual application
   alpha, scoring mask and reference. Use the pinned local three-control solver
   with its existing bounds[.25,4], neutral start,500 evaluations and tolerances
   1e-10; report RGB8 residuals/rank/bounds separately. These are experimental
   solver settings, not adopted quality thresholds. Failed/degenerate fits have
   no fabricated label and remain in the attempt ledger. Neutral targets require
   exact unchanged/support consistency. Reference supplies supervision only.

The artifact includes an empty admission CSV header as a future evidence format;
it contains no admitted rows or newly queued photos. No old mask approval,
programme replay, favourable average or generated fit substitutes for these gates.

## Predeclared evaluation and stop decision

Compare automatic corrected outputs against uncorrected inputs on identical
declared scoring support, with the original photo as reference. Record per-image
RGB8 MAE and relative CIEDE2000, regressions/tails, stage failures and technically
measurable coverage. Oracle target-fit residuals describe operator capacity only;
they are not automatic-model results. Parameter MAE against approximate targets
cannot by itself establish photographic improvement or uniquely true parameters.

Report core exposure/colour/combined, clean changes and composite stress-design
results separately, retaining clipping/failure subdivisions. Show denominators
and per-source/person summaries so extra variants do not imply extra people.
Do not select a successful subset for the headline score. If aggregate weights
are used, freeze them before outcomes. Report supported official evaluation
labels separately from estimated labels; disclose missing/uncertain categories,
lighting and beard/face-covering limitations. Calibration/correction final subjects
must be independent of the learned components being appraised.

Quantitative acceptance thresholds, supported task precision, tree settings and
training weights remain **unset**. They need a justified freeze based on the
actual admitted cohort before fitting; no threshold is invented to pass the
generated probes. Clean evaluation must report all unwanted changes; whether a
nonzero alteration is acceptable requires a separately declared criterion.

After a good initial automatic model, use the existing professional Google Form,
refine using its feedback, then re-review. Keep feedback development and final
appraisal roles distinct. Android integration requires Python/Android parity and
actual-device performance evidence; these checks do not follow from recipe math.

**Stop now at the plan.** No photo batch, review queue, calibration or tree fit is
activated. The largest unresolved requirement is substantive matching skin/MST
admission and justified evaluation, alongside usable source/support/person
evidence. DAST/STW emails remain user-reported sent/awaiting replies, not a
guaranteed answer or mandatory dependency. New evidence must address a named
gate; do not repeat metadata inventories, old-subject fits or formula tweaks.

## Completion evidence for this planning task

Script406 builds `outputs/integrated_correction_plan_v1/`: recipe contract,
readiness/gates, proposed case matrix, empty admission schema and source/evidence
hashes. It verifies saved manifests and source hashes, schema/JSON/CSV consistency
and that admissions/processing/fits remain inactive. No images, model weights,
new target fits or training are included. Existing98focusedtests/2.51seconds
remain the prior code verification; no new pytest run is needed for this plan.
