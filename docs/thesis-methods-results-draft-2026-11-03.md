# TrueHue: methods and interim experimental results

**Working thesis draft, updated 3 November 2026. Development is ongoing.**
This document updates the working account through the completed script406 plan.
It does not replace the submitted proposal, certify thesis completion or claim
panel approval. The older methods/results draft and dated evidence remain intact.
Read with the [updated discussion and interim conclusion](thesis-discussion-limitations-conclusion-draft-2026-11-03.md).

## Study objective and evidence boundaries

The study investigates whether skin-tone-aware correction can improve
synthetically distorted photographs relative to their original photographic
references. The original photograph supplies the reconstruction target, not an
instrumental measurement of a person's intrinsic skin colour. This interpretation
matches the submitted proposal's objectives and limitations, particularly PDF
pages10–14 (printed3–7), learning procedure at PDF63 (printed56), and reference-
based evaluation at PDF65 (printed58). No colourimeter or newly recruited
controlled-capture cohort is required merely to make this photographic claim.
Suitability of sources, permissions, measurement, independent evaluation and
reference limitations still require explicit evidence.
([Verified proposal scope](proposal-scope-validation-2026-11-03.md).)

The retained pipeline is face detection, facial skin measurement, ITA estimation,
calibrated MST mapping, facial-statistics feature construction and decision-tree
prediction of gamma, red gain and blue gain. Reliable MST mapping and reliable
automatic correction remain unfinished. Four evidence types are distinguished:
historical automatic-model experiments, qualitative mask diagnostics, target-aware
operator fits, and generated-array arithmetic checks. Their metrics do not
establish the same claim and are not pooled as a single performance result.

## Current development methods

### Measurement and correction support

Measurement and correction use separate supports. Measurement aims to select
facial skin while excluding the eyes, eyebrows, mouth/lips, hair and a conservative
nasal-base region. Neck pixels and correction alpha are excluded from ITA and
facial skin statistics. Predicted skin classes and programmed exclusions do not
prove that every selected pixel is actual skin: beard, glasses and coverings
remain observed sources of contamination.

The user-adopted correction design covers the selected whole face, including
internal facial features and hair/objects within its outline, together with the
associated visible neck. Explicit protected pixels override this support.
Enclosed correction holes are filled, and correction fades inward at the outer
boundary of the combined face/neck support using a fixed smoothstep. Filling
correction holes does not add those pixels to measurement. Six of16 saved cases
changed in the continuity check, with588 pixels filled; outer notches and a
forehead-coverage concern remained. Earlier approvals do not automatically apply
to changed supports. The previews use fixed demonstration parameters rather
than a newly trained automatic model.
([Adopted design](adopted-masking-design-2026-11-01.md);
[continuity results](reference-r1-and-continuity-results-2026-11-01.md).)

A pretrained FaceOcc visible-face veto was investigated as an additional
measurement component. It removes selections from the existing parser mask
rather than replacing the correction tree. Its MediaPipe five-anchor alignment
to the saved template is a documented TrueHue adaptation, not equivalence to
the upstream3DDFA preprocessing. FaceOcc is the preferred experimental candidate,
not a validated measurement method or an adopted demo component. Old parser and
FaceOcc feature/lookup contracts cannot be interchanged.
([Comparison and limitations](faceocc-comparison-evidence-2026-11-01.md).)

### Synthetic distortion and target construction

Table2 does not fully specify transform order, brightness units, contrast pivot
or the conversion from colour-slider values to RGB. The existing direct-gamma
interpretation was audited on generated pixels: a neutral input value64 became
56,59 and65 under the light/medium/dark exposure settings. Thus progressively
stronger underexposure was not established by that interpretation. The user
authorised a documented formula revision while retaining three correction
outputs. This is an implementation change, not a claim that the proposal
already specified the new formulas.
([Table2 audit](proposal-distortion-recipe-audit-2026-11-03.md).)

Two experimental recipe layers were subsequently defined. Core exposure uses
direct exponent1/g for underexposure and g for overexposure, with Table2 gamma
magnitudes .85/.70/.60. Core colour reduces red for a relatively cool cast or
blue for a relatively warm cast using gain1-abs(slider)/255. Combined core cases
apply the power before attenuation. Extra contrast and additive brightness/
colour offsets are omitted from these core probes. Attenuation also darkens:
these are not pure chromaticity changes or calibrated physical white-balance
errors. They are not equivalent to the earlier additive interpretation.

The full directional offset/contrast/additive-colour recipe is retained as a
separate composite stress design. Its clipping and large residuals are not
discarded. A recipe's stress-design membership is distinct from whether a
particular image actually clips. Unchanged controls, core candidates and stress
outcomes are reported separately. A no-clipping technical role is not proof
of recoverability or permission to admit a training source.
([Exposure revision](directional-exposure-revision-results-2026-11-03.md);
[role rules](synthetic-development-role-results-2026-11-03.md);
[colour definitions](core-colour-recipe-results-2026-11-03.md).)

