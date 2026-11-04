# Where the implementation differs from the proposal

31 October 2026. Compared with the user's Word copy, especially Sections1.4,
4.1–4.3.2,4.5 and4.10, plus the saved implementation/results records.
This is a consolidated list of documented differences, not a claim that every
experiment became the final method. The original proposal is unchanged.

## First: professional feedback is retained

The proposal already allows professionals to review results during testing and
refinement. The user confirmed that this will be adopted: first obtain a good
initial correction model, ask professionals for ratings/comments through the
existing Google Form, use relevant feedback to improve the model, then ask for
their opinions again. This is **not a departure from the proposal**.

No professional ratings have been collected, and the current failed candidates
do not establish the good initial model required to start that phase. Earlier
notes saying opinions come only after completion were too restrictive if read
as prohibiting refinement. Do not erase those historical notes or fabricate
responses; this clarification supersedes that interpretation.

Call rounds used to improve the model **development feedback**. Save each model
version and the corresponding ratings. Once the model is frozen, report a
clearly separate final appraisal; ratings/images used to guide refinement cannot
be presented as untouched final evaluation. The number of rounds and final
evaluation membership still need a declared procedure. No emails, recruitment
or Form changes are authorized merely by recording this workflow.

## A. Actual choices that differ from, or add detail to, the paper

| # | Paper or intended approach | What we actually did | Status |
|---|---|---|---|
| 1 | Section4.3.2 mentions MediaPipe Face Detection or Haar | Used OpenCV YuNet for face detection | Used in evaluated research pipeline and current demo |
| 2 | Scope says HSV/YCrCb, but detailed method says YCrCb within the face box | Used HSV AND YCrCb together | Resolves an inconsistency in the paper; disclose the actual rule |
| 3 | Face box, largest skin component and minimum1000 pixels | Added required landmarks, detailed eye/brow/full-mouth exclusions, morphology order and versioned support | Additional measurement details; not all explicitly supplied by the paper |
| 4 | Uniform256x256 image size | Fixed whole-frame resizing before detection, INTER_LINEAR, one-face rule and YuNet0.85 | Implementation details beyond the paper, not a change away from its256 target |
| 5 | A calibrated ITA-to-MST lookup for categories1–10 | Used a subject-balanced monotone/isotonic interpolation lookup with half-up rounding | An explicitly experimental calibration method; not final validation |
| 6 | An operational1–10 mapping | The packaged lookup actually emits1–9 and never10 | Known coverage shortfall, not an approved removal of MST10 |
| 7 | MST-E described as evaluation-only in Section1.4, but also used to derive the lookup in4.3.2 | Used it for disclosed mapping development and evaluation, never correction-tree training | Existing paper ambiguity; adviser wording/terms still need reconciliation |
| 8 | ITA, MST and facial color statistics feed the tree | Added six explicit statistics: how often each masked RGB channel equals0 or255 | Extension to the feature description; retained research reference uses eleven features |
| 9 | An ordinary regression tree learns gamma/red/blue outputs | Forced a leaf to output no correction when it contains a fitting clean control | Added safety policy; not ordinary unmodified regression and not a guarantee for unseen clean faces |
| 10 | Synthetic distorted/reference pairs, ordinarily described as three variants | Added original images as explicit no-correction training controls | Additional training design |
| 11 | Table2 distortion settings | Chose concrete formulas, units, clipping/rounding and operation order not fully specified in the paper | Engineering assumptions, not a verbatim reproduction of author equations |
| 12 | Three Table2-style distortions per source | Also generated separate gamma-only lightening and darkening pairs | Supplemental recipe; not the full Table2 method |
| 13 | Severity depends on MST, with darker groups receiving stronger distortion | Several historical comparisons used fixed assigned recipes rather than a completed validated tone-dependent design | Development departure; tone/severity coverage remains incomplete |
| 14 | Distortion/reference pairs provide correction targets | For composite/clipped cases, fitted approximate gamma/gain settings against the reference; known gamma inverses were used where justified | Target-construction choice; clipping and the operator can prevent exact recovery |
| 15 |70/15/15 split stratified by MST, with five-fold validation | Used frozen source-held26/32-fold development comparisons; separate600-source allocation preserves70/15/15 counts but not proven MST stratification | Different executed evaluation procedure; final roles remain reserved |
| 16 | Representative subset spanning the intended MST groups | Used reviewed source/mask subsets with explicit exclusions, duplicates, technical holds and exact variant approvals | Additional admission controls; they do not establish balanced tone coverage or distinct people |
| 17 | FairFace and SCIN correction sources | Latest121-case correction comparison is FairFace-only | SCIN metadata/support was audited, but this is not a completed combined-dataset evaluation |
| 18 | Consistent improvement against uncorrected inputs, including subgroup reporting | Added an exact zero-changed-pixel clean gate and conservative comparative adoption gates | Extra predeclared research acceptance rules, not new runtime thresholds |
| 19 | Main evaluation emphasis on parameter MAE, CIEDE2000 and MST groups | Recent decisions emphasize reference-mask CIEDE2000, clean harm, case/source weighting and primary/stress/variant breakdowns | Additional reporting; it does not substitute for unfinished parameter-MAE/MST fairness evidence |
| 20 | Deploy correction through ONNX Runtime Mobile | Exported a portable decision-tree JSON and checked a Java evaluator | Different tree-deployment route; it does not establish complete Android integration |
| 21 | Training on GX10 or Colab | Actual recorded work uses a local Windows Python3.14 environment | Environment difference; do not claim unused hardware |
| 22 | Android is the end-user application | Built a Python desktop demo as an interim tool | Extra deliverable; Android has not been replaced in the approved scope |
| 23 | One proposed trained correction model | Demo deliberately retains older ten-source baseline5/fold1 while research candidates remain separate | A practical development distinction, not a final-method decision or deployment of the best research reference |
| 24 | Main fair-comparison objective | Added hash-bound artifacts, saved memberships, duplicate/exposure records, exact-mask reviews and replay verification | Reproducibility safeguards rather than changes to the correction family |

