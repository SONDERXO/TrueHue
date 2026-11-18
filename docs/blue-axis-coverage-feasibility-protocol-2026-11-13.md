# Fixed blue-axis coverage extension: preparation and first-fit design

13 November 2026. User authorized specifying the bounded blue-coverage test. **Design only. No new photo conditions/features, fits, predictions, masks or review task executed.** Current acceptableposthocdevelopmentrecipe and all11models/reviews remain frozen and unadopted. This is not an independenttone/finalvalidationplan.

## Distinct rationale and retained scope

Current281representation has actualrededit signal and acceptableexposeddevelopmentreview; separate40generatedblueprobes verify blueaxisresponse/inversealgebra. CurrentlearnedBcontrol is1everywhere because originaltargets areconstant. This supports testing whether this SAMEfixedrepresentation/predictorfamily can learn explicitvariablebluecontrols. Prior broadcolour/combinedexperiments existed and stayclosed; merely adding role names was not a sufficientrepair. This extension tests a newrepresentation under fixedadditionalcontrolcoverage, not a promise that morecopies/sources solvegeneralization. It changes the conditioncoverage, so results are not a causalablation of onefeature or a direct old/newSSEcomparison on differentrosters.

Retain originalphotographicrestoration versusuncorrected, inputITA/MST/traditional281features, oneordinarytree predictinggamma/red/blue, singlephoto, face/visible-neck/manualsupport, darker-skinpriority. Naturalcomplexion is not a correctionlabel. OfficialMSTlabels are not necessary to generate pairedcontrolledtargets, but this11sourceunlabelledcohort cannot establishdarker-skinbiasreduction or independenttonecoverage. IndependentSCIN/MST-Eeligibilityholds remain; no newdataadmission or reservedrolechange.

## Exact sources and conditions

Use ONLYthe11reviewedFFHQsourceIDs54632,39568,29617,16061,52445,32685,53146,48879,49131,59807,46795, in originalpreparationorder.29863remains excluded. No raworiginals. For newconditionpreparation, decode ONLYinput_rgb8 from the EXACT11boundidentitypaired_pixels.npzcontainers after path/hashchecks. Those identityarrays supply the photographicreference, not a newcapture or physicalcolourtruth. Fullcontainerhashing reads compressedarchivebytes but no reference/maskarray is decoded from it for this preparation.

Retain EXACT44existing identity/under/over/redcool inputs, targets and281float32features by savedmetadata/containerbindings; do not regenerate their pixels or silentlychange labels. For eachsource append:

| Newrole | Forwardoperation on RGB8/255 | Finalquantization | Nominalinversecontrols gamma/red/blue |
|---|---|---|---|
|blue_decrease|multiplyB by245/255, R/Gunchanged|clip0..1 thenround-to-even255|1,1,255/245|
|blue_increase|multiplyB by255/245, R/Gunchanged|clip0..1 thenround-to-even255|1,1,245/255|

Pureblueonly, fixedstrength. No newgamma+blue realconditions, severities, brightness/contrast/offsetTable2expansion or grid. Generatedcombinedprobes remain engineeringonly. These names describe channeloperations, not guaranteedperceivedwarm/cool. Nominalinverse valid beforeclip/quantization; do not claim perfectrecoverability. Keep ALL22newconditions including clippedcases, reporting total/clippedchannels, clippedpixels and eventualscoringregionclipping. No outcome-based pixel/conditionexclusion or inverseoptimizer.

Total66availableplannedconditions=11sources*6roles; proposedattemptledger72including all6excluded29863roles. Old48ledger unchanged; newledger records the extension separately. Any actualfeature/preparationfailure remains explicit and stops completeness; do not replace/drop sources or inventavailablecounts before processing.

## Matching feature and support contracts

For22newinputs recompute ALL16originalfeatures from each actualdistortedinput using the SAMEsavedmeasurementmask, compute_masked_lab_statistics/rounding/minimum1000, existing shared_core_mst mapping coefficients/contracthash, scene_features and green_distribution_features. Do NOTcopy cleanLab/ITA/MST/scenevalues, infer officialMST or refitlookup. Append unchanged6gapfeatures and259jointlogcolourfeatures, rounding tofloat32 in frozen281order. Bluechanges Lab/ITA/MST even whengreen samplesunchanged. Verify on the11identityinputs that recomputing thisfullpipeline reproduces savedcanonicalfeatures before accepting newconditionfeatures; mismatch stops, not an automaticcontractrepair.

