# Decision Log

29 October 2026: User explicitly reiterates fidelity to thesis implementation.
Keep semantic-parser experiments diagnostic, not a final replacement for
rule-based masking. Test existing color support constrained to face geometry
before component selection; no threshold/architecture change. The refinement
reduces spill but cannot recover missing color support. Add exact-achromatic
reference exclusion reflecting the user's monochrome-photo direction; exclude
13 of 406 non-reserved training sources in a separate audit. Keep ITA/MST,
facial statistics and gamma/red/blue decision tree; no active model promotion.
[Progress and remaining gates](paper-method-correction-progress.md).

28 October 2026: Complete all 418 post-quarantine training attempts before
review or fitting. Preserve the 157 failed/unavailable cases and the clipping
annotations on 254 of 261 target candidates. Numerical success is not source
approval; successful dark-severity coverage remains absent. No held-out
preprocessing, active model change or photographer evaluation.
[Preparation results](correction-training-preparation-results.md).

28 October 2026: Execute the predeclared duplicate-only access phase before
new-cohort fitting. Quarantine suspected historical/cross-role connected
overlaps without changing frozen roles or replacing IDs. Keep validation/test
closed to quality and model-outcome inspection; disclose computational decoding.
The verified training queue contains 418 unreviewed candidates, not approved
training examples. [Audit results](correction-duplicate-audit-results.md).

28 October2026: Userauthorizessubstantialcorrectiondata/trainingredesign. Freeze
newmetadata-only600candidate allocation outsidehistorical650:420train,90dev
validation,90finaltest,preserveoldpartitions/exposure. Holdvalidation/testoutof
initialdevelopment,requireduplicateauditandreviewbeforefitting. Thisdoesnot
authorizeautomaticcandidateadmissionorclaimMST/personvalidation. Continue
ITA/MSTdecisiontreemethod;photographersafterfinishedmodel/existingGoogleForm.
[Design and verification](correction-data-redesign-results.md).

28 October2026: User accepts1398(body),68453(holes),59944(hair),66156(background),
63087(body)with explicitconcerns; rejects12222referenceclothingand60381bodypart.
Preserve exactdecisions/concerns on reviewed processing; no mask changes or
hairfreeclaim for59944. Expanded15sourcefixedcomparisonshowsbaseline5matched
improvementbutallmethodsretaincleanharm;noactivationorgaterelaxation.
[Results](table2-reviewed-fifteen-source-results.md).

28 October2026: User clarifies photographer opinions belong after correction
model completion, using the existing Google Form. Local forms/protocol remain
unused historical artifacts and are not a development prerequisite. Focus on
model improvement. Fixed control-aware partition experiment subsequently fails
both gates; preserve results without activation or post-hoc tuning.
[Model comparison](table2-control-partition-results.md).

28 October 2026: Import explicit expansion decisions: reject40048/42532/63870
for selected hair; accept67583/83205/84364. Keep exact reasons and prior holds.
Fixed eight-source/16pair comparison fails overall and identity gates despite
lower distorted-only error. Preserve failure, do not activate or relax gates.
Investigate earlier correction-support versus measurement-mask distinction
before further cohort fits. [Results](table2-reviewed-expansion-results.md).

28 October 2026: Expand the Table2stress development cohort using six fixed
previously reviewed TRAIN sources with accepted controls and no rejected or
uncertain prior variants; no performance-based replacement sampling. All
regenerated masks require exact-version review. Prepared combined22pair/11source
fold plan conditionally; preserve old failed candidate and zeroidentityharm gate.
No fit before new review. [Expansion record](table2-stress-expansion-results.md).

28 October 2026: User accepts22211/22454/62331/6236/75027with stated concerns;
rejects51739because mask admits facial hair from another person. Import exact
statement without overwriting prior reviews or fixing masks. Ten separately
admitted experimental pairs evaluated in five rebuilt source-group folds.
Candidate fails identity gate despite lower mean error; retain failed result,
do not activate or relax gate. [Reviewed Table 2 results](table2-reviewed-stress-results.md).

28 October 2026: User approved the recommended separate clipped Table 2
experimental training path. Implemented versioned exception with mask/scene,
source-role, input-MST and approximate-target requirements intact. Reference
lookup selects an explicitly estimated severity only; distorted lookup supplies
the input feature. No official labels inferred. Twelve candidates remain
unadmitted pending exact square256 visual review. Six provisional folds use
source/duplicate groups, not verified person identities. Zero identity error
increase is the predeclared conservative development gate, not a perceptual
threshold. [Record and review](table2-stress-preparation-results.md).

Track key technical and design decisions here.

| Date | Decision | Rationale | Alternatives considered |
|------|----------|-----------|------------------------|
| 2026-09-09 | Use CIELAB L*/b* for ITA computation | Standard formula from literature; directly maps to Fitzpatrick/MST scales | Direct RGB classification (less interpretable) |
| 2026-09-09 | Decision-tree regression for correction parameters | Lightweight, interpretable, fast inference on-device | Neural network (too heavy for on-device), linear regression (underfit) |

### 2026-09-22 – Skin Mask V2 selected for ITA pipeline

- Decision:
  Select Skin Mask V2 as the facial-skin segmentation method for the next
  implementation stage: CIELAB conversion and ITA computation.

- Selected V2 pipeline:
  YuNet face detection → face crop → HSV/YCrCb candidate skin mask →
  morphological cleanup → largest connected component → landmark-based
  exclusion of eyes, eyebrows, and mouth/lips → final facial skin mask.

- Alternative tested:
  Skin Mask V3 added one post-exclusion MORPH_CLOSE operation using a 7×7
  elliptical kernel, followed by another largest-connected-component pass.