Depth3, seed42, minimum leaf1, no weighting, exact failure handling and input-only
features are concrete research settings that need to be reported. Where the
paper leaves a setting unspecified, choosing it is an implementation detail,
not automatically a violation of the proposal.

## B. Historical experiments that were not adopted as the final method

These belong in an experiment history or limitations discussion, not a statement
that the thesis silently switched methods.

| Experiment/change | What happened |
|---|---|
| Native224 measurements and four-feature Lab/ITA trees without MST | Early baselines; later paper-aligned research returned to256 and retained input-derived MST |
| Reciprocal gamma | Earlier operator convention differed from the direct exponent in the proposal. Direct-gamma research now uses the explicit correct operator; the legacy demo remains separate. Only gamma is reciprocated when converting |
| Deeper trees and different leaf sizes | Investigated; no safe general upgrade adopted |
| Extra brightness, chromatic distributions/quantiles and different target coordinates/scales | Investigated; negative results retained, no silent final-schema replacement |
| Weighting, extra clean controls, support/abstention guards and special split objectives | Investigated in development; no validated final/runtime policy adopted from those trials |
| Larger normal-primary and source-expanded training candidates | Both completed frozen comparisons failed and were not adopted |
| Mask hole filling, contour/component reordering and alternative color rules | Diagnostics; no replacement of the hashed evaluated mask contract |
| Learned face parser for fuller face coverage | User authorized the preview; improves some coverage but is an additional learned stage. Separate from evaluated correction and now on hold for adviser discussion |
| Two auxiliary facial-hair exclusion models | Rejected after removing normal skin; automatic use remains off |
| Manual exclusion brush | Optional local mask-preparation/preview tool, not the intended automatic correction workflow |
| Material/paint/makeup protection extensions | Explored/deferred, not silently added to the retained runtime method |

The proposal already specifies a learned face detector as an option. The new
method question concerns adding/replacing the **masking stage** with a learned
parser, not whether the entire proposal prohibited every learned component.

## C. Unfinished or proposed work — not changes we have implemented

| Item | Honest status |
|---|---|
| Reliable correction improvement | Not established; both successor candidates fail the agreed gates |
| Final MST calibration and independent validation | Not completed; lookup is experimental with weak exact accuracy and limited support |
| Full ten-category / light-medium-dark fairness evaluation | Not established; no claim that the paper's10% disparity criterion was completed or satisfied |
| Correct combined FairFace/SCIN coverage and tone-dependent generation | Not completed by the current comparison |
| Independent final test | Not run; historical exposure disclosed and reserved roles locked against tuning |
| Parameter-MAE, final MOS and Android latency reporting | No complete final objective/evaluation package exists; earlier diagnostics do not satisfy all these requirements |
| Professional feedback → refinement → re-review | Retained plan from the paper, now clarified; starts after a good initial model, not with the current failed models |
| Complete Android correction app/device tests | Still required and on hold; a scaffold/APK or Java parity is not the integrated pipeline |
| Visible neck correction | Later user request differs from the paper's explicit facial-only scope; not implemented and needs a scope decision |
| Controlled reference-photo collection | Draft proposal only; no recruitment, purchase, collection or runtime reference input implemented |
| Neutral/color chart at inference | Not proposed for immediate runtime adoption; collection draft uses it only for offline reference evidence |
| A beard-specific final model or parser adoption | Not approved/adopted into correction; on hold |

## What stayed the same

Face detection → selected facial skin → ITA → input-derived MST plus facial
statistics → decision-tree gamma/red/blue correction remains the retained
direction. No correction CNN has replaced the decision tree. The256 target size,
masked correction and unchanged-image baseline remain. No expert ratings have
been invented, and no proposal reference has been silently replaced with a new
source. This list identifies actual changes and gaps without declaring every
prototype or software test a completed thesis result.

## Evidence locations

Source manuscript: `C:/Users/NYTHAN/Downloads/Copy of Thesis Proposal Document.docx`.
Implementation: `src/face_detection/detect_faces.py`,
`src/skin_masking/skin_mask.py`, `src/ita_estimation/square_measurement.py`,
`src/ita_estimation/monotone_lookup.py`,
`src/model_training/training_identity_leaf_policy.py`,
`src/distortion_generation/paper_gamma.py`, `src/demo/service.py`.

History: [existing alignment record](thesis-method-alignment.md),
[retained MST method](mst-method-retained.md),
[endpoint features](endpoint-feature-tree-results.md),
[latest comparison](broader-source-comparison-results.md),
[MST audit](mst-evidence-checkpoint-2026-10-30.md),
[mask preview](face-mask-coverage-repair-results.md),
[professional-feedback clarification](expert-feedback-refinement-policy.md).

Earlier Word review comments on Sections4.1/4.10 should be read with this
clarification: feedback-driven refinement is retained, not removed. The current
Word copy is still a review draft, not an accepted final methodology.
