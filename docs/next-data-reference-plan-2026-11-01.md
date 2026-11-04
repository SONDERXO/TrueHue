# Next data and reference plan

1 November 2026. Planning result only. No images opened, measurements generated,
calibrators fitted, correction trees trained, or roles changed for this plan.
Retain ITA + calibrated MST + facial statistics → decision-tree gamma/red/blue
correction. Reliable mapping and automatic correction remain unfinished.

## Reconciled supply

Script355 reads saved allocation, duplicate, exposure, review and official-label
metadata. Evidence: `outputs/next_cycle_data_plan_v1/`, including input hashes,
all19 MST-E subject dispositions and the389 remaining FairFace source records.
Counts describe the available records, not a new visual audit or availability
check. Historical review files can be incomplete exposure records.

| Supply | What is actually available | Limit |
|---|---|---|
| MST-E completed development | 15 subjects,418 attempts,393 current measurements | Already exposed; mapping unreliable |
| MST-E outside that cycle | Four dataset subjects;337 unique photograph keys | All four historically processed/review-recorded; not untouched |
| FairFace frozen training | 420 allocated,418 duplicate-screen clear | Screen clear does not establish distinct people |
| FairFace outside old32 and preferred18 | 389 sources:236 pending-review targets,60 distorted failures,80 reference failures,13 unavailable targets | Already development-exposed; no official MST labels |
| SCIN saved head/neck candidates | 368 images/cases;14 historical training candidates,354 unallocated; nine prior local paths | No verified person separation or equivalent duplicate clearance; availability not rechecked |
| Reserved correction roles | 90 development-validation and90 final-test allocated | Remain locked; earlier computational duplicate exposure disclosed |

The four MST-E subjects are additional to the completed cycle, not newly acquired
independent subjects or a final test. Preserve automatic failures and pending
reviews; do not reinterpret these as current mask or reference decisions.

| Subject | Official category (1–10) | Unique photos | Historical rows: pending / automatic failure |
|---|---:|---:|---:|
| subject_1 | 2 | 73 | 65 / 7 |
| subject_9 | 4 | 91 | 85 / 4 |
| subject_11 | 5 | 107 | 95 / 10 |
| subject_10 | 9 | 66 | 48 / 16 |

Official full-dataset subject counts by category1–10 are
2,3,2,2,2,2,1,2,2,1. The completed cycle has2,2,2,1,1,2,1,2,1,1.
Adding the four could address singleton support at4/5/9, but cannot address7/10.
Two people per category permits a split; it does not establish adequate sample
size. No genuinely new, verified independent labelled subjects are established
by these records. Official categories1–10 must remain distinct from code indices0–9.

SCIN retains151 agreeing India/US annotations,216 disagreements and one
unavailable pair. Preserve both labels and gradability; do not choose the label
that helps results. Case IDs alone do not prove different people. The agreeing
subset lacks category9/10 support in the prior audit. SCIN is not a ready-made
solution to missing labels or reference lighting.

## Which photographs can be references?

Keep three separate decisions for each exact file/hash:

1. Photographic reference: adequate detail, no obvious filter/cast or mixed-light
   problem, no unrecoverable skin clipping, documented visible makeup/paint,
   facial hair and coverings. Acceptance means a useful photographic target,
   not measured intrinsic skin colour. Uncertain lighting means hold.
2. Measurement: actual selected facial skin and exclusions under contract
   `1bdef31c41b09b52744beb685a97ec2574f8918dd7b6245289a724512a0c26f7`.
   Parser class/exclusion checks alone cannot approve this decision.
3. Correction: whole selected face plus associated visible neck, explicit
   protections, and the adopted inward union-edge alpha. Accept exact support
   and alpha separately from reference lighting and measurement.

Six migration anchors2434/25517/39083/63509/42965/77101 retain their exact
source-photo decisions as historical evidence. They are plausible photographic
reconstruction targets, not neutral-light or true-colour standards. Ten available
preferred-support candidates still need exact source decisions; two technical
holds59172/67581 remain. Historical brow/mask decisions do not approve the current
measurement/correction design. No additional photograph is approved by this plan.
Use these existing16 available files first for a qualification audit; do not
select another attractive-looking replacement batch or ask for a broad review.