- Reason:
  V2 removed eye and eyebrow regions more effectively than V1 and produced
  more acceptable overall facial-skin masks than V3. V3 did not provide a
  consistent enough improvement in cheek coverage and holes to justify adding
  the extra morphological step.

- Known limitations:
  Some cheek regions remain inconsistently detected, and small holes may
  appear under poor or uneven lighting. Lower-light images, especially those
  with darker skin, require careful mask-quality review.

- Impact:
  The selected V2 mask will be used to select facial skin pixels for CIELAB
  statistics and ITA computation. ITA results remain image-derived estimates,
  not clinical or identity labels.

- Commit:
  <paste the commit hash>

  ### 2026-09-27 – Selected facial skin mask version

- Decision:
  Skin Mask V2 was selected for the ITA estimation pipeline.

- Selected pipeline:
  YuNet face detection → face crop → HSV/YCrCb candidate mask →
  morphological cleanup → largest connected component →
  landmark-based exclusion of eyes, eyebrows, and mouth/lips →
  final facial skin mask.

- Alternatives:
  V1 lacked landmark exclusions and frequently included eye and eyebrow
  regions. V3 added post-exclusion hole filling but did not consistently
  improve results enough to justify the additional operation.

- Reason:
  V2 produced the best overall balance between retaining facial skin and
  removing non-target facial features in the pilot review.

- Known limitations:
  Cheek coverage may remain inconsistent, and masks may become fragmented
  under poor or uneven lighting, especially in darker facial regions.

- Next step:
  Apply the frozen V2 pipeline to MST-E to compute ITA values against known
  MST labels and prepare an ITA-to-MST mapping procedure.

### 2026-10-11 – ITA-to-MST calibration interpretation

- Input:
  Cleaned MST-E calibration results generated using Skin Mask V2, manual
  quality review, and image-derived CIELAB/ITA computation.

- Diagnostic finding:
  The full dataset showed substantial overlap and non-monotonic ITA values
  across the ten official MST labels. A conservative well-lit subset improved
  the broad brighter-to-darker ordering, but adjacent MST labels continued to
  overlap substantially.

- Decision:
  The system will not claim precise MST 01–10 classification from ITA alone.
  ITA will remain a continuous numerical input to the decision-tree correction
  model together with facial-region color statistics.

- MST use:
  MST labels will be interpreted primarily through light (MST 01–03), medium
  (MST 04–07), and dark (MST 08–10) groups for distortion-severity planning,
  evaluation, fairness reporting, and expert Mean Opinion Score summaries.

- Calibration condition:
  The diagnostic analysis confirmed that poor lighting substantially changes
  image-derived ITA values. Calibration findings are therefore interpreted as
  exploratory and conditional on the image quality and lighting represented
  in the reviewed dataset.

- Limitation:
  ITA derived from ordinary processed smartphone photos does not provide
  sufficiently stable separation for exact ten-level MST prediction under
  varied lighting, pose, subject, and image-processing conditions.

- Impact:
  MST-E remains calibration/evaluation-only. FairFace and SCIN remain the
  training sources for the correction model.

  ### 2026-10-11 – Broad MST grouping selected

- Input:
  The manually reviewed, conservative, well-lit MST-E calibration subset
  containing 245 valid Skin Mask V2 outputs.

- Broad groups:
  - Light: official MST 01–03
  - Medium: official MST 04–07
  - Dark: official MST 08–10

- Results:
  - Light: n = 84, median ITA = 8.57°
  - Medium: n = 109, median ITA = -15.66°
  - Dark: n = 52, median ITA = -47.62°

- Separation:
  The average adjacent-pair common-language effect-size/AUC was 0.747 for
  the three broad groups, compared with 0.594 for the individual ten MST
  labels. Broad groups therefore showed better separation.

- Decision:
  The system will not claim precise MST 01–10 prediction from ITA alone.
  ITA will remain a continuous input feature to the correction model.
  Light, medium, and dark MST groups will be used for synthetic-distortion
  severity planning, fairness-stratified evaluation, and expert MOS reporting.

- Limitation:
  Broad groups remain partially overlapping because image-derived ITA is
  affected by lighting, pose, image processing, and skin-mask quality.
  The grouping is an exploratory interpretation framework, not a clinical,
  racial, ethnic, or permanent classification.

  ### 2026-10-15 – SCIN subset suitability review

- Selection:
  184 candidate images selected using official SCIN eMST metadata.

- Finding:
  Manual inspection found only one image containing a visible face.
  Most selected images depicted non-facial body regions or close-up skin
  conditions.

- Interpretation:
  Sampling by eMST alone did not produce a usable facial-image subset.
  These images are unsuitable for the current facial-only correction pipeline.

- Decision:
  Pause SCIN processing. Continue technical development using FairFace while
  consulting the adviser about SCIN's role in the final study.

- Scope:
  The application remains restricted to facial skin-tone correction.

### 2026-10-23 - Proposal alignment checkpoint

- Compared the original proposal with the Python prototype; retained scope is
  distinct from experimental policies and incomplete requirements.
- Record: [thesis-method-alignment.md](thesis-method-alignment.md). Consult and
  update it when preparing future thesis edits; it is not an approved amendment.
- Resolve masking, MST mapping, dataset roles, distortion recipe and final
  split/tuning protocol before expanded training or replacement-model selection.
- Existing prototype/data remain preserved. No new model fitted or policy adopted.


## 2026-10-23 - Method recommendations and local evidence

- Saved docs/method-decisions-2026-10-23.md; recommendations remain separate
  from approved methodology. Mapping cannot be treated as operational.
- Script 48 audited all 30 saved training dimensions: all 224x224, not 256x256.
- SCIN metadata: 737 head/neck cases; 368 have at-distance image candidates.
  No candidate image accepted, downloaded or added to training.
