# MST feasibility decision: no calibration run now

1November2026. User authorised a concrete feasibility decision on one expanded
FaceOcc-based study. Script383 reconciled saved technical measurements, official
subject/category metadata and admission records. No pixels decoded, new masks
generated, calibrator/tree fitted or lookup exported.

**Decision: NO-GO for another calibration now.** A limited expanded development
study is possible in principle, but its required preparation/admission evidence
does not currently exist. Do not turn promising masks into a weak lookup or
repeat the stopped15-subject fit. This is not a finding that ITA→MST is impossible
or that recruiting participants is mandatory.

## Current matching evidence versus potential inventory

| Evidence | Subjects | Photo/attempt denominator | What it supports |
|---|---:|---:|---|
| Current FaceOcc MST-E diagnostic records | 4 | 33attempts;23technical measurements;10failures | Exposed masking diagnostics, zero calibration-admitted rows |
| Previous nostril-only calibration | 15 | 418attempts;393measurements | Saved weak development mapping under a DIFFERENT measurement method |
| Potential expansion of previous418keys plus337additional keys | 19 | At most755attempts, not prepared/admitted as FaceOcc cohort | Inventory/planning only, not a new processing instruction or guaranteed success count |

The23FaceOcc-measured MST-E photographs concern subject_1/category2,
subject_9/category4, subject_11/category5 and subject_10/category9. Each category
has only one measured subject. Every held-subject photo therefore lacks another
measured fitting subject of its own category. Interpolated predictions could
still be computed; lack of category support is not proof numerical prediction
is impossible. It makes this tiny cohort a poor basis for the intended broad
mapping and does not satisfy actual-skin eligibility.

Full official inventory subject counts by category1–10 are
2,3,2,2,2,2,1,2,2,1. It could permit category-separated fitting/evaluation at
1/2/3/4/5/6/8/9, if actual records qualify;7/10cannot have independent fitting
and evaluation subjects from this inventory alone. Two people is merely the
structural minimum for separation, not adequate sample-size or precision proof.

Neither the393old measurements nor FairFace's estimated tones may be inserted
as matching FaceOcc measurements/official labels. More photos of the same people
do not supply new independent subjects. All19MST-E subjects have historical
development exposure; no untouched validation is created by resplitting them.

## Would an expanded study add anything defensible?

Potentially yes: an explicitly limited engineering study could investigate
whether the fixed FaceOcc veto changes mapping behaviour on an expanded exposed
cohort, using the same retained calibration recipe and held-subject rules.
This would differ materially from a radius/calibration-setting tweak because
it introduces an evaluated occlusion component and potentially four additional
subjects. It would not isolate the causal effect of FaceOcc if measurement and
cohort change together. A comparison requiring causal attribution needs matched
eligible rows and separately reported cohort expansion, not pooled old/new scores.

That potential does **not** activate a fit. The current records lack an exact
admitted matching-mask cohort, with known beard/covering/skin-loss concerns
resolved or held under a pre-result eligibility policy. The no-go is therefore
about current evidence and scope, not a blanket requirement for a pristine final
test before every development experiment.

## Conditions that would change this decision

Only revisit calibration when there is new substantive evidence:

1. Exact subject/image/label/duplicate/exposure and role manifest under the fixed
   FaceOcc measurement contract, with actual-skin eligibility reasons established
   before mapping results. Retain all failures/holds; do not fit just favourable
   cases from the49diagnostic attempts.
2. A bounded, justified scope and a single preparation/evaluation protocol. No
   claim of untouched or ten-category validation; unsupported categories explicit.
   No broader processing of755records just to see whether accuracy rises.
3. Predeclared subject-balanced retained isotonic recipe, same-row fitting-subject
   median baseline, subject-held grouping, category/lighting support and failure
   denominators. Choose no calibrator setting on outcomes. Necessary comparative
   gates alone do not establish reliable mapping; task adequacy/uncertainty must
   be justified before fitting.
4. One run then stop, no automatic all-row lookup export or correction training.
   A failed result remains evidence rather than initiating another small sweep.

No additional manual annotation batch, recruitment or adviser-response gate is
imposed here. Current four qualitative judgments and35technical parity checks
remain useful evidence but do not fulfil these conditions. Another software
replay or metadata recount would not add the missing measurement validity.

## Practical direction after this decision

Keep FaceOcc as the preferred experimental candidate and the old method as
baseline. Keep reliable MST and automatic correction explicitly unfinished.
For work that can proceed without pretending the mapping is solved, consolidate
the demonstrable implementation, reproducibility and negative/positive thesis
results and existing experimental Android parity/delivery evidence. This decision
does not authorise swapping the Android/Python correction model or omitting MST.
Any later request to implement a limited experimental mapping must explicitly
resolve the scope/admission question above; do not infer it from "continue".

Panel record: there is promising masking evidence and a documented reason not
to claim model validation. No new MST algorithm, category thresholds, correction
model or final dataset is adopted. Retain ITA + calibrated MST + facial statistics
→ decision-tree gamma/red/blue correction. Do not turn lack of readiness into
an unsupported claim of methodological impossibility.

## Saved evidence

outputs/faceocc_mst_feasibility_v1/decision.json records the go/no-go result;
matching_attempts.json and matching_subjects.json give33attempt/23success/four
subject denominators; category_support.json compares previous15subjects, current
four FaceOcc subjects and full19inventory; input_sha256.json binds source records.
Script383asserted33unique MST-E attempts,23technical successes and755potential
keys, and checked input hashes unchanged. No pytest rerun for metadata-only
decision work. Last broader run911passed/29.48s excluded desktop GUI because
Tcl/Tk is unavailable, not a full-suite pass.
