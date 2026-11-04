# Fixed brightness features on protected direct-gamma regression

30 October 2026. Test one representation hypothesis on the same approved
historical15-source/30-pair development cohort: six existing brightness
statistics may help distinguish unchanged darker faces from artificially
distorted inputs. Keep inputITA,experimentalMST,meanLab and all target values.
Do not add source IDs, reference statistics, severity labels or corrected pixels
to prediction features.

Use exactly script72's existing statistics: L*p10/median/p90/IQR and occupied
input-mask bounding-box half mean differences left−right/top−bottom. Same
OpenCV8bitLab conversion,linear percentiles,minimum1000total and100perhalf
pixels. Package them and verify parity with that historical helper. This is a
declared facial-statistics extension, not a new intrinsic-tone estimator;
earlier brightness experiments were unsuccessful on other data/targets.

Freeze eleven features (five retained plus all six additions), depth3/seed42/
leaf1, unweighted direct-gamma targets and existing15held-source folds. Fit one
tree per fold and evaluate its raw and fitting-control-protected outputs.
Compare against the saved protected five-feature direct-gamma baseline and no
correction on exactly the same masks/pixels. No feature subset,depth,threshold
or weight search. Protection uses fitting controls only. Hold all variants of
each source/duplicate group out together. If features are unavailable, retain
the failure and stop rather than silently dropping rows or imputing references.

Report all/clean/distorted errors, clean harm, interventions and parameter
predictions. The zero-clean-harm/overall-benefit gate remains necessary, and
sparse abstention is not a finished useful model. Preserve old negative
comparisons, concerns, clipping and weak MST limitations. This is repeatedly
exposed development evidence, not independent final testing. No automatic demo
schema expansion/preset change, new-mask admission or held-out-source access.