- Recorded YuNet detector substitution and recommended isolated 256x256
  preprocessing comparison before final feature/pair regeneration.
- Audit completed successfully, inputs hashed; Markdown links checked.
  No learner refitted, source partition changed or proposal rewritten.


## 2026-10-23 - Completed square preprocessing and local SCIN check

- Script 49 compared eight existing sources at native224 and explicit256
  before detection; all16 branches succeeded, native features exactly match.
- ITA changes -0.276 to +3.862 degrees; mask IoU0.908-0.978 is agreement
  only, not segmentation accuracy. All eight boards inspected by Codex.
- SCIN368 metadata candidates:9 available locally, all9 zero face detections;
  previews inspected, none admitted. Other359 untested, no downloads.
- Preserved first partial run with NumPy coordinate serialization failure;
  corrected integer conversion and separate completed run recorded.
- Verified masks/dimensions/crop bounds,baseline equality,input hashes and links.
  Existing447 tests passed. No refit, runtime-default change or partition change.
- Results:docs/square-preprocessing-results.md; completed evidence and boards
  outputs/square_preprocessing_complete_v1/. Next: distorted-input robustness
  check before separately versioned256 training data; MST remains unresolved.


## 2026-10-23 - Distorted-input square preprocessing robustness

- Script50 checked all38 existing attempts,76 native/square branches.
  Train30,dev3,stress4 all remain successful;22454/color remains below1000
  skin pixels(231 native,387 square). No new failures or recovered exclusions.
- Native successful Lab/ITA matches stored rounding tolerance0.00011.
  Largest ITA shift+8.0011deg source19/color; agreementIoU0.6882-0.9784.
- Codex inspected19,22454,12288,62331 boards; fragmentation persists.
  Success flags do not establish mask quality or training suitability.
- Verified76 mask shapes/counts/crop bounds,38 outcomes,stress separation
  and unchanged input/model/table hashes;447 existing tests passed.
- No refit,regeneration,label/partition change or runtime policy change.
  Resize-after-distortion check is not a resize-before-generation dataset.
- Results:docs/square-distorted-input-results.md;outputs/square_distorted_inputs_v1/.
  Next:separate256 development generation with clipping/quality rechecks;
  final MST/SCIN/method issues remain unresolved.


## 2026-10-23 - Fresh square256 development dataset

- Scripts51/52 built and verified38 attempts from freshly resized clean sources
  and recomputed generation/input masks, including optional material hair veto
  support without invoking correction learner.30train candidates,3dev,4stress,
  1excluded; zero routing changes. Training has zero clipping; stress2239pixels.
- Known-inverse quantized reconstruction max3channel levels on unclipped pairs.
  Excluded22454/color392pixels; failure features blank, support unavailable.
- Verified saved recipe/pixels,features,targets,seven source folds and original
  hashes.447 tests passed. All8boards visually inspected by Codex.
- Separate mask_quality_assessment flags22454dark,12288color,62331color,19color.
  No human labels altered and no automatic cohort deletion/retraining.
- New table version controlled_square256_v1; old224 tables/model/runtime intact.
  Dataset technically generated, not cleared for retraining or final thesis.
- Results docs/square-development-dataset.md; next resolve mask-quality rule
  and flagged cases while retaining unresolved MST/SCIN/method requirements.


## 2026-10-23 - Consistent square mask-quality screening

- Frozen exploratory whole/quadrant retention rule before scoring all38pairs:
  min100regional pixels,estimation>=50%,correction>=80%; prior visual flags
  also hold. Designed after development inspection, not a validated cutoff.
-22 screen-pass training candidates from6sources;8held in separate manifests.
  Original30 rows exactly partitioned without modification; no final-cohort claim.
- Holds:12288dark/color/identity/mild,22211dark/color,22454dark,62331color.
  Source12288 has contaminated generation support; hair removal must not be undone.
  Source19color remains dev-only despite flag; all stress/exclusions retained.
- Saved raw HSV/YCrCb rejection counts; no threshold changes or forced mask fill.
- Verified exact disjoint partition,six source folds,original hashes,doc links.
  Seven meaningful tests added;454full-suite tests passed. No learner fitted.
- Artifacts docs/square-mask-quality-screen.md;outputs/square_mask_quality_v1/;
  data/manifests/square_mask_quality_v1/. Selection favors pipeline robustness
  and must be disclosed; final eligibility/MST/method questions remain unresolved.


## 2026-10-23 - Source hair contamination removal experiment

- Script54 applied existing hair veto to clean generation support for all8
  sources/38attempts, no thresholds widened, no estimation algorithm change.
- Source12288 removes2524predicted-hair pixels. Training screen22->25, but
  all3new passes already pass using old masks against cleaned denominator.
  Identity input/estimation/correction unchanged: not segmentation improvement.
-5mask-loss cases remain held:12288color,22211dark/color,22454dark,62331color.
  Three reference-related holds are candidate-only; old22/8 manifests unchanged.
- Script55 exact24clean labeled pixels:11/12skin retained generation before/after,
  hair3->1/4,paint0/3both,other0/5both. Existing clean correction12skin,1hair,
  0paint. No new shifted-output or universal material-protection claim.
- Independently checked8removal subsets/38saved recipes/clipping and hashes;
 454tests passed. Source overlay all8 and12288pair board visually inspected.
- Artifacts docs/hair-clean-generation-results.md,outputs/hair_clean_generation_v1/.
  No model fit,proposal change,human relabel,training promotion or runtime adoption.


## 2026-10-23 - Fixed YCrCb-only estimation ablation

- Script56 compared all38 hair-clean square inputs using paired face geometry,
  exclusions,morphology,largest component and unchanged material/hair correction.
  Only removed HSV intersection; no tuning,learner fit or runtime adoption.
