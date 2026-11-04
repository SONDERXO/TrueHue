# Changes to track for the thesis-panel request letter

Living register, started1November2026 at the user's explicit request. Update it
whenever a substantive method/scope change is proposed, adopted or rejected.
This supplies evidence for a future request-of-changes letter; it is not the
letter, a submitted request, panel approval or a claim of completed validation.

The baseline column uses the proposal records in implementation-plan.md and
thesis-method-alignment.md. Before drafting the final letter, verify exact
wording, page/section and affected diagrams/tables against the submitted paper.
Do not invent original-paper wording or page numbers. This register prioritises
current changes; the alignment record retains the longer experiment history.

| ID | Original-paper baseline / wording to verify | Current change and reason | Status for letter | Evidence |
|---|---|---|---|---|
| C01 | Rule-based HSV/YCrCb skin masking | Existing pretrained face parser plus anatomical exclusions introduced for broader coverage and feature separation | User-authorised for continued development; learned segmentation is a substantive method change, not validated ground truth | face-mask-coverage-repair-results.md; adopted-masking-design-2026-11-01.md |
| C02 | Skin-mask stage used in the original pipeline; exact shared-use wording to verify | Separate measurement support from correction support: skin-only facial measurement, broader correction | Adopted development design; document both masks explicitly in method/diagram | adopted-masking-design-2026-11-01.md |
| C03 | Face/skin correction scope; exact original region description to verify | Correct whole selected face, including internal features and hair/objects inside outline, plus associated visible neck; explicit protections override | User-adopted correction-region expansion; does not establish correct colour or universal coverage | face-and-neck-correction-requirement.md; whole-face-support-results-2026-11-01.md |
| C04 | Binary application details not assumed to be specified in paper | Fixed inward smoothstep blending at combined face/neck boundary; enclosed correction holes filled to avoid untreated patches | Adopted rendering/continuity changes; outer gaps remain; record target/scoring implications | seamless-support-results-2026-11-01.md; reference-r1-and-continuity-results-2026-11-01.md |
| C05 | Original facial measurement exclusions; nostril treatment to verify | Conservative nasal-base guard added to existing eye/brow/mouth/hair exclusions; neck excluded | Implemented measurement revision; matching cycle completed but unreliable MST mapping NOT adopted | whole-face-support-results-2026-11-01.md; nostril-mst-calibration-results-2026-11-01.md |
| C06 | Original preprocessing/framing and input statistics to verify | Explicit full-frame square256 measurement, pinned parser/landmark dependencies and mask-contract hashes | Current development implementation detail; note if materially different from paper; old features/lookups cannot transfer | semantic-measurement-results-2026-10-31.md; mst-method-retained.md |
| C07 | MST-E described as evaluation-only in fixed scope, with calibration wording elsewhere in proposal | Explicit MST mapping-development/calibration role separated from correction-tree training; subject-held development evaluation and disclosed exposure | Role clarification/possible amendment requiring exact paper reconciliation; no MST-E correction-tree fitting, no untouched-test claim | mst-calibration-evaluation-design.md; nostril-mst-calibration-results-2026-11-01.md |
| C08 | ITA + calibrated MST + facial statistics → decision-tree gamma/red/blue correction | Retained; four-feature baselines and expanded feature experiments do not replace this method | Core unchanged; final feature list/settings still require freeze and evidence, not every experimental variant in letter | mst-method-retained.md; thesis-method-alignment.md |
| C09 | Table2 distortions and three correction outputs | Explicit transform order and approximate three-parameter recovery targets where composite/clipped distortions lack exact inverse | User-authorised development interpretation; document approximation, clipping and residual error rather than claiming exact recovery | paper-distortion-target-checkpoint.md; table2-target-fit-results.md |
| C10 | Dataset split/stratification and evaluation procedures to verify | Duplicate quarantine, source/subject grouping, exposure ledgers, development/final roles; current allocations not verified ten-tone/person-disjoint validation | Evaluation safeguards and unresolved departures; final split not claimed completed | correction-duplicate-audit-results.md; existing-data-feasibility-results-2026-11-01.md |
| C11 | Professional review in testing/refinement | Existing Google Form after a good initial model, feedback-informed refinement and re-review; frozen final appraisal separate | User clarification aligned with recorded proposal phase; not automatically a requested amendment; no responses fabricated | expert-feedback-refinement-policy.md |
| C12 | Proposal abstract (PDF2) names FairFace/SCIN for synthetic distorted-original training pairs | FFHQ added as a photographic-source feasibility pool; ordinary originals may serve as restoration references | User-authorised bounded source acquisition/screen; not final training-dataset adoption or panel approval; MST work deferred, not removed | ffhq-source-preparation-results-2026-11-03.md |

