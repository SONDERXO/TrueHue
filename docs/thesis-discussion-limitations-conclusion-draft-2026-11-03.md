# TrueHue: discussion, limitations and interim conclusion

**Working thesis draft, updated 3 November 2026. Development is not finished.**
This updates the interpretation of the saved experiments without presenting them
as a completed final evaluation. The older31October draft remains historical.
Use the accompanying [methods and interim results](thesis-methods-results-draft-2026-11-03.md)
for experimental tables and primary local evidence links. No new experiment was
run to write these sections, and the submitted proposal is unchanged.

## Discussion

The work to date establishes a reproducible research implementation and several
useful diagnostic findings, while leaving the principal performance questions
unresolved. Separating the measurement region from the correction region
addresses a practical difference between estimating facial skin statistics and
rendering a visually continuous correction. Eyes, lips, hair and neck need not
contribute to skin measurement even when the adopted correction support covers
the whole selected face and associated visible neck. Filling enclosed correction
holes and blending inward at the outer combined boundary reduce untreated
patches and abrupt transitions in previews. These changes improve the intended
coverage/rendering design; the previews do not establish a newly learned model's
correction accuracy. Outer gaps and image-specific association concerns remain.

Measurement validity remains a separate issue. The fixed FaceOcc comparison
removed several premarked non-skin selections without reducing technical
availability, and two of four human comparisons preferred it. However, the beard
mark remained, assistant inspection identified possible skin loss, and there
was no dense ground-truth annotation or independent-subject accuracy estimate.
The later19-subject study supplied11 favourable structured answers but retained
seven concerns/uncertainties and one failure, as well as conflicting notes.
These outcomes support continued investigation of visible-face constraints;
they do not justify treating every successful mask or favourable answer as an
admitted calibration measurement.

The matching nostril-excluded cycle reinforces this distinction. Its393
measurements reproduced the programmed exclusions, yet subject-held category
error was2.125 versus2.097 under the prior semantic mask. Exact accuracy was
12.98%, below the same-row median baseline's13.99%. Lower ordinal error than
that baseline did not establish a reliable categorical estimator. This cycle
therefore did not justify adopting a new lookup or training the correction tree
with incompatible old features. A different measurement model requires matching
calibration evidence rather than transferring earlier results by association.

Historical automatic decision-tree comparisons also showed why favourable mean
error is insufficient. Endpoint features improved an early matched result, but
clean-image changes prevented adoption. Later source/data expansions failed
their comparative quality and clean-image requirements. These rejected candidates
remain negative results, not intermediate versions silently promoted into the
current pipeline. More variants do not supply more independent people, and the
experiments do not establish that additional data alone will solve the problem.

The PPR10K studies investigated a different question: whether a chosen correction
operator can approximate a known photographic edit. Adding a fourth contrast
control reduced the six-image check-region mean relative colour error from4.793
to2.759, but two indoor cases worsened and clipping increased in four photographs.
A further eight-photo comparison was promising in its original regions, but
subsequent inspection found clothing/background contamination in two regions.
Those original statistics remain mixed-region evidence. This correction of the
interpretation matters: numerical agreement over a selected polygon cannot be
called certified facial-skin performance merely because the polygon was intended
to represent a face.

The later fixed soft-boundary rendering check reduced endpoint and flattened-
pair counts on identical revised regions while retaining similar average colour
agreement. The parameters were saved target-aware fits, not predicted outputs,
and no refitting occurred. These observations identify a possible operator
capacity/detail trade-off. They do not establish recovery of texture, generalised
automatic correction or adoption of a fourth output. The paper's gamma/red/blue
schema remains the retained direction.

Generated-image checks clarified the implementation of synthetic supervision.
The original Table2 interpretation did not guarantee progressively stronger
underexposure, and composite offsets/clipping could not be assumed exactly
invertible by three controls. The revised development recipes make exposure
direction explicit and distinguish core examples, unchanged controls and
composite stress cases. Colour attenuation avoids forward clipping in the
fixed probes but also darkens the image; it is not physical white-balance truth.
Local target fits left small residuals on core probes and large residuals on
some stress probes. Even zero forward clipping did not prevent rounding-related
endpoint loss. This supports explicit operator/target contracts and reporting of
unrepresentable cases, not a claim that the automatic model has improved.

The proper research claim remains photographic restoration feasibility toward
an original reference. The submitted proposal already excludes proof of recovery
of actual skin colour. A measured intrinsic-colour dataset is therefore not a
mandatory prerequisite for that written objective. Suitable ordinary photographs
can serve as references under justified quality, rights, support and allocation
rules. This scope clarification does not bypass the still-missing reliable MST
component or the need for an admitted, independently evaluated correction cohort.

## Limitations and threats to validity