- Coverage screen25->27/30;22211dark and62331color recover experimentally.
 12288color,22211color,22454dark still fail. Historical excluded row not promoted.
- Original24point clean/global-color probes96observations,allavailable:
  clean both12skin/1hair/0paint/0other;shift baseline9skin,candidate12skin,
  both0hair/paint/other. Global probes differ from masked-generation data.
- Visual4source boards show added support toward surroundings; coverage alone
  cannot approve candidate. Outside-generation pixels reported,not truefalsepositives.
- Verified152saved masks/counts,baseline exactreproduction and input hashes.
 454tests passed. Original22/8manifests,model and humanlabels unchanged.
- Results docs/ycrcb-estimation-ablation.md;outputs/ycrcb_estimation_ablation_v1/.
  Next focused new-region material/boundary review; no automatic adoption.


## 2026-10-23 - Review YCrCb added correction regions

- Script57 prepared all38 exact added/removed masks,component boxes/interior
  points and eight source boards,without inference or original-mask edits.
- Codex inspected all38 rows: facial recovery mixed with yellow clothing12288,
  collar/shoulder22211,neck/collar62331,and other border/peri-eye uncertainty.
  Source-level observations are not pixel annotations or human review labels.
- Across repeated variants103581added/2removed pixels; not truefalsepositive
  counts. Preserve prior24point regression limits and remaining hair error.
- Candidate not integrated,noheld promotion,nomodel fit. Next experiment:
  input-derived facial boundary with both skin-loss and spill regression checks;
  remember earlier outline method lost forehead. No boundary fix in this step.
- Verified76saved change masks,component sums,mask algebra,38case coverage,
  unchanged hashes and doc links. Production unchanged; previous454tests result
  retained,not rerun for read-only review outputs.
- Artifacts docs/added-correction-region-review.md,
  outputs/added_correction_region_review_v1/visual_findings.json and boards.


## 2026-10-23 - Correction-only lower-face boundary experiment

- Script58 applied fixed landmark168 split/oval below split,upperband unchanged,
  min75%retention guard. Existing estimator/features/targets/cohort/model intact.
-38/38 square masks available,min87.61% retained. All8boards inspected:
  clothing/collar spill reduced but sideface/jaw skin also trimmed. Not adopted.
-48selected clean/globalshift observations unchanged:12skin,0paint/other each,
  hair1clean/0shift. These points do not cover every removed facial edge.
-83184native224 clean/shift sentinel:fulloval6.63%/6.13%;lower rule would
  retain10.26%/10.64%;both explicitly rejected,not repaired or silentlyfallback.
-103715removed pixels over repeated variants,87884inside/15831outside
  generationregion; not annotated falsepositive counts. Screen27->19training
  passes,reference contamination and edge loss disclosed. No eligibility changes.
-Verified38subsets/upperbands,48point outcomes,sentinel rejects,and hashes.
  Six tests added;460fullsuite passed. No model fit or runtime adoption.
-Results docs/lower-face-boundary-results.md,outputs/lower_face_boundary_v1/.
  Next distinct hypothesis:restrict onlyYCrCb additions,preserve original support;
  existing baseline material errors remain explicit.


## 2026-10-23 - Additions-only correction boundary

- Script59 preserves originalHSV/YCrCb correction support and unions only
  lower-boundary-checkedYCrCb proposal. Same75%proposal guard BEFOREunion.
-38/38masks available;0baseline pixels lost;84332additions retained,19249
  blocked(not annotatednon-skin). Screening27/30vs19priorfullrestriction.
-48point probes available:12skin/0paint/0other eachvariant,hair1clean/0shift.
  Historical83184rejects linked as priorcontrols,not new inference. Four tests
  cover invalidgeometryhiddenbyunion,basepreservation,holes and new-onlyspill.
- All8boards/38rows inspected:usefulrecovery without prior edge loss,but
  existing yellowclothing/neck/border spill remains byconstruction. Notintegrated.
- Verified38unions/subsets/accounting,48points,unchanged hashes;464tests passed.
  Originalruntime,features,22rowmanifest,humanlabels,model and partitions intact.
- Results docs/additions-only-boundary-results.md;outputs/additions_only_boundary_v1/.
  Next freeze maskcandidate and compare actual corrections with same baseline
  features/frozenparameters acrossmasks;exclude unavailablefeatures explicitly.


## 2026-10-23 - Corrected-output comparison at fixed parameters

- Script60 attempted38hair-clean square inputs:37success/1baseline-feature
  exclusion22454color;111correctedPNG and148metricrows. No hidden imputation.
- Recomputed4baselineHSV/YCrCb features,predicted once with original frozen
  tree,identical3parameters across original,unrestrictedYCb,additions masks.
  No oracle/reference features,YCbfeature substitution or fitting.
- Common-region DeltaE dev3/1source:input10.768,original7.061,additions6.690.
  Stress4input7.176,original13.753,additions13.754. Training-source30
  original6.320->6.006,not heldout. Outside error improves versus unrestricted
  but remains worse than original mask; no universal improvement claim.
- Identity7input0->7.415; mild7input2.739->7.463. Wrong parameters remain
  main failure; no claim unchanged source is calibrated true color.
- All8boards/37rows inspected:some color-shift patches improve,seams and
  overcorrection persist. No new labeled paint evaluation or expertMOS claim.
- Independently verified111PNGs against sameparameter formula,outsidemask
  invariance,baselinepixel preservation,38attempts/148metrics and hashes.
 464tests passed; model/runtime/cohort/reviewlabels unchanged.
- Results docs/corrected-mask-comparison-results.md;
  outputs/corrected_mask_comparison_v1/. Next freeze mask and plan source-grouped
  learning comparison with controls,retaining held cases and unresolvedmethod record.


## 2026-10-23 - User requests face and visible neck correction