Use sameboundselectedsupport as the currentreview:10exactreviewed+earbundles,59807exactapprovedmanualforehead/neck/microphone support, measurementbyteunchanged/protectionmanualremovalsretained. Newconditionmeasurement/support are samegeometrypropagations, explicitlyassisteddevelopment, not automaticnewparserproof. No newparserinference or maskgeneration. Forfeaturepreparation onlymeasurementmasks needdecode; correction/protection/alpha decode happens only in separatelyspecifiedlaterimageassessment. Bindingmetadata is allowed now; actualarrayaccess laterrequiresgeneratedengineering/readiness.

## Source roles and learning budget

Preserve11existingphotoheldfolds; eachwouldhave60fitting/6heldconditions, allvariants of a source together. Metadata binds all11folds now, but execution scope afterengineering is preparation66records THEN ONEfirstfold60row fit excluding16061. No heldpredictions/renders/scores/reviews in preparation/firstfit. Newfeaturecontainer can include exposedheldmetadata, but joinfilters fittingcaseIDs BEFORE feature/targetaccess. No pairedreference/source/roleoracle in X.

ONEordinaryaxisDecisionTreeRegressor: same281features/raw3positivecontrols/squared_error/best/depth4/seed42/minleaf1/minsplit2/allfeatures/nopruning/weights/scaling. Exactlyonefitcall, no restart/ensemble/grid/PCA/subset/depthchange. Newoutputdirectories refuse existing complete/partialattempts. Originalfirst40tree cannotbe reused as this60fitcandidate: it remains frozen, and no oldmodel is refitted/rescored/promoted.

## First-fit diagnostic and stop

Independentoptimizer-free verifier reconstructs60rows, allfeatures/targets/foldexclusions, exportnative/scalarroutes,31node/depth4bound and everyraw3controlleafmean. Report total/percontrol/perroleSSE, leafsourcecomposition, actualhistogramcoordinatesused, identitydeviations, blueleafrange and bothblue-rolemeanpredictions. Report original40subsetnewcandidatefittingerror alongside SAVEDfirst40report descriptively, without re-predicting the oldmodel or imposing an oldmodeluniversalwinnergate.

Bluelearningfittinggate:

1. Blueleafvalues are numericallynonconstant (range>1e-12).
2. NewcandidateblueSSE is strictlylower than the bestfittingconstantbluepredictor (meanofall60trainingblue targets), by>1e-12*max(1,constantSSE). Baseline is an analyticalconstant, not anotherfittedcorrectionmodel. This prevents calling a tinyuniformoffset from1 learnedconditionalbluecorrection.
3. Fittingmeanbluecontrol onblue_decreasecases>1+1e-12 and onblue_increasecases<1−1e-12. These are knowninverse directions atfitstage, not a runtimeflag/oracle or perceptualthreshold.

Invalidengineering or failure of anybluefittingcheck stops thisfixedfeasibilityroute without rescue. Passing supports only considering a distinctprospective11foldsourceheldcomparison; fittingcoverage alone does not demonstrate usablebluecorrection/retainedexposure/identitypreservation. If no occupancycoordinatesareused, disclose rather than claim the histogram suppliedthegain. Fixeddepthlimitscapacitybut281features/60rows/10sources still risk sourceoverfit.

## Engineering and later-stage boundary

Before actualpreparation/fitting, implement andgenerated-test one-shotgeneration/clipcounts/inverses/full281featureparity/frozenmapping/no source-labelleak, 44exactreuse, 22newrecords, first60join/portableexport/independentleafmeans/nooverwrite/noretry. BindQA/code/version/roster/support/mappinghashes. No engineeringfailure used to alter recipes/targets. This design currentlyNONEXECUTABLE.

Only if firstfitpasses can a laterexplicitcomparisonplan consider10remainingfits+EXACTnew60firstcandidateSHAreuse/allfitsverifiedbeforeheldscoring,66controlvectors/primaryrenders, numericalbenefit separatelyunder/over/redcool/blue_decrease/blue_increase and the revisedno-unwantedidentityrule. Numericalfailureendsbefore newvisualburden; identitiesfirstearlyunwantedstop. No66caseuserreview is launched or required now. Futurevisualreuse, if proposed to reduceburden, must be explicitlypredeclared and verify identicalinput/output/reference/support/viewingcontract; never copy oldratings to changedoutputs. No fullcomparison selectedby this specification.

Independenttonequalification/finalmodelselection/Table2bluecombined/severity/MOS/Android remain incomplete. No final24/olderlockedcontentor manifests, raworiginals, sourceretrieval/recruitment, runtimeAndroid/manuscript/dependencychanges/commits. Modelunfinished/paperpaused/November14targetatrisk/timeunspecified/no completionpromise. Approvedmanual59807/ears and allhistoricalartifacts retained.