**Ongoing development and incompatible versions.** The runtime demo, newer masks,
FaceOcc service, experimental three-output targets and four-control PPR operator
are different artifacts. No end-to-end model with all newer components has been
validated. Historical automatic-model scores cannot be transferred to revised
supports, lookups or operators, and software consistency does not establish
scientific validity.

**Photographic references and measurement.** An original dataset photograph is
a reference for reconstructing that photograph, not a measurement of intrinsic
skin reflectance or ideal lighting. Approval of a correction mask does not
certify lighting or actual-skin measurement. Beard, glasses, covering, boundary
loss, blur and exposure concerns remain. The PPR expert edits represent another
photographic supervision choice and were not admitted as the paper's synthetic
training references. Approximate diagnostic polygons exclude neck and do not
validate adopted whole-face/neck rendering.

**Subjects, labels and exposure.** The nostril-excluded evaluation used15 exposed
subjects, with177 of393 measured photos lacking another fitting subject in the
same category. The completed19-subject skin review did not establish an adequate
matching cohort. Variants, video frames, source IDs and publisher group IDs are
not interchangeable with independently verified people. Cross-source person/
duplicate relations and earlier development/reserved exposure require explicit
handling. No untouched final ten-category fairness evaluation is claimed.

**ITA/MST interpretation.** ITA and mapped MST derive from measured image colour;
MST is not an independent illumination observation. Lighting, masks and skin
appearance may confound category estimation and correction. The experiments
do not isolate one cause or prove that the retained method is mathematically
incapable of useful photographic correction. Neither an estimated label nor a
photographic category annotation measures intrinsic skin truth. A compatible
mapping must be evaluated directly, not inferred from improved image appearance.

**Operator and target capacity.** Clipping destroys distinctions, and positive
gamma/gain correction cannot recover all lost input information. Local least-
squares convergence is not global optimality, unique true parameters or a good
automatic prediction. Float fitting and RGB8 evaluation differ because of rounding.
The soft candidate alters endpoints even at neutral controls and remains distinct
from the exact-neutral three-control renderer. Target-aware block checks within
a known photograph do not establish generalisation to an unseen person/photo.

**Metrics and comparisons.** Relative CIEDE2000 measures appearance disagreement
against the chosen reference on declared support, not physical accuracy or expert
preference. RGB8 MAE, category MAE, clipping counts, endpoint counts and qualitative
marks have different meanings. Their denominators and supports differ across
cycles; results are not pooled into one improvement percentage. Revisions to
diagnostic regions were disclosed and old results preserved. Generated arrays
are not facial data, and group names in those probes do not establish MST coverage.

**Training and final evaluation.** The proposed14-case matrix is a diagnostic plan,
not an adopted sample distribution. Actual source/support/person admission,
matching MST, final features, adequacy, weights, splits and numeric acceptance
criteria remain unresolved. Stress failures must stay visible, and reference
images cannot enter inference features. No successful-only subset or repeated
same-subject refit can substitute for independent evidence.

**Deployment and professional assessment.** The Android app has saved emulator
and fixed-example parity evidence using the older experimental baseline, but
not broad/physical-device validation of the newer development pipeline. Actual
phone performance, wider input parity and correction effectiveness remain open.
No completed professional opinion scores or final MOS are claimed. The existing
Google Form is planned after a good initial model, followed by feedback-informed
refinement and re-review; that stage has not been completed.

## Interim conclusion

TrueHue has produced a traceable research implementation, a clearer separation
of measurement and correction masks, improved correction continuity in previews,
bounded FaceOcc diagnostics and explicit synthetic recipe/target definitions.
The completed experiments also identify weak MST mapping, actual-skin selection
concerns, failed automatic-model successors, operator clipping/detail trade-offs
and the limits of target-aware fits. These are interim findings and useful
development evidence, not proof of a finished correction system.

The current evidence does not justify a claim of reliable ten-category MST
mapping, reliable automatic correction across skin tones, intrinsic skin-colour
recovery or completed thesis evaluation. The retained goal is the proposal's
skin-tone-aware photographic restoration task with three correction outputs.
The separate fourth-control experiment remains unadopted. Recording method
changes does not imply panel approval or completion of academic review.

Further development requires substantive source/support/person and matching
MST admission evidence, followed by one justified, predeclared evaluation and
training cycle. No additional formula search, same-cohort calibration or tree
fit is justified merely by completing this writing update. DAST/STW access
requests remain unanswered according to the user's latest report; no access,
cohort or future result is assumed. New data alone is not guaranteed to solve
the observed limitations.

These sections should be revised as development produces new evidence. Final
conclusions, comparative fairness claims, deployment claims and professional
appraisal must wait for the corresponding completed evaluation. See the
[integrated plan](integrated-correction-development-plan-2026-11-03.md) and
[change register](panel-change-register.md) for the current next gates and the
record of differences from the submitted proposal.
