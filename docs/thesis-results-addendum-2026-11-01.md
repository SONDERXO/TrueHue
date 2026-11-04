# Methods/results/discussion addendum — 1 November 2026

Evidence-based writing draft, to accompany the30October methods/results and
31October discussion drafts. Not inserted into the submitted paper, accepted
by a panel, or represented as final validation. Exact proposal pages still need
verification before a request-of-changes letter.

## Methods update

Development now separates correction support from measurement support.
Correction covers the selected whole face and associated visible neck, including
internal features and objects/hair inside the face outline, with explicit pixel
protections overriding it. Enclosed correction holes are filled and a fixed
inward smoothstep blends the combined face/neck outer edge. This avoids treating
anatomical measurement exclusions as uncorrected internal patches. Illustrative
preview parameters are not learned predictions.

Measurement retains selected facial skin/nose from a pretrained parser with
anatomical eye/brow/mouth exclusions and a conservative nasal-base guard. Neck
and correction alpha do not contribute to Lab/ITA/MST. Predicted classes do not
guarantee that every selected pixel is actual skin. These learned-mask and
support/rendering changes differ from the proposal's recorded rule-based stage;
the panel register tracks them separately from retained ITA/MST/tree scope.

An isolated FaceOcc visible-face veto was evaluated as an additional measurement
component. Its fixed MediaPipe five-anchor/template alignment is a documented
TrueHue adaptation rather than the upstream3DDFApreprocessing. The threshold and
model stayed fixed. The candidate is removal-only on the preferred measurement,
not a replacement for the correction tree and not generative skin recovery.
It remains preferred for experimental development, not deployed in the demos.

## Saved results

The matching nostril-excluded calibration attempted418photographs from15exposed
subjects;393measurements and25failures were retained. Subject-held ordinalMAE
was2.124682 and exact-category accuracy12.98%, versus same-row median-baseline
MAE2.854962 and exact accuracy13.99%. Lower ordinal error alongside worse exact
accuracy does not establish reliable ten-category mapping. No lookup adoption
or correction training followed.

The first FaceOcc diagnostic retained25attempts, with17outputs/eight prior
failures. Three of four premarked non-skin points were removed, while two of two
marked skin points remained; a beard mark persisted. These sparse exposed
diagnostics are not full-mask accuracy or an independent test.

The broader qualitative cycle retained24attempts, with18pairedoutputs and six
failures. A four-case human review preferred FaceOcc in two and rated two similar,
with no reported useful-skin loss in thosefour. Separate assistant inspection
of all18pairs identified possible cheek-skin loss and unresolved boundary/
occluder concerns. Dense annotation was not completed; the planned23-image task
was explicitly replaced with a lower-burden qualitative design.

An isolated service exactly replayed35saved successful aligned inputs, masks
and features across49attempts;14failures remained unavailable. This establishes
software consistency only. No calibration or correction admission was inferred.

## Application implementation

The Android application has actual local emulator execution evidence beyond
the scaffold: six native reliability tests and eighteen JVM tests passed in the
saved31October check. One fixed development example reproduced Python input,
mask and corrected pixels; gallery selection, failure reporting and image/report
export were exercised. Physical-phone/general-photo parity and performance
remain unestablished. The app uses the older experimental baseline5/fold1,
experimental lookup and rule-based mask, not FaceOcc or the new whole-face/neck
correction support. Reproducing a failed-quality baseline is not proof of
effective correction.

## Discussion and conclusion boundary

The evidence supports improved correction continuity, targeted reductions in
some unwanted measurement selections, and a reproducible software implementation.
It does not establish actual-skin accuracy in arbitrary gallery images, reliable
MST or effective final automatic correction. Four currently FaceOcc-measured
MST-E subjects cannot support the intended mapping; older measurements are
incompatible. Even the19subject inventory has singleton categories7/10.
No repeated small same-subject fit was run to disguise this limitation.

Retain the positive and negative results together. The legitimate conclusion is
that masking and implementation progressed while the central measurement/
mapping/correction validation remains incomplete. A working demo, software tests
or user preference is not a substitute for those scientific results. The
required ITA + calibrated MST + facial-statistics decision-tree method is
retained; no unlabelled proxy or dropped-MST substitution is adopted.