## Proposed or rejected items: do not present as adopted amendments

### 3 November 2026 — C12 FFHQ source work, MST deferred

User authorised proceeding with FFHQ and handling ITA-to-MST later. This permits
source preparation independently of calibration, while retaining calibrated MST
in the eventual three-output method. Official metadata and12 preselected aligned
photographs were acquired and checksum-verified; all12 retained. Assistant contact-
sheet screen only, no source/mask/training admission or independent-person/tone
coverage claim. No segmentation/model inference, fitting, synthetic variants,
runtime switch or recognition task. Per-photo authors/licences and publisher
alignment/cropping are recorded. These photos are development-exposed.

Full provenance, limitations, source-only gallery and bounded next support check:
`ffhq-source-preparation-results-2026-11-03.md`. FFHQ use is an explicit additional
source relative to the proposal, not certified true-colour data. No panel approval
claimed. DAST acquisition was dropped at the user's request; no payment or further
contact. SCIN/STW are not automatically activated by this FFHQ work.

### 3 November 2026 — C09/C10 integrated recipe and admission plan

User authorised one integrated plan after the generated recipe checks. The plan
consolidates existing definitions; no new formula, photographic batch, model fit
or dataset admission occurred. Proposed future diagnostic matrix:one clean,
eight core exposure/colour/combined cases and five full-composite stress-design
cases per admitted source, using one provenance-bound severity assignment.
This is not the paper's verbatim case distribution or an adopted training ratio.
Stress-design membership stays fixed even when an individual case has no clipping;
all failed cases and observed clipping remain reported separately.

Paper baseline verified:PDF60/printed53,62/55,63–66/56–59. Keep the original-reference
synthetic-restoration task, three correction outputs and input-derived ITA/MST/
statistics; four-control PPR work remains a separate unadopted experiment. The
paper's70/15/15 split is recorded but no feasible person-disjoint allocation is
claimed. Source/support/person/MST admission, full features, training mix and
justified evaluation acceptance remain missing. No physical true-colour evidence
is made mandatory for this photographic task.

Evidence and full gates:`integrated-correction-development-plan-2026-11-03.md`;
script406 artifacts:`outputs/integrated_correction_plan_v1/`. Seven parent
packages/21artifact hashes/23unique source hashes/seven frozen parent-manifest
hashes checked; zero admitted template rows and no processing/fits. Status:
**planning complete; recipe candidates preserved; training inactive; no panel
approval or submitted-proposal edit**. Future source activation needs substantive
new gate evidence, not another inventory, same-subject fit or formula sweep.

### 3 November 2026 — C09/C10 normal colour and combined candidates

User authorised the normal colour-error generated check. New isolated version
`core_directional_gamma_single_channel_attenuation_v1` reduces red for a cool
cast or blue for a warm cast, with gain1-abs(Table2 slider)/255. Combined cases
use the existing power-only under/over exposure definitions. This differs from
Table2's slider wording and the earlier additive interpretation; the warm
counterpart is explicit, extra offsets/contrast are omitted from core probes,
and attenuation also darkens rather than changing chromaticity alone. These
are engineering scenarios, not calibrated real-camera errors or unchanged
paper settings. Earlier additive/full-composite clipped cases remain stress
evidence. Paper baseline PDF60/printed53,62/55,63–64/56–57.

Reason: supply nonclipping colour/combined development probes compatible with
the retained three controls, while separately preserving clipping limitations.
18 fixed generated probes plus one exact clean control;18local target fits,
no photos/tree/MST fits.98focusedtests pass; rounding/boundary residuals and384
new endpoint samples retained. Status: **user-authorised experimental development,
not final training recipe, dataset admission, runtime adoption or panel approval**.
See `core-colour-recipe-results-2026-11-03.md` for formulas, provenance and all
results. Earlier notes that normal colour has no candidate are superseded;
final distribution, real-source/MST admission and evaluation are still unresolved.

### 3 November 2026 — C09/C10 normal, stress and clean separation