An isolated three-output solver constructs approximate correction targets using
the supplied application alpha and scoring support. One bounded local least-
squares fit starts at[1,1,1], uses bounds[.25,4] for each control, maximum500
evaluations and tolerances1e-10. It fits float encoded-RGB error and separately
reports actual RGB8 rendering error, rank and bound status. Neutral controls
receive exact neutral settings; unsuccessful/degenerate fits receive no usable
target. The analytic unblended inverse is not assumed valid after clipping,
blending or quantisation. A reference can supply supervision and metrics but
cannot enter inference features. Solver outputs are not automatic predictions
and have not been admitted as a new real-photo training table.
([Target-construction evidence](blended-recovery-target-results-2026-11-03.md).)

## Interim results

### Historical automatic-model comparisons

Earlier exposed-cohort decision-tree experiments remain part of the research
record; they are not results for the revised masks/recipes. The47-case endpoint-
feature comparison reduced mean CIEDE2000 from8.013 to5.300 against its matched
comparator, but one of26 clean originals changed and the candidate was not
adopted. A later105-case comparison improved normal-primary error from8.312 to
6.629 while worsening stress error from11.279 to18.000 and increasing clean
failures from one to three. In the121-case source-expansion comparison the
candidate's total error was7.956 versus6.613 for its reference, and four of32
clean originals changed. Both successors were rejected. These experiments have
different membership and cannot be compared as one controlled progression.
([Endpoint results](endpoint-feature-tree-results.md);
[primary comparison](reviewed-primary-training-results.md);
[source-expansion comparison](broader-source-comparison-results.md).)

### Matching nostril-excluded MST evaluation

The completed cycle attempted418 photographs from15 exposed subjects, retaining
393 successful measurements and25 failures. The same successful rows and
subject-held memberships were used for the prior semantic and revised nostril-
excluded comparisons. No alternative radius or fitting recipe was tried after
the result. The following are image-weighted development metrics, not final
population accuracy.

| Metric | Prior semantic | Nostril-excluded | Same-row median baseline for revised cycle |
|---|---:|---:|---:|
| Mean absolute MST-category error | 2.097 | 2.125 | 2.855 |
| Exact-category accuracy | 12.47% | 12.98% | 13.99% |
| Within one category | 36.64% | 35.88% | Not reproduced here |

Despite reproducible exclusion checks, beard and face-covering contamination
remained visible.177 of393 measured photos lacked a different fitting subject
with the same official category. Repeated photos did not establish additional
independent people. The mapping was not adopted, and no new correction tree or
runtime lookup followed this cycle.
([Full calibration report](nostril-mst-calibration-results-2026-11-01.md).)

### FaceOcc and actual-image qualitative evidence

The fixed25-attempt diagnostic produced17 outputs with eight retained parent
failures. Premarked non-skin points still selected decreased from4/4 to1/4;
both marked skin points remained. The beard point persisted. Median selection
retention was95.44%, which is not true-skin recall. Sparse assistant marks do
not establish dense-mask accuracy or a general error-reduction percentage.

A broader cycle retained24 attempts,18 paired outputs and six failures. In the
four-case human comparison, two preferred FaceOcc and two were judged similar.
Assistant inspection separately identified possible skin loss and unresolved
occluder concerns. An isolated service exactly replayed35 saved successes across
49 attempts with14 retained failures; that is software consistency, not35 mask
admissions. The later fixed19-subject study yielded11 favourable structured
answers, seven concerns/uncertainties and one original processing failure.
Notes and assistant concerns remained distinct. Only MST1/4/5 had two favourable
people each before other concerns; this was not sufficient calibration admission.
([FaceOcc comparison](faceocc-comparison-evidence-2026-11-01.md);
[human comparison](faceocc-qualitative-conclusion-2026-11-01.md);
[service replay](faceocc-development-service-results-2026-11-01.md);
[19-subject results](mst-subject-skin-study-results-2026-11-02.md).)

### PPR10K operator-capacity experiments

These experiments used known editor-A targets to fit parameters per photograph,
not a trained tree's predictions. Their hard, approximate face-only polygons
did not validate the adopted whole-face/neck blending or actual-skin measurement.

| Fixed diagnostic | Saved result | Interpretation |
|---|---|---|
| Six three-control fits | Check-region mean relative CIEDE2000 13.44→4.79 against uncorrected source | Target-aware approximation; wedding pink/flat residuals remained |
| Same six, added contrast control | Three-control4.793→four-control2.759; four improved/two indoor cases worsened | Experimental capacity change, not fourth-output adoption |
| Eight further fixed photos | Check-region mean4.964→2.552; increased clipping in six | Original regions included mixed content in two cases; not certified skin-region performance |
| Fourteen saved adjustments, revised support and soft boundary | All-region mean2.548→2.522; endpoints1461→364; specified flattened pairs986→153 | Same saved parameters, no refits; not directly comparable to earlier check-only scores |

