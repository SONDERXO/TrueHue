# TrueHue: adviser progress briefing

Prepared for 7 November 2026, 11:00 PM, Asia/Manila. Current through the completed clean-constrained gate comparison. This is a discussion briefing, not a final thesis or approved method amendment.

## Opening statement

“TrueHue aims to correct exposure and colour in a single-person photograph on an Android phone. We have built working Python and Android prototypes, developed facial measurement and object-protection tools, and completed a sequence of controlled model experiments. The strongest recent progress is a better experimental skin-tone estimator and evidence that correction helps many distorted inputs. The main unresolved problem is deciding when to leave an already acceptable photo unchanged. The newer model is still under development and has not replaced the older demo model.”

## Intended system and terminology

The retained method is photo input → face detection → facial-skin measurement → Lab/ITA → calibrated Monk Skin Tone (MST) estimate → decision-tree correction controls → correction/no-correction decision → rendered result. The controls are gamma/exposure, red gain and blue gain. ITA is an image-based colour angle; MST is a skin-tone score, not an ethnicity prediction. Lab describes lightness and colour components. The gate decides whether to apply predicted controls.

The research target is restoration of synthetically altered photographs toward their original photographic references. This does not demonstrate recovery of intrinsic biological skin colour. A colourimeter or new participant recruitment is not automatically required for this photographic claim. Original reference photos themselves can contain lighting casts.

## Work completed from the beginning