User authorised the generated-image separation check. Implemented version
`synthetic_core_stress_clean_roles_v1`, not final training/dataset adoption or
panel approval. Compared with Table2's composite settings (PDF62/printed55),
initial normal **exposure-only** probes use gamma alone; offsets/contrast/colour
remain saved and their clipped examples are stress cases. Normal colour/combined
settings and future sampling proportions remain unresolved. This decomposition
is a substantive implementation choice, not described as unchanged Table2.

Reasons: separate solvable exposure probes from destructive clipping, preserve
unchanged controls, disclose all failures and prevent favourable-fit-only
evaluation. Role selection uses forward clipping/support/identity evidence,
not fitted residuals. Roles do not admit sources or establish recoverability.
24 generated cases retained:3clean/6core candidates/15clipping stress; only6new
target fits, no tree/MST fitting/photos.85focusedtests passed. Full baseline,
rules, limitations and evidence: `synthetic-development-role-results-2026-11-03.md`.
Retain the paper's photographic-restoration aim and three correction outputs.

### 3 November 2026 — C09 authorised development update

The user approved developing the exposure-formula revision and specifically
requested tracking changes outside the paper. This supersedes the earlier
"user decision pending" note below for permission to implement, but does not
adopt the tested formula as final training policy or establish panel approval.

New isolated version `directional_exposure_pivot_gamma_offset_rgb8_v1` uses
explicit under/over scenarios: direct exponent1/g versus g, contrast pivots1
versus0, negative versus positive Table2 brightness magnitudes. Earlier0.5-pivot
code and all historical artifacts remain intact. Additive colour shifts remain
an engineering slider interpretation. Six scenario definitions include clean
controls; their training proportions are unspecified. Blending/rounding order
and approximate three-output target construction are documented explicitly.

Reason: the previous formula could brighten dark pixels in the supposedly
stronger underexposure setting. New arithmetic satisfies direction/severity
ordering on all256 levels, but severe clipping and large target-fit residuals
remain.18 generated probes, zero real photos or training;37focusedtests pass.
Retain ITA/calibrated MST/facial statistics/tree and gamma/red/blue outputs.

Paper baseline and detailed before/after table, formulas, evidence and limitations:
`directional-exposure-revision-results-2026-11-03.md`. Paper locations:
PDF38/printed31,60/53,62/55,63–64/56–57. Status: **user-authorised experimental
development; final training recipe unadopted; panel approval unclaimed**.

3 November 2026 Table2 formula decision pending: script402 audited all nine
existing direct-gamma severity/variant combinations on generated pixels. The
dark-setting exposure recipe can brighten input64 to65, while light gives56
and medium59; progressively stronger underexposure is not established. Recommend
a documented exposure-formula revision retaining the three correction outputs,
with explicit under/overexposure scenarios. No revised formula adopted or photo
batch activated. Verified proposal PDF38/printed31,60/53,62/55,63–64/56–57.
See `proposal-distortion-recipe-audit-2026-11-03.md`.

3 November 2026 C09 implementation update: an isolated direct-gamma three-control
blended target solver now accounts for the supplied correction alpha, clipping
and final RGB8 rounding. Exact neutral controls are preserved; difficult residuals
are reported rather than treated as exact inverses. Generated-array diagnostics
only, no training/admission/runtime adoption. This extends the existing approximate
target-construction proposal; the final Table2 recipe and scoring policy remain
unfrozen. Proposal PDF63/printed56 specifies three correction outputs and
PDF65/printed58 uses the original image as reference. See
`blended-recovery-target-results-2026-11-03.md`. No intrinsic-colour claim or
fourth-output adoption follows from this work.

| Item | Current status and what to say |
|---|---|
| Hard face-outline intersection for measurement | One isolated diagnostic completed; user prefers old measurement overlay. Unadopted: removes spill but loses useful skin and retains covering errors. Keep as rejected candidate evidence, not the requested final method. See face-contained-measurement-results-2026-11-01.md. |
| FaceOcc visible-face occlusion veto | One frozen diagnostic completed:25attempts/17outputs/8retained failures; removes flagged neck/clothing and face-covering points, retains beard point. Median parent retention95.44%; no new technical failures. Not adopted; actual-skin reliability/Android unresolved. Uses explicit MediaPipe five-anchor bridge instead of upstream3DDFA preparation, a potential C01/C02/C06 amendment if later justified. See faceocc-single-diagnostic-results-2026-11-01.md. |
| New participant/reference-photo collection | Planning discussed, currently impractical; not required or started. Do not claim new recruitment, signatures, captures or amended sample size. Existing-data route investigated instead. |
| Beard-specific model | Still held. General occlusion research does not silently adopt a beard model. |
| Reliable ten-category MST / final correction model | Unfinished, not an adopted achievement. Poor mapping and contamination remain disclosed; no failed research successor silently promoted. |

