# Thesis method alignment and future editing record

29 October 2026: User reiterates paper-method fidelity. Semantic parsing stays
diagnostic. New rule experiment retains existing HSV/YCrCb and anatomical
exclusions, changes face-constraint/component ordering, and demonstrates limited
containment rather than recovered coverage. Exact-achromatic reference rejection
implements the user's monochrome-source direction without a saturation cutoff.
No active mask/MST contract/tree change; dataset/calibration/correction-quality
requirements remain open. [Current progress](paper-method-correction-progress.md).

28 October2026: Newmetadata-only600candidate design excludesallhistorical650
andrecordedexposures;420train/90development-validation/90finaltestcandidates,
preservingoriginaldatasetboundariesandoldallocations. Candidate70/15/15counts
arenotMSTstratified,eligiblecountsorverifiedsubjectseparation. Noimagebytes
opened,newfeatures,trainingorvalidationoutcomes. Duplicationaudit/suitability
pending.724softwaretests pass;noactiveassetpromotion.
[Frozen redesign](correction-data-redesign-results.md).

28 October2026: Exactfixed-supportaccountingfindsdistortedCIEDEfloor4.445,
learned11.598,existingRGBfitted8.902;lightlearned/fittedgaplargerthanmedium.
Fixedfitting-onlycontrol/severityweightsimprovedistortedmeanslightlybutworsen
cleanharm;conservativevariantstillfails. Noautomaticmethod/assetadoption;
715tests pass. [Audit and weighting](table2-recovery-budget-and-weighting.md).

28 October2026: Fitting-only gamma/red/blue targetstandardization worsens
same30pairreconstruction10.133vs8.534unscaledbaseline;conservativevariant9.320
stillharms3cleancontrols. Noadoptionoroutputweightsearch. Raw-unitportable
exportsretainparameterschema;709softwaretests pass. [Scale experiment](table2-target-scaling-results.md).

28 October2026: Properinnergroupselectionoverminleaf1/2/4on15sourcecohort
fits630inner5featuretrees/1260predictions;allsettingsfailinnercleanrequirements.
All15outerdecisionsidentity,nobenefit(overall10.076equalsnocorrection). No
adoptionorindependentfinalclaim,nosearch/gateexpansion. [Nested regularization](table2-nested-regularization-results.md).

28 October2026: Training-leaf float32rangeguard onconservative5model passes
bothgatesontheexposed30paircohort(overall9.796vs10.076,clean0),butcorrectsonly
1of15distortedinputsandabstainson21of30queries. Frozenstresslightworsensand
darkreceivesnocorrection. Notfinishedorindependentlyvalidated;guardmetadata
extendsthebaretreepolicyandisnotadoptedmethodamendment. Noactiveassetchange.
[Support-guard findings](table2-leaf-support-results.md).

28 October2026: Conservativeleafpolicyon15sourcebaseline5improvesoverall
8.534to7.995andreducescleanharm6to2,butdistortederror11.598to12.326.
1398/75027remainharmed,identitygatefails. Separateexperimentaloutputpolicy,
notadoptedmethodoractiveasset. [Five-feature policy findings](table2-five-feature-leaf-results.md).

28 October2026: Fifteen-source/30pairreviewedcomparisonretainsqualifiedhair/
body/backgroundacceptancesandnew12222/60381rejections. Fixedbaseline5bestoverall
8.534vsnocorrection10.076;matchedold20improves9.643to8.702. Howeverbaseline5
harms6clean,chroma9harms8,clean-leafharms2;allfailadoption.4estimatedlight/
11medium/nodark;unverifiedpersonseparation,weakMST,approximateclippedtargets
andmaskconcernsremain. Noactive/Androidpromotion orfinalvalidityclaim.
[Expanded comparison](table2-reviewed-fifteen-source-results.md).

28 October2026: Fixedlarger60TRAINsourcepreparationfromremaining146metadata
candidates,notreplacement/relabelingofpriorholds.59reference/49distortedvalid
measurements,48targets;7qualitativeprovisionaluser-review,53held. No admissions
or fits.2experimentaldarkassignmentsbothunusable,so no darktrainingcoverage.
Allremainexposeddevelopment,photographicreferencesnotcalibratedtruth;MST/person/
finalevaluationlimitationsunchanged. [Larger preparation](table2-source-expansion60-results.md).

28 October2026: Photographer opinions deferred by user until model completion,
using already existing Google Form; local review forms unused. New single-tree
experimentalGinicontrolpartition objective worsenssame20pairCIEDE2000to12.815
andharms4cleancontrols;bothgatesfail. Notordinaryregressiontrainingorapproved
methodamendment;noactivation.705softwaretests pass. [Results](table2-control-partition-results.md).

28 October2026: Repeated localPython timing now has20warmups/100measured
calls,median61.63ms/p9575.52ms,all120calls exactsavedoutputparity. Separate
construction/IOscope and recorded desktop environment; not Androidlatency or
passingquality. Actualphotographerresponses/finalMOSremainpending.
[Timing findings](development-mst-benchmark-results.md).

28 October2026: Localpresentation-blindedreference-suitabilityreview prepared
for2photographers/10existingreferences. Noactualresponsescollected. Thisis
categoricaldevelopmentreference screening,notfinalcorrectionMOSorcalibrated
skintruth. Modelqualitygatefailuresremain;reviewdoesnotautomaticallyrevoke
oldmaskacceptancesoradmit/retrainasubset. [Prepared review](photographer-reference-review-ready.md).

28 October2026: Integrated3methodstresscheck102calls/99outputs/3knownfailure
occurrences on34fixedinputs. Lightprobesremainworsethannocorrectiononmean;
medium/darkimprovewithresiduals;cleanharms7/6/1. Matchsuccessfuldenominators,
reportfailed75027darkandavoidpooledunequalsourcescore. Counterfactualseverity
isnotcomplexioncoverage; noproductqualityorindependentfinalclaim.
[Integrated stress findings](development-mst-stress-results.md).

28 October2026: Separate explicit Python development runner now executes
square256measurement/ITA/experimentalMST/5or9featuretree/correction with
contract/schema/provenance checks.20savedheldcases reproduce exactly and1known
detectionfailure remains;701tests pass. This is software integration/parity,
not validated MST or passing correction quality; default model unchanged.
LocalPython timing observations are not Android latency. [Runner findings](development-mst-pipeline-results.md).

28 October2026: Training-only nested selection of the conservative candidate
fails every inner clean gate across10outergroups/90innerfits/180innerpredictions.
All20outerpredictionsselectidentity:zerocleanharmbutnocorrectionbenefit,overall
10.577equalsnocorrection. No candidate passesbothgates. Same20pair4methodreport
includes separately labeled approximate gamma/red/blue targetMAE, not MSTlabel
or calibratedskinMAE. Historicalexposurepreventsindependentfinalclaims.
[Nested safety and comparative results](table2-nested-safety-results.md).

28 October2026: Experimental training-control leaf-output policy on saved
chroma9trees reduces harmed held clean inputs6to1,with all10distorted outputs
unchanged. Meanall8.538,clean2.767,distorted14.309CIEDE2000.75027clean remains
severely harmed27.672; strictgatefails. Output policy differs from ordinary
regression leaf means and is not an adopted method amendment. No new split
fitting or runtime promotion. [Policy findings](table2-clean-leaf-policy-results.md).

28 October 2026: Separate nine-feature correction experiment retains five
Lab/ITA/MSTinputs and adds chromaIQR/lightness-chroma covariance from unchanged
actual-input support. Fixed same20pairs/10sourcefolds/settings. OverallCIEDE2000
9.643to8.898,clean5.489to3.488,but distorted13.797to14.309 and6cleancontrols
harmed; candidate fails identitygate. No final schema/runtime adoption or new
MSTcalibration.695softwaretests pass; scientific validation remains limited.
[Chroma-distribution comparison](table2-chroma-distribution-results.md).

28 October 2026: User-reviewed expansion to ten source groups/20pairs improves
overall reconstruction (10.577to9.643CIEDE2000) but harms7/10unchangedcontrols
(mean5.489), failing identity gate. Fixed recipe,source/known-duplicategroup
held folds,weak input-derived MST,2estimatedlight/8medium/no dark.713rejected
for hair;51803minor-holeconcern preserved. No final model adoption, verified
person-disjointness or full-category validation. [Ten-source findings](table2-reviewed-ten-source-results.md).

28 October 2026: Eight accepted sources tested at all three Table2 severities
as counterfactual diagnostics, not new MST labels or training admissions.
23/24measurements succeed;75027dark fails detection. Clipping and residual
reconstruction error rise substantially with severity. Fixed-reference
three-parameter RGB fits retain meanCIEDE2000 2.613/9.391/15.942 across eight
sources at light/medium/dark. These are reference-informed local-fit capacity
results, not learned performance, global lower bounds or final evaluation.
Keep Table2/three-output scope and document approximation, clipping, failures
and unequal successful denominators. No final model adoption or mask change.
[Coverage and capacity findings](table2-counterfactual-coverage-results.md).