- User explicitly wants selectedperson neck corrected along withface. Recorded
  authorized development direction in docs/face-and-neck-correction-requirement.md
  and implementationplan; not a formally amended thesis or completedfeature.
- Keep faceITA measurement/current4features separate fromfullimage face+neck
  correction support. No neck skin means explicit faceonly behavior. No blind
  facebox expansion or genericbody-skin selection ofclothing/arms/otherpeople.
- Existing lowerjaw restriction is historicalfaceonly,not final neck boundary.
  Reassess actualneckskin as validtarget separately fromunwantedcollar/clothing;
  oldfacialgeneration/error scores do not validate neck. Preserve historicalnotes.
- Prioritize parameterovercorrection before expandingcorrection area,then
  version neckgeometry/support and widerframe cases with separate neckmetrics.
- Proposal PDF13/printed6 explicitly facialonly; scopeexpansion saved for
  laterthesisedits. No PDF/runtime/model/data change; docs links verified.


## 2026-10-24 - Fixed source-held-out correction-control training

- Scripts61/62 reused frozen22screen IDs/6sources,recomputed original4features
  on hair-clean256 inputs,fixed additions mask,unclipped known inverse targets.
  Original10types versus22with12controls; depth3seed42,6sourcefolds each.
-12fold models saved only outputs;66predictions(44learned+22no-correction).
  No held8,externaldev,stress or reservedtest fitted/scored; no runtime replacement.
- MeanDeltaE no-correction5.156,olderrecipe9.512,controls6.916;equal-source
 4.771/9.120/6.828. Controlshelpbutstillnotreliable,no generalizationclaim.
- Identity6mean6.767(all6worsen),mild6mean4.956(vs2.818input;2worsen).
  Controls beatsinput on2/6source means. No claimed overcorrectionfix.
- Script63 traced12controls to actualtrainingleafmeans without heldsource.
  Identity51739/75027routed darkinverse;22454identitycolorinverse.
- All6boards/22OOFrows visually inspected. Verifiedsource/duplicate disjointness,
  exactsavedmodel prediction replay,schema,targets,screenIDs and originalhashes.
 464tests passed after61/62;63read-only leaf checks passed.
- Results docs/correction-controls-sourcecv-results.md;
  outputs/correction_controls_sourcecv_v1/. Next source/featurecoverage audit
  and varied suitable developmentdata plan;no arbitraryclamps or reviewedIDrules.
  Neckrequirement retained,but no expansion of these unreliable settings yet.


## 2026-10-24 - Training-source coverage and bounded18source screen

- Script64 audited current22pairs/6sources and trainingpool450:316unreviewed,
 78automaticfail,26provisional,22review/geometryexcluded,8uncertaingeometry.
-284unreviewed TRAINsuccess sources had no recorded prior developmentexposure.
  Selected18 by six native-photo-Lrankbins/seed42hash,not MST or severitylabels.
  Appended18IDs to development_exposure_additions.jsonl BEFOREprocessing.
-17numericalsuccess/1landmarkfailure22905 at256. Script65/Codex inspectedall18
  on6sheets:20555promisingfollowup only,other17held. Zero trainingadmissions,
  humanpendinglabels unchanged; masksuccess is not sourceacceptance.
-5/6held identitycontrols inside each feature marginalrange;only6236Loutside.
  Severe51739/75027/22454errors thusnot just rangeextrapolation. Jointcoverage
  and parameteridentifiability unproven. No confidence/skin-tone inference.
- Verified18uniqueTRAIN IDs/maskcounts/subsets,exposureledger,originalhashes
  and reportlinks. FeaturePNG/SVG generated,PNGvisually checked;464tests passed.
  No reservedtest imageprocessed,no correctionlearner fitting or runtimechange.
- Results docs/training-coverage-audit.md;outputs/training_coverage_audit_v1/;
  data/manifests/training_coverage_audit_v1/candidate_disposition.json.
  Next20555fixedvariant suitabilitycheck and bounded18fromremaining266;
  no adding sources merely to improve scores. Neckcoverage still untested.


## 2026-10-24 -20555fixedvariants and second18source screen

- Script66 generated20555fivefixed variants:allnumericalsuccess,0clipping,
  experimental support available. Fourpass retention; colorholds at1788skin
  pixels/4.57%generationretention despite86.0%correctioncoverage. No feature
  substitution,admission or correction-model inference/fitting.
- Next18TRAIN sources chosen from266remaining by same6native-Lrankbins/
  seed42hash,excluding earlier18IDs. Exposure ledger appended BEFOREprocessing.
  All18numericalsuccess;Codex inspectedall6sheets and20555fivevariant board.
-14272,39108,3705,84897promisingfollowup only,14held;zero admissions.
  Originalhumanpendinglabels,22rowcohort,model,partitions unchanged.
- Bothbatches36newdevelopmentexposures(35success/1landmarkfail),not population
  rate,not MSTlabeling,and no reservedtest/externaldev imagery inspected.
- Verified5savedrecipes/inversetargets/clipping,18maskcounts/subsets,ledger
  disjointness,originalhashes and doclinks.464tests passed.
- Results docs/source-screening-followup.md,outputs/source_screening_followup_v1/,
  data/manifests/source_screening_followup_v1/candidate_disposition.json.
  Nextfixedvariants on4candidates and measurementconsistency comparison;
  moredata alone cannot repair severeHSVcolor-shift measurementloss.
  Neckrequirement preserved,no neckcorrectionimplemented.


## 2026-10-24 - Fourcandidate20variant estimator reliability check

- Script67 checked14272,3705,39108,84897 on samefivefixedsettings.
 20geometry/feature/support successes,40pairedbaseline/YCrCb measurements.
  No cleanfeature fallback,threshold tuning,learnerprediction/fitting or admission.
