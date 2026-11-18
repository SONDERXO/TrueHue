# One nested correction-benefit gate — 6 November 2026

The user authorizes the benefit-aware decision experiment after the mistake
diagnosis. Freeze the design before fitting. Use the same whole-scene420attempts,
10publisher-key folds,12facial+scene inference features and saved outer
face-plus-scene depth3corrector. Compare with the saved synthetic-membership
scene gate on identical inputs, controls, support and availability. No new
photographs, distortion recipes, target fits, masks or role admissions.

Change the gate supervision only: apply-correction label1means that an inner
subject-held correction reduces RGB8MAE against its photographic reference;
label0means equal/worse error. Strict gain>0, no tuned margin. References are
used to construct training labels, never inference features. Real-world image
quality or intrinsic colour is not the target. Keep the same fixed logistic
settings,12features, weighted training-only standardization, equal key/class
mass and zero-logit decision boundary. No threshold or classifier search.

For outer key H and gate-training key S, train a label-generating correction
tree with both H and S excluded. Each row of its fitting key T receives MST
from a ridge excluding H,S,T. Its prediction on S uses an MST ridge excluding
H,S. Thus neither H nor S labels/references can enter that label-generating
corrector, its normalization or upstream estimator. Use the original fixed
depth3/seed42/minleaf1unweighted correction fitting procedure. Do not reuse
outer held benefit outcomes or in-sample correction residuals for supervision.

Cache identical exclusion sets:45two-key-excluded label-generating correction
trees and120three-key-excluded MST ridges. Reuse existing55one/two-key-excluded
MST ridges and all10outer correction trees. Fit up to10gates. No all-data model
or new tuning setting. The inner corrector uses fewer keys than the outer one;
its estimated benefit is a training proxy, not guaranteed outer-corrector gain.

Use all397available input-feature rows for gate labels even where a correction
target fit is unavailable; only the existing357rows with targets supervise
correction trees. If a gate-training key lacks either benefit class, record
that outer gate unavailable and return unchanged; do not invent labels or drop
the key to satisfy weighting. Other implementation failures must be reported.

Report operational clean/core/stress errors, equal-key means, clean false
corrections, missed useful corrections, avoided harmful corrections and applied
harm, plus synthetic-membership counts for comparison with the prior gate.
Keep14original failures unscored and nine undefined-ITA unchanged; unavailable
gates are not true negatives. Outer reference outcomes are evaluation only.

Verify exclusion sets/memberships at all three grouping levels, fitting-only
normalization, inner benefit labels by saved prediction replay, gate scaling
and linear prediction, and all406scored output replays. Inspect all29clean and
the two predeclared core/stress cases per original including failure contexts.
Stop after this comparison. No model adoption, threshold/feature/depth sweep,
automatic follow-up fit, runtime change, data sharing or source expansion.
Borrowed support, studio/chart acquisition cues and private terms remain.
