# TrueHue completion specification — 9 November 2026

User clarification after the native-pipeline diagnostic: **the final correction
model must remain a decision tree**. This is a binding constraint, not a pending
architecture question. Retain the existing ITA/MST and automatic single-photo
requirements. Do not select a different final predictor, hide another predictor
behind a nominal tree, or restart the failed feature/leaf searches. Any proposed
input extractor must have explicit resource, rights and thesis-method implications;
none is approved or selected by this clarification.

Status: evidence-based completion requirements and current go/no-go decision.
User authorised preparation after the proposal reassessment. This document
does not approve failed models, amend the thesis, freeze an unspecified final
experiment, or reopen the spent correction cycle.

## Deliverable and scope

Deliver an automatic local photographic-correction model, then a compatible
Android application. Retain ITA, MST and a lightweight decision tree, with
explicitly demonstrated rather than merely available skin-tone conditioning.
Original photographs are synthetic-restoration targets, not calibrated skin
reflectance. No real-camera-bias or intrinsic-colour recovery claim follows.

Retain the user's existing face/visible-neck goal and protection requirements.
The proposal itself is face-only; describe neck support as an extension. No
manual correction step is introduced. Do not silently remove neck, glasses or
material protection to obtain a passing result. Full automatic transparent-lens
versus frame parsing remains unvalidated, not an established capability.

Do not start parser training, acquire FaceSynthetics, use the unpermitted DINO
decoder/code, or repeat failed parser/guard searches. Those routes remain
deferred. Existing human references are evaluation evidence, not an app input.

## Current promotion decision: NO-GO

| Candidate/family | Evidence | Disposition |
| --- | --- | --- |
| Original aligned comparator | Changes 2/22 development and 2/18 later usable clean inputs | Retain as comparator; not a clean-preserving finished model |
| Facial exception / local refinement | Clean preservation improves; recovery falls; known stress RGB harm from 6.67 to 31.53; refinement reproduces prior outputs | No promotion |
| Global colour-nonharm | Protects scored inputs but loses useful corrections and fails joint recovery gates | No promotion |
| Fixed-structure nonharm | Core RGB 12.0396/12.5411 versus aligned 8.0287/9.7567 | No promotion |
| Green-feature nonharm | All 756 outputs equal global parent; core RGB 10.1310/10.9828; benefits 88/75 versus aligned 106/84 | No promotion; bounded correction cycle closed |
| SegFace mask substitution | Usable cases 3 to 5 of 6, selected skin points 39 to 74; unwanted points 3 to 7, including four new hair/beard inclusions | No mask adoption; fixed screen closed |

Development/later are exposed cohorts, not independent final validation. Counts
of conditions and publisher groups are not counts of verified identities.
No reviewed candidate establishes an accepted narrower operating range either;
selecting a favourable subset now would require separate justification and
evaluation. Identity everywhere is not successful correction.

The result is a functioning experimental pipeline with unresolved model quality,
not a finished automatic correction model. Software replay passing does not
override failed photographic quality gates.

## Completion checkpoints

| Checkpoint | Required evidence | Current status |
| --- | --- | --- |
| Decision model | Existing joint gates below, reproducible fitting/predictions, changed-output review | FAIL |
| Automatic support | Existing fixed coverage/protection comparison; no new definite unwanted reviewed points; dense limitations visible | Unresolved; SegFace FAIL |
| Compatible pipeline | One versioned mask/preprocess/measurement/ITA-MST/features/model/rendering contract; matching calibration and costs | Not qualified; desktop currently mixes newer masking and historical controls/features |
| Frozen study | Complete manifest and protocol, no calibration/test overlap, meaningful group labels and missing-case accounting | Not ready |
| Independent appraisal | Qualified frozen model, specific holdout-access decision, no tuning after results | Not started; 8 groups/24 photos byte-unread |
| Runtime delivery | Matching Python/Android assets, control/output/protection parity, actual phone timing and failure/save/export checks | Pending; older Android prototype is not this model |
| Paper completion | Actual methods/results/limitations, genuine expert MOS, no unsupported fairness claims | Pending |

### Existing numerical adoption gates remain binding

On both fixed development/later cohorts: zero edits to usable clean inputs; no
increase relative to the original aligned comparator in core or stress regional
RGB MAE, CIEDE2000 means or harm counts; no decrease in benefit counts. Preserve
all missing measurements/references in the attempt ledger. Keep the existing
bound metric definitions and tolerances, rather than inventing new ones here.

Key aligned targets: core RGB <=8.028694/9.756669, core DE
<=3.4406/4.1886 (rounded here), core benefits >=106/84; stress RGB
<=39.2219/43.9462, stress DE <=15.2563/16.6843 and benefits >=45/43
(rounded means here; bound records are authoritative). Explicitly report known
large harms, whole-scene results and protected-pixel invariants. No aggregate
pass can conceal a failed support or runtime requirement.