28 October 2026: User rejects three expansion masks for hair contamination and
accepts three. Reviewed cohort now eight sources/16pairs; fixed source-group
held evaluation harms four clean controls and is worse overall than no
correction. Bothgatesfail. No finalvalidity, verifiedpersondisjointness or
allMSTcategorycoverage; weakMST, estimatedseverity, clippingandmasklimitations
remain. Preserve negative results and exact mask reviews. Any broader
application-mask diagnostic must retain input-derived measurement compatibility;
changing ITA support requires lookup reassessment.
[Reviewed expansion findings](table2-reviewed-expansion-results.md).

28 October 2026: Fixed Table2expansion processes six previously exposed FairFace
TRAIN sources under unchanged square256/frozen experimentalMST/approximate-target
contracts. Twelve successful measurements and six targets do not confer training
admission; changed masks/scenes await user review. Estimated grouping supplies
five medium/onelight, no dark. Severe clipping, mask loss and photographic
reference limitations remain explicit. Combined11source/22pair plan is provisional,
not final independent evaluation or verified person separation.
[Expansion results](table2-stress-expansion-results.md).

28 October 2026: User-reviewed Table 2 experimental correction evaluated on five
exposed FairFace source groups, ten pairs, five source-held folds. Approximate
targets, limited estimated light/medium grouping and weak input MST are explicit;
no dark-source coverage, final independent evaluation or person-disjoint proof.
Mean reconstruction improves but one unchanged image is harmed; model fails
the frozen identity gate. User rejects51739and accepts remaining masks with
recorded concerns. No mask modifications or runtime promotion.
[Full findings](table2-reviewed-stress-results.md).

28 October 2026: User authorized a separate experimental clipped-input Table 2
training path with approximate targets and all stated safeguards. The current
preparation stages six FairFace sources, twelve candidates and provisional
source-group folds, pending exact mask/scene review. Reference MST severity
assignment is a weak experimental estimate, not official complexion labels;
current candidates cover only light/medium groups. Distorted-input MST remains
the actual feature. Existing unclipped policy and reviews are preserved.
Document the exception, irrecoverable clipping, estimated grouping, limited
coverage and unverified cross-source person identity in thesis edits.
[Preparation and limits](table2-stress-preparation-results.md).

Checked: 23 October 2026. Status: development checkpoint, not an approved amendment.

Current training-design checkpoint,24 October2026: [review and fixed next-source protocol](training-design-checkpoint.md). Current39 pairs span10 sources; only3 sources have all5 variants. No final model adoption; the broader source-review plan has not been executed.

Latest experiment completed24 October2026:

[Training coverage and expansion plan](training-coverage-audit.md) screens18
new training-only development sources, logs their exposure and holds all from
fitting pending suitability checks. No reserved-test imagery was inspected.
Photo-lightness sampling bins are not MST categories or tone-conditioned severity.

[Source-screening follow-up](source-screening-followup.md) records20555's fixed
variants and18 more training-only sources. Color-shift estimation still fails
the quality screen on20555 despite numerical success; four new source candidates
remain pending. No retraining, cohort promotion or neck correction occurred.

[Four-candidate variant checks](candidate-variant-checks.md) recorded20 probes
under paired estimation policies.14272/84897 are promising for a separately
versioned development expansion; source/variant holds and clipping remain
explicit. No runtime estimator, model or approved final cohort was changed.

[Proposed31-pair development stage](development-expansion31-stage.md) adds nine
pending screen-pass pairs from14272/84897 alongside the frozen22. Eight fold
plans are prepared, with clipping/held cases kept out. Staging is not final
cohort approval, model fitting, neck implementation or a methodology amendment.

[source-held-out correction-controls comparison](correction-controls-sourcecv-results.md).
Twelve experimental fold trees were fitted on the existing22-ID development
selection. Controls improve against the older recipe but remain worse than no
correction overall; the runtime model and final study scope are unchanged.

**New user requirement,23 October2026:** correction should include the selected
person's visible neck as well as face. [Requirement and implementation plan](face-and-neck-correction-requirement.md).
The proposal explicitly limits correction to the face (PDF13/printed6), so save
this as a requested scope expansion for later thesis editing. Facial ITA
measurement remains the current estimator; neck correction is not implemented.
Prior neck/collar spill findings need separation: neck skin can be desired,
while clothing/collars remain unwanted. Old metrics do not validate neck quality.

Follow-up: [method recommendations and verified local evidence](method-decisions-2026-10-23.md).
The audit confirmed that all 30 current training inputs are 224x224 and that
the detector is YuNet; these differ from the proposed square 256x256 processing
and named detector choices. The 256 config value was not applied to those inputs.

Completed check: [native versus square preprocessing](square-preprocessing-results.md).
All eight sources succeeded at 256x256; existing training pairs remain 224x224.
Nine locally available targeted SCIN candidates returned zero detected faces;
the other candidates remain untested.

The [distorted-input resolution check](square-distorted-input-results.md) also
completed: no new failures among 37 prior successes, with the original exclusion
retained. Mask fragmentation persists; this is not a new 256 training table.

Later follow-up: [fresh 256 development dataset](square-development-dataset.md)
is now built separately (30 training candidates,3 development,4 stress,1 exclusion).
No learner was fitted. Mask-quality flags remain and must be resolved before
automatic retraining; original 224 artifacts remain unchanged.

[Mask-quality screening](square-mask-quality-screen.md) now records eight held
training pairs and22 exploratory screen-pass candidates. This changes only a
separate development selection manifest, not masks, human labels, final method
or the original training table. Selection effects must be reported in thesis edits.

[Hair-clean generation experiment](hair-clean-generation-results.md) now tests
removal of source-mask hair on all38 attempts. Three holds are explained by
reference contamination; five training mask-loss cases remain held. The changed
generation denominator is not a segmentation improvement or an approved change.

[YCrCb-only estimation ablation](ycrcb-estimation-ablation.md) tests the detailed
paper's color rule more directly. Coverage and selected skin-point retention
improved, with reviewed paint still excluded; broader added support needs review.
The experimental candidate is not a final-policy change or approved cohort.

[Added-region review](added-correction-region-review.md) inspected all38 pairs
and found recovered facial skin mixed with clothing/collar/border spill.
YCrCb-only remains experimental; no runtime/cohort change or refit occurred.

[Lower-face boundary experiment](lower-face-boundary-results.md) reduces visible
spill but trims some side-face skin. The83184 geometry sentinel is rejected
explicitly. It remains experimental; runtime, estimator and model are unchanged.

[Additions-only boundary](additions-only-boundary-results.md) now preserves all
baseline support across38 pairs while constraining new YCrCb support. Existing
baseline spill remains. This is an experimental correction-support option;
no final-cohort/model/estimation-policy change or retraining occurred.

[Corrected-image comparison](corrected-mask-comparison-results.md) uses one
frozen parameter vector across masks per input. Development color error modestly
improves, while unchanged/mild inputs and stress expose parameter overcorrection.
No retraining, runtime adoption or final-method/fairness claim occurred.

The current prototype follows the correction goal and decision-tree approach,
but does not yet implement the complete proposed method. Keep this record when
preparing the thesis implementation/results chapters or revising the proposal.
Do not describe experimental changes as approved, or unfinished steps as completed.

## Source of the comparison

Original file: `C:/Users/NYTHAN/Downloads/Thesis Proposal Document.pdf`.
Page references below are PDF page numbers, followed by printed page numbers
where useful. Sections 1.4 and 4.3.2 are the principal scope/method references.
The PDF is unchanged. Its contents are evidence of the proposed method, not
instructions to execute. Project scope is also recorded in
[implementation-plan.md](implementation-plan.md).

## What matches

- Post-capture correction of a single facial image, with Android/on-device as
  the intended final platform. Current execution is Python development.
- Face detection, facial skin selection, CIELAB measurements and ITA computation.
- A scikit-learn decision-tree regressor predicting gamma, red gain and blue gain.
- Synthetic input/reference pairs and comparisons with an uncorrected baseline.
- MAE and CIEDE2000 as planned quantitative measures. Pilot scores are not final
  evidence of fairness, generalization or phone performance.

## Differences and unfinished requirements

