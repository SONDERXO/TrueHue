# One pretrained exposure-correction alternative: scope/backend decision needed

15 November2026. After separatecamera-inspired1NN AND paired-referenceprototype tests failedcolour/preservation anduserreported noadditionalportraits, reviewed ONE different source of learned correction knowledge. No more small-classifier/source/conditionqueue is selected. PriorMSECmention onNov9was a datasetlead; this is a distinct pretrainedMODEL inference/scope review, no dataset acquisition or prior-photo re-review.

## Primary evidence and current practical state

[Afifi etal.,CVPR2021](https://openaccess.thecvf.com/content/CVPR2021/html/Afifi_Learning_Multi-Scale_Photo_Exposure_Correction_CVPR_2021_paper.html) addresses bothunder/overexposure with a spatialnetwork separatingcolour/detail processing; publishedexposure dataset has over24000images. That is relevant to the pointwise/clipping and small-corpus limitations, NOT evidence of TrueHueportraitperformance, natural identitypreservation or darker-skinbiasreduction.

Pinned officialrepository:[mahmoudnafifi/Exposure_Correction commit9ce36271db133da208ee7e20f9e0f99fdef75b63](https://github.com/mahmoudnafifi/Exposure_Correction/tree/9ce36271db133da208ee7e20f9e0f99fdef75b63).12primarysourcefiles+releasemetadata cached/text-hashed in `outputs/msec_pretrained_scope_review_v1`. Source was read, not imported/executed. Model listing advertises `models/model.mat`28167349bytes; listingGitblobSHA is saved, NOT a verifieddownloadSHA256. **No checkpointbytes or portraitdataset downloaded.** The officialrepo includes thecheckpoint directly, so no new collection is required merely to run the pretrainedbenchmark.

Official READMErequires MATLAB2019b+DeepLearningToolbox. CPUinference is explicitly implemented; GPUoptional. Fourpyramidlevels withcustomMATLABlayers and a dlnetworkobject are used. The256input author path resizes to512, usesS=[1,1,1,1], packedLaplacianinputtimes255, networkprediction/255, thenresizesback. Optionalhistogramadjustment/fusion defaultOFF and were notused forpaperresults. No tuningthoseoptions, spatialstrengthmaps or selectinganothercheckpoint follows automatically.

License file is CC-BY-NC-SA4.0; READMEstatesresearch/noncommercial. DatasetderivesfromMITAdobeFiveKandfollowsits terms. Retainauthornotices/citation/restrictions; no commercial/publicappapproval inferred andno dataset/training-image rights clearance or pretrainingoverlap claim. This is a source fact, not comprehensive legaladvice. Android/export/latency/memory are unverified, and noauthorPython/ONNX/TFLitepath was found in theinspectedinferencefiles. Do not substitute an unofficialport andclaimauthorparity.

Local `matlab`command was NOTfound throughPATH; neitherdefaultProgramFilesMATLABdirectory was found. This is a scopeddiscovery result, NOT proof the user hasnoother/university/onlineinstallation/license. MATLAB/DeepLearningToolboxavailability is unknownandneededfromuser. Noinstall/licensecheck/networkmodelscript run or MATLABprojectcreated.

## Concrete proposed assessment, pending user decision

Only if explicitly allowed AND supportedbackendavailable: one fixed officialcheckpoint, originalauthorCPUinference, S1/fusionOFF/ppOFF. RetainMITMSECnotices. Verify transferlimit/hash andexpectedmodelmetadata beforeinference; no trainingcode, datasetdownload, secondcheckpoint or portfallback. First generatedRGBarrays: finite/deterministicshape/output andrepeatbehavior; record identity changes, do notrequireexactneuralidentityunjustifiably. Preserveoriginals, versionedoutputs/refuseoverwrite/failureevidence.

Firstrealbenchmark would be FOURexistinginputs:29617under/32685over fromtheoldseveretask ANDsamepeople/roles fromnewcamera-inspiredtask. This is a smallfeasibilitycomparison, notmodelqualification or resumedoldtargetfits. WholeimageCNNoutput would be compositedthroughsameapprovedalpha/protection onto input, guaranteeingdeclaredoutside/protected pixelsunchanged. No newmasks/sourcephotos/reference-derivedinferenceinputs. Onlyinputpixels feednetwork; references used afterwards forcomparison. No newuserratingsbefore imagesarenotobviouslybad. IfvisiblyunacceptableSTOPfixedbenchmark, no scale/fusion/strength/rescue; ifpromising, require a separatelyfixedfullidentity+colour+exposurecomparison andhumanusefulness checks.

THISISAMAJORRESEARCHMETHODAMENDMENT: a pretrainedRGB-to-imageCNN replaces frozenReIQA+traditionalcontrolpredictor/globalrenderer. Earlieruserapprovalcoveredchangingfinalhead WHILEretainingfrozenfeatures, not silentlyreplacingthatpipeline. ITA/MST would initiallyremainmeasurement/evaluation components, NOT falselyclaimedCNNconditioning; a skin-tone-awareconditioningclaim would requireadditionalvalidateddesign. Identity/colouracceptances ofoldmodels do nottransfer. Papereditingremains paused and no adoption/rewrite requesteduntilworkingcandidate/evidenceexists.

Even successfulMSECexamples would NOTprovide independentMSTlabels/portraitcohort, proof of reduceddarker-skinbias, expertMOS, finalAndroidintegration or a justifiedFridaycompletionpromise. Goal remains useful exposureANDcolourrestoration/preservedcomplexion, not genericbeautification. If theuserkeepsthecurrentparametric/frozen-featuremethod scope orhasno backend, this alternative is not executable asproposed; do not quietlyreplaceit with anothermodelqueue. Need an explicit nextresource/scope decision rather than claim the model is finished.

## Current boundary

Onlypublicprimarysource/metadata+existingdocs andscopedbackenddiscovery in this review.0newweights/models/photos/inference/ratings/raworiginal/lockedCONTENTSOR MANIFESTS/runtimeAndroid/manuscript changes. Priorfailures remainclosed, allartifacts/manualears/ratings preserved/modelunfinished/paperpaused/workingFridayNov20before12Manila.