- Fixedbaseline screen:15pendingpasses,3qualityholds,2clippedstress.
 14272all5passes;84897fourunclippedpasses+brightstress5pixels.
 3705color baseline19.5%generationretention,YCb61.7%,support78.0%;stillholds.
 39108dark/color lower-left correctionholds,brightstress508pixels;source
  boundary nearjewelry/collar needsreview,not proofneckskin should beexcluded.
- Codex inspectedall4boards/20rows;originalhumanlabels remainpending.
  Candidateexpansion proposal14272five+84897four=9pairs/twosources,not yet
  consolidated/admitted or finalthesisapproved. Preserveall20attempts.
- Verified20savedrecipes/inversetargets/clipping,40stats/retention records,
  existingexposure and model/source/review hashes;464tests passed.
- Artifacts docs/candidate-variant-checks.md,outputs/candidate_variants_v1/,
  data/manifests/candidate_variants_v1/screen_disposition.json.
  Next separatelyversioned9pair expansion with baselinefeatures/sourcegroups;
  no mixtureofYCbfeatures,stresspromotion or neckcorrectionclaim.


## 2026-10-24 - Stage nine proposed development pairs beside frozen22

- Script68 stagedcontrolled_expansion31_v1:old22fieldvalues unchanged,
 14272five+84897fourunclipped proposedrows;31pairs/8sourcegroups.
  BaselineHSV/YCrCb4features recomputed,knowninverse3targets validated.
- References savedcandidate67inputs/masks,no regenerateddata or YCrCbfeature
  mixing. Raw master/humanpending/finaltrainingReadyFalse statuses preserved.
- All20candidateattempts recorded:9proposed,9heldnotstaged,2stressnotstaged.
  Original8held and20555color remainoutside;no reservedtest/externaldev touched.
-8sourcefold plans;fixednextcompare original22subsetvs expanded31,depth3seed42,
  sameheldsourceprobes,original/new probe reports,controls/nocorrectionbaseline.
  Plansonly,0fits,no modelpromotion or runnerredirect.
- Duplicate recheck8decoded hashes/dHash<=4 no candidate links;identityunverified.
  Verified31x4features/31x3targets,all31measurements,new9recipe/clippingchecks,
  22exactoldrows,foldcoverage,helddisjointness,originalhashes anddoclinks.
 464tests passed. Neckrequirement/methoddistinctions unchanged.
- Artifacts docs/development-expansion31-stage.md,
  data/manifests/controlled_expansion31_v1/,outputs/controlled_expansion31_v1/.


## 24 October 2026: fixed eight-source expansion comparison

Executed script69 on staged31 with original22 versus expanded31 and no-correction baselines. Sixteen source-disjoint fold models; 93 predictions; saved-model replay and unchanged-input hashes verified. Mean reconstruction deltaE: no correction5.460, original6.601, expanded7.804; shared22 original6.916 versus expanded8.165; new9 original5.831 versus expanded6.924. Dark probes improved but mild and unchanged controls still regress. All31 image comparisons visually inspected. 464 tests passed. No runtime promotion, external/reserved evaluation, neck implementation or proposal amendment. Next recommended diagnosis: control-regression leaf/feature-target conflicts. See [comparison](development-expansion-comparison.md).


## 24 October 2026: control-error branch diagnosis

Script70 replayed32 unchanged/mild predictions across16 existing fold models, checked disjoint source/duplicate groups, exact predictions, leaf-target means and unchanged hashes. Both models harm8/8 unchanged probes; mild failures rise2/8 to5/8;8/16 controls worsen versus original. Wrong-distortion pure leaves and mixed-target leaves coexist. Diagnostic training-fold-scaled nearest examples do not prove physical ambiguity. No new fitting or runtime change. Recommend one fixed depth3 versus unrestricted-capacity comparison, same31/eight folds, report training and held-source controls, no depth search or automatic promotion. Neck/MST/proposal distinctions unchanged. See [diagnosis](expansion-control-diagnosis.md).

Verification after the diagnostic: **464 tests passed**.


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


### 2026-10-26 - Anatomical/contour candidates remain experimental

Completed the [fixed ablation](anatomical-contour-results.md) across32savedinputs,ninegeneration sources andnativehair/paintregressions. Wider eye/brow exclusions reduce manual-exclusion overlap but remove valid skin. Constrained expansion does not repair the annotated cheek and is unavailable on paint cases. Do not adopt either candidate,replace training artifacts or refit. Preserve previous review decisions and holds. Next fixed diagnostic should examine landmark inference framing before further margin/color tuning. This is not an approved thesis-method amendment.


### 2026-10-26 - Dense parser is an anatomical candidate, not a final skin mask

The [fixed face-parser experiment](dense-face-parser-results.md) shows a new contour representation can include the annotated cheek, and removal-only parsing can remove a prior hair point. Paint area remains selected and one vetoed case fails the existing retention screen. Keep D/V diagnostic; preserve original masks, inputs, human decisions, technical holds and folds. Do not regenerate or train from these outputs. Any expansion needs a separately fixed combined anatomical/material-protection comparison and explicit thesis/device-cost documentation.


### 2026-10-26 - Combined parser masks retain a technical paint-protection hold

The user authorized autonomous recommended development. Completed fixed A/F/C masks and one fixed C2 material-boundary guard across143 known cases, with independent replay and481passing tests. C/C2 include the missed cheek and improve some contamination witnesses, but C2 adds113/69 protected painted pixels in clean/shift correction and loses labeled skin. Preserve the useful parser candidate without adopting it, regenerating training inputs or fitting a model. All prior reviews/holds/folds remain intact. The [readiness report](../outputs/parser_material_boundary_v1/readiness.json) records policy-level technical holds for the current32 pairs; these are not reversals of their original human decisions. See [results](parser-material-combination-results.md).