## Retained scope and unresolved letter details

1November2026 MSTfeasibility decision: no-go for calibration now. CurrentFaceOcc
MST evidence33attempts/23technical measurements/four subjects/categories2/4/5/9;
zero calibration admission. Old393features incompatible; prospective19subject
inventory still singleton7/10. A limited expanded development question is
possible in principle but not activated. No new algorithm/scope amendment or
validation claimed. See faceocc-mst-feasibility-decision-2026-11-01.md.

1November2026 preferred experimental method packaged as an isolated reusable
service;35saved successes exactly replay/14failures fail closed. This is software
integration/parity, not new mask/MST/correction validation or runtime adoption.
See faceocc-development-service-results-2026-11-01.md. Existing proposed scientific
changes and their limitations are unchanged; no new method family introduced.

1November2026 user selected FaceOcc-assisted measurement as preferred
EXPERIMENTAL development direction and authorised bounded planning. This is not
active runtime adoption or panel approval. See faceocc-bounded-development-plan-
2026-11-01.md and49attempt eligibility ledger. Measurement admission/matchingMST/
correction-training gates remain inactive; no processing/fitting follows
automatically. Keep old measurement as baseline and all failed/held evidence.

1November2026 actualfour-case export imported: twoFaceOccpreferred(29321/74882),
twosimilar(39083/77101), no reported useful-skin loss in thesefour. Full24attempt
record/assistant18inspection retains skin-loss and occlusion concerns outside/
within the user subset. Qualitativecyclecomplete; not adopted or independent
validation. See faceocc-qualitative-conclusion-2026-11-01.md for factual future-
letter wording, exact judgments and preserved historical-scope distinctions.

1November2026 manual-workload amendment authorised BEFORE new predictions:
the23-image polygon task is superseded by assistant inspection of all24attempts
and four fixed human qualitative judgments.18paired outputs/6failures retained;
human decisions pending. Original annotation artifacts preserved. This is a
qualitative procedure, not completed dense-patch scoring or full-mask accuracy.
See faceocc-light-review-results-2026-11-01.md. No automatic model adoption.

1November2026 broader evaluation authorised: fixed24existing-data attempts,
23available originals/1decode failure, prediction-hidden skin/occluder polygon
patch annotation prepared; annotations and model comparison pending. This adds
an explicit evaluation procedure, not an adopted segmentation change. Patch
scores cannot be reported as full-mask accuracy or independent validation.
See faceocc-broader-annotation-ready-2026-11-01.md and frozen protocol.

1November2026 saved defence evidence: see
[paired FaceOcc comparison](faceocc-comparison-evidence-2026-11-01.md) and
outputs/faceocc_comparison_evidence_v1/comparison.html. Same25attempts:
17/25availability both, marked non-skin selected4/4→1/4, skin2/2→2/2.
This supports further evaluation of an additional measurement veto, not replacing
the correction model or claiming overall accuracy. Candidate remains unadopted;
letter-ready factual wording and explicit limitations are preserved in that record.

Retain Android, on-device processing, one gallery-image face, ITA/MST and the
decision-tree gamma/red/blue operator. No cloud inference, generative skin
reconstruction, new runtime reference image, new model family for correction or
automatic replacement of the thesis method is adopted by masking research.

For each final requested change, supply: verified original section/page;
replacement wording; practical reason; implementation and evaluation evidence;
known limitations; affected methodology, scope, figures, data and evaluation;
and whether it is already implemented experimentally or only proposed.

Keep these statuses separate: user development authorisation, technical result,
requested panel amendment, and actual panel approval. No panel letter is sent
or described as approved until that action/evidence exists. Software tests do
not establish scientific validity. Reviewer approvals remain file/scope bound.

No paper text, dataset, model or runtime changed while preparing this register.

## 2 November 2026: FiveK reference-source feasibility