| Phase | Work completed | What we learned / current standing |
| --- | --- | --- |
| Initial implementation, through October | Established Python environment, configuration, face detection, skin selection, Lab/ITA arithmetic, synthetic exposure/colour changes, target-control fitting, baseline comparisons and reproducible reports. | The pipeline can run, but arithmetic correctness alone does not establish natural correction. |
| Initial data preparation | Inventoried FairFace, SCIN and MST-E sources, labels, group roles and permissions; prepared manifests and held-group experiments. | FairFace does not supply the required MST labels; many inspected SCIN images were unsuitable for facial work. Dataset availability is different from suitability. Historical evaluation allocations remain preserved. |
| Early correction development | Built and evaluated decision-tree candidates, clean/no-correction controls, saved-tree export and portable inference. | Some earlier trees altered unchanged photos or lost to the no-correction baseline. Failed candidates and their results were retained. |
| MST calibration work | Tested mapping ITA to MST, including matching recalibration after measurement changes. A historical cycle produced 393 measurements from 418 attempts across 15 subject-held folds. | That cycle's ordinal MAE was 2.125 and exact category agreement 12.98%; it was not adopted. These older category results are not directly comparable with the newer continuous-score experiment. |
| Face and neck development, late October–early November | Separated skin-only measurement from wider face/visible-neck correction; examined brows/lips, nostril exclusions, correction-hole filling and inward boundary blending. | Broader correction helps coverage, but measurement must remain restricted. Hole filling and wider regions do not establish object safety. |
| Masking and occlusion diagnostics | Evaluated the existing parser, FaceOcc visibility veto, face-contained support, appearance preprocessing and a larger ResNet34 parser. Documented alignment adaptations and saved-mask replays. | Missed skin, beard/hair contamination, coverings and uncertain boundaries remain. Larger parsing improved selected skin coverage while also increasing unwanted inclusions. |
| Android prototype | Implemented gallery input, local face/skin/ITA/MST/tree processing, failure reporting, before/trial comparison and mask inspection; built a debug APK and checked portable-tree parity. Polished consultation UI on November 5. | A functional prototype exists using the older experimental pipeline. Newer research masks/models are not integrated. Latest recorded Android build had 18 JVM tests passing, zero lint errors and 45 warnings; that is not new phone validation. |
| Reference and operator diagnostics | Examined reference suitability, PPR10K examples and a separate four-control smooth rendering candidate; checked clipping, gamma conventions and exact blended target fitting. | Reference-aware “oracle” control fitting tests what an operator can do when given the target; it does not measure learned prediction. Four-control work was not adopted; three outputs remain retained. |
| Synthetic recipe audit | Audited proposal Table 2 interpretation; documented directional exposure changes, colour attenuation, and separate clean/core/stress roles. Tested generated arrays and photographic recovery. | Clipping and quantisation can prevent exact restoration. Recipe departures are recorded for future thesis/panel discussion. |
| FFHQ photographic preparation | Prepared 12 fixed photographic lineages and 168 clean/core/stress conditions; checked fixed-support recovery and actual-input mask recovery, with failures preserved. | Fixed-support oracle core RGB MAE fell from 18.665 to 0.135; actual-input support core residual was 0.591. These are target-aware fits, not automatic-model accuracy or 168 independent people. |
| Research infrastructure | Created private review pages, source/hash manifests, reproducible scripts, source checkpoints, navigation, experiment reports and a method-change register. | Experiments and failures can be traced and replayed. Raw data, labels, weights and private reviews stay ignored by Git. |
| Stellenbosch acquisition, November 5 onward | Obtained the skin-tone dataset directly from Rensu Theart; inventoried 285 publisher groups and 21,375 JPEGs, all 224×224; prepared bounded cohorts and preserved source decimal scores. | Research use only, cite the source paper, no redistribution without consent. Publisher groups are grouping keys, not verified identities across sources. Large archive size does not equal a large evaluated cohort. |
| Completed human references | Finished the six-photo sparse-point review and manual patch review: 36 polygons covering 3,156 native union pixels. | These are limited development references. Some marks include neck; no full-face skin/object ground truth follows. No repeat annotation is needed. |
| Contextual MST experiment, November 6 | Compared ITA + Lab with ITA-only and a training-group median in publisher-group-held folds on 30 fixed photos from 10 groups; 29 measurements available. | Continuous-score MAE: 0.7314 versus 2.3655 and 2.9655. Promising within this exploratory cohort; not independent real-world validation or proof of fairness. |
| Correction-model sequence, November 6–7 | Tested an initial correction tree, clean-example balancing, colour-distribution features, increased capacity, a gate, whole-scene features, scene-aware and benefit-aware gates, separate exposure/colour predictors and a retrained gate. | Several candidates improve average distorted-input error. More correction can also create more harmful edits. None of these newer candidates has been adopted. |
| Separate-group and actual-input checks | Froze a full candidate for 24 later photos across eight separately selected publisher groups; tested 336 synthetic inputs using borrowed masks and then masks derived from actual distorted inputs. | Actual-input masking exposed failures hidden by original-photo masks. Later groups have since become development-exposed and are no longer an untouched final test. |
| Detector fallback and diagnosis | Tested one fixed fallback for zero-face failures; usable measurements increased from 275 to 291 of 336. Traced a harmful recovered correction through features, gate and tree leaves; tested removal of two gamma scene-chroma features. | More usable measurements can enable harmful corrections. The feature restriction did not resolve the focal case. Fallback and restriction remain experimental. |
| Latest gate work, November 7 | Tested expected signed benefit, then a version constrained to leave every fitting clean example unchanged. Completed 11 constrained fits and independent artifact/constraint checks. | Fitting clean constraints passed, but unseen clean photos were still edited. Latest candidate failed its predeclared acceptance screen and was not adopted. |

## Features available today

| Capability | Python desktop demo for tonight | Newer Python research work | Android prototype |
| --- | --- | --- | --- |
| Select a photo and run locally | Available | Available through research scripts | Available |
| Face detection, selected-skin view, Lab/ITA, MST and three correction controls | Older experimental pipeline | Newer measurement and continuous-MST candidates evaluated | Older experimental pipeline |
| Before/result comparison and clear failure messages | Available; three image panels | Saved comparison boards and reports | Available |
| Save output and traceable report | Desktop export available | Private model/metric/trace artifacts | Verify actual phone save flow before claiming it works |
| Face/visible-neck support and blending | Not integrated into live desktop inference | Implemented and diagnosed in separate previews | Not integrated |
| Object protection and transparent-lens treatment | Not integrated into live desktop inference | Candidate vetoes; transparent/opaque/uncertain glasses choice in separate preview | Not integrated |
| Decide whether correction is beneficial | Not the latest research gate | Multiple evaluated candidates; clean preservation unresolved | Not the latest research gate |
| Adviser progress view | Updated for November 7 | Aggregate findings only | No change for this meeting |

For transparent prescription glasses, the intended behaviour is to protect frames/rims while keeping visible facial areas through lenses. Current preview support uses an explicit glasses choice and an approximate rim envelope; automatic glasses-type recognition and exact frame segmentation are not solved.

## Latest results to explain