### 2026-10-26 - Broader protection test does not unlock regeneration

Inventoried114known TRAIN sources and froze17frames before51global diagnostic probes. Forty-eight available probes produce448candidate masks; three seed failures remain unavailable. Provisional Codex makeup/mark interiors are separately labeled, with no changes to original user references/reviews. C2still selects851/880/479user-paint pixels clean/dark/color and new cosmetic/mark interior pixels. Numerical validity does not overcome failed protection/coverage gates. Preserve this experimental candidate, all prior holds and the revised unexecuted training plan. No mask adoption, training-pair regeneration, admission or fitting. Next material-specific design must declare suitable references/evaluation before further candidates; no threshold sweep or application-user annotation requirement follows. [Results and thesis distinctions](paint-protection-validation-results.md); [machine-readable readiness](../outputs/paint_protection_validation_v1/readiness.json). Independent replay and481tests pass.

### 2026-10-27 - Preserve original references and flag material-boundary ambiguity

Cached attribution shows seed overlap with protected labels and persistent feature/material-region selections. Scalar-distance witness pairs also reveal mixed-boundary uncertainty on visual inspection; their saved label order is not proof of physical paint/skin inseparability. Keep exact original labels and historical scores, append the reference-quality caveat and require versioned actual adjudication before using them as material ground truth. No automatic relabeling, cutoff sweep, new mask adoption, training-pair regeneration or fitting. [Checkpoint and next reference/evaluation requirements](material-protection-design-checkpoint.md). Previous holds/approvals/folds remain;481tests pass.

### 2026-10-27 - Investigate CPM pattern supervision without adopting transfer or native mask assumptions

Retain CPM pattern branch as a feasibility lead after primary-source review. Its checkpoint was downloaded within a fixed bound and statically inspected without model execution; it has actual synthetic pattern-mask supervision. UV input/native restoration, inconsistent source preprocessing/cutoff paths and legacy runtime/export parity must be resolved before a prospective image test. Do not resize portrait masks as if UV coordinates were native, pick a cutoff on known paint references, run makeup removal as correction truth or bypass material-reference adjudication. Preserve environment, labels/reviews/folds and training holds. [Feasibility](cpm-pattern-feasibility.md); [readiness](../outputs/cpm_pattern_preflight_v1/readiness.json).491tests pass; no image inference/regeneration/admission/fitting.

### 2026-10-27 - User defers CPM and resumes the core thesis pipeline

The user explicitly sets CPM aside and keeps paint/makeup handling as a limitation. This supersedes CPM's prior next-work recommendation; preserve its artifacts as historical evidence. Do not continue its conversion/UV/material-model work. Resume bounded core ITA/MST/decision-tree/on-device implementation without silently clearing source holds or inventing an operational MST rule. Implemented [portable frozen-tree inference](core-tree-portability-results.md): exact parity,2556-byte JSON and a package-free evaluator,519passing tests. No retraining/runtime adoption. The original mask/decision-tree quality limitations and unfinished MST, face/neck, finaldata/splits/evaluation/expertMOS/Android requirements remain.

### 2026-10-27 - Core software availability is separate from MST and correction quality

Added [unified input-only core runner](core-pipeline-check-results.md) with stage-level reports and the frozen portable tree.37/38known attempts available; original measurement failure retained. Always mark operational MST unavailable/null and proposal incomplete; the existing continuous-feature development regressor can produce an output without pretending to implement MST-conditioned correction. The frozen model worsens7/7unchanged and4/7mild controls, so integration success does not warrant final learner adoption. No parameter/mask edits, cutoff tuning, source promotion, training, split/review changes or CPM resumption.537tests and independent replays pass. Continue core control-aware/source-grouped model-quality work while preserving mapping/data limitations.

### 2026-10-27 - Control additions improve the old recipe but do not justify replacement

Executed the user's authorized fixed comparison on current core native224data, with22eligible IDs and8held diagnostics. Primary source-held-out mean errors5.129no correction,9.389older recipe and6.865with controls; revised still harms6/6unchanged and2/6mild probes. The frozen current model is retained only as a separately labeled seen-source comparator. Save14experimental fold trees and the negative result; no runtime replacement, held-row promotion, final production fit or follow-up cutoff/depth/feature sweep. All original decisions/folds/artifacts preserved;546tests pass. [Results and next rationale requirement](core-control-comparison-results.md); [declared gate outcome](../outputs/core_control_comparison_v1/readiness.json). CPM remains deferred; operational MST and final-study requirements remain unresolved.


### 2026-10-28 - Preserve diagnostic evidence; investigate coverage before more fitting

Completed the [saved-fold diagnostic](core-feature-conflict-results.md):11/12primary controls have nearer conflicting targets under standardized Lab distance, while one failed identity control has matching nearest support but routes elsewhere. Five harmful controls have no matching target in their leaf. No exact feature collisions; metric sensitivity and sparse support prevent an impossibility claim. Keep the current model and all masks/reviews/holds/folds unchanged. Do not infer a new no-op cutoff, guessed MST label or feature removal from this audit. Audit existing reviewed source/reference suitability and independent coverage before a separately declared data stage. No new fit or source admission;555tests and independent arithmetic replay pass. CPM remains deferred and paint/makeup protection a limitation.


### 2026-10-28 - Existing source readiness reconciled; portable thesis checkpoint built

Audited114previously exposed TRAIN sources and75recorded pair attempts:35accept,11reject,2uncertain,27pending;10accepted sources,2complete-five. Proposed32regenerated candidates across9sources retain unresolved coverage and differ from core native224/four-feature processing. All9folds preserve exact pair/source/duplicate-group separation; no new core admission is established. Independent replay checks75decisions/notes/statuses,114source rows,32IDs and9folds with unchanged original hashes. Scripts125/126; [results](core-source-readiness-results.md). No raw images opened, inference, fits, masks, reviews or exposure changes.