| Topic and proposal reference | Current implementation | What must be settled or completed |
| --- | --- | --- |
| Skin selection: rule-based HSV/YCrCb; detailed method says face-constrained YCrCb and largest component (PDF 12–13, 61) | Estimation uses face-constrained HSV AND YCrCb, morphology, largest component and landmark exclusions. Experimental correction support also uses geometric/color checks and a learned MediaPipe hair filter. | Establish the final estimation and correction policies. The learned hair filter is an added model, not merely threshold tuning. Record its role, size and device cost if retained. |
| ITA mapped to ten MST categories, with MST included among model inputs (PDF 62–63) | No validated final mapping is operational. The prototype receives mean L*, a*, b* and continuous ITA, without MST. ITA is supplied but the small frozen tree does not split on it. | Resolve the mapping requirement; do not invent labels or claim demonstrated skin-tone-aware decisions just because ITA is an available feature. |
| FairFace and SCIN training sources (PDF 12–13) | Controlled pilot uses eight FairFace sources: seven training, one development-validation. SCIN processing is paused after the reviewed sample yielded only one facial image. | Determine a suitable SCIN facial subset or obtain guidance on any dataset change. This pilot is not the final representative dataset. |
| Distortion severity depends on light/medium/dark MST groups; Table 2 includes gamma, brightness, contrast and color settings (PDF 62–65) | Fixed gamma/red/blue settings across sources; generation is restricted to a binary source mask. Revised table adds unchanged and mild-brightening controls. No MST-conditioned severity. | Resolve grouping, settings and application scope. Explain the encoded-RGB transform and inverse targets; do not equate current settings with Table 2. Brightness offsets/contrast are not implemented as separate operators. |
| 256 × 256 resizing (PDF 60–61) | Current preparation uses a 256-side development configuration; some earlier MST diagnostics used a larger detector input. | Verify actual saved dimensions and aspect-ratio handling against the proposed square resize before final runs. Keep diagnostic resolutions distinct. |
| 70/15/15 MST-stratified split and five-fold validation procedure (PDF 62, 65) | Provisional 650-source allocation is 450/126/74, not the proposed split. The tiny pilot is 7 training sources/1 development source. Seven source-grouped inner fold plans exist; no models have been fitted with them. | Fix the final split and model-selection protocol before expanded training. Keep source variants/known duplicates together; subject independence remains unverified. Source-grouped checks do not implement MST stratification. |
| MST-E described as evaluation-only, but also supplies mapping calibration (PDF 12–13, 62) | MST-E images/labels have already been reviewed and used in calibration/diagnostics. Mapping work is paused. | Disclose development exposure and define separate calibration/evaluation roles. Previously inspected data cannot be presented as wholly untouched final evaluation. |
| Evaluation overall and by MST; disparity rule and expert MOS (PDF 65–66) | Small development reconstruction checks exist. No completed final MST-stratified evaluation, disparity analysis or photographer MOS. | Complete these after the method and model are fixed. Ordinary source photos are relative reconstruction references, not calibrated true skin color. |
| Entire application operates on Android (PDF 13) | Python correction option and desktop timing only; final Android integration/device validation unfinished. | Complete phone integration, offline operation and device speed/memory checks. Desktop timings are not phone benchmarks. |

## Paper ambiguities to preserve for later clarification

These issues originate in the proposal, rather than being implementation results:

1. The scope/abstract describes HSV/YCrCb, while the detailed final masking
   method specifies YCrCb inside a detected face. State the actual final rule.
2. MST-E is called evaluation-only but is also used to derive mapping thresholds.
   Clearly identify calibration and evaluation data and their separation.
3. Table 2 includes brightness and contrast settings, while the learner predicts
   only gamma and red/blue gains. Explain which transformations are generated
   and what those three outputs can restore; clipping loses information.
4. The proposal describes five-fold model selection on the validation split.
   Clarify the intended training/tuning/test roles before implementing the final
   selection procedure; do not quietly rewrite this as an already approved rule.

## Current checkpoint and recommended order

1. Preserve the current prototype and experimental results as development
   evidence. Do not expand training or select a replacement model yet.
2. Resolve the final skin/correction policy, MST requirement, dataset roles and
   distortion recipe against the proposed method. Record adviser guidance if
   a substantive change is retained; this document is not approval.
3. Fix final source eligibility, split/grouping rules and tuning boundaries.
   Record all prior data exposure, failures and exclusions.
4. Run training comparisons only within that documented protocol, then complete
   Android integration and the quantitative/expert evaluations.

The latest table contains 30 development training pairs, including 14 additions
on existing training sources. The original 16-pair model remains frozen; the
revised table has not been used to fit a replacement. See
[exposure-identity-training-revision.md](exposure-identity-training-revision.md).
The optional hair filter and its limitations are documented in
[integrated-correction-option.md](integrated-correction-option.md).

## Use this record when writing the thesis

For each row above, record the final decision, date, any adviser guidance,
implementation/artifact version and supporting experiment. Then describe what
was actually implemented, why it differs, and its measured limitations. Keep
proposed, approved, implemented and evaluated statuses separate. Preserve
unsuccessful experiments and data exclusions in the development history.

Automatic paint exclusion is not guaranteed: reviewed paint points were
excluded, but the added segmentation model has no paint class. An optional
protected-region mask guarantees only the marked pixels remain unchanged;
it must not be described as fully automatic paint recognition or a required
user step without reconciling the proposal's photo-selection-only workflow.

This file is the persistent reference for future thesis edits. Update it when
decisions change rather than relying on conversation memory. No proposal text,
model, dataset allocation or runtime policy was changed by this checkpoint.


## 24 October 2026: fixed eight-source expansion comparison

Executed script69 on staged31 with original22 versus expanded31 and no-correction baselines. Sixteen source-disjoint fold models; 93 predictions; saved-model replay and unchanged-input hashes verified. Mean reconstruction deltaE: no correction5.460, original6.601, expanded7.804; shared22 original6.916 versus expanded8.165; new9 original5.831 versus expanded6.924. Dark probes improved but mild and unchanged controls still regress. All31 image comparisons visually inspected. 464 tests passed. No runtime promotion, external/reserved evaluation, neck implementation or proposal amendment. Next recommended diagnosis: control-regression leaf/feature-target conflicts. See [comparison](development-expansion-comparison.md).


## 24 October 2026: control-error branch diagnosis

Script70 replayed32 unchanged/mild predictions across16 existing fold models, checked disjoint source/duplicate groups, exact predictions, leaf-target means and unchanged hashes. Both models harm8/8 unchanged probes; mild failures rise2/8 to5/8;8/16 controls worsen versus original. Wrong-distortion pure leaves and mixed-target leaves coexist. Diagnostic training-fold-scaled nearest examples do not prove physical ambiguity. No new fitting or runtime change. Recommend one fixed depth3 versus unrestricted-capacity comparison, same31/eight folds, report training and held-source controls, no depth search or automatic promotion. Neck/MST/proposal distinctions unchanged. See [diagnosis](expansion-control-diagnosis.md).


## 24 October 2026: fixed tree-capacity diagnostic

Script71 compared depth3/unrestricted on same31/eight source folds;16 fold models,93 predictions, no runtime promotion. Unrestricted training parameter MAE effectively zero, actual depths7?12; held-source mean deltaE7.804?8.589 (equal-source7.767?8.402). Shared22 slightly improved8.165?8.034; new9 worsened6.924?9.946. Unchanged mean6.303?7.603 with harmed count8/8?7/8; mild7.127?8.753 with harm5/8?6/8. Dark probes improved. Depth3 exactly reproduces prior run; independent saved training/held prediction replay, disjoint-group checks and unchanged hashes passed. All16 controls visually inspected;464 tests passed. Serialization-only initial run failure corrected and incomplete artifacts retained. Recommend fixed input-only brightness-distribution/spatial feature audit before further fitting; no claim that features necessarily solve illumination/complexion ambiguity. Neck/MST/proposal distinctions remain pending. See [results](tree-capacity-comparison.md).


## 24 October 2026: input-only brightness feature audit

Script72 froze ten inputs before extraction: original4 plus L* p10/median/p90/IQR and image-relative left-right/top-bottom mean differences. Same31 saved inputs and baseline estimation masks; no references or targets enter feature calculation. All31 original/eroded probes available, minimum half13,563 pixels. One-pixel erosion retains91.8?96.1%; largest shadow-quantile change1.961 L*, no validated robustness cutoff. Original4 match frozen table, independent quantile/regional means verify all31, repeated extraction deterministic, original hashes unchanged. No fitting/runtime change,464 tests passed. Next fixed eight-source depth3 comparison baseline4 versus proposed10, no feature/depth search. Neck/MST/final-method requirements remain pending. See [audit](brightness-feature-audit.md).


## 24 October 2026: fixed four-versus-ten input comparison

Script73 fit16 depth3 fold models on same31/eight source groups,93 held-source records; frozen brightness10 versus baseline4, no feature/depth search. Mean deltaE7.804 to6.150, still worse than no correction5.460; equal-source7.767 to5.956 versus5.126 no correction. Shared22 improves8.165 to6.615; new9 improves6.924 to5.013. All8 unchanged probes still harmed; mild harm5/8 to4/8. Four source means improve,three worsen,one unchanged. All31 boards inspected; independent saved training/held replay with actual schema and baseline exact reproduction verified; original hashes unchanged;464 tests passed. Keep candidate experimental and runtime unchanged. Recommend ten-feature remaining-control leaf/mask coverage audit before more tuning/data. Proposal feature distinction retained; neck/MST/final-data/evaluation remain pending. See [results](brightness-feature-comparison.md).


## 24 October 2026: ten-feature control and input-mask diagnosis

Script74 replayed32 controls across16 saved4/10-feature models, checked disjoint groups, exact predictions/leaf means and unchanged hashes. Twelve controls remain harmful,three remain better than no correction,one earlier failure improves; no new harm transition. Four controls worsen versus baseline,including one still beneficial mild probe.51739 controls remain in same dark-only6236/84897 leaves;62331 controls remain same color-only14272/75027/84897 leaves.12/16 ten-feature traces mix targets. All16 mask overlays inspected: broad support,min quadrant15.9%,not a ground-truth mask-quality pass. Record pose/box/hairline and lower-jaw uncertainty;neckskin is not automatically spill.464 tests passed,no fitting/runtime/human-label change. Recommend bounded predeclared training-only new-source screen with brightness/color spread and unchanged/mild controls,ledger-aware,no cherry-picking against known errors. Keep10-feature schema frozen,reserved data untouched;neck/MST/proposal distinctions pending. See [diagnosis](brightness-control-diagnosis.md).