Original dataset scope lists FairFace/SCIN for correction and MST-E evaluation;
verify exact submitted-paper wording before the letter. User authorised a fixed
six-source FiveK preview investigation as an alternative to recruitment. External
reference data are PROPOSED/EXPLORATORY, not adopted training data or panel-approved.
Six deterministic C thumbnails inspected; person tags include swimmers/distant
people and portrait cases retain hair/glasses/pose concerns. Zero admitted.
Photographic restoration is distinct from true-colour validation. ITA + calibrated
MST + facial-statistics decision tree, runtime and reserved roles unchanged.
Evidence: fivek-source-feasibility-results-2026-11-02.md and
outputs/fivek_source_feasibility_v1/. No automatic expanded batch or fit.

2 November follow-up: exact two previously identified FiveK C TIFFs acquired and
colour-managed views inspected. See fivek-full-resolution-results-2026-11-02.md.
One detailed photograph is a possible reconstruction diagnostic; the other has
noise/glasses/lighting concerns. STOP before reference admission/training, zero
admitted. No masks/fit/runtime change or new data-method adoption. Original
RGB16 retained; quantised ICC viewing copies are not numeric evaluation targets.

2 November explicit follow-up: user requested verification of labelled skin
measurements. Four saved MST-E masks selected deterministically, one per current
subject, for no-drawing yes/no/uncertain review. This is new scoped visual
evidence collection, not the prior FairFace preference review or general mask
accuracy. Human answers pending; no automatic cohort admission, calibration or
fit. See mst-four-skin-check-ready-2026-11-02.md and script385. This proposed
evaluation-procedure detail requires original-paper comparison for the letter;
no method adoption/panel approval claimed. Stop after four, retain parent failures.

2 November actual four-MST review imported: MSTSKINCHECK.json, strict385 binding
passed. Three exact masks visually favourable; one explicitly selects stubble/
facial hair. Four judgeable, no obvious skin loss reported. See
mst-four-skin-check-results-2026-11-02.md. Qualitative evidence only; no automatic
whole-subject admission, three-clean-only calibration, runtime/model adoption or
new follow-up batch. Prior pending status is historical; review cycle complete.

2 November user explicitly accepted 15 additional simple checks: frozen full
19-person eligibility study prepared (scripts386?388), four actual reviews
preserved, 14 new reviewable masks and one retained subject17 parent failure.
14 fixed CPU FaceOcc passes and14 exact saved-service replays; no calibration,
training or runtime change. New human answers PENDING. Expanded evidence
procedure only, not panel-approved method/data adoption. See
mst-subject-skin-study-protocol-2026-11-02.md and
mst-subject-skin-study-ready-2026-11-02.md. All failures/knownconcerns retained,
no replacement/automatic next batch or small clean-only fit.

2 November full existing-subject skin review COMPLETE: actual14 new answers
imported388;19 outcomes retain4 prior judgments/1parentfailure. Structured
responses11favourable/7concern-or-uncertain/1failure; lightingnote subject4 and
assistant concerns retained separately. Only MST1/4/5 have two structured
favourable subjects, not final admissions or adequate calibration proof. STOP
beforefit, no clean-only subset/newbatch/replacement/tuning. See
mst-subject-skin-study-results-2026-11-02.md. Evidence update, not method adoption
or panelapproval; prior pending-status entries are historical.

2 November online-source follow-up: actual publicDAST36JPEG/3people/15instrument
records and STW annotationCSV inspected under userauthorisation, no training.
Potential role DAST controlled-reference/measurement, STW humanMSTlabels remains
PROPOSED, not adopted or panelapproved; CST is not MST. DAST metadata/profile/
observer/rights gaps and STW42312rows/3587providerkeys vspaper42313/3564 retained.
No new mask/ITA/MST algorithm/tree/runtime change, reserved roles untouched.
See dast-and-stw-readiness-results-2026-11-02.md and unsent inquiry drafts.
Future activation needs provenance/permissions/roleprotocol, no automaticfit or
newreview/recruitment. This adds concrete source evidence, not more oldcohort
calibration.


2 November2026 user-authorised PPR10K bounded inspection completed: six fixed
source/editor-A pairs in two groups acquired and inspected, actual RGB16/RGB8
embedded sRGB verified. Promising photographic appearance examples only, not
measured true-colour references, MST labels or training admissions. Both groups
are publisher-validation and these six photos are now development-exposed;
existing TrueHue roles unchanged. Operator approximation unresolved; no fits,
inference, method adoption or panel approval. Dataset use remains proposed only.
See ppr10k-fixed-sample-inspection-2026-11-02.md. Frozen delivery snapshots
preserved; no new snapshot generated for this inspection.


