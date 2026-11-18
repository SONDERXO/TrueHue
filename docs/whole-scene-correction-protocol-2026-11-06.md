# Whole-photograph distortion and scene-feature comparison

6November2026. User authorizes one paired experiment after the failed gate.
Apply the existing14-case/common-medium recipe matrix to each original224RGB
scene using all-one synthesis alpha, before the frozen native crop and256resize.
These controlled whole-image photometric perturbations are not calibrated
physical illumination or proof of real-camera realism. Retain all30originals,
10publisher keys,420attempts and the existing landmark failure/no replacement.

For29available originals, require that cropping/resizing their decoded original
scenes exactly replays saved clean input pixels and clean measured features.
Use saved measurement masks only for statistics, correction application and
scoring. Distortion affects the whole scene, but correction output remains
restricted to the256working measurement region; outside-mask pixels equal the
distorted input. Mask contamination remains, so this is not a guaranteed
object-protected full-face/neck output or input-derived-mask validation.

One fixed scene feature set from the distorted full224scene only:
natural log of(meanR+1)/(meanG+1), natural log of(meanB+1)/(meanG+1), OpenCV-L*
10th/50th/90thlinear percentiles, fraction of pixels with any RGB channel exactly
zero, and fraction with any RGB channel exactly255. The +1is a fixed code-value
stabilizer, not a fitted parameter; endpoint fractions are not physical clipping
truth. Seven features, no feature/region/threshold search. Scene statistics
depend on scene content as well as imposed transforms and may exploit the
release's studio acquisition; no causal illuminant claim.

Measure each distorted crop's own Lab/ITA under the original1000pixel guard.
Generate one new bounded target fit per nonclean available pair using retained
settings; clean neutral shortcut. Preserve target/feature failures. New recipes
and crops differ from prior restricted-region synthesis, so do not reuse its
targets or directly compare its error means as a feature-only improvement.

Run a matched pair on these new inputs/targets: original five features versus
five plus seven scene features. Both use original unweighted target-scaled
depth3/seed42/minleaf1trees and identical training membership. Reconstruct nested
MST features from the saved55ridges only after exact clean-feature parity is
verified; no source-label substitution, changed grouping or new MST fit.
Inner calibration excludes own+outer key; outer excludes held key. Clean-only
calibration versus synthetically distorted features remains distribution shift.

Fit20correction trees:10folds times2methods. No previous gate, balanced weights,
chroma features or unlimited depth. Retain allattempt denominators; failed
predictions are unchanged where support exists, and missing originals receive
no fabricated colour error. Report clean/core/stress MAE/CIEDE2000, equal-key
means, harms, clean identity, target failures and raw/clipped MST predictions.
Do not declare unseen-person accuracy, scientific admission or app readiness.

Freeze code/source/protocol hashes before new variants/fits. Save private full
scene inputs, working crops, features, targets, nested trace, models/predictions
and artifacts. Verify feature formulas, nested membership, both models' portable
predictions, renderer/outside-mask invariance and original-source hashes without
refitting. Inspect all29clean comparisons and two preselected combined-cool-under
and stress-combined-under cases for all30originals, including failure context.
Stop after this one matched comparison; no automatic nextfeature/gate/depth/model
sweep, expansion, runtime change or source sharing. Dataset private terms retain.