## 24 October 2026: bounded brightness/color source batch

Script75 selected18 new TRAIN sources from248 ledger-aware eligible candidates:3L* rank bins x3b* within-bin ranks x2hash selections,policy saved and exposures appended before processing. All18 numerical/brightness-feature successes;all9boards visually inspected.6356 and62676 promising follow-up only;16held with reasons,0training admissions. Independent selection/ledger-prefix/allocation/hash checks passed;230 eligible candidates remain. Frozen10-feature schema/runtime unchanged,0fits,464 tests passed. Next recommended fixed5-variant checks for6356/62676 with unchanged/mild controls,clipping/retention/features/support before staging. No reserved/externaldev use;neck/MST/proposal distinctions remain pending. See [screen](brightness-color-source-screen.md).


## 24 October 2026: two brightness/color candidate variant checks

Script76 checked6356/62676 across5fixed variants each.10geometry/support successes,10finite frozen ten-feature sets,0clipping.62676all5 pass existing coverage screens;6356bright/identity/mild pass, dark/color held with baseline retention38.9%/18.7% and correction58.0%/36.4%.All10boards inspected,temple/side-lighting/pose/jaw caveats retained.8pairs proposed for separate staging,2held,0admitted,0fits.Independent10recipes/targets/clipping,20stats/retention,10brightness recalculations and unchanged hashes verified;464 tests passed. Recommend separate39-pair stage and duplicate/group/provenance checks before any fixed31-v39 ten-feature comparison. No runtime/human-label/reserved-test/neck/MST change. See [checks](brightness-color-variant-checks.md).


## 24 October 2026: proposed39-pair development stage

Script77 staged original31 unchanged plus8proposals from6356/62676,ten sources. Separate39x10 feature table with original frozen schema;all39input measurements recomputed,39x3inverse targets checked,allunclipped. All10 prior attempts preserved:8proposals/2held;6356dark/color and earlier holds excluded. Exact decoded/dHash<=4 screen across10sources found no candidate links;identity independence unverified. Ten disjoint source-fold plans cover39rows once,original31fit nonempty throughout. Independent readiness/allhash/schema/oldrow checks pass;464 tests passed.0modelsfit,no runtime/mastereligibility/humanlabels change. Fixed same39probe31-v39 ten-feature depth3 comparison planned;not a final holdout. Neck/MST/proposal distinctions remain pending. See [stage](development-expansion39-stage.md).


## 24 October 2026: fixed31-versus39 ten-feature comparison

Script78 fit20 source-group fold models,117predictions on same39probes. Original31 versus expanded39 mean deltaE6.253 to7.594,no correction5.384;equal-source6.346 to7.476. Shared31 reproduces prior6.150 then worsens7.171;new8 6.653 to9.235. Both harm10/10identity and5/10mild;dark5.343 to11.219,mild mean slightly improves. All39 boards inspected;independent training/held replay,original31 fit-subset,source/duplicate separation,unchangedhash checks pass;464 tests passed. No runtime promotion/final model. Recommend training-design checkpoint before more incremental pairs: independent-source count,variant imbalance,photo-reference limitations and complexion/illumination ambiguity;larger predeclared review protocol before fitting. Do not discard sources because result worsens. Reserved/neck/MST/human-label/proposal status unchanged. See [comparison](development39-comparison.md).


## 24 October 2026: training-design checkpoint

Metadata audit confirms39pairs/10sources,only3complete-five sources;unweighted source influence varies2.5x. Synthetic reconstruction references are not calibrated skin truth;current overcorrection and unstable source expansion preclude adoption. Saved fixed proposed60-ID TRAIN metadata list from230eligible,3L*ranks x2b*ranks x10hash choices,no rawimages opened/no ledger append/no fits. Proposed five source folds,consistent review statuses/allfailed variants,source-total-weight1 and complete-five sensitivity;not approved final methodology or guarantee of improvement. Plan frozen before executing broader source review,then assess yield before variants/fitting. Prior54ledger entries/currentruntime/humanlabels/reserveddata unchanged. Neck/MST/finaldata/expert/Android tasks remain pending. See [checkpoint](training-design-checkpoint.md).


## 24 October 2026: fixed60-source screen completed

Script79 executed exact predeclared60 TRAIN sources,no replacements;ledger appended before rawreads,prior54preserved,total114;170unused remain. All60 numerical/brightness successes;all12boards/60sources visually inspected.15promising variant-followup only,45held with individual reasons;no admission,distortion orfit. Separate reference/measurement/correction statuses,correctionregion explicitly not yet assessed. Promising plannedfold counts4/4/2/4/1,fold5fragile;no silent reallocation. Exactlist/folds/ledger/all60savedstatistics/brightness/originalhash checks pass;464 tests passed. Next75fixed variant attempts across15sources,duplicatecheck beforestaging,freezealldispositions beforefit; no extra replacement sources implied. Runtime/humanlabels/reserved/neck/MST/proposal unchanged. See [screen](training-source60-screen.md).


## 24 October 2026:75 variant checks and user review

Script80 checked15sources x5variants:75geometry/support/ten-feature successes.7clippedstress,5coverageholds,63unclippednumericalpasses. All75 previews inspected;source-wide contamination holds51446scarf/55007hair/56444foliage remove15,leaving48pairs/12sources pending user review. Preserveall75/historicalsource observations. Independent75recipes/targets/clipping,150stats/retention,75brightness/hash checks;25source duplicate screen no links;464tests passed. Local review.html groups12boards/48pendingdecisions withJSONexport;image references and corrected JSsyntax verified,no interactivebrowser QA. No fit/admission/masterlabel/ledger change. Nextuserreview,then reconcileexclusions and source/foldcoverage beforestaging. Neck/MST/thesis distinctions pending. See [review instructions](training-source60-variant-checks.md).


## 24 October 2026: completed user variant review imported

Script81 imported exact Documents/truehue_source60_variant_review.json;48IDs/provenance verified,35accept/11reject/2uncertain/0pending. Exactexport archived;allusernotes preserved,27prior exclusions unchanged,75records retained,0admitted/0fits. Accept35across10sources,fold1-5counts6/15/8/3/3,only42532/83205complete5. Sevenaccepted technicalnote followups:31154hair3,60162background2(rejectedcontrols stayrejected),63870baselinehijab2. Preserve humanacceptances;do not equate cleaner correctionmask with cleanmeasurement. Uncertain31154dark/47217color remainheld.67454other-personneck rejection does not reject selected-person ownneck requirement. Independent48decisions/notes,27exclusions/hash checks pass. Runtime/masterlabels/ledger/schema unchanged. Nextfocused7case measurement/generation/correction contaminationaudit beforestaging/fitting;neck/MST/thesis distinctions pending. See [review results](source60-user-review-results.md).


## 24 October 2026: seven accepted-note cases inspected

Script82 audited generation/measurement/correction with explicit Codex visual witness rectangles,not full annotations.31154hair/background witness generation614/measurement620-624/correction611-624;60162background generation45/measurement0/correction0,actual45inputpixels changed;63870fabric generation0/measurement692/correction0. Seven useracceptances preserved,separate technicalholds,no repairs/features/model edits. Other28candidates leave originalfold counts4/13/8/0/3,plannedfivefoldNOTready;no reassignment. Trialwitness removal only diagnostic,not a fix. Originalhashes/acceptances/ledger unchanged;464tests passed. Nextrecommended versioned non-skin exclusion ablation acrossall75 andpriorhair/paintregression,allthree maskstages,reviewbefore regeneration/refit. Neck/MST/thesisdistinctions pending. See [inspection](source60-note-inspection.md).


## 24 October 2026: fixed three-stage semantic non-skin veto

Script83 fixed existingmask AND predictedbody/face-skin before running75oldinputs/15sources plus48original224label probes.15generation/150input masks removal-only,75feature sets independently replayed;464tests passed,hashes unchanged.60162generationwitness45to0;63870measurementfabric692to0;31154generation614to363 andacceptedmeasurement/correction still contaminated. Coverageoriginaldenominator70to68,47217dark/color newlyfail(userreject/uncertain),63870dark facialloss(alreadyheld). Earliercorrectionlabeledskin12/12retained clean/shift,paint0/3retained exclusion;1clean hairpoint persists. Sparsepointsnotareaproof. Inspectedall15sourcegenerationcomparisons andtargetedvariantboards;30-board usergallery ready. No adoption/regeneration/fitting;sevenacceptedtechnicalholds/fold4empty remain. Semanticveto newexperimental methoddistinction;neckbodyclassnotnecklocalization/MSTunfinished. See [experiment](non-skin-veto-experiment.md).


## 24 October 2026: isolated two-source consistent regeneration

Script84 regenerated60162/63870 x5fixed variants with83semantic veto at clean generation and recomputed input measurement/correction. Four prioraccepted candidates pass:60162dark/color,63870identity/mild;allfour witnessoverlaps0,remainingmaskreviewpending. All10previews inspected. Bothbrightsclipped63/73,63870dark/colorcoveragefails,60162identity/milduserreject preserved. Independent10recipes/targets/clipping,20stats/retention,10features,sourcepolicy/hash checks pass;464tests passed. Focused4candidate before/aftergallery prepared.0fits/0admissions;31154held/fold4empty,old28notconsistentwithnewmaskpolicy unlesswholecohort reprocessed. Do not mixpolicyversions or silentlyregroup. Neck/MST/thesisdistinctions remainpending. See [regeneration](non-skin-two-source-regeneration.md).