“Clean” means no additional synthetic distortion; it does not mean physically neutral lighting. RGB MAE is average absolute channel error in 0–255 codes; lower is better, but it is not a naturalness score.

| Evaluation | Retained frozen research gate | Signed-benefit gate | Clean-constrained gate |
| --- | ---: | ---: | ---: |
| Development held-group clean photos changed | 3/29 | 27/29 | 7/29 |
| Development core-distortion RGB MAE | 13.51 | 9.63 | 11.26 |
| Later clean photos changed | 1/23 | 23/23 | 3/23 |
| Later core RGB MAE, actual-input masks with detector fallback | 17.43 | 11.65 | 14.06 |

The clean-constrained gate improves on the signed gate's clean behaviour and improves distorted-input means versus the retained gate, but still fails the required zero changed clean photos in both cohorts. It also harms more core cases than the retained gate: 15 versus 9 of 232 development variants and 5 versus 2 of 184 later reference-scored variants. It is not adopted. The retained research comparator is itself experimental and is not the model running in the desktop demo.

All 290 fitting constraint occurrences passed, but they repeatedly involve the same 29 clean originals across fitting configurations. They are not 290 independent photos or people. The latest focused suite recorded 38 passing tests in 6.86 seconds; tests establish checked software behaviour, not scientific validation.

## Limitations and unfinished requirements

1. **Clean preservation:** training protection does not reliably protect unseen clean photos. Better mean distortion error cannot conceal unwanted edits.
2. **Measurement and masks:** missed/fragmented skin, beard/hair contamination, glasses/covering uncertainty, tiny selected regions, hard visible correction boundaries and outright failures remain.
3. **Limited evaluation:** fitting cohorts are small despite the large archive. Repeated folds, variants, conditions and review pixels are dependent; publisher keys are not cross-dataset identity verification. Exposed groups cannot be recycled as an untouched final test.
4. **Synthetic-to-real transfer:** controlled alterations do not represent every camera, lighting condition, shadow or white-balance error. Studio backgrounds/charts may provide acquisition-specific cues.
5. **Reference limits:** original photographs are photographic references, not intrinsic skin truth. RGB error and CIEDE2000 do not replace perceptual naturalness or expert review. Manual patches are sparse and partly include neck.
6. **MST limits:** the new estimator is exploratory; mask contamination, illumination sensitivity, range clipping and limited highest-range untouched coverage remain relevant. Fairness across skin tones is not established.
7. **Pipeline mismatch:** borrowed original masks can make results look better than actual-input masks. Restricted-region correction experiments do not validate the full object-protected face/neck renderer.
8. **Integration:** newer models are not adopted or ported. Physical-phone checks, broader parity, end-to-end timing and final app regression work remain after model selection.
9. **Professional appraisal:** actual photographer feedback, refinement and re-review through the existing Google Form remain future work after a good initial model. No MOS or expert approval is invented.
10. **Permissions and academic process:** restricted dataset images/labels/private boards cannot be redistributed without consent. Method changes are documented; adviser/panel approval is not assumed. No scientific admission flags have been enabled.

## What we need

- One evidence-based next correction decision, with explicit clean-preservation and distorted-input acceptance criteria. No automatic parameter, threshold, feature or capacity sweep.
- A model and masking/rendering combination that passes a frozen end-to-end assessment, keeping failures and denominators visible.
- A justified independent evaluation design using eligible existing evidence where possible; another dataset or recruitment is not automatically required and cannot guarantee success.
- After an acceptable initial model: actual professional feedback, controlled refinement and a separately frozen final appraisal.
- A permitted personal/example photo and a rehearsal on the presentation computer. The meeting demo must not depend on sharing restricted research boards.
- For the conference: venue/track, official template, page limit and deadline timezone. These determine whether a prototype/development paper is suitable. No submission or outreach has been authorized.
- Adviser guidance on academic expectations, acceptable reported contribution and remaining thesis deliverables. This meeting is not a prerequisite for routine authorized development.

## Proposed next work and projected dates

These are planning targets prepared November 7, not an approved experiment schedule or a guarantee of model success. Model development stays the first priority; writing uses existing results without triggering new fits.