Built script127 to produce an image-free, offline [thesis checkpoint](../outputs/thesis_checkpoint_v1/index.html) and machine-readable provenance from four hash-verified saved reports. It separates37/38software availability from inadequate correction quality and explicitly unfinished MST/neck/finaldata/evaluation/Android. This packaging does not rerun tests/inference or imply final validation. Preserve current baseline; stop serial small-cohort tuning. Deadline requested from user to prioritize actual submission requirements. CPM deferred; no commit.


### 2026-10-28 - November6 delivery cutoff and Android tree port started

User confirmed all three deliverables (Python, Android, thesis results) beforeNovember7. AdoptNovember6working cutoff; [delivery plan](deadline-delivery-plan.md) records targets and evidence gates. This explicitly authorizes Android work. Existing Compose scaffold was present despite stale AGENTS state; its image repository is still a pass-through stub, not integrated inference.

Gradle8.9 downloaded into ignored workspace cache after restricted socket failure; retry succeeded. Local JDK21.0.8 runs it. No Android SDK found in checked common locations; user asked for existing SDK/test phone. Added immutable platform-independent Java tree inference and strict Android JSON asset loader, packaged byte-identical frozen development JSON. Script128 compiles Java targeting11 and executes44vectors (23saved,12boundaries,9double/float32rounding) with exact Python leaf/parameter parity;15invalid cases rejected, state immutability checked. Android Kotlin loader/APK/device not compiled/tested yet. [JVM verification](../outputs/android_tree_parity_v1/verification.json).

No model fit/replacement, data admission, mask/review/fold changes, guessed MST or CPM work. Delivery work must report unresolved MST, correction harm, neck, finaldata/reference/evaluation and actual expert MOS honestly. Next Android gate is SDK/build and real image processing; JVM parity alone does not complete Android integration. Not committed.


### 2026-10-28 - Workspace Android SDK and first verified debug APK

User has a phone and no Studio/SDK. Installed official command-line tools19.0, platform35, build-tools34.0.0 and platform-tools37.0.1 under ignored outputs/android_toolchain; published archive checksum verified and package revisions recorded. Standard SDK installation licenses handled by SDK Manager. Gradle configuration passes; subsequent full build passes51tasks. Initial AAR-task failure is preserved with unknown exact cause after PowerShell stderr interrupted diagnostics; build script fixed to preserve output and check exit status. No dependency-version changes.

APK10,770,836bytes SHA256`5e7df735dae338a252eebd6aa9011e27c2fa1c7fc94d28cc6ac732b7ca050d4d`; development signature verifies and tree asset exactly matches frozen export.14actual Android-module unit tests pass; lint0errors/27warnings retained. Scripts129?131 reproduce setup/build/artifact checks. [Build results and limits](android-build-results.md), [verification](../outputs/android_build_check_v1/verification.json), [phone instructions](android-device-testing.md). No phone install/launch or hardware timing; image repository remains pass-through and full Android correction is not integrated.

AGENTS Android-state sentence corrected to reflect existing scaffold and explicit user authorization. Original model/data/masks/reviews/folds unchanged; no new fitting/admission, guessed MST or CPM work. Next is actual on-device image pipeline integration, followed by real phone checks; expert MOS scheduling remains external. Not committed.


### 2026-10-28 - Control-aware development candidate built and quality-held

User prioritized Python model completion and paused Android. Frozen protocol before one full22pair/six-source development fit: existing native224four-feature/depth3/seed42/leaf1/unweighted recipe,8held IDs excluded, no new cohort/threshold/feature/mask/source. Added strict build-contract and activation-evidence validation;19newtests. Exported2129-byte joblib SHA256`28c49d4386f2d0b2926593432735cbc195964219625ed7ed3f4c7cff5a64098e` and3501-byte portableJSON; all30probes/20boundaries and isolated package-free inference match. Existing source-held-out recipe evidence5.129no correction/6.865candidate,6/6identity and2/6mild harm, keeps status held_quality_failure. No active model/config/Android replacement.

Separately declared fixed replay of38known attempts:37outputs/1original failure. All-row22seen-source mean5.129to2.807 is training reconstruction, not generalization; all6fitted unchanged controls still altered. External3/one exposed source10.666to10.913 (original runtime7.609); clipped4stress7.227to11.311; held8diagnostics8.866to7.524. No new search/selection/fit follows. All8boards inspected; legacy boundary/coverage and wrong-tone defects retained.

Independent arithmetic verifies22targets,6leaf means, recipe gate from individual held-source predictions and37pixel/metric replays; outside-mask pixels and original artifact hashes unchanged.574tests passed in25.37s. Scripts134?136; [build/results and thesis limitations](control-aware-model-build-results.md), [gallery](../outputs/control_aware_candidate_replay_v1/review.html), [verification](../outputs/control_aware_candidate_replay_v1/verification.json). Model construction is implemented, not final correction quality. MST/method guidance requested; original paper baseline remains until an actual decision. Expanded32notadmitted; CPM deferred; no commit.


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

### 2026-10-28 - Preserve Table 2 clipping and qualify recovery

The authorized full Table 2 operator clips all18known-source feasibility probes;17measure successfully. Do not tune distortion severity or override current unclipped-training eligibility to obtain a fit-ready cohort. Fixed-reference-mask evaluation exposes lost mask coverage and nonzero oracle residuals; oracle fitting is not learned performance. Prepared a separately versioned clipping-stress experiment design for an explicit methodological decision, retaining all prior mask/source holds. [Results](table2-known-source-feasibility-results.md), [proposed change](table2-clipping-stress-design.md). No correction-tree fitting or runtime adoption.