## 25 October 2026: user approved four regenerated mask candidates

User confirmed focused60162dark/color and63870identity/mild comparisons lookgood. Saved exact approval scope/statement in data/manifests/non_skin_regenerated_two_v1/user_changed_mask_approval.json,linked to immutable summary/dispositions hashes. Four changed masks approved,not final training admission or runtimepolicy adoption. Originalrejects/stress/coverage holds and31154technicalhold unchanged. Other28acceptedpairs still oldmaskpolicy;fullcohortmustbe regenerated/rechecked consistently beforefit. Fold4 remains empty;no silent reassignment/fitting. Verification:fourIDs match prioraccepted/unclipped/coveragepass records andoriginalhashes unchanged. No code/model change or test rerun needed for approval record.


## 25 October 2026: remaining28 accepted candidates regenerated

Script85 regenerated exact28 previouslyaccepted/nontechnicalhold pairs across7sources with same three-stage veto as4userapproved regenerated masks.28unclipped/geometry/support/ten-feature/retention successes;all28previews inspected;7beforeafterboards for changedmask userreview. Independent28recipes/targets/clipping,56stats/retention,28brightness/sourcepolicy/originalhash checks pass;464tests passed. Consistent32candidate pairs/9sources,noadmission/no fits. Originalfivefold counts6/15/8/0/3 retained infeasible. Saved explicit proposed9source-held folds(eachpaironce),source-weighteddepth3 vsnocorrection;not executed,retrospective development redesign,duplicate/group recheck atstaging. Originalrejects/uncertain/31154hold/masterlabels/ledger/runtime unchanged. Nextchangedmaskreview thenstageconsistent32 and verifyrevisedprotocol;neck/MST/thesis distinctions pending. See [regeneration](non-skin-remaining28-regeneration.md).


## 25 October 2026: qualified review and correction-gap audit

User says remaining28 generallyokay but facialgapsneedimprovement;recorded exact qualifiedreview,no blankettraining/coverageapproval. Script86 inspected32correctionmasks,rebuilt intentionaleye/brow/completemouth exclusions,found11masks/122unprotectedenclosedpixels. Countsnotgroundtruth,totalcoverageerror oracceptance:boundaryconnectedgapsnotcounted,nearfeaturecomponentsprotected. Inspected7994/67583/40048boards,all9boardsavailable. No maskfill/feature/generation/runtime/modelchange. Nextseparatecorrectiononly gap-recoveryexperiment withprotectedfeatures/materialandpaint/hairchecks across32;no blindfill/boxexpansion. Measurementcanremainrepresentativesubset,correctionneedsfullerfacialcoverage;blendingnotcoveragevalidation.31154held,fold4empty,ninesourceplanunexecuted;neck/MST/thesisdistinctions pending. See [checkpoint](correction-coverage-checkpoint.md).


## 25 October 2026: correction-only enclosed-gap recovery tested

Script87 fixed<=64pixel enclosedcomponent,>2pixelprotectedmargin,allskinsemantic/materialgates;32inputs,48reused224label observations. Added19pixels in2masks:40048identity17plausiblecheek,60162color2edgepixelsvisuallyambiguous. Other30unchanged;no adoption/claimfullcoverage. Measurement/generation/features/inputshashes unchanged,6syntheticsafety cases/32savedreplays pass,464tests passed. Earliercorrectionskin12/12clean/shift andpaint0/3unchanged;1cleanhairpointpersists. Twochangedboards/zooms ready. Largerboundaryconnectedgapsnotaddressed;nextseparateboundary/exclusionmargininspection,no blindfill/thresholdrelaxation.31154held/eval4empty/ninesourceplanunexecuted;neck/MST/thesisdistinctions pending. See [test](correction-gap-recovery-test.md).


## 25 October 2026:40048 cheek gap localized

Userpointsout rightcheek. Diagnosed image-right patchx200-204/y122-128:detectorcrop rightedges204/205/204 dark/identity/mild restrict correctionmask. Dark/mildgap connectsoutside;identity17pixelhole enclosedandrecovered earlier. Maskoutsidecropverifiedzero. Annotated3cases,no masks/data/model/reviewchanges. Recommend bounded paddedprocessingcrop experiment withface/material/anatomicalconstraints across32+hair/paintregression,not blindfill/rectangle. Accountfororiginalgenerationmaskseams/undistortedpatch beforefreshtraining.31154held/fold4empty unchanged. See [diagnosis](40048-cheek-gap.md).


## 25 October 2026: padded correction-crop test

Script88 fixed10%padding/faceoval/YCb/semantic/material/anatomicalgates on32savedinputs:29available,3explicitlyunavailable(67583dark,60162dark/color),28changed/17,940addedpixels(notverifiedskin).40048dark0added,identity27,mild18. Earliercrop-onlydiagnosis incomplete:probe202/124 alsooutsideoval/YCbfail;darkmaterial3.39>3;sourcegenerationexcludedprobe andinputstillmatchesreference.83184clean/shiftgeometryrejected. Paintprobesallunavailable,NOTpaint-safetypass;9/12skinpointsassessableandretained pervariant. Verified29unions/exclusions/bounds/hashchecks;464tests passed,noadoption/regeneration/fitting. Nextrequiresjointgeneration/contourcoverage evidence andassessablepaintregression,notthresholdtuningtoonecase.31154held/fold4empty/ninesourceplanunexecuted;neck/MST/thesisdistinctions pending. See [test](padded-correction-crop-test.md).


## 25 October 2026: small facial-boundary annotation set prepared

Script89 prepared standaloneoffline canvasreview for40048clean256,16798paintnative224,60162clean256.3knownsources,no newexposure/no prefilledlabels. Greenfacialskin/redexclusion/yellowuncertainpolygons,zoomoriginalpixelcoords,draftsave/import/delete/exportJSON;outsideunlabeled,neckleftunmarkednotnegative. Manifest/image/sourcepixels/hashes verified,old24labels/model/ledger unchanged. JSsyntax andNode mockDOMlogic checks pass;browser skill connection noavailablebrowser,so nointeractivebrowserQA. Nextuserdraw3referenceboundaries,returntruehue_face_boundary_review.json path,then validate/rasterizeuncertainty-aware beforecoverageexperiments. No maskrule/training/runtimechange;neck/MST/thesisdistinctions pending. See [guide](face-boundary-review-guide.md).


## 26 October 2026: facial-boundary annotation export remains draft

The available three-frame export passes structural, provenance and polygon-geometry checks, but 40048 is not marked complete and the export is a draft. See the [experiment log](expirement-log.md) entry for the exact export hash and archived validation report. No annotations or historical review decisions were changed; no masks were rasterized or modified and no model was fitted.

This human polygon task adds development diagnostic evidence to the proposed automated method; it does not establish final segmentation accuracy or introduce a required end-user annotation step. The references include native 224 and existing 256 frames and three already exposed sources, so they cannot be presented as a new independent evaluation set or uniform final preprocessing. No uncertain regions were supplied in this draft; that is not proof of boundary certainty. Outside polygons remains unlabeled, and neck left unmarked does not revoke the requested neck correction expansion. Existing proposal differences and unfinished MST, dataset/split, neck, expert evaluation and Android requirements remain unresolved. Complete and revalidate the export, then inspect boundaries before any coverage experiment.


## 26 October 2026: completion confirmed and reference audit finished

The reviewer clarified that40048 was complete and the unchecked box was an oversight. Its exact confirmation is stored separately against the original draft hash; no original JSON flag, polygon or note was rewritten. All three frames are now completed development references. [Boundary reference results](face-boundary-reference-results.md) records23 saved-mask comparisons and the local visual gallery.

The references confirm the missed cheek probe remains absent even in padded candidates, while substantial eye/brow exclusion overlaps persist in generation/measurement/correction. High selected-skin coverage is not adequate validation. The16798 area comparison uses older pre-semantic-veto masks and cannot validate current learned-veto paint safety. No pipeline rule, inputs, features, eligibility, prior human decisions or model changed;467tests pass. Next is a predeclared anatomical-exclusion/contour investigation across all three stages with assessable paint regression, not automatic training. Human boundary references remain additional development diagnostics on exposed mixed-resolution sources, not final independent evaluation or a required application-user workflow. All earlier unresolved proposal requirements remain pending.


## 26 October 2026: fixed anatomical/contour ablation completed

[Protocol](anatomical-contour-protocol.md) and [results](anatomical-contour-results.md) record E(exclusion margins) and EC(bounded contour support) on32savedinputs/ninesources plusnativehair/paintregressions. Exclusionoverlap improves with valid-skinloss;annotatedcheekremainsmissing. ECfails geometry on3cohortcorrections and allpaint probes,so no paint-expansion safety claim. Neither candidate adopted;0regeneration/fit,priorlabels/holds/foldsunchanged. Independent196maskreplay/44measurementfeaturechecks and471tests pass.