All389 remaining FairFace records remain inventory, not the next fitting cohort.
Their historical estimated severity is52light/256medium/1dark/80unavailable;
these estimates cannot establish tone coverage. Photo counts cannot replace
verified people or independent lighting evidence. Existing well/poorly-lit
MST-E labels describe capture groups, not calibrated colour accuracy.

Facial hair is recorded separately from measurement contamination. Whole-face
correction intentionally covers hair inside the outline. A visible beard does
not automatically exclude a person: hold measurement use if actual beard or a
covering contaminates selected pixels. Record that before seeing predictions.
No beard detector, mask adjustment, outcome-based exclusion or hidden refit.
Keep held cases in attempted/eligibility denominators and descriptive reports.

## Bounded next cycle: reference and subject readiness, no fit

Freeze this as readiness cycle R1. Its entire scope is the four named MST-E
subjects' existing metadata and the existing18 preferred-support dispositions
(16 available plus two technical holds). No replacements, new recipes, mask
settings, features or tree comparisons. The389-source inventory and368 SCIN
records provide coverage context only, not additional processing queues.

Before opening any further pixels, create an exact hash-bound R1 manifest with
person/duplicate group, original role, all known exposure, label source and both
SCIN annotations if relevant, lighting provenance, source decision and reason,
measurement decision, correction/alpha version, and unresolved status. Keep
unknown identity or lighting explicitly unknown. Reuse exact source judgments
and notes; never copy changed mask judgments. This plan does not authorize a
bulk visual review or image processing as part of the present planning task.

R1 deliverable is one eligibility/coverage table: all18 dispositions, counts of
usable photographic targets versus independently documented lighting references,
per-category verified-person support, beard/covering holds, technical failures,
and which capture/label evidence is absent. There is no correction score to
optimize in R1 and no model training at its end automatically.

Stop after that single audit. If existing evidence cannot establish independent
label support and qualified references, record **not ready**; do not refill the
queue or refit the15 exposed subjects. The current metadata already fails a
ten-category independent-support requirement at7/10. A full ten-category cycle
therefore needs genuinely additional independently labelled people, or an
explicitly limited claim with unsupported categories reported. More data alone
is not a success criterion.

If acquisition is needed, update the existing controlled-reference proposal to
the adopted masks/alpha before any capture. Freeze feasible participant counts,
consent/use permissions, subject roles, label provenance, lighting/device and
repeat-reference procedure, and repeatability criteria. A chart is an offline
reference aid, not a runtime input or automatic MST label. No outreach,
recruitment, purchase or download is performed by this plan. Adviser response
timing is not a technical gate.

## Requirements before a later single fitting cycle

Do not invent a ready training cohort while these prerequisites are unresolved.
Before processing/fitting, publish a separate frozen manifest and protocol:

- Evidence-backed capture scope, independent subject/duplicate groups, exact
  admitted references, all holds/failures and missing tone/lighting coverage.
- One matching subject-balanced calibration method and fixed subject roles;
  calibration development separate from correction fitting. No old lookup.
  State numeric task-appropriate acceptance criteria before outcomes; they
  remain unresolved here, so this document cannot unblock fitting.
- Input-only ITA, calibrated MST and facial statistics; no reference labels or
  lighting metadata as runtime features. Freeze tree settings and one comparison
  against same-row no-correction and training-subject median MST baselines.
- Group all variants/controls by person/known duplicates. Use only authorised
  development roles; reserved correction data stays locked. Generate targets
  with the actual blended operator; old hard-mask inverse targets do not transfer.
- Report exact/within-one MST accuracy, ordinal/equal-subject error, category
  and lighting support, all-attempt failures, reference-region colour errors,
  face/neck/internal-feature and union harm, clipping/stress and identity controls.
  Empty regions are unavailable. Retain zero-changed-pixel clean protection and
  outside-application preservation. Real captures are not exact synthetic inverses.
- One run then stop: failure of support, reference quality, clean protection or
  predeclared performance gates means no adoption and no same-cohort tweak.
  Better pooled error cannot override regional harm. No automatic demo switch.

Professional review uses the user's existing Google Form after a good initial
correction model, followed by versioned refinement/re-review. It is not the
missing reference-admission prerequisite and no professional was contacted.

## Verification

Script355 completed with allocation/subject-count assertions and unchanged input
hash checks. It reads metadata only and refuses output overwrite. No Python
pipeline code changed; pytest was not rerun for this inventory/documentation
work. The last full-suite result remains890passed in20.10seconds, historical.
