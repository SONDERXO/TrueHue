# Joint log-colour candidate: engineering passed, photo usefulness untested

13 November 2026. User requested further methods research. **A distinct representation has positive generated response and is worth specifying for an exposed input-only audit. No real training recipe is qualified yet.** This is not a reopening of the failed ensemble or a trusted neutral-patch/cast detector.

[Protocol](joint-log-colour-generated-protocol-2026-11-13.md); src/model_training/joint_log_colour.py; scripts/check_joint_log_colour_generated.py; outputs/joint_log_colour_generated_v1. Barron ICCV2015primary PDF sections2–3 read: diagonal channel edits translate log-colour distributions. Our additional common-gamma scaling relation follows directly from logarithms for positive values. These encoded-RGBoperator relationships hold before rounding/clipping; no physical camera-response interpretation. We borrow the representation motivation, not its learned convolution/author implementation/benchmark performance.

One coarse16x16bilinearly accumulated joint histogram, range−2..2, uniform counts, whole-frame positiveRGBpixels, explicit availability/positivefraction/clippedfraction.259features, not appended to a model. This retains cross-channel joint occupancy rather than per-channel histogram gaps, a largest1DDFTpeak, luminanceNSS or LabIQR/covariance summary. The old22features are untouched. Scoped search found no prior implementation/trial; earlier ensemble proposal only cited Barron as an unselected route.

## Verified engineering

Exactly96generatedrecords:8scenes*4roles*3processingconditions, all independent scalar log/bin/bilinear/normalization replays.24,864values verified, maximum absolute scalar error3.808064974464287e-14 (limit1e-12 numerical only). Partition-of-unity/nonnegative occupancy, missingblack handling, unchanged inputs, duplication invariance and R/Btranspose verified. Three fixed positive RGBtriples passed the analytical edit relationships. Additional generated boundary/invalid-input checks passed: clipped coordinates versus scalar exact, three invalid arrays rejected. Generatedfixtures stay separate from scientific data.

The correlated/anticorrelated palettes have identical per-channel code histograms and means but distinct joint descriptors. This establishes retention of a relationship omitted by marginal statistics; it does not prove all old22feature vectors collide or incremental prediction value.

Native histogram L1response to mildcool red attenuation:

| Generated scene | Identity-to-cool L1 |
|---|---:|
|Neutral ramp|.305098|
|Correlated/anticorrelated palettes|.323364 each|
|Skin-like material palette (not a tone label)|.296449|
|Material/blue-background mixture|.258706|
|Zero-channel/positive mixture|.360069|
|Saturated palette|.293945|
|Prior-edited acceptable palette|.296522|

All8native scenes respond. Neutral gamma variants have identical histograms to neutral identity; nonneutral gamma changes the distribution. This is compatible with keeping the existing exposure cues and adding colour-context information, not standalone gamma inference or correct-direction prediction. No L1quality threshold was selected. None of these8identityinputs clipped coordinates; a separate generated extreme-ratio pair tests boundary clipping. All are arithmetic responses, not correction-benefit evidence.

## Limits and next gate

JPEG90changes29/32descriptors; down/upbilinearresize changes29/32. Maximum histogram L1difference reaches2 (small floating excess~3e-14), so processing may replace almost all occupied mass. This cannot be called processing-robust or merely an augmentation to ignore. Whole-frame backgrounds can dominate. Zero-channel exclusion is material: the zero-mixture fixture has only.1875positive fraction before processing. Already-red-edited acceptable identity exactly matches the material's newcool descriptor. Such collisions limit interpretation; they do not establish actual contradiction on photos or forbid imperfect features in a learned predictor.

The realistic hypothesis is that a learned predictor may use joint colour-distribution context with existing ITA/MST/exposure measurements. It is not a claim of universal added-edit identification. The fixed259feature addition would increase dimensionality substantially relative to40fitrows/10sources, raising overfitting concerns. A new training experiment is not justified solely by these responses or a published illuminant estimator.

Next defensible action is ONEseparately specified, hash-bound, input-only audit of exact44already-exposed development packs: finite/missing/clipping behavior, independence from oldfeatures/marginal summaries, quantized mild-colour responses, processing/content confounds and source-transfer limitations, with no fit or tuned cutoff. Do not decode references/masks or use paired differences as inference inputs. That audit has not been selected/executed by this result; it needs exact roster/support/code bindings and independent verification before a real read. No automatic bin/grid/normalization/selector/feature-subset rescue follows.

Root-polynomial calibration was reviewed and not selected: it learns cameraRGB-to-standardcolour conversion and exposure-scaling behavior, rather than directly supplying the unknown added edit for our photographic-reference task. This does not impose a chart/newcamera/RAW requirement on TrueHue.

No source photographs/cache arrays/raworiginals/final24/olderlocked bytes, new parser inference, model fits/predictions, runtime/Android/manuscript changes, dependencies/downloads or commit. Model unfinished/paper paused; closed failures, approved manual59807/ears and darker-skin bias priority retained. Generated palettes do not establish tone-aware benefit. November14target remains at risk; no completion promise.