EC's added pixels replace absolute HSV/YCrCb checks with learnedface-skin classification,localdistance andinput-relativeLab checks. This and scale-dependent anatomical margins extend the proposed rule-based method; they are separately tested development changes,not an approved final methodology. Exposed humanreferenceframes remain diagnostic andmixed224/256. Syntheticinputsstilluseoldgenerationmasks;do not report these as consistently regenerated training data or completed finalsegmentationevaluation. Neck,MST,finaldataset/split/evaluation,expertMOS andAndroidrequirements remainunfinished. Nextrecommended fixedlandmark-framingcomparison is developmentwork,not proposalapproval.


## 26 October 2026: landmark framing compared without adoption

[Fixed framing comparison](landmark-framing-results.md) tests53samecases withfull-native-image landmarks versuspreviousfirst-successcrop. Rules/thresholds/originalmasksunchanged. Mixedeye/browresults,annotatedcheekstillmissing,paintECstillunavailable;no framingadoption orregeneration/fit. All199candidate masksindependentlyreplayed,44measurementfeaturesverified,471tests pass. Preserve priorhuman decisions/holds/folds. Thisdevelopmentablationdoesnotcomplete finalsegmentation,neck,MST,data/split/expert/Androidrequirements oramendproposal. Nextsemanticpredictionagreementauditbeforefurthergeometrytuning;legacyfeatureholesmeanthisisnotafreshmaskrebuild.


## 26 October 2026: semantic model class mismatch documented

[Cached semantic-reference audit](semantic-reference-audit-results.md) uses55existingnative maps,9reference-frame comparisons and48pointobservations with0newinference/fit. Face-skinretains99.55-100% labeledskin butincludesessentiallyallcleanfeatureexclusions and94.27/96.35% of16798paintarea(clean/shift). All3paintpointseachvariantpredictedface-skin. Thismodelprovidescoarsefaceregions,notrequiredfeature/paintseparation;earliercombinedmaskpointpassesmustnotbecreditedtosemanticpaintrecognition. No rule/runtime/data/modelchange.471testspass,originalhashespreserved. Nextsegmentation-designcheckpointmustseparatecontour/anatomical/paintrequirementsbeforeanotherpolicy. Learnedmodel/proposal distinction andneck/MST/finaldata/splits/evaluation/expert/Androidgapsremainpending.


## 26 October 2026: dense anatomical parser tested separately

[Design/protocol](face-parsing-protocol.md) and [results](dense-face-parser-results.md) record one pretrained BiSeNet ResNet18 ONNX candidate with separate anatomy classes. D raw skin/nose support includes the missing40048cheek, while V old-mask intersection removes prior hair-point contamination and preserves12/12skin points. D selects99.43/98.17% of painted area; V retains1327/1001painted pixels despite passing sparse paint points. Neither adopted.32measurement cases valid,31retention passes with60162dark flagged; original approvals/holds/folds unchanged.158mask replays/44feature checks and475tests pass; no regeneration or correction-tree fit.

This is another learned segmentation model beyond the proposal's rule-based stage. Record actual53,205,364-byte model and internal512 inference with native224/256 restoration, source training dataset, desktop median0.2268s and unverified Android/backend parity/memory costs. No Android app was built. Anatomical classes do not imply paint recognition or calibrated skin-color truth. No final dataset/evaluation or proposal-amendment claim. MST mapping, neck localization, final split/data/reference/expert evaluation and Android remain unfinished.


## 26 October 2026: parser/material combination and boundary guard

[Fixed combination and follow-up results](parser-material-combination-results.md) cover53 current/reference cases plus all90 historical source/variant cases. C/C2 recover the annotated cheek and preserve all12 skin points per variant, while wider exclusions/material guards lose labeled skin. C2 still selects851/479 painted pixels clean/shift, including113/69 newly selected versus original correction masks. Numerical current32/32 passes do not validate paint safety. Neither mask adopted;0regeneration/admission/fit. Previous user decisions,31154 hold, empty originalfold4 and revised unexecuted plan remain unchanged. Independent1072mask replays,476measurement checks,136reference checks and481tests pass.

Dense learned parsing/coarse semantic intersection, fixed anatomical margins, global relative-Lab vetoes, omitted L* in chroma C, and the adaptive fixed2pixel C2 safety margin all exceed the proposed rule-based stage. Record their definitions, exposed mixed224/256 references,53.2MB model/internal512 inference and unverified phone costs. No automatic paint recognition, calibrated skin truth, final independent evaluation or required application annotation workflow is implied. User authorization to continue autonomously does not amend the proposal or approve every candidate. Neck localization, operational MST, final data/split/evaluation, expert MOS and Android remain unfinished. Further regeneration/fitting is held on measured mask defects, not routine user confirmation.

## 26 October 2026: broader protected-material development validation

[Results](paint-protection-validation-results.md) add an inventory of114already exposed TRAIN sources and17frozen mixed224/256frames with51global diagnostic probes. Original three user reference rasters/polygons and historical decisions remain unchanged;13new Codex cosmetic/mark interiors are explicitly provisional/unverified, not expert or user truth. Ambiguous colored appearance and lighting have no invented material labels;16798remains the only user-annotated broad paint face. The selected set and repeated probes are not independent people or final evaluation.

Unchanged A/F/C/C2produce448masks on48available probes; three seed failures remain unavailable. C2retains851/880/479paint pixels clean/dark/color plus provisional cosmetic/mark interior overlap. All192measurement sets are numerically valid, but protection, coverage and historical holds remain unresolved;0regeneration/admission/fit or runtime adoption. Independent replay, original hashes, full visual boards and481tests verified. Whole-image gamma/gain probes (11clipped color probes) are distinct from proposed masked synthetic training pairs; no inverse targets or training manifest were made.

Learned parsing/material guards and provisional development annotation are additional methodology beyond the proposed rule-based mask. They establish neither calibrated skin truth nor automatic paint recognition, advisor approval, final segmentation/fairness performance, phone feasibility or a required application-user annotation step. No source/fold/user-decision revision is implied. Neck localization, operational MST, final data/reference/splits/evaluation, expert MOS and Android remain unfinished. Material-specific design needs representative references and a separately declared evaluation before another candidate.

## 27 October 2026: material seed audit and reference-quality prerequisite

[Cached attribution/design checkpoint](material-protection-design-checkpoint.md) accounts for60region/probe funnels and560stage/region counts on the existing frozen51probes. Material seeds overlap original paint-group exclusion labels (614clean16798pixels), but this is not a verified physical contamination rate or causal explanation of the median. Scalar-order examples are valid under saved labels; visual review flags mixed paint/skin boundaries, so they do not establish physical-material inseparability. Original annotations and older numerical results remain unchanged; separate QA requires adjudication before treating these regions as material ground truth.

The next material design requires explicit label taxonomy/uncertainty, versioned actual reviewer adjudication, representative ordinary-skin/material/lighting coverage, exposure/source-group separation and predeclared three-stage protection/coverage evaluation. This is a development requirement, not a new application-user task or a completed expert study. No new inference/model/mask policy, regeneration, admission or fit;481tests pass. Existing learned-stage/proposal differences and unfinished neck/MST/finaldata/splits/reference/evaluation/expertMOS/Android requirements remain.

## 27 October 2026: CPM material-supervision feasibility lead

[Focused source/preflight investigation](cpm-pattern-feasibility.md) identifies CPM's synthetic-pattern-supervised branch as a relevant lead, without adopting it or evaluating image masks. Pinned source snapshots and one130.43MBcheckpoint are retained locally. Static legacy metadata inspection executes no model/serialized classes. Source preprocessing/cutoff differences and UV versus native-coordinate domain must be resolved before study inference; no software environment change, CPU/export/phone parity or calibrated material claim is implied.491tests pass including10new offline artifact-inspection checks.

Learned material segmentation, PRNet-style UV geometry and a conversion runtime would be further additions to the proposed rule-based stage; the full makeup-transfer system is not the proposed decision-tree correction model. No generated bare-face image becomes a true color target. Dataset/checkpoint terms are separate from code licensing, and the current material-reference adjudication prerequisite remains. No new study source exposure, training admission, regeneration, correction fit or review/fold revision. Operational MST, selected-person neck, final data/reference/splits/evaluation, expert MOS and Android remain unfinished.

## 27 October2026: material-model expansion deferred; core tree portability

The user explicitly set CPM aside and retained paint/makeup protection as a limitation. Its previous feasibility lead/next conversion steps are historical, not the active implementation plan. No formal proposal amendment, new universal-protection requirement or reversal of original source/variant holds follows. Earlier face/visible-neck direction remains recorded and pending.

[Core tree portability](core-tree-portability-results.md) exports the existing four-feature prototype to2556-byte JSON and validates a standard-library evaluator against23saved feature rows,12boundary vectors and23synthetic RGBcorrections. All splits/leaves match exactly; package-free `-I -S` inference and519tests pass. No model fitting, mask change, image exposure, training admission, generation, production runtime adoption or Android implementation occurred. This directly supports the proposed on-device decision-tree component, but preserves the prototype's small-data/quality limitations and departure from MST-conditioned inference. Operational MST remains unresolved; no labels guessed or threshold table fabricated. Finaldata/reference/splits/evaluation, expert MOS, selected-person neck and Android remain unfinished.

## 27 October2026: auditable core orchestration with explicit missing MST