2 November2026 PPR10K same-six operator diagnostic explicitly authorised and
completed: fixed assistant approximate face-only regions, six target-aware
gamma/red/blue fits, no MST or decision-tree training. Relative image appearance
check-block errors improve6/6 (equal-image mean13.44->4.79), visible pink/contrast
residuals remain. Local numerical approximation, not global-optimality, new-photo
validation, true-colour recovery or training admission. Face-only hard diagnostic
regions do not revise adopted face+neck blending/support. Method/dataset adoption
and panel approval not claimed. See ppr10k-operator-diagnostic-results-2026-11-02.md.


2 November2026 saved PPR10K residual diagnosis: contrast compression pattern
across all six oracle results; no new fits. A fourth scalar contrast output is
PROPOSED ONLY, not user-authorised/adopted/panel-approved. Would change retained
gamma/red/blue output design; ITA/calibrated MST/statistics/tree retained.
Concrete single-candidate comparison proposed in ppr10k-residual-diagnosis-2026-11-02.md.
No implementation or new rendered improvement, runtime/source roles unchanged.


2 November2026 user explicitly authorised ONE fourth-control contrast experiment,
now complete. Same6PPR10K target-aware fits: relative colour difference improves
4/6 (mean4.793->2.759);2indoor regressions and increased clipping4photos retained.
Strong wedding approximation improvement, not general validation. Contrast remains
EXPERIMENTAL ONLY, not adopted fourth decision-tree output/runtime amendment or
panel approval; original3output design retained pending explicit adoption.
ITA/calibrated MST/facial statistics/tree retained,0MST/treefits/admissions.
See ppr10k-contrast-diagnostic-results-2026-11-02.md. No submitted thesis or
formal letter edit; frozen delivery snapshots unchanged.


2 November2026 user-authorised new-group PPR10K comparison complete: fixed8
publisher-training groups/onephotoeach, same3/4control operators and settings.
All8checkblock colour errors improve(mean4.964->2.552);6increasedclipping,
904highresidual/clipping and prior2indoorregressions preserved. Target-aware
capacity evidence, not automatic prediction/person-independent validation or
MST coverage. Fourth contrast remains EXPERIMENTAL, not adopted output-schema
or runtime amendment or panel approval.0MST/treefits/admissions.
See ppr10k-new-group-comparison-results-2026-11-02.md; snapshots unchanged.


2 November2026 saved detail check qualifies contrast evidence: real per-channel
highlight flattening in some face areas.904/1188approximate polygons include
shirt/background; previously reported new8/8colour improvements are mixed-region
statistics, not certified complete-face/skin accuracy. Prior outputs preserved.
Fourth output remains EXPERIMENTAL/not adopted or panelapproved; no new fits,
mask repair, runtime amendment or training. See ppr10k-clipping-detail-results-2026-11-02.md.


2 November2026 user-authorised bounded response to clipping/region issues:
source-only conservative904/1188diagnostic regions revised, oldfits unchanged;
one fixeds=.02smooth boundary evaluated on14saved4controloutputs without
refitting. FewerRGB8endpoints1461->364 and flattenedvaryingpairs986->153,
similar all-regioncolourmatch2.548->2.522,3slightregressions retained.
Experimental implemented candidate only, not adopted4thoutput/rendering/runtime
or panel approval; fine-detail preservation and generalmaskvalidity not proved.
ITA/MST/tree retained. See ppr10k-smooth-boundary-results-2026-11-02.md.
Frozen snapshots/submittedpaper unchanged.


2 November2026 user-authorised training-readiness PLAN and candidate FREEZE
completed, not training or adoption. Four-control+smooths=.02contract
248aeae5d7d1c30c89fc31cccefa8418083059f4f6d8be2c78394da6b8f9679e
is experimental reference only; original runtime3outputschema retained.
Four-output/rendering changes remain proposed for possible later adoption,
not panel-approved. ITA/calibratedMST/statistics/tree/ondevice scope retained.
No admitted cohort/matchingMST/identitysplit/cleanimagepolicy established;
smoothneutral is not exactidentity and old inverse targets cannot transfer.
See correction-training-readiness-plan-2026-11-02.md. Submittedthesis/open
discussiondraft and immutable delivery snapshots unchanged;0newfits/inference.