Source-only inspection identified a blue shirt in the904 region and bright
background in1188. Original results were preserved as mixed-region evidence.
The later rendering check used identical revised regions for hard/smooth
comparison, retained all14 saved settings and did not refit them. Eleven image
errors improved slightly and three worsened. Endpoint/adjacent-pair counts are
code-level measures, not percentages of texture recovered. Prior indoor
regressions were not erased. The fourth contrast control and soft boundary
remain separate experimental candidates, not runtime or tree-schema changes.
([Three-control diagnostic](ppr10k-operator-diagnostic-results-2026-11-02.md);
[contrast comparison](ppr10k-contrast-diagnostic-results-2026-11-02.md);
[new groups](ppr10k-new-group-comparison-results-2026-11-02.md);
[region/detail correction](ppr10k-clipping-detail-results-2026-11-02.md);
[saved-parameter rendering check](ppr10k-smooth-boundary-results-2026-11-02.md).)

### Generated-image recipe and target checks

| Bounded check | Observation | What it does not establish |
|---|---|---|
| Script401, three generated cases | Clean0→0; matching distorted-input MAE25.078→target-fit0.253; complex clipped44.380→15.267 | Automatic prediction or full representability |
| Script403,18 probes | Exposure direction/severity ordered; severe clipping and large residuals retained | A training-ready recoverable distribution |
| Script404,24 retained cases | Three clean/six exposure core candidates/15 clipping stress; new core residual0.048–0.242 | Actual faces, person coverage or perfect inversion |
| Script405,18 new probes plus clean | No forward clipping; colour/combined residual0.008–0.273; clean exact | Physical white balance, lossless processing or generalisation |

Errors in this table are mean absolute RGB8 channel-code differences over
positive-alpha pixels, not CIEDE2000 or percentages. Script405 used a chromatic
ramp different from the earlier neutral ramp; these rows are not a controlled
recipe leaderboard. It retained384 summed new endpoint channel samples from
rounding despite no forward clipping. The latest98 focused tests passed in
2.51seconds, but this is not a new full-suite result or model-quality measure.
([Target checks](blended-recovery-target-results-2026-11-03.md);
[exposure](directional-exposure-revision-results-2026-11-03.md);
[roles](synthetic-development-role-results-2026-11-03.md);
[colour](core-colour-recipe-results-2026-11-03.md).)

## Application status and unfinished evaluation

The saved Android evidence includes six native emulator tests,18 JVM tests and
one fixed-example Python pixel-parity check. It uses the older experimental
baseline5/fold1, lookup and rule-based masks, not FaceOcc or the newer whole-
face/neck support. Physical-device/general-photo parity and performance remain
unestablished. Working app functions and software tests do not validate correction
quality. Professional Google Form appraisal has not been completed; the recorded
sequence is a good initial model, feedback-informed refinement and re-review.
([Implementation evidence](delivery-checkpoint-2026-11-01.md).)

The integrated plan proposes a future14-case diagnostic matrix per admitted
source:one unchanged control, eight core cases and five composite stress-design
cases. This is not a selected training ratio, independent sample size or final
evaluation allocation. Source/reference/support admission, person/duplicate
grouping, matching MST, full feature schema, justified adequacy, training weights
and acceptance criteria remain unresolved. No new real-photo training followed
the recipe checks. DAST/STW requests are user-reported sent; as of this update
the user reports no reply or new files. Access alone would not resolve every gate.
([Integrated plan](integrated-correction-development-plan-2026-11-03.md).)

## Status of changes from the submitted proposal

| Change | Present status |
|---|---|
| Learned parsing and separate measurement/correction supports | User-authorised development; mask/rendering design adopted, actual-skin validity incomplete |
| Whole-face/neck coverage, hole filling and inward blending | Adopted for continued development; no automatic-model validation follows |
| FaceOcc veto and custom alignment | Preferred experimental candidate; not deployed or independently validated |
| Revised Table2 interpretations, clean/core/stress decomposition and local target construction | Authorised experimental development; final data/training distribution unadopted |
| Fourth contrast control and soft clipping | Separate unadopted experiment; retained output schema stays three controls |
| Grouping, role and admission safeguards | Explicit requirements; adequate final cohort/split not established |

Exact source wording, page references, decisions and evidence are maintained in
the [panel change register](panel-change-register.md). Recording a change or user
development approval is not panel approval. These are interim methods/results
for continued editing and later institutional chapter/reference formatting.