[Unified core check](core-pipeline-check-results.md) adds an input-only Python entry point for fixed detection, HSV/YCrCb complete-mouth masking, Lab/ITA and portable-tree correction. Every available output explicitly records unavailable/null MST and proposal_complete=false. This exposes the existing continuous-feature-regressor difference from the proposed MST-conditioned method; it does not resolve mapping or rename ITA as MST. No learned material/parser candidate is introduced; CPM remains deferred and paint/makeup a limitation.

All38previously exposed controlled attempts retained:37available,1original measurement failure. Available saved features match, original-model predictions/transforms/metrics replay, outside-mask pixels unchanged and537tests pass. Frozen tree worsens7/7unchanged,4/7mild and3/4clipped stress probes despite improvement on3one-source development probes. These are relative synthetic reconstruction diagnostics, not calibrated complexion, independent final performance, expert MOS or phone timing. No final model adoption, training/regeneration/admission, newsource exposure, review/fold change or neck/Android implementation. Finaldata/reference/splits/evaluation and operational MST remain unfinished.

## 27 October2026: core control-aware training ablation remains insufficient

User-authorized [fixed control-recipe comparison](core-control-comparison-results.md) fits14experimental source/group-held-out trees on current core224inputs/four Lab-ITA features/legacy masks. Only22previous screen-pass IDs may fit;8held remain diagnostic-only. Transferring those prior256screen IDs is a conservative fit gate, not native-mask accuracy or final cohort approval. Seven diagnostic outer groups include held-only12288; no external/clipped/failed input is fitted. Frozen runtime is seen-source history and explicitly separate from fair CV.

Controls reduce primary mean CIEDE2000from9.389older recipe to6.865, but no correction5.129remains better.6/6unchanged and2/6mild primary probes worsen; sole complete-five source also worsens versus older recipe. All7boards inspected;14model replay refits,120metric/prediction replays,24post-hoc leaf means and546tests pass. Runtime, original labels/reviews/folds and data eligibility unchanged; no new source, regeneration, final production model or search. Additional unchanged/mild variants, selected development IDs and source-group evaluation are declared methodology distinctions, not an approved final MST-conditioned method. MST/neck/finaldata/reference/splits/evaluation/expertMOS/Android remain unfinished; CPMdeferred and paint/makeup a limitation.


## 28 October2026: saved-fold diagnostic does not establish feature impossibility

The [feature/target diagnostic](core-feature-conflict-results.md) reuses saved source-held-out folds without fitting. Different synthetic inverse targets are nearer than matching targets for11/12primary controls under fitting-only standardized Lab distance. Five controls route into leaves with no matching target; one harmful identity probe has matching nearest-target support outside its leaf. These observations implicate both measurement/target overlap and sparse tree routing. No exact cross-source feature collisions were found; four-dimensional distance changes one ordering. Neither a mathematical impossibility claim nor a new distance-based correction rule is warranted.

This is post-hoc development evidence on selected known sources, not independent accuracy or expert/calibrated skin truth. ITA is derived from recorded meanL/b but can still help tree representation; it is retained. No invented MST mapping, model replacement, mask edit, data admission, source exposure or review/fold change.555tests and independent replay pass. The next justified investigation is existing reviewed source/reference suitability and independent control/distortion coverage, with a declared policy before any additional data stage. All unresolved core requirements and the deferred CPM/material limitation remain.


## 28 October2026: source readiness and demonstration packaging

The [existing-source audit](core-source-readiness-results.md) preserves all original reviews and shows no newly established core-ready expansion:32regenerated candidates use a different256/veto/ten-feature policy and retain coverage concerns. Nine proposed folds are source/duplicate-group separated but subject independence remains unverified. No calibrated reference/MST evidence is supplied by old photographic acceptance. The offline thesis checkpoint reports software availability and negative correction findings separately. No data admission, mask adoption, fit, final performance claim or methodology amendment follows. MST/neck/finaldata/splits/expertMOS/Android remain unfinished; CPM remains deferred.


## 28 October2026: Android deliverable authorized and JVM component parity

User requires Python, Android and thesis results before7November; working cutoff6November. Existing Android scaffold was discovered and is now explicitly authorized for extension. Java inference matches44Python vectors and rejects15invalid cases; no Android Kotlin/APK/device result is claimed. Frozen four-feature development tree port preserves the existing difference from proposed MST-conditioned inference. No mapping/model improvement or new data/mask adoption follows. [Schedule and unresolved requirements](deadline-delivery-plan.md).


## 28 October2026: buildable Android scaffold, not integrated correction

Workspace SDK setup, actual debug APK compilation/signature, packaged frozen-tree parity,14Android-module unit tests and lint0errors/27warnings now verified. [Build report](android-build-results.md). The image repository still passes through its input; no phone deployment, actual image-pipeline integration, hardware timing, MST validity or correction-quality improvement is claimed. Proposal differences and all original reviews/holds/folds remain. SDK/build progress does not complete the thesis method; core integration, neck, final data/reference/split evidence, expert MOS and phone evaluation remain. CPM stays deferred.


## 28 October2026: fixed control-aware artifact remains development-only

Built one all22/six-source four-feature native224depth3candidate, not a new method comparison. Reused source-held-out recipe evidence fails numerical/nonharm gates; active model unchanged.37known image replays retain1failure, show better seen-source reconstruction but worse one-source external development10.913versus10.666no correction. No final accuracy or calibrated complexion claim.574tests and independent leaf/pixel/evidence replay pass. [Full build/results](control-aware-model-build-results.md). Continuous ITA/Lab, native224, fixed synthetic severity and selected FairFace-only sources still differ from the proposed MST/256/tone-dependent/FairFace+SCIN method. Adviser/method question pending; no amendment inferred. All original reviews/holds/folds and the unresolved MST/neck/data/reference/evaluation/expert requirements remain; Android on hold and CPM deferred.


### 2026-10-28 - User retains MST; proposal verified and MST feature interface added

User explicitly answered retain the paper's MST method. Direct four-feature trees remain development baselines, not final candidates. Original proposal PDF62?63re-read using PDF skill/isolated reader: MST-E-calibrated ITA lookup and both ITA/MST plus facial statistics enter the model. Evaluation-only versus calibration wording remains an explicit proposal ambiguity; no new calibration/evaluation subjects assigned or MST-E correction training admitted.

Added versioned calibrated-lookup and five-feature builder interface, with strict ordered thresholds, measurement-contract binding, declared held-subject/report provenance, official1?10to config0?9conversion, input-derived MST and no four-feature fallback. Declarations alone do not prove scientific validation. No real thresholds or mapping accuracy claim.21synthetic-interface tests;595full tests pass in12.15s. Core runtime remains MST unavailable and unchanged.

SCIN metadata companion labels audited preserving both India/US annotations:5033cases,2008agree/2996disagree/16one-sided/13unavailable. Head/neck-at-distance368cases:151agree/216disagree/1unavailable; no agreement casesMST9/10, only9candidate paths locally available. No new image exposure/download, source admission or preferred-annotator selection. Independent5033row reconciliation and original hashes pass. Script137; [method/interface/data checkpoint](mst-method-retained.md), [audit](../outputs/mst_retention_checkpoint_v1/summary.json), [verification](../outputs/mst_retention_checkpoint_v1/verification.json). Next gate is consistent256measurement/calibration roles/protocol, not additional directLab fits. Android on hold; CPM deferred; no commit.


### 2026-10-28 - Square256 MST measurement and fixed calibration executed

Continued authorized MST path; CPM deferred and Android on hold. Frozen protocol before418historically reviewed MST-E attempts. Script138uses a single256whole-frame INTER_LINEAR measurement contract:396success,21detection/1mask-stage failures retained. Twelve predetermined boards inspected; fragmentation and possible hair/background/glasses selection remain. Independent recomputation checks396saved masks/Lab/ITA sets and original hashes; verifier corrected to existing float32 channel means rounded before ITA, without modifying outputs. Native stderr/PowerShell session exit1despite completed output is disclosed, not treated as a clean exit.607tests pass in11.16s.

Script139fixed subject-median/isotonic-center diagnostic on15subjects pools categories and cannot create nine distinct thresholds. Five categories have one subject;0available held-subject predictions, not0%accuracy. No production lookup/correction fit/adoption. Preserve negative findings and original reviews; subsequent method work requires explicit measurement/reference and independent-subject rationale. [Results](mst-square256-results.md). Created [cross-account handoff](CODEX-HANDOFF.md) with exact workspace/current state, user decisions and next gates. No commits/uploads.


### 2026-10-28 - Saved MST measurement/support diagnosis

Executed fixed metadata/feature-only script140: all396ITA values recompute from roundedLab, none has nonpositiveb. Across100different-category subject-median pairs66ordered/34reversed (5same-label separate). Maxwithin-subject range121.645degrees; existing lighting groups show large contrasts, confounded by pose/mask/capture. Fiveheld folds lose singletonMST4/5/7/9/10; tenotherfolds poolcenters. No claim onecause or mathematicalimpossibility. Independent15subject/105pairreconciliation and originalhashes pass. No image access/newfit/mask orlabelchange. [Results/next reference-quality diagnostic](mst-measurement-diagnosis-results.md). RetainMST;607previous tests, runtimeunchanged. Androidpaused,CPMdeferred,nohandoffwork,notcommitted.


### 2026-10-28 - Fixed12 sparse measurement-region QA with uncertainty preserved