| Date / window | Intended deliverable | Dependency / stop decision |
| --- | --- | --- |
| November 7, before 11:00 PM | Adviser briefing, updated desktop progress view and rehearsed prototype | Use aggregate results and a permitted photo; identify older live model clearly. |
| November 8 | Agree on one next technical step; proposed saved-trace audit of constrained-gate clean failures versus retained gate | Audit existing outputs only if selected; do not fit from this briefing. |
| November 9–11 | Target one bounded correction intervention and evaluation, if evidence justifies and user authorizes it | Freeze protocol first; retain/reject by predeclared criteria. If it fails, revise the forecast rather than adopt it for the deadline. |
| November 12 | Model-readiness checkpoint and conference claim/scope decision | Separate prototype/development findings from validated final-model claims. |
| November 13 | Target a coherent conference draft and checked submission files, if venue requirements and scope are settled | Existing evidence can support writing; suitability and adviser feedback remain unresolved. |
| November 14 | User-reported conference submission deadline | Submission readiness is not completion of the correction model. No automatic submission. |
| November 15–21 | Provisional window for model stabilization, integration/parity, phone timing and initial professional feedback | Only feasible if an acceptable candidate emerges early and reviewers are available. Otherwise reschedule. |
| November 22–28 | Provisional window for refinement, frozen evaluation and thesis/demo consolidation | Conditional on prior results and review turnaround; no guaranteed final completion date. |

**Projected completion to communicate:** aim for a conference-ready evidence package by November 13; use November 28 as a provisional project-completion planning target, with low confidence and a reassessment on November 12. A validated final correction model has no defensible fixed completion date yet. The earlier before-November-7 target was not met for model completion or final evaluation; the working prototype was delivered. Do not present the new target as a scientific forecast or adviser-approved extension.

## Suggested meeting flow (10–15 minutes)

1. State the objective and opening progress summary (1 minute).
2. Explain the development phases and the distinction between a working app and an effective model (3 minutes).
3. Show the desktop demo using a permitted single-face photo: input, selected skin, ITA/MST estimate and trial result; explain any failure honestly (3 minutes).
4. Open Research progress and show the latest aggregate comparison, including clean failures (2 minutes).
5. Explain remaining work, conditional timeline and the November 14 submission decision (2 minutes).
6. Discuss expectations: contribution required for the conference, thesis evaluation expectations, and how documented method departures should be handled. Do not imply formal approval from the discussion alone.

Suggested response to “Why is it taking longer?”: “Each stage exposed a different failure: skin selection affects measurement; measurement affects tone estimation; correction can improve distorted photos while worsening clean ones. We now have reproducible comparisons and a clear unresolved acceptance requirement. We have kept failed results rather than integrating a model just because its average error improved.”

## Evidence and full project navigation

- [Project guide and chronological results](README.md), [full research library](navigation/research-library.md), [method-change register](panel-change-register.md).
- [Verified proposal scope](proposal-scope-validation-2026-11-03.md), [historical interim methods/results](thesis-methods-results-draft-2026-11-03.md), [historical MST cycle](nostril-mst-calibration-results-2026-11-01.md).
- [Object protection](object-protected-correction-results-2026-11-05.md), [clear lenses](clear-lens-correction-results-2026-11-05.md), [reference-aware photographic recovery](ffhq-correction-target-results-2026-11-05.md), [actual-input support](distorted-input-support-results-2026-11-05.md).
- [Received dataset](stellenbosch-received-data-results-2026-11-05.md), [sparse reference results](stellenbosch-reference-point-results-2026-11-06.md), [patch results](skin-patch-measurement-results-2026-11-06.md).
- [Exploratory MST](exploratory-real-mst-results-2026-11-06.md), [split predictors](split-control-predictors-results-2026-11-06.md), [frozen later-group check](frozen-split-subject-check-results-2026-11-06.md).
- [Actual-input mask check](input-derived-mask-check-results-2026-11-06.md), [detector fallback](detector-appearance-fallback-results-2026-11-06.md), [signed gate](signed-benefit-gate-results-2026-11-07.md), [latest constrained gate](clean-constrained-gate-results-2026-11-07.md).
- [Android prototype status](android-consultation-update-2026-11-05.md), [desktop meeting guide](simple-python-demo.md).

This November 7 briefing supersedes older dated briefing statements that no real contextual MST or photographic correction-tree experiment exists. Those experiments now exist as exploratory evidence; their existence does not establish model admission, generalization or final validation.
