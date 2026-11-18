# One benefit-gate retraining for split predictors — 6 November 2026

The user approves retraining benefit supervision for the changed split
corrector. Keep the12inputs, original10publisher-key folds, same420whole-scene
attempts,357correction-supervised rows and397gate-feature rows. Keep all targets,
images, borrowed masks, fixed gate settings and zero-logit threshold. No depth,
weight, feature, classifier or threshold search.

For outer key H and label key S, fit a gamma head and paired red/blue head
excluding H,S. Each of their fitting keys T receives MST from the previously
saved ridge excluding H,S,T. Predict S using MST excluding H,S. The strict
positive reduction in RGB8MAE versus unchanged input labels benefit1; ties/
harm label0. References supply training supervision only. Outer H outcomes
never enter those fits, labels or gate scaling.

Cache45two-key-excluded split pairs:90new head-tree fits. Reuse the120saved
three-key-excluded plus55saved one/two-key-excluded MST ridges; zero new MST
fits. Reuse the20saved outer head trees and all target fits; no new outer
corrector, masks, distortion generation or cohort admission. Fit up to10gates
with the unchanged fixed logistic/key-class-balanced procedure. If any training
key lacks a benefit class, record that gate unavailable/unchanged rather than
invent labels or omit the key.

Compare the new gate with the prior frozen joint-corrector gate applied to the
same split outputs, plus split ungated and unchanged input. Preserve14original
failures without scoring support and nine undefined-ITA fallbacks. Report
clean/core/stress errors and equal-key/perceptual means, harms, missed useful
corrections and mild-cast behavior; do not equate synthetic membership with
benefit. Inner trees use fewer fitting keys than the outer corrector, so labels
remain proxies whose transfer is tested, not assumed.

Verify cached ridge bindings/exclusions,45inner-pair training roles/head
normalization/raw leaf means,3573rendered inner labels, gate scaling/logits
and406outer outputs without refitting. Inspect all90fixed clean/core/stress
boards including three failure contexts. Freeze resulting artifacts and stop
after the one comparison. No automatic threshold retry, final all-data model,
new subject sample, app integration or acceptance of residual risk. Any broader
evaluation needs its own frozen candidate and source/group protocol. Private
research/noncommercial, citation and no-redistribution terms retain.