The proposal's uncorrected baseline is also mandatory. It answers whether
restoration improves the input; the aligned comparator measures whether later
development has retained the earlier recovery. Report both. These gates do not
prove universal safety, naturalness or fairness.

## Automatic failure and coverage accounting

Retain existing explicit failures: unavailable face/landmarks, unavailable or
invalid skin measurement, and the existing 1,000-normalized-pixel measurement
guard. Never borrow a clean/reference mask for an input that failed. No new
confidence threshold, mask-quality classifier or range guard is introduced.
Passing the pixel guard does not prove absence of beard contamination.

For an explicitly failed measurement, preserve the original image and record a
distinct unavailable/no-correction reason. A valid model's identity decision is
a separate outcome. The intended app should explain that no correction could
be made automatically; this specification does not change runtime behavior.

Use all attempted source/condition rows as the coverage denominator. Report
measurement success, abstentions/failures, identity decisions, useful corrections
and harms separately, with source/group counts and per-MST coverage where labels
are eligible. Fourteen failed clean measurements are failures, not learned
preservation. Report conditional quality alongside coverage; no dropping failed
dark images or relabelling unavailable attempts as safe successes.

## Final protocol readiness contract

These are required fields, not a claim that the final protocol is frozen:

1. Bind exact permitted source manifests, role assignments, grouping and hashes.
   All derivatives of one source stay together; publisher grouping is not proven
   subject separation. Existing development/later results remain development.
   Do not open or hash final-photo bytes to fill this document.
2. Fit measurement calibration and MST only inside eligible fitting roles.
   Resolve the proposal's MST-E evaluation-only versus lookup-calibration
   contradiction in the method amendment. No final-data calibration. Document
   actual permitted replacement data and continuous contextual MST changes.
3. Bind the exact mask, exclusions, native/normalized geometry, colour conversion,
   ITA formula, MST interface, feature order, tree/action library and renderer.
   A changed mask requires compatible calibration and fitting evidence; old
   costs cannot automatically be carried across the change.
4. Bind actual augmentation code/configuration, gamma convention, operation order,
   channel units, clipping and three proposed distortions or an explicit amended
   condition set. The 14-condition diagnostics are not silently the proposed
   three. Do not choose recipes from favourable evaluation scores.
5. Freeze RGB/DE masks and denominators, benefits/harms tolerances, source-group
   aggregation, missing-case policy, parameter-error interpretation and MST
   strata. Predicted MST on distorted images is not independent ground truth.
6. Keep the proposal's 10% disparity interpretation unresolved until explicitly
   defined. Recommended candidate for method review: per-group relative DE
   improvement 100*(mean input DE - mean output DE)/mean input DE, with max-minus-
   min measured in percentage points. This is a proposed clarification, not the
   paper's established formula. Record undefined zero-baseline groups, group
   counts, raw differences and the confound from tone-dependent severity. No
   fairness pass/fail can be reported until this choice is settled in advance.
7. Freeze the candidate and protocol together, obtain the specific final-read
   decision, evaluate once, retain an unfavourable result, and never recycle the
   final set into tuning. Genuine expert MOS follows readiness; no fabricated
   ratings, assistant substitutes or automatic outreach.

## Next work and stop rule

The immediate specification and promotion review are complete. There is no
eligible model to integrate or send to final evaluation. The next technical
deliverable, if pursuing the working model, is a training-only feasibility brief
for a substantive redesign that supplies missing decision evidence. Its exact
requirements and failure disposition are in the linked decision brief. No new
fit is authorised merely by naming this task. More documentation is not model
improvement; a redesigned model must eventually pass the same checkpoints.

No deadline or guarantee is offered. A limited-results thesis is a separate
possible academic outcome, subject to user/adviser agreement, and cannot replace
the user's working-model goal by default.

## Evidence

- [Proposal reassessment](paper-reassessment-and-recommendation-2026-11-09.md)
- [Proposal requirements tracker](thesis-proposal-completion-tracker-2026-11-08.md)
- [Existing completion gates](model-completion-plan-2026-11-09.md)
- [Green comparison](green-feature-correction-results-2026-11-09.md)
- [Fixed-structure comparison](fixed-structure-nonharm-results-2026-11-09.md)
- [Correction decision traces](remaining-correction-decision-trace-2026-11-09.md)
- [Clean-error traces](aligned-clean-error-trace-results-2026-11-08.md)
- [SegFace screen](segface-loader-and-mask-screen-results-2026-11-09.md)
- [Redesign decision brief](correction-redesign-decision-brief-2026-11-09.md)