Prepared original-only crops and froze24Codex provisional cheek points before scores. Savedmask selects204/216patchpixels,22full/1missed/1partial. PostscorevisualQA flags both frame7points near glasses; keep exact originalpoints/scores and separate uncertainty caveat, never24validatedlabels. Patch/full-mask ITAdifferences-18.379to34.492are spatial/reference diagnostics, not validated alternative features. No candidate mask/lookup/training or source exposure. Independent24overlap checks and originalsource/mask/reference hashes pass. Scripts141/142; [results](mst-region-quality-results.md), [review](../outputs/mst_region_quality_v1/review.html). Need actual representative reference adjudication plus independent-subject support before next estimator fit; no automatic cheek-only adoption. Latest607tests; runtimeunchanged,Androidpaused,CPMdeferred,notcommitted.


### 2026-10-28 - User reviews sparse regions; frame7moved below glasses

User accepts other marked frames and flags7as too close to glasses, requesting adjustment for glasses wearers. Preserved originalV1points/scores and saved explicit user statement in outputs/mst_region_quality_v2/user_review.json. Only frame7coordinates changed to lower lateral cheeks; visual inspection confirms clearance, but revised coordinates are not yet user-confirmed. Other11frames unchanged. Rule: inspect actual frames/lenses, keep entire patch/displayed square clear, relocate to assessable cheek or mark unavailable; no universal downward shift or automatic glasses detector claimed. [Revised review](../outputs/mst_region_quality_v2/review.html). No rescoring/estimator/mask/model/calibration changes or accuracy approval. Androidpaused,CPMdeferred.


### 2026-10-28 - User confirms revised frame7; reviewed-region replay rejects premature estimator adoption

Preserved confirmation against exactV2coordinatehash. Both revisedframe7patches fullyselected; aggregate204/216pixels unchanged. Script143independently checks24patchLab/ITA/overlaps and originalhashes. All4same-subjectpairs reported: across3differentlyrecordedlighting pairs reviewedpatchITAdifferences120.146/37.891/84.868 exceed fullmask73.167/32.623/73.853; samepoorlightingpair2.887vs4.576. Sparse pose/light/reference confounding precludes causal or universalclaims, but no evidence supports adopting this cheek-only estimator. Metadataonlywelllitcount leaves7singletoncategories, so no filtering/fit applied. [Results and concrete method/data gate](mst-reviewed-regions-results.md). No model/mask/lookupchange;607latesttests,Androidpaused,CPMdeferred.


### 2026-10-28 - Calibration/evaluation design and exact subject folds frozen

User authorized design. [Protocol/design](mst-calibration-evaluation-design.md) fixes disclosedMST-E mapping-development role (never correction-tree fitting/freshfinaltest), same-contract measurement, subject-exclusion/equal-subjectweights, availability/unsupported-fold denominators, baseline/percategory/lighting reporting and deployment evidence requirements. No newalgorithm/fit selected; strictmidpointfailure preserved. Script144freezes15folds partitioning418attempts/396success/22failures, with exact fittingIDs/support/lightingweights. Fivefolds loseheldcategory. Independentpartition/lighting/hashverification passes. [Plan](../outputs/mst_evaluation_design_v1/fold_plan.json). Tenoutputlabels do not imply tenindependentlyvalidated categories; additionalindependentlabeledsupport or actualagreedlimitedevaluationclaim needed. No sourceallocationchange/admission, masks/labels/thresholds/runtime edits, acquisition/outreach or adviserapproval implied. Androidpaused,CPMdeferred,latest607tests unchanged; notcommitted.


### 2026-10-28 - Limited MST evaluation scope prepared for adviser review

User chose preparelimitedevaluationscopeforadviserreview. Created [concrete adviser draft](adviser-mst-limited-scope-proposal.md), retainingtenlabelMSTarchitecture, separating exposeddatamappingdevelopment from correctiontraining/freshfinaltest, supportlimitedcategoryclaims, lighting/availability/baselines and deadlinecontingency. CurrentMST1/2/3/6/8have2measuredsubjects;4/5/7/9/10oneeach. Scope qualification doesnotvalidatefailedlookup. No adviserapproval, outreach, newdata/fit/mask/admission or finalclaim. Script145preservesunrepresentedsubjectreviewstatuses and prepares supportcounts; independent10category/418attempt/396success accounting and originalhashes pass. [Support](../outputs/mst_limited_scope_proposal_v1/support.json). Actualscopeagreement and justifiedmappingevidence remain prerequisites. Androidpaused,CPMdeferred;607latestruntimetests,notcommitted.


### 2026-10-28 - Limited-scope evaluation implementation completed

Continued authorized infrastructure while adviser-reviewproposal remainspending. Added reusable src/evaluation/mst_validation.py strictsubjectheld reporting: explicitallmeasuredpredictionsorNone, medianbaselinefromfitsubjectsonly, unsupportedcategoryflags, image/equal-subject metrics and MST/lighting/subject denominators. Script146reports existing418attempts/396measured/22failures/0predictions,180measurementswithoutheldcategorysupport; undefinedaccuracy/pairedcomparison preserved, baselineonlyseparate. Independentdenominators/hashchecks pass.620tests in14.25s including13newtests. [Implementation/report](mst-limited-evaluation-implementation.md). No calibratorfit/export, model/mask/review/admissionchange or adviserapproval. Androidpaused,CPMdeferred,notcommitted.


### 2026-10-28 - Confirmed scope; fixed monotone mapping and input feature path implemented

Userexplicitlyconfirmed adviserapprovaloflimitedscope; recorded as userreportedconfirmation, not independentadvisermessage. Frozen newprotocol for historical decreasingisotonicrecipe onfixedsquare256data,15heldsubjectfits,subjectweights,no tuning.396predictions/22failures; equal-subjectMAE2.306vs3.0median, supportqualified2.266vs3.2passdeclareddevelopmentchecks. Exactaccuracy11.11%vs14.39%baseline remainsweak;180lackheldcategorysupport. Nofinalvalidationclaim.

Oneall396developmentfit saves23knots, actualoutputsMST1?9(noMST10). Separateexperimentalschema preserves this defect; nofake9boundaries or validationclaim. Portable443vectorparity;15newtests,635fulltests in12.81s. Script149inputonly256measurement?ITA?experimentalMST reproducesknownsourcefeatures and addsfifthMSTindex; nocorrection/defaultreplacement. Scripts147?149; [results/limits](mst-monotone-square256-results.md). Existing224data cannot be mixed;256candidateeligibilityandtone-dependenttransformgroups remainunresolved. Need review of weakmapping/noMST10 beforepromotion; noadditionalsearch/admission. Originalreviews/masks/failedartifacts preserved,Androidpaused,CPMdeferred,notcommitted.


### 2026-10-28 - MST-aware training contract and Table2target incompatibility

Userauthorizednextpaperalignedstep. Added explicit square256fivefeaturetrainingrowvalidator: eligibleTRAINonly,FairFace/SCIN(noMST-Ecorrectiontraining),same measurement/lookuphashes,distortedinputmappedMST,sourcegroups,unclippedsuccess and exactinversevalidation.17newtests pass. No existing held32pairs admitted or modelchanged. [Target/design checkpoint](paper-distortion-target-checkpoint.md) explains Table2offset/contrast cannot generally be inverted by gamma/red/bluealone; clippinglosesinformation. RecommendedretainfullTable2andfitapproximate3paramrecoverytargets,residualsreported; userdecisionasked beforecompositegeneration. Operatororder/units/contrast/colorconversion must beexplicit, not invented as proposalmandates. Existinggrouping1?3/4?7/8?10provenance retained. No fit/regeneration/runtimechange. Androidpaused,CPMdeferred;notcommitted.


### 2026-10-28 - FullTable2 composite and approximate target fitting implemented

UserselectedfullTable2withapproximate3paramrecoverytargets. Frozenexecutioninterpretationandoptimizerbeforetests; retainedgamma/red/blueoutputs. New table2_composite.py and recovery_targets.py implement explicitpower/contrast/brightness/redblue/finalclip and boundedTRFleast-squares(identitystart,.25?4bounds),residual/convergence/rank/support/clippingreports, no exactinverseclaim. Trainingcontract distinguishesapproximatecompositefromexacttargets; noadmissionoverrides.671tests pass12.08s (12newoperator/target+7compositecontract). Script150syntheticonly32?fixture: RMSEidentity/fitted .135/.029light,.252/.109medium,.324/.174dark;21/486/741clippedpixels retained, not learnedperformance. [Fullresultsandlimits](table2-target-fit-results.md). No studyimagesopened,correctiontreefit,cohortadmission/mask/runtimechange. Nextdeclaredknown-source256feasibilitybeforetraining;Androidpaused,CPMdeferred,notcommitted.

### 28 October 2026 - Table 2 feasibility and clipping limitation

Full Table 2 with approximate three-output recovery remains user-authorized. Six-source diagnostic retains18clipped attempts,17measurements and one detection failure; none meets current unclipped training admission. Report fixed-reference-mask reconstruction and mask-retention losses, not intersection-only or oracle-as-learned claims. Proposed separately labelled clipped-input development training would change the admission rule and remains a methodological decision; no such training executed. Reference pipeline masks are not expert truth, source complexion groups are not assigned by severity probes, and weak experimental MST remains qualified. [Results](table2-known-source-feasibility-results.md), [design](table2-clipping-stress-design.md).
